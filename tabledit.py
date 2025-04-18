from __future__ import annotations
import re, uuid, json

import streamlit as st
from sqlalchemy import create_engine, text, inspect

# ──────────────────────────────────────────────────────────────
# Safe rerun helper
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# ──────────────────────────────────────────────────────────────
# Database connection (Neon Postgres)
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()
inspector = inspect(engine)

# ──────────────────────────────────────────────────────────────
# Constants
TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

# ──────────────────────────────────────────────────────────────
# Block ↔ HTML serialization
def block_html(block: dict) -> str:
    t = block["type"]
    p = block["payload"]

    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0;">{p["text"]}</p>'
            f'<!--BLOCK_END-->'
        )
    if t == "youtube":
        url = p["url"].replace("watch?v=", "embed/")
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{url}" frameborder="0" allowfullscreen></iframe>'
            f'<!--BLOCK_END-->'
        )
    if t == "image":
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{p["url"]}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )
    if t == "embed":
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{p["url"]}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )
    # CSV → styled div
    lines = p["csv"].strip().splitlines()
    headers = lines[0].split(",") if lines else []
    rows = [r.split(",") for r in lines[1:]]
    table = "<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
    for r in rows:
        table += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    table += "</tbody></table>"

    return (
        f'<!--BLOCK_START:csv-->'
        f'<div style="color:{p["color"]};font-size:{p["size"]}px;">{table}</div>'
        f'<!--BLOCK_END-->'
    )

BLOCK_RGX = re.compile(
    r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S
)

def html_to_blocks(html: str) -> list[dict]:
    blocks: list[dict] = []
    for m in BLOCK_RGX.finditer(html or ""):
        t = m.group("type")
        content = m.group("html")

        if t == "text":
            m2 = re.search(
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*)</p>',
                content,
                re.S,
            )
            if m2:
                c, s, txt = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "text",
                    "payload": {"text": txt, "color": c, "size": int(s)}
                })

        elif t == "youtube":
            url = re.search(r'src="([^"]+)"', content).group(1)
            url = url.replace("embed/", "watch?v=")
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "youtube",
                "payload": {"url": url}
            })

        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "image",
                "payload": {"url": url}
            })

        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "embed",
                "payload": {"url": url}
            })

        elif t == "csv":
            m2 = re.search(
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</div>',
                content,
                re.S,
            )
            if m2:
                c, s, _ = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "csv",
                    "payload": {"csv": "", "color": c, "size": int(s)}
                })
    return blocks

# ──────────────────────────────────────────────────────────────
# Load & prime session_state
def load_row(table: str):
    q = text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(q).fetchone()

@st.cache_data(show_spinner=False)
def cached_load(table: str):
    return load_row(table)

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = cached_load(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id if row else None
        st.session_state["title_raw"] = row.title if row else ""
        st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# UI – Sidebar & Table Management
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

with st.sidebar:
    st.header("Section")
    chosen_table = st.selectbox("Table", TAB_NAMES)
    if st.button("Tables"):
        st.session_state["show_tables"] = True
    if st.session_state.get("show_tables") and st.button("Back to Editor"):
        st.session_state["show_tables"] = False

# ──────────────────────────────────────────────────────────────
# Show Table Editor if toggled
if st.session_state.get("show_tables"):
    st.subheader("🗄️ Manage Tables")
    tables = inspector.get_table_names()
    if not tables:
        st.info("No tables found.")
    else:
        tbl = st.selectbox("Select table to drop", tables, key="drop_tbl")
        confirm = st.checkbox(f"Confirm drop '{tbl}'", key="conf_drop")
        if st.button("🗑️ Drop Table", disabled=not confirm, key="drop_btn"):
            engine.execute(text(f"DROP TABLE IF EXISTS {tbl}"))
            st.success(f"Dropped table '{tbl}'.")
            st.experimental_rerun()
    st.stop()

# ──────────────────────────────────────────────────────────────
# Prime state for editor view
prime_state(chosen_table)

# ──────────────────────────────────────────────────────────────
# Title Editor
st.subheader("Title")
col1, col2, col3 = st.columns([3,1,1])
with col1:
    title_text = st.text_input("Text", st.session_state["title_raw"], key="title_txt")
with col2:
    title_color = st.color_picker("Color", "#000000", key="title_color")
with col3:
    title_size = st.number_input("Size(px)", 8,72,24, key="title_size")
raw_html = st.checkbox("Treat title as raw HTML", value=False, key="title_raw_html")

title_html = title_text if raw_html else f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_text}</h2>'


