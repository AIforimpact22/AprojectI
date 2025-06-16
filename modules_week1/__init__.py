import streamlit as st
from github_progress import get_user_progress, update_user_progress
from . import tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11
import re

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available.")

def parse_tab_title(title):
    m = re.match(r"(\d+(?:\.\d+)*)(.*)", title)
    if m:
        numbers = m.group(1)
        try:
            parts = tuple(map(int, numbers.split(".")))
        except Exception:
            parts = (0,)
        return parts
    return (0,)

def show():
    username = st.session_state.get("username", "default_user")
    week = 1
    user_prog = get_user_progress(username)
    progress = user_prog.get("week1", 0)
    if progress < 1:
        progress = 1

    # Define the list of hardcoded tabs for Week 1
    default_tabs = [
        ("1.1 Introduction to Python", tab1.show),
        ("1.2 You made it!", tab2.show),
        ("1.3 What is Python?", tab3.show),
        ("1.4 Python Script?", tab4.show),
        ("1.5 Libraries", tab5.show),
        ("1.6 Google Colab", tab6.show),
        ("1.7 Assignment 1", tab7.show),
        ("1.8 APIs", tab8.show),
        ("1.9 Assignment 2", tab9.show),
        ("1.10 Real-Time", tab10.show),
        ("1.11 Wrap Up", tab11.show)
    ]

    # Sort the tabs
    all_tabs_sorted = sorted(default_tabs, key=lambda x: parse_tab_title(x[0]))

    tab_titles = [t[0] for t in all_tabs_sorted]
    tab_funcs = [t[1] for t in all_tabs_sorted]

    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            if i < progress:
                tab_funcs[i]()
            else:
                st.info("This tab is locked. Please complete previous tabs to unlock.")

            # "Mark as Read" button on the last unlocked tab.
            if i == progress - 1 and progress < len(tab_titles):
                key = f"marking_week1_tab{i+1}"
                if key not in st.session_state:
                    st.session_state[key] = False
                if st.button("Mark as Read", key=f"week1_tab{i+1}", disabled=st.session_state[key]):
                    st.session_state[key] = True
                    update_user_progress(username, week, progress + 1)
                    st.info("Progress updated. Please click on the next tab to view the content.")
                    safe_rerun()

if __name__ == "__main__":
    show()
