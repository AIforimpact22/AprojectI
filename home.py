# app.py  – instrumented + circular-import–safe
import os
import time
import functools
import logging
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
#  Debug / instrumentation toggles
# ──────────────────────────────────────────────────────────────────────────────
DEBUG_SQL   = os.getenv("DEBUG_SQL", "1") == "1"   # default ON while testing
SHOW_SQL_UI = os.getenv("SHOW_SQL_UI", "0") == "1" # also show timings in sidebar

if DEBUG_SQL:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
    )

# ──────────────────────────────────────────────────────────────────────────────
#  Monkey-patch mysql-connector so every cursor.execute() is timed
# ──────────────────────────────────────────────────────────────────────────────
def _patch_mysql_execute() -> None:
    """Wrap mysql.connector.cursor.MySQLCursor.execute with a timer (once)."""
    if not DEBUG_SQL:
        return

    import mysql.connector
    if getattr(mysql.connector, "_timed_execute_patched", False):
        return   # already patched

    real_exec = mysql.connector.cursor.MySQLCursor.execute
    timings_key = "_sql_timings"

    def timed_exec(self, operation, params=None, multi=False):
        t0 = time.perf_counter()
        result = real_exec(self, operation, params=params, multi=multi)
        dur_ms = (time.perf_counter() - t0) * 1000

        # Console log
        logging.info("[SQL] %7.1f ms  %s", dur_ms,
                     (operation if isinstance(operation, str) else str(operation))
                     .split()[0])

        # Optional per-query list in Streamlit session state
        if SHOW_SQL_UI:
            st.session_state.setdefault(timings_key, []).append(
                (operation.split()[0], dur_ms)
            )
        return result

    mysql.connector.cursor.MySQLCursor.execute = timed_exec
    mysql.connector._timed_execute_patched = True


_patch_mysql_execute()  # must run *before* any DB query occurs

# ──────────────────────────────────────────────────────────────────────────────
#  Regular app imports (only those that do **not** create a circular import)
# ──────────────────────────────────────────────────────────────────────────────
from theme           import apply_dark_theme
from database        import create_tables      # now auto-timed
from sidebar         import show_sidebar
from style           import show_footer
from importlib       import import_module
from github_progress import get_user_progress


# ──────────────────────────────────────────────────────────────────────────────
#  Utility helpers (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available.")


def enforce_week_gating(selected: str) -> bool:
    """Return True if the user is allowed to open that week’s module."""
    if selected.startswith("modules_week"):
        try:
            week = int(selected.replace("modules_week", ""))
        except ValueError:
            return True
        if week == 1:
            return True
        required = {2: 10, 3: 12, 4: 12, 5: 7}
        username = st.session_state.get("username", "default_user")
        user_prog = get_user_progress(username)
        prev_key  = f"week{week-1}"
        return user_prog.get(prev_key, 0) >= required.get(week, 0)
    return True


# ──────────────────────────────────────────────────────────────────────────────
#  Main Streamlit app
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    page_start = time.perf_counter()   # ⏱ build timer

    st.set_page_config(
        page_title="Code for Impact",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_dark_theme()
    create_tables()                    # DB work (timed by patch)

    # Always have a page key
    st.session_state.setdefault("page", "offer")

    page      = st.session_state["page"]
    logged_in = st.session_state.get("logged_in", False)

    # ───────────────────────────────────────────────────────────────────────────
    # 1) Post-login flows
    # ───────────────────────────────────────────────────────────────────────────
    if logged_in:
        show_sidebar()

        if page == "logout":
            st.session_state["logged_in"] = False
            st.session_state["page"]      = "offer"
            safe_rerun()
            return

        if page == "home":
            # **Lazy import eliminates any circular dependency**
            import home as _home_module
            _home_module.show_home()
        else:
            if page.startswith("modules_week") and not enforce_week_gating(page):
                st.warning("You must complete the previous week before accessing this section.")
                st.stop()
            try:
                module = import_module(page)
                if hasattr(module, "show"):
                    module.show()
                else:
                    st.warning("The selected module does not have a 'show()' function.")
            except ImportError as e:
                st.warning(f"Unknown selection: {e}")

    # ───────────────────────────────────────────────────────────────────────────
    # 2) Pre-login flows
    # ───────────────────────────────────────────────────────────────────────────
    else:
        if page == "offer":
            import offer; offer.show()
        elif page == "login":
            import login; login.show_login_create_account()
        elif page == "loginx":
            st.warning("Course 2 Login is not available yet.")
            if st.button("Go Back"):
                st.session_state["page"] = "offer"
                safe_rerun()
        elif page == "course2_app":
            from second.appx import appx; appx.show()
        else:
            import login; login.show_login_create_account()

    # ───────────────────────────────────────────────────────────────────────────
    # 3) Footer (always)
    # ───────────────────────────────────────────────────────────────────────────
    show_footer()

    # ───────────────────────────────────────────────────────────────────────────
    # 4) Instrumentation output
    # ───────────────────────────────────────────────────────────────────────────
    total_ms = (time.perf_counter() - page_start) * 1000
    st.sidebar.info(f"⏱ Page build: {total_ms:.0f} ms")

    if SHOW_SQL_UI and "_sql_timings" in st.session_state:
        with st.sidebar.expander("SQL timings"):
            for verb, dur in st.session_state["_sql_timings"]:
                st.write(f"{verb:<6} {dur:,.1f} ms")


if __name__ == "__main__":
    main()
