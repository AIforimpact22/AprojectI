from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit
from streamlit_quill import st_quill
from streamlit_ace import st_ace

# ──────────────────────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.rerun()

@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

TAB_NAMES   = [
    "introtab1",
    "introtab2",
    "introtab3",
    # Week 1
    "w1tab1","w1tab2","w1tab3","w1tab4","w1tab5","w1tab6","w1tab7","w1tab8","w1tab9","w1tab10","w1tab11",
    # Week 2
    "w2tab1","w2tab2","w2tab3","w2tab4","w2tab5","w2tab6","w2tab7","w2tab8","w2tab9","w2tab10","w2tab11","w2tab12",
    # Week 3
    "w3tab1","w3tab2","w3tab3","w3tab4","w3tab5","w3tab6","w3tab7","w3tab8","w3tab9","w3tab10","w3tab11","w3tab12",
    # Week 4
    "w4tab1","w4tab2","w4tab3","w4tab4","w4tab5","w4tab6","w4tab7",
    # Week 5
    "w5tab1","w5tab2","w5tab3","w5tab4","w5tab5","w5tab6","w5tab7","w5tab8",
]
BLOCK_TYPES = {
    "Text":        "text",
    "Image URL":   "image",
    "CSV → Table": "csv",
    "Text/Rich":   "rich",
    "Text/HTML":   "html",
    "Video URL":   "video",
}

# (helper functions omitted for brevity; unchanged) ...

# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()

if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    # List pages as buttons instead of dropdown
    for table_name in TAB_NAMES:
        if st.sidebar.button(table_name):
            st.session_state["chosen_table"] = table_name
            safe_rerun()

    # Default to first page if none selected yet
    if "chosen_table" not in st.session_state:
        st.session_state["chosen_table"] = TAB_NAMES[0]

    chosen = st.session_state["chosen_table"]
    prime_state(chosen)

    # Title management (unchanged)
    if st.session_state.get("clear_title_input"):
        for k in ("title_txt","title_color","title_size","title_raw_html","clear_title_input"):
            st.session_state.pop(k, None)
    st.subheader("Title")
    c1,c2,c3 = st.columns([3,1,1])
    with c1:
        st.text_input("Text", st.session_state["title_raw"], key="title_txt")
    with c2:
        st.color_picker("Color", "#000000", key="title_color")
    with c3:
        st.number_input("Size(px)", 8,72,24, key="title_size")
    raw = st.checkbox("Raw HTML", value=False, key="title_raw_html")
    title_html = (
        st.session_state["title_txt"] if raw
        else f'<h2 style="color:{st.session_state["title_color"]};'
             f'font-size:{st.session_state["title_size"]}px;">'
             f'{st.session_state["title_txt"]}</h2>'
    )
    u_col, d_col = st.columns([1,1])
    with u_col:
        if st.button("🔄 Update Title"):
            update_title_db(chosen, title_html)
            st.success("Title updated.")
            safe_rerun()
    with d_col:
        if st.button("🗑️ Delete Title"):
            delete_title_db(chosen)
            st.session_state["clear_title_input"] = True
            st.success("Title deleted.")
            safe_rerun()

    st.markdown("---")
    st.subheader("🧩 Content Blocks")
    # ... (rest of content-block management unchanged) ...

    if st.button("💾 Save All"):
        update_content_db(chosen)
        st.success("All content saved.")
        safe_rerun()

    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(title_html, unsafe_allow_html=True)
    live_html = "<br>".join(
        p for p in (block_html(b) for b in st.session_state["blocks"]) if p
    )
    st.markdown(live_html, unsafe_allow_html=True)
