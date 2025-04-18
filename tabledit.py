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
TAB_NAMES = [
    "introtab1", "introtab2", "introtab3",
    "w1tab1", "w1tab2", "w1tab3", "w1tab4", "w1tab5", "w1tab6", "w1tab7", "w1tab8", "w1tab9", "w1tab10", "w1tab11",
    "w2tab1", "w2tab2", "w2tab3", "w2tab4", "w2tab5", "w2tab6", "w2tab7", "w2tab8", "w2tab9", "w2tab10", "w2tab11", "w2tab12",
    "w3tab1", "w3tab2", "w3tab3", "w3tab4", "w3tab5", "w3tab6", "w3tab7", "w3tab8", "w3tab9", "w3tab10", "w3tab11", "w3tab12",
    "w4tab1", "w4tab2", "w4tab3", "w4tab4", "w4tab5", "w4tab6", "w4tab7",
    "w5tab1", "w5tab2", "w5tab3", "w5tab4", "w5tab5", "w5tab6", "w5tab7", "w5tab8"
]

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
