# tabledit.py
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()
TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]

def main():
    st.subheader("🔧 Table Editor")
    table = st.selectbox("Select table", TAB_NAMES)
    rows = engine.connect().execute(
        text(f"SELECT id, title, content FROM {table} ORDER BY id")
    ).fetchall()

    if not rows:
        return st.info("⚠️ No rows in this table.")

    for row in rows:
        st.markdown(f"**Table:** `{table}` • **Row ID:** {row.id}")
        # strip HTML for title preview
        plain = row.title
        plain = plain.split(">", 1)[-1].rsplit("<", 1)[0]
        st.write(f"**Title:** {plain}")
        st.markdown("**Live preview:**")
        st.markdown(row.content, unsafe_allow_html=True)

        if st.button(f"🗑️ Delete row {row.id}", key=f"del-{table}-{row.id}"):
            engine.begin().execute(
                text(f"DELETE FROM {table} WHERE id = :id"), {"id": row.id}
            )
            st.success(f"Deleted row {row.id}.")
            st.experimental_rerun()

        st.markdown("---")
