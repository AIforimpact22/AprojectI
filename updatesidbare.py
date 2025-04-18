# updatesidbare.py
import streamlit as st

def navigation() -> str:
    st.sidebar.header("📂 admin")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        content_manager = st.button("Content Manager")
    with col2:
        table_editor = st.button("Table Editor")
    
    if table_editor:
        st.session_state.current_page = "Table Editor"
    else:
        st.session_state.current_page = "Content Manager"
    
    return st.session_state.get("current_page", "Content Manager")
