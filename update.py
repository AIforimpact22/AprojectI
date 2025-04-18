# update.py
from __future__ import annotations
import re, uuid, json
from urllib.parse import urlparse, parse_qs

import streamlit as st
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# 0. Safe rerun helper
# Avoids AttributeError on some Streamlit builds

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# 1. DB connection
@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )
engine = get_engine()

# 2. Constants
TAB_NAMES   = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

# 3. Serialization / parsing

def ensure_https(u: str) -> str:
    return u if u.startswith(("http://", "https://")) else "https://" + u


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
            f'<iframe width="560" height="315" src="{youtube_embed(p["url"])}" frameborder="0" allowfullscreen></iframe>'
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
    # CSV → wrap table in styled div
    lines = p["csv"].strip().splitlines()
    hdrs = lines[0].split(",") if lines else []
    rows = [r.split(",") for r in lines[1:]]
    table = (
        "<table><thead><tr>" +
        "".join(f"<th>{h}</th>" for h in hdrs) +
        "</tr></thead><tbody>"
    )
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
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>',
                content,
                re.S,
            )
            if m2:
                c, s, txt = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "text",
                    "payload": {"text": txt, "color": c, "size": int(s)},
                })
        elif t == "youtube":
            url = re.search(r'src="([^"]+)"', content).group(1).replace("embed/", "watch?v=")
            blocks.append({"uid": str(uuid.uuid4()), "type":"youtube", "payload":{"url": url}})
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":str(uuid.uuid4()), "type":"image", "payload":{"url": url}})
        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":str(uuid.uuid4()), "type":"embed", "payload":{"url": url}})
        elif t == "csv":
            m2 = re.search(
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px',
                content,
            )
            if m2:
                c, s = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "csv",
                    "payload": {"csv": "", "color": c, "size": int(s)},
                })
    return blocks

# 4. Load & prime session_state
@st.cache_data(show_spinner=False)
def load_row(table: str):
    with engine.connect() as conn:
        return conn.execute(
            text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
        ).fetchone()

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

# Main
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()
if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    st.title("✏️ Edit Title")
    c1, c2, c3 = st.columns([3, 1, 1])
    title_txt = st.text_input("Text", st.session_state["title_raw"], key="title_txt")
    title_color = st.color_picker("Color", "#000000", key="title_color")
    title_size = st.number_input("Size(px)", 8, 72, 24, key="title_size")
    raw_html = st.checkbox("Treat as raw HTML", value=False, key="title_raw_html")
    title_html = title_txt if raw_html else f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_txt}</h2>'

    # Content Blocks
    st.subheader("🧩 Content Blocks")
    a1, a2 = st.columns([3, 1])
    new_type = a1.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
    if a2.button("➕ Add Block", key="add"):
        uid = str(uuid.uuid4())
        t = BLOCK_TYPES[new_type]
        payload = {"text": "", "color": "#000000", "size": 16} if t == "text" else ({"url": ""} if t in ("youtube", "image", "embed") else {"csv": "header1,header2\nrow1,row2", "color": "#000000", "size": 16})
        st.session_state["blocks"].append({"uid": uid, "type": t, "payload": payload})

    to_delete = None
    for idx, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        exp_key = f"exp_{uid}"
        colA, colB, colC, colD = st.columns([5, 1, 1, 1])
        colA.markdown(f"**Block {idx+1} – {blk['type']}**")
        if colB.button("🖉 Edit", key=f"edit-{uid}"):
            st.session_state[exp_key] = not st.session_state.get(exp_key, False)
        if colC.button("🗑️ Delete", key=f"del-{uid}"):
            to_delete = idx
        if colD.button("✔︎ Update", key=f"upd-{uid}"):
            st.session_state[exp_key] = False
            safe_rerun()

        with st.expander("", expanded=st.session_state.get(exp_key, False)):
            if blk["type"] == "text":
                blk["payload"]["text"] = st.text_area("Text", blk["payload"]["text"], key=f"text_{uid}")
                blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{uid}")
                blk["payload"]["size"] = st.slider("Size(px)", 8, 48, blk["payload"]["size"], key=f"size_{uid}")
            elif blk["type"] in ("youtube", "image", "embed"):  # URL inputs
                label = "Image URL" if blk["type"] == "image" else "URL"
                blk["payload"]["url"] = st.text_input(label, blk["payload"]["url"], key=f"url_{uid}")
            else:  # CSV
                blk["payload"]["csv"] = st.text_area("CSV", blk["payload"]["csv"], key=f"csv_{uid}")
                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                blk["payload"]["size"] = st.slider("Font Size(px)", 8, 48, blk["payload"]["size"], key=f"csv_size_{uid}")

        st.markdown("---")

    if to_delete is not None:
        st.session_state["blocks"].pop(to_delete)

    if st.button("💾 Save / Update", key="save"):
        full_html = "".join(block_html(b) for b in st.session_state["blocks"])
        with engine.begin() as conn:
            if st.session_state["row_id"]:
                conn.execute(
                    text(f"UPDATE {chosen} SET title=:t,content=:c WHERE id=:id"),
                    {"t": title_html, "c": full_html, "id": st.session_state["row_id"]},
                )
            else:
                conn.execute(
                    text(f"INSERT INTO {chosen}(title,content)VALUES(:t,:c)"),
                    {"t": title_html, "c": full_html},
                )
        st.success("Saved ✔︎ – refreshing…")
        safe_rerun()

    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown("".join(block_html(b) for b in st.session_state["blocks"]), unsafe_allow_html=True)
