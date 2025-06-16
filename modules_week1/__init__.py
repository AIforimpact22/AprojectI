import streamlit as st
import os
import re
import importlib.util
from github_progress import get_user_progress, update_user_progress

# Use absolute imports instead of relative
import modules_week1.tab1 as tab1
import modules_week1.tab2 as tab2
import modules_week1.tab3 as tab3
import modules_week1.tab4 as tab4
import modules_week1.tab5 as tab5
import modules_week1.tab6 as tab6
import modules_week1.tab7 as tab7
import modules_week1.tab8 as tab8
import modules_week1.tab9 as tab9
import modules_week1.tab10 as tab10

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available.")

def parse_tab_title(title):
    """
    Extracts a numeric tuple from the beginning of the title.
    E.g., "1.1 Introduction to Python" -> (1, 1)
          "1.1.1 New" -> (1, 1, 1)
    """
    m = re.match(r"(\d+(?:\.\d+)*)(.*)", title)
    if m:
        numbers = m.group(1)
        try:
            parts = tuple(map(int, numbers.split(".")))
        except Exception:
            parts = (0,)
        return parts
    return (0,)

def load_update_tabs():
    """
    Loads update tabs for Week 1 from the updates folder.
    Uses importlib.util to load modules directly from the file location.
    Each update module should define a variable TAB_TITLE.
    """
    update_tabs = []
    updates_folder = os.path.join(os.getcwd(), "updates")
    if os.path.isdir(updates_folder):
        for file in os.listdir(updates_folder):
            if file.startswith("tab") and file.endswith(".py"):
                if file.endswith("update.py"):
                    filepath = os.path.join(updates_folder, file)
                    sanitized_module_name = file[:-3].replace('.', '_')
                    try:
                        spec = importlib.util.spec_from_file_location(sanitized_module_name, filepath)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        if hasattr(mod, "show"):
                            title = getattr(mod, "TAB_TITLE", None)
                            if title and title.startswith("1."):
                                update_tabs.append((title, mod.show))
                    except Exception as e:
                        st.error(f"Error loading {file}: {e}")
    return update_tabs

def show():
    username = st.session_state.get("username", "default_user")
    week = 1
    user_prog = get_user_progress(username)
    progress = user_prog.get("week1", 0)
    if progress < 1:
        progress = 1

    # Default hardcoded tabs
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
    ]

    # Load update tabs for Week 1.
    update_tabs = load_update_tabs()

    # Merge default and update tabs.
    all_tabs = default_tabs + update_tabs

    # Sort tabs
    all_tabs_sorted = sorted(all_tabs, key=lambda x: parse_tab_title(x[0]))
    tab_titles = [t[0] for t in all_tabs_sorted]
    tab_funcs = [t[1] for t in all_tabs_sorted]

    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            if i < progress:
                tab_funcs[i]()
            else:
                st.info("This tab is locked. Please complete previous tabs to unlock.")

            # Mark as Read
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
