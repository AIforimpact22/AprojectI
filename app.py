import streamlit as st
from theme import apply_dark_themeMore actions
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
    """
    Enforces that a weekly module is accessible only if the previous week is fully completed.
    For example, if Week 1 has 10 tabs, then Week 2 will be unlocked only if the user's progress
    for "week1" is 10. Similarly, Week 3 will be unlocked only if "week2" progress is 12, etc.
    """
    if selected.startswith("modules_week"):
        try:
            week = int(selected.replace("modules_week", ""))
        except ValueError:
            return True  # Allow if the format is invalid.
            return True
        if week == 1:
            return True  # Week 1 is always accessible.
        # Define required progress for previous weeks.
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

    # Add the 'updates' folder to sys.path so that modules within it can be imported.
    updates_path = os.path.abspath("updates")
    if os.path.isdir(updates_path) and updates_path not in sys.path:
        sys.path.append(updates_path)
    
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
            # Use gating logic based on GitHub progress.
            if not enforce_week_gating(selected):
                st.warning("You must complete the previous week before accessing this section.")
                st.stop()
            try:
                # First, try importing the module with the given name.
                try:
                    module = import_module(selected)
                except ImportError:
                    # If not found, try importing from the updates folder.
                    module = import_module("updates." + selected)
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
