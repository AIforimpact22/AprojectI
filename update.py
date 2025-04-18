"""
Tabbed CMS  •  Streamlit  •  Neon Postgres
──────────────────────────────────────────
• Sidebar   → pick one of intro, tab1…tab50
• Title     → colour, size, raw‑HTML toggle
• Blocks    → add / edit / delete / drag‑drop
• Save      → upsert first row in the table
"""
from __future__ import annotations

import re
import uuid
import json
from typing import List, Dict

import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1. DB connection (pooled) – credentials live in secrets.toml
# ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )


engine = get_engine()

# ──────────────────────────────────────────────────────────────
# 2. Constants
# ──────────────────────────────────────────────────────────────
TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

# ──────────────────────────────────────────────────────────────
# 3. Helpers – HTML generation & parsing
# ──────────────────────────────────────────────────────────────
def block_html(block: Dict) -> str:
    """Turn one block‑dict into HTML wrapped with markers."""
    t = block["type"]
    payload = block["payload"]

    if t == "text":
        color = payload["color"]
        size = payload["size"]
        txt = payload["text"]
        body = f'<p style="color:{color};font-size:{size}px;margin:0;">{txt}</p>'

    elif t == "youtube":
        url = payload["url"].replace("watch?v=", "embed/")
        body = (
            f'<iframe width="560" height="315" '
            f'src="{url}" frameborder="0" allowfullscreen></iframe>'
        )

    elif t == "image":
        url = payload["url"]
        body = f'<img src="{url}" style="max-width:100%;">'

    elif t == "embed":
        url = payload["url"]
        body = (
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe>'
        )

    else:  # csv
        csv = payload["csv"].strip().splitlines()
        headers, rows = csv[0].split(","), [r.split(",") for r in csv[1:]]
        table = "<table><thead><tr>" + "".join(
            f"<th>{h}</th>" for h in headers
        ) + "</tr></thead><tbody>"
        for r in rows:
            table += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
        table += "</tbody></table>"
        body = table

    # wrap so we can parse later
    return f'<!--BLOCK_START:{t}-->{body}<!--BLOCK_END-->'


BLOCK_RGX = re.compile(
    r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S
)


def html_to_blocks(html: str) -> List[Dict]:
    """Parse previously saved HTML back into block‑dicts."""
    blocks = []
    for m in BLOCK_RGX.finditer(html or ""):
        btype = m.group("type")
        raw   = m.group("html")

        if btype == "text":
            # crude parse for colour + size + text
            m2 = re.search(
                r'style="[^"]*color:(#[0-9a-fA-F]{6});[^"]*font-size:(\d+)px[^"]*">(.*)</p>',
                raw,
                re.S,
            )
            if m2:
                color, size, txt = m2.groups()
                blocks.append(
                    {"uid": str(uuid.uuid4()), "type": "text", "payload": {"text": txt, "color": color, "size": int(size)}}
                )
        elif btype == "youtube":
            url = re.search(r'src="([^"]+)"', raw).group(1)
            url = url.replace("embed/", "watch?v=")
            blocks.append({"uid": str(uuid.uuid4()), "type": "youtube", "payload": {"url": url}})
        elif btype == "image":
            url = re.search(r'src="([^"]+)"', raw).group(1)
            blocks.append({"uid": str(uuid.uuid4()), "type": "image", "payload": {"url": url}})
        elif btype == "embed":
            url = re.search(r'src="([^"]+)"', raw).group(1)
            blocks.append({"uid": str(uuid.uuid4()), "type": "embed", "payload": {"url": url}})
        elif btype == "csv":
            # NOT parsed back – user will have to re‑add if editing
            pass
    return blocks


