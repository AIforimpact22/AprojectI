# modules_week1/tab1.py
import streamlit as st
from db import get_engine
from sqlalchemy import text

def show():
    engine = get_engine()
    row = engine.connect().execute(
        text("SELECT title, content FROM w1tab1 LIMIT 1")
    ).fetchone()

    if row:
        # Title saved as raw HTML <h2>…</h2>
        st.markdown(row.title, unsafe_allow_html=True)
        # Content is the concatenated blocks
        st.markdown(row.content, unsafe_allow_html=True)
    else:
        st.info("No content has been published yet.")
