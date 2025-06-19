# app.py
import os, time, functools, logging
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
#  Debug / instrumentation toggles
# ──────────────────────────────────────────────────────────────────────────────
DEBUG_SQL   = os.getenv("DEBUG_SQL", "1") == "1"   # default **on** for testing
SHOW_SQL_UI = os.getenv("SHOW_SQL_UI", "0") == "1" # log to page as well as console

if DEBUG_SQL:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%H:%M:%S",
    )

# ──────────────────────────────────────────────────────────────────────────────
#  Monkey-patch mysql.connector to time every query
# ──────────────────────────────────────────────────────────────────────────────
def _patch_mysql_execute():
    """Wrap mysql.connector.cursor.MySQLCursor.execute with a timer."""

    if not DEBUG_SQL:
        return                              # skip entirely in prod

    import mysql.connector
    if getattr(mysql.connector, "_sql_patched", False):
        return                              # only patch once

    original_execute = mysql.connector.cursor.MySQLCursor.execute
    timings_key      = "_sql_timings"

    def timed_execute(self, operation, params=None, multi=False):
        t0 = time.perf_counter()
        result = original_execute(self, operation, params=params, multi=multi)
        dur_ms = (time.perf_counter() - t0) * 1000

        # Console log
        logging.info("[SQL] %6.1f ms  %s", dur_ms,
                     (operation if isinstance(operation, str) else str(operation))
                     .split()[0])

        # Optional on-page log
        if SHOW_SQL_UI:
            st.session_state.setdefault(timings_key, []).append(
                (operation.split()[0], dur_ms)
            )

        return result

    mysql.connector.cursor.MySQLCursor.execute = timed_execute
    mysql.connector._sql_patched = True


_patch_mysql_execute()              # patch as soon as possible, before imports below

# ──────────────────────────────────────────────────────────────────────────────
#  Regular app imports
# ──────────────────────────────────────────────────────────────────────────────
from theme import apply_dark_theme
from database import create_tables      # <- queries now get timed automatically
from sidebar import show_sidebar
from home import show_home
from style import show_footer
from importlib import import_module
from github_progress import get_user_progress



# ──────────────────────────────────────────────────────────────────────────────
#  Helpers unchanged
# ──────────────────────────────────────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available.")


def enforce_week_gating(selected):
    if selected.startswith("modules_week"):
        try:
            week = int(selected.replace("modules_week", ""))
        except ValueError:
            return True
        if week == 1:
            return True
        required_progress = {2: 10, 3: 12, 4: 12, 5: 7}
        username        = st.session_state.get("username", "default_user")
        user_prog       = get_user_progress(username)
        prev_week_key   = f"week{week-1}"
        prev_progress   = user_prog.get(prev_week_key, 0)
        return prev_progress >= required_progress.get(week, 0)
    return True


# ──────────────────────────────────────────────────────────────────────────────
#  Main app with page-build stopwatch
# ──────────────────────────────────────────────────────────────────────────────
def main():
    page_start = time.perf_counter()          # ⏱️ start

    st.set_page_config(
        page_title="Code for Impact",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_dark_theme()
    create_tables()                           # all its SQL is now timed

    if "page" not in st.session_state:
        st.session_state["page"] = "offer"

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
            show_home()
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
                st.warning("Unknown selection: " + str(e))

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
    page_ms = (time.perf_counter() - page_start) * 1000
    st.sidebar.info(f"⏱️ Page build: {page_ms:.0f} ms")

    if SHOW_SQL_UI and "_sql_timings" in st.session_state:
        with st.sidebar.expander("SQL timings"):
            for verb, dur in st.session_state["_sql_timings"]:
                st.write(f"{verb:<6} {dur:,.1f} ms")


if __name__ == "__main__":
    main()
