import streamlit as st
from importlib import import_module

def show():
    try:
        from .tab1 import show as show_tab1
        from .tab2 import show as show_tab2
        from .tab3 import show as show_tab3
        
        tab1, tab2, tab3 = st.tabs(["Welcome", "Course Instructions", "Stay Connected"])
        with tab1: show_tab1()
        with tab2: show_tab2()
        with tab3: show_tab3()
    except Exception as e:
        st.error(f"Error loading introduction module: {str(e)}")
        st.warning("Please report this issue to support.")
