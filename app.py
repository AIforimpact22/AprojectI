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
import streamlit as st

def show_sidebar():
    # Custom CSS for sidebar styling (removed animated title CSS)
    st.markdown("""
        <style>
        /* Sidebar container padding */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f0f2f6;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
        
        /* Button styling */
        .stButton button {
            background-color: transparent;
            border: 1px solid #4ECDC4;
            color: #4ECDC4;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background-color: #4ECDC4;
            color: white;
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        # Display logo above the sidebar content.
        st.image("logo.jpg", use_container_width=True)

        # Home section
        with st.expander("🏠 HOME", expanded=False):
            if st.button("Home Page", key="home", use_container_width=True):
                st.session_state["page"] = "home"

        # Modules section
        with st.expander("📘 MODULES", expanded=False):
            if st.button("Introduction", key="modules_intro", use_container_width=True):
                st.session_state["page"] = "modules_intro"
            if st.button("Week 1: Introduction to Coding", key="modules_week1", use_container_width=True):
                st.session_state["page"] = "modules_week1"
            if st.button("Week 2: Generate Comprehensive Codings", key="modules_week2", use_container_width=True):
                st.session_state["page"] = "modules_week2"
            if st.button("Week 3: Deploy App through Github and Streamlit", key="modules_week3", use_container_width=True):
                st.session_state["page"] = "modules_week3"
            if st.button("Week 4: Data Week", key="modules_week4", use_container_width=True):
                st.session_state["page"] = "modules_week4"
            if st.button("Week 5: Finalizing and Showcasing Your Personalized Project", key="modules_week5", use_container_width=True):
                st.session_state["page"] = "modules_week5"

        # Help section
        with st.expander("❓ HELP", expanded=False):
            if st.button("Help Center", key="help", use_container_width=True):
                st.session_state["page"] = "help"

        # Logout section
        with st.expander("🚪 LOGOUT", expanded=False):
            if st.button("Logout", key="logout", use_container_width=True):
                st.session_state["page"] = "logout"

    # Return the currently selected page or default to "home"
    return st.session_state.get("page", "home") 
