import streamlit as st
from theme import apply_dark_theme
from database import create_tables
from sidebar import show_sidebar
from home import show_home
from style import show_footer
from importlib import import_module
from github_progress import get_user_progress
import sys
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
    st.set_page_config(page_title="Code for Impact", layout="wide")
    apply_dark_theme()
    create_tables()

    if "page" not in st.session_state:
        st.session_state["page"] = "offer"

    if st.session_state.get("logged_in", False):
        show_sidebar()
        selected = st.session_state.get("page", "home")

        if selected == "logout":
            st.session_state["logged_in"] = False
            st.session_state["page"] = "offer"
            safe_rerun()
        elif selected == "home":
            show_home()
        else:
            if not enforce_week_gating(selected):
                st.warning("You must complete the previous week before accessing this section.")
                st.stop()
            try:
                # Only try to import directly from selected module name
                module = import_module(selected)
                if hasattr(module, "show"):
                    module.show()
                else:
                    st.warning("The selected module does not have a 'show()' function.")
            except ImportError as e:
                st.warning("Unknown selection: " + str(e))
    else:
        if st.session_state["page"] == "offer":
            import offer
            offer.show()
        elif st.session_state["page"] == "login":
            import login
            login.show_login_create_account()
        elif st.session_state["page"] == "loginx":
            st.warning("Course 2 Login is not available yet.")
            if st.button("Go Back"):
                st.session_state["page"] = "offer"
                safe_rerun()
        elif st.session_state["page"] == "course2_app":
            from second.appx import appx
            appx.show()
        else:
            import login
            login.show_login_create_account()

    show_footer()

if __name__ == "__main__":
    main()                    
