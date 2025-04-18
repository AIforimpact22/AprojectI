# db.py
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource
def get_engine():
    conn = st.secrets["postgres"]["connection_string"]
    return create_engine(conn, pool_pre_ping=True, isolation_level="AUTOCOMMIT")
