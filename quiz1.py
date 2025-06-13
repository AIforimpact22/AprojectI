import streamlit as st
import sys
from pathlib import Path
from github_progress import get_user_progress, update_user_progress
from . import tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10

# Add project root to Python path for quiz1.py access
sys.path.append(str(Path(__file__).parent.parent))
import quiz1  # Import from root directory

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available.")

def show():
    username = st.session_state.get("username", "default_user")
    week = 1
    user_prog = get_user_progress(username)
    progress = user_prog.get("week1", 0)
    
    # Initialize progress to at least 1
    if progress < 1:
        progress = 1

    # Updated tab structure with Quiz1
    tab_titles = [
        "1.1 Introduction to Python",
        "1.2 You made it!",
        "1.3 What is Python?",
        "1.4 Python Script?",
        "1.5 Libraries",
        "1.6 Google Colab",
        "1.7 Assignment 1",
        "1.8 APIs",
        "1.9 Assignment 2",
        "1.10 Real-Time",
        "1.11 Quiz1"  # New quiz tab
    ]

    tab_funcs = [
        tab1.show, tab2.show, tab3.show, tab4.show, tab5.show,
        tab6.show, tab7.show, tab8.show, tab9.show, tab10.show,
        quiz1.show  # Quiz function from root
    ]

    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            # Content visibility control
            if i < progress:
                tab_funcs[i]()  # Show tab content
            else:
                st.info("This tab is locked. Please complete previous tabs to unlock.")

            # Progress update mechanism
            if i == progress - 1 and progress < len(tab_titles):
                session_key = f"marking_week1_tab{i+1}"
                
                # Initialize marking state
                if session_key not in st.session_state:
                    st.session_state[session_key] = False
                
                # Create marked button with state management
                if st.button(
                    "Mark as Read",
                    key=f"week1_tab{i+1}",
                    disabled=st.session_state[session_key]
                ):
                    st.session_state[session_key] = True
                    update_user_progress(username, week, progress + 1)
                    st.info("Progress updated. Please click the next tab.")
                    safe_rerun()

if __name__ == "__main__":
    show()
