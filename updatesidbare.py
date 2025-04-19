# updatesidbare.py
import streamlit as st

def navigation() -> str:
    st.sidebar.header("📂 admin")
    col1, col2 = st.sidebar.columns(2)
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Content Manager"
    
    with col1:
        if st.button("Content Manager"):
            st.session_state.current_page = "Content Manager"
    with col2:
        if st.button("Table Editor"):
            st.session_state.current_page = "Table Editor"
    
    return st.session_state.current_page
