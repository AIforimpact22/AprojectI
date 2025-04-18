# utils/db.py
import streamlit as st
from sqlalchemy import create_engine, text
from typing import Tuple, Optional

@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

def fetch_content(table_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (title_html, content_html) from the first row of `table_name`,
    or (None, None) if the table is empty.
    """
    engine = get_engine()
    q = text(f"SELECT title, content FROM {table_name} ORDER BY id LIMIT 1")
    with engine.connect() as conn:
        row = conn.execute(q).fetchone()
    if row:
        return row.title, row.content
    return None, None
