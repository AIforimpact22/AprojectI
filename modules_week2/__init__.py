import streamlit as st
from github_progress import get_user_progress, update_user_progress
from . import tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12
import os
import re
import importlib.util

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
    For example:
      "2.1 Breaking Down Scripts!" -> (2, 1)
      "2.10 Some Title" -> (2, 10)
      Non-numeric titles like "the Scale up Week" or "Assignment 3" are handled separately.
    """
    if title == "the Scale up Week":
        return (0, 0)  # Ensure this appears first
    elif title.startswith("Assignment"):
        # Assignments should appear after numbered tabs
        return (999, int(title.split(" ")[-1]))  # Assign a high number to ensure they appear last
    else:
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
    Loads update tabs for Week 2 from the updates folder.
    Each update module should define a variable TAB_TITLE that starts with "2.".
    """
    update_tabs = []
    updates_folder = os.path.join(os.getcwd(), "updates")
    if os.path.isdir(updates_folder):
        for file in os.listdir(updates_folder):
            if file.endswith("update.py"):
                filepath = os.path.join(updates_folder, file)
                # Create a sanitized module name (replace dots with underscores)
                sanitized_module_name = file[:-3].replace('.', '_')
                try:
                    spec = importlib.util.spec_from_file_location(sanitized_module_name, filepath)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "show"):
                        # Retrieve TAB_TITLE from the module.
                        title = getattr(mod, "TAB_TITLE", None)
                        if title and title.startswith("2."):
                            update_tabs.append((title, mod.show))
                except Exception as e:
                    st.error(f"Error loading {file}: {e}")
    return update_tabs

def show():
    username = st.session_state.get("username", "default_user")
    week = 2
    user_prog = get_user_progress(username)
    progress = user_prog.get("week2", 0)
    if progress < 1:
        progress = 1

    # Default hardcoded tabs as defined in your original code.
    default_tabs = [
        ("the Scale up Week", tab1.show),
        ("2.1 Breaking Down Scripts!", tab2.show),
        ("2.2 Quiz", tab3.show),
        ("2.3 Scale up scripts", tab4.show),
        ("2.4 Merging & Reversing", tab5.show),
        ("2.5 G.C for Researchers", tab6.show),
        ("2.6 Case Study", tab7.show),
        ("2.7 Limitations of G.C", tab8.show),
        ("2.8 Google Sheets API", tab9.show),
        ("2.9 GitHub for webapp", tab10.show),
        ("Assignment 3", tab11.show),
        ("Assignment 4", tab12.show)
    ]
    
    # Load update tabs for Week 2.
    update_tabs = load_update_tabs()

    # Merge default and update tabs.
    all_tabs = default_tabs + update_tabs

    # Sort all tabs by the numeric tuple extracted from their titles.
    all_tabs_sorted = sorted(all_tabs, key=lambda x: parse_tab_title(x[0]))

    tab_titles = [t[0] for t in all_tabs_sorted]
    tab_funcs = [t[1] for t in all_tabs_sorted]

    tabs = st.tabs(tab_titles)

    for i, tab in enumerate(tabs):
        with tab:
            if i < progress:
                # Call the function to display content.
                tab_funcs[i]()
            else:
                st.info("This tab is locked. Please complete previous tabs to unlock.")

            # "Mark as Read" button on the last unlocked tab.
            if i == progress - 1 and progress < len(tab_titles):
                key = f"marking_week2_tab{i+1}"
                if key not in st.session_state:
                    st.session_state[key] = False
                if st.button("Mark as Read", key=f"week2_tab{i+1}", disabled=st.session_state[key]):
                    st.session_state[key] = True
                    update_user_progress(username, week, progress + 1)
                    st.info("Progress updated. Please click on the next tab to view the content.")
                    safe_rerun()

if __name__ == "__main__":
    show()
