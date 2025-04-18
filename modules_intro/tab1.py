# modules_intro/tab1.py
import streamlit as st
from utils.db import fetch_content

TABLE_NAME = "introtab1"   # ← the actual table name in Neon

def show():
    title_html, content_html = fetch_content(TABLE_NAME)

    if title_html:
        st.markdown(title_html, unsafe_allow_html=True)
    else:
        st.info("No title set yet.")

    if content_html:
        st.markdown(content_html, unsafe_allow_html=True)
    else:
        st.info("No content yet.")
