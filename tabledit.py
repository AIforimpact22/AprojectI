# tabledit.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# DB connection
# ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def list_tables():
    return ["intro"] + [f"tab{i}" for i in range(1, 51)]

def fetch_rows(table: str) -> pd.DataFrame:
    df = pd.read_sql(text(f"SELECT * FROM {table} ORDER BY id"), engine)
    return df

def delete_row(table: str, row_id: int):
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": row_id})

# ──────────────────────────────────────────────────────────────
# UI
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Table Editor", layout="wide")
st.title("🗂️ Table Browser & Row Deleter")

with st.sidebar:
    st.header("Manage Tables")
    if st.button("Show tables"):
        st.session_state.show = True
    if st.session_state.get("show"):
        table = st.selectbox("Select table", list_tables(), key="table_sel")

if st.session_state.get("show"):
    df = fetch_rows(table)
    st.subheader(f"Contents of `{table}`")
    st.dataframe(df)

    st.markdown("### Delete a row")
    delete_id = st.number_input("Row ID to delete", min_value=1, step=1, key="del_id")
    if st.button(f"🗑️ Delete ID={delete_id}", key="del_btn"):
        delete_row(table, delete_id)
        st.success(f"Deleted row {delete_id} from {table}")
        st.experimental_rerun()
