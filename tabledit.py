# tabledit.py
import re
import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()
TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]

def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]*>", "", html or "")

def main():
    st.subheader("🔧 Table Editor")

    table = st.selectbox("Select table to manage", TAB_NAMES)
    if not table:
        return

    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT id, title, content FROM {table} ORDER BY id")).fetchall()

    if not rows:
        st.info("⚠️ No rows in this table.")
        return

    for row in rows:
        plain_title = strip_tags(row.title)
        st.markdown(f"**Table:** `{table}` — **Row ID:** {row.id}")
        st.markdown(f"**Title:** {plain_title}")
        st.markdown("**Live content preview:**")
        st.markdown(row.content or "", unsafe_allow_html=True)

        if st.button(f"🗑️ Delete row {row.id}", key=f"del-{table}-{row.id}"):
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": row.id})
            st.success(f"Deleted row {row.id} from `{table}`.")
            st.experimental_rerun()

        st.markdown("---")

if __name__ == "__main__":
    main()
