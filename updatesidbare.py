# updatesidbare.py
import streamlit as st

def navigation() -> str:
    st.sidebar.header("📂 Navigation")
    return st.sidebar.radio("", ["Content Manager", "Table Editor"], index=0)
