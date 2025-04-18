# update.py
from __future__ import annotations
import re, uuid, json
from urllib.parse import urlparse, parse_qs

import streamlit as st
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# Safe rerun helper
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# Database connection
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )
engine = get_engine()

# Constants
TAB_NAMES   = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

# Serialization / Parsing

def ensure_https(u: str) -> str:
    return u if u.startswith(("http://","https://")) else "https://" + u


def youtube_embed(u: str) -> str:
    url = ensure_https(u)
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        vid = parsed.path.lstrip("/")
    else:
        vid = parse_qs(parsed.query).get("v", [None])[0]
    return f"https://www.youtube.com/embed/{vid}" if vid else url


def block_html(block: dict) -> str:
    t = block["type"]
    p = block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">{p["text"]}</p>'
            f'<!--BLOCK_END-->'
        )
    if t == "youtube":
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{youtube_embed(p["url"])}" '
            f'frameborder="0" allowfullscreen></iframe>'
            f'<!--BLOCK_END-->'
        )
    if t == "image":
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{ensure_https(p["url"])}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )
    if t == "embed":
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{ensure_https(p["url"])}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )
    # CSV → wrap table
    lines = p["csv"].strip().splitlines()
    headers = lines[0].split(",") if lines else []
    rows = [r.split(",") for r in lines[1:]]
    table = '<table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>'
    for r in rows:
        table += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
    table += '</tbody></table>'
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
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>', content, re.S)
            if m2:
                c, s, txt = m2.groups()
                blocks.append({"uid":str(uuid.uuid4()),"type":"text","payload":{"text":txt,"color":c,"size":int(s)}})
        elif t == "youtube":
            url = re.search(r'src="([^"]+)"', content).group(1).replace("embed/","watch?v=")
            blocks.append({"uid":str(uuid.uuid4()),"type":"youtube","payload":{"url":url}})
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":str(uuid.uuid4()),"type":"image","payload":{"url":url}})
        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":str(uuid.uuid4()),"type":"embed","payload":{"url":url}})
        elif t == "csv":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px', content)
            if m2:
                c, s = m2.groups()
                blocks.append({"uid":str(uuid.uuid4()),"type":"csv","payload":{"csv":"","color":c,"size":int(s)}})
    return blocks

# Load / prime state
@st.cache_data(show_spinner=False)
def load_row(table: str):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT id,title,content FROM {table} ORDER BY id LIMIT 1")).fetchone()

def strip_html_tags(raw: str) -> str:
    return re.sub(r'<[^>]+>', '', raw)

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = load_row(table)
        st.session_state.update({
            "table": table,
            "row_id": row.id if row else None,
            "title_raw": strip_html_tags(row.title) if row else "",
            "blocks": html_to_blocks(row.content) if row else [],
        })

# Main app
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()
if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    # Title editing with Edit/Update
    title_txt = st.session_state.get("title_txt", st.session_state["title_raw"])
    title_color = st.session_state.get("title_color", "#000000")
    title_size = st.session_state.get("title_size", 24)
    raw_html_flag = st.session_state.get("title_raw_html", False)

    st.subheader("Title")
    col_disp, col_edit, col_upd = st.columns([6,1,1])
    col_disp.markdown(f"**{st.session_state['title_raw']}**")
    if col_edit.button("🖉 Edit Title"):
        st.session_state['edit_title'] = True
    if col_upd.button("✔︎ Update Title"):
        st.session_state['title_raw'] = title_txt
        st.session_state['edit_title'] = False

    with st.expander("Edit Title", expanded=st.session_state.get('edit_title', False)):
        title_txt = st.text_input("Text", title_txt, key="title_txt")
        title_color = st.color_picker("Color", title_color, key="title_color")
        title_size = st.number_input("Size(px)", 8,72,title_size, key``` (truncated due to length)
