import streamlit as st
from theme import apply_dark_theme
from database import create_tables
from sidebar import show_sidebar
from home import show_home
from style import show_footer
from importlib import import_module
from github_progress import get_user_progress
import os

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
        username = st.session_state.get("username", "default_user")
        user_prog = get_user_progress(username)
        prev_week_key = f"week{week-1}"
        prev_progress = user_prog.get(prev_week_key, 0)
        return prev_progress >= required_progress.get(week, 0)
    return True

def main():
    # ⚙️ Force sidebar expanded on load
    st.set_page_config(
        page_title="Code for Impact",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_dark_theme()
    create_tables()

    # — ensure a page is set
    if "page" not in st.session_state:
        st.session_state["page"] = "offer"

    page      = st.session_state["page"]
    logged_in = st.session_state.get("logged_in", False)

    # —───────────────────────────────────────────────────────────────────────────
    # 1) Render sidebar unconditionally
    # —───────────────────────────────────────────────────────────────────────────
    show_sidebar()

    # —───────────────────────────────────────────────────────────────────────────
    # 2) Handle logout immediately
    # —───────────────────────────────────────────────────────────────────────────
    if page == "logout":
        st.session_state["logged_in"] = False
        st.session_state["page"]      = "offer"
        safe_rerun()
        return

    # —───────────────────────────────────────────────────────────────────────────
    # 3) Home page
    # —───────────────────────────────────────────────────────────────────────────
    if page == "home":
        show_home()

    # —───────────────────────────────────────────────────────────────────────────
    # 4) Not-logged-in flow
    # —───────────────────────────────────────────────────────────────────────────
    elif not logged_in:
        if page == "offer":
            import offer
            offer.show()

        elif page == "login":
            import login
            login.show_login_create_account()

        elif page == "loginx":
            st.warning("Course 2 Login is not available yet.")
            if st.button("Go Back"):
                st.session_state["page"] = "offer"
                safe_rerun()

        elif page == "course2_app":
            from second.appx import appx
            appx.show()

        else:
            import login
            login.show_login_create_account()

    # —───────────────────────────────────────────────────────────────────────────
    # 5) Logged-in & modules flow
    # —───────────────────────────────────────────────────────────────────────────
    else:
        # module gating
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

    # —───────────────────────────────────────────────────────────────────────────
    # 6) Footer
    # —───────────────────────────────────────────────────────────────────────────
    show_footer()


if __name__ == "__main__":
    main()
