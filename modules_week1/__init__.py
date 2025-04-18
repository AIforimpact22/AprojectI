import streamlit as st
 from github_progress import get_user_progress, update_user_progress
 from . import tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11
 import os
 import re
 import importlib.util
 
 def safe_rerun():
     """
     Reruns the Streamlit app using the available rerun functionality.
     """
     if hasattr(st, "experimental_rerun"):
         st.experimental_rerun()
     elif hasattr(st, "rerun"):
 @@ -31,94 +34,103 @@
 
 def load_update_tabs():
     """
     Loads update tabs for Week 1 from the updates folder.
     Each update module should define a variable TAB_TITLE (a string starting with "1.")
     and a function show() that renders the content.
     Dynamically loads update tabs for Week 1 from the updates folder.
     Each update module should be in the folder 'modules_week1/updates' and must define:
       - TAB_TITLE (a string starting with "1.")
       - show() function to render its content.
       
     The update module is imported using its full package name so that any relative imports inside
     work properly.
     """
     update_tabs = []
     # Use the directory of this file as the base to locate the updates folder.
     # Locate the updates folder relative to this file.
     base_dir = os.path.dirname(__file__)
     updates_folder = os.path.join(base_dir, "updates")
     
     if os.path.isdir(updates_folder):
         for file in os.listdir(updates_folder):
             if file.endswith("update.py"):
                 filepath = os.path.join(updates_folder, file)
                 # Create a sanitized module name (replace dots with underscores)
                 sanitized_module_name = file[:-3].replace('.', '_')
                 # Construct the module name using the package name. __package__ is "modules_week1".
                 module_name = f"{__package__}.updates.{file[:-3]}"
                 try:
                     spec = importlib.util.spec_from_file_location(sanitized_module_name, filepath)
                     spec = importlib.util.spec_from_file_location(module_name, filepath)
                     if spec is None or spec.loader is None:
                         st.error(f"Could not load spec for {file}.")
                         continue
                     mod = importlib.util.module_from_spec(spec)
                     spec.loader.exec_module(mod)
                     # Check that the module provides both a show function and a valid TAB_TITLE.
                     
                     # Validate that the update module has a TAB_TITLE and show() function.
                     if hasattr(mod, "show") and hasattr(mod, "TAB_TITLE"):
                         title = getattr(mod, "TAB_TITLE")
                         if isinstance(title, str) and title.startswith("1."):
                             update_tabs.append((title, mod.show))
                         else:
                             st.warning(f"Module {file} has an invalid TAB_TITLE. It should be a string starting with '1.'")
                     else:
                         st.warning(f"Module {file} does not have required attributes 'show' and 'TAB_TITLE'.")
                 except Exception as e:
                     st.error(f"Error loading {file}: {e}")
     return update_tabs
 
 def show():
     """
     Shows the Week 1 content with default and update tabs. The user’s progress is used to lock/unlock tabs.
     """
     username = st.session_state.get("username", "default_user")
     week = 1
     user_prog = get_user_progress(username)
     progress = user_prog.get("week1", 0)
     if progress < 1:
         progress = 1
 
     # Default hardcoded tabs.
     # Hardcoded default tabs.
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
         ("1.11 Quiz 1", tab11.show)
     ]
 
     # Load update tabs for Week 1.
     # Load dynamic update tabs.
     update_tabs = load_update_tabs()
 
     # Merge default and update tabs.
     all_tabs = default_tabs + update_tabs
 
     # Sort all tabs by the numeric tuple extracted from their titles.
     all_tabs_sorted = sorted(all_tabs, key=lambda x: parse_tab_title(x[0]))
 
     tab_titles = [t[0] for t in all_tabs_sorted]
     tab_funcs = [t[1] for t in all_tabs_sorted]
 
     tabs = st.tabs(tab_titles)
 
     # Display the content for each tab.
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