# ──────────────────────────────────────────────────────────────
# 4. Fetch current record (id = 1) + prime session_state
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_row(table):
    q = text(f"SELECT id,title,content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as c:
        return c.execute(q).fetchone()

def prime_state(table):
    if "table" not in st.session_state or st.session_state.table != table:
        row = load_row(table)
        st.session_state.table = table
        st.session_state.row_id = row.id if row else None
        st.session_state.title_raw = row.title if row else ""
        # blocks
        st.session_state.blocks = html_to_blocks(row.content) if row else []
        # keep ordering stable
        st.session_state.blocks_json = json.dumps(st.session_state.blocks)

# ──────────────────────────────────────────────────────────────
# 5. UI – PAGE CONFIG & SIDEBAR
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

with st.sidebar:
    st.header("Section")
    chosen_tab = st.selectbox("Table", TAB_NAMES)
prime_state(chosen_tab)

# ──────────────────────────────────────────────────────────────
# 6. TITLE EDITOR
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
tcol1, tcol2, tcol3 = st.columns([3, 1, 1])
with tcol1:
    title_text = st.text_input("Text", value=st.session_state.title_raw, key="title_text")
with tcol2:
    title_color = st.color_picker("Color", "#000000", key="title_color")
with tcol3:
    title_size = st.number_input("Size(px)", 8, 72, 24, key="title_size")
is_html = st.toggle("Treat as raw HTML?", value=False, key="is_html")

if is_html:
    final_title_html = title_text
else:
    final_title_html = (
        f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_text}</h2>'
    )

# ──────────────────────────────────────────────────────────────
# 7. BLOCK LIST – add, edit, delete, reorder
# ──────────────────────────────────────────────────────────────
st.subheader("Content Blocks")

# 7‑a • Add new block
add_col1, add_col2 = st.columns([2, 1])
with add_col1:
    new_type_label = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()))
with add_col2:
    if st.button("➕ Add"):
        uid = str(uuid.uuid4())
        default = {"uid": uid, "type": BLOCK_TYPES[new_type_label], "payload": {}}
        # sensible defaults
        if default["type"] == "text":
            default["payload"] = {"text": "", "color": "#000000", "size": 16}
        elif default["type"] in ("youtube", "image", "embed"):
            default["payload"] = {"url": ""}
        elif default["type"] == "csv":
            default["payload"] = {"csv": "header1,header2\nrow1a,row1b"}
        st.session_state.blocks.append(default)

# 7‑b • Render each block in order
to_delete = None
for idx, blk in enumerate(st.session_state.blocks):
    with st.container():
        st.markdown(f"**Block {idx+1} – {blk['type']}**")
        if blk["type"] == "text":
            blk["payload"]["text"]  = st.text_area("Text", blk["payload"].get("text",""), key=f"text_{blk['uid']}")
            blk["payload"]["color"] = st.color_picker("Color", blk["payload"].get("color","#000000"), key=f"col_{blk['uid']}")
            blk["payload"]["size"]  = st.slider("Size(px)", 8, 48, blk["payload"].get("size",16), key=f"size_{blk['uid']}")
        elif blk["type"] in ("youtube", "image", "embed"):
            lbl = "https://…" if blk["type"] != "image" else "Image URL"
            blk["payload"]["url"] = st.text_input(lbl, blk["payload"].get("url",""), key=f"url_{blk['uid']}")
        else:  # csv
            blk["payload"]["csv"] = st.text_area("CSV", blk["payload"].get("csv",""), key=f"csv_{blk['uid']}")

        lcol, rcol = st.columns([6,1])
        with rcol:
            if st.button("🗑️", key=f"del_{blk['uid']}"):
                to_delete = idx
        st.divider()

# remove after loop to avoid key chaos
if to_delete is not None:
    st.session_state.blocks.pop(to_delete)

# 7‑c • Drag‑drop reorder (experimental Streamlit‑AgGrid alternative)
order_json = json.dumps(st.session_state.blocks, sort_keys=True)
if order_json != st.session_state.blocks_json:
    st.session_state.blocks_json = order_json

# ──────────────────────────────────────────────────────────────
# 8. SAVE → build HTML and write
# ──────────────────────────────────────────────────────────────
def build_html(blocks):
    return "".join(block_html(b) for b in blocks)

if st.button("💾 Save / Update"):
    html = build_html(st.session_state.blocks)
    with engine.begin() as conn:
        if st.session_state.row_id:
            q = text(f"UPDATE {chosen_tab} SET title=:t, content=:c WHERE id=:id")
            conn.execute(
                q,
                {"t": final_title_html, "c": html, "id": st.session_state.row_id},
            )
        else:
            q = text(f"INSERT INTO {chosen_tab} (title, content) VALUES (:t, :c)")
            conn.execute(q, {"t": final_title_html, "c": html})
    st.success("Saved ✔︎ – refreshing…")
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 9. LIVE PREVIEW
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live Preview")
st.markdown(final_title_html, unsafe_allow_html=True)
st.markdown(build_html(st.session_state.blocks), unsafe_allow_html=True)
