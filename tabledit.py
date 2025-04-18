# tabledit.py
import streamlit as st
from sqlalchemy import create_engine, text, inspect

# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()
inspector = inspect(engine)

st.set_page_config(page_title="Table Editor", layout="wide")
st.title("🗄️ Table Editor")

# Sidebar: pick table to delete
with st.sidebar:
    st.header("Delete a Table")
    tables = inspector.get_table_names()
    if not tables:
        st.info("No tables found.")
    else:
        tbl = st.selectbox("Select table", tables, key="sel_table")
        confirm = st.checkbox(f"Confirm deletion of '{tbl}'", key="confirm_delete")
        if st.button("🗑️ Drop Table", disabled=not confirm):
            engine.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
            st.success(f"Table '{tbl}' dropped.")
            # refresh inspector cache
            st.experimental_rerun()

# Main: show current tables
st.subheader("Current Tables")
st.write(inspector.get_table_names())
