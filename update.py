# update.py
from __future__ import annotations
import re, uuid, json

import streamlit as st
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# ───── Safe rerun helper ─────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# ───── DB connection ─────
@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

# ───── Constants ─────
TAB_NAMES   = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

# ───── HTML serialization ─────
def ensure_https(u: str) -> str:
    return u if u.startswith(("http://","https://")) else "https://" + u

def block_html(b: dict) -> str:
    t = b["type"]; p = b["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p><!--BLOCK_END-->'
        )
    if t == "youtube":
        url = ensure_https(p["url"]).replace("watch?v=", "embed/")
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{url}" '
            f'frameborder="0" allowfullscreen></iframe><!--BLOCK_END-->'
        )
    if t == "image":
        url = ensure_https(p["url"])
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{url}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )
    if t == "embed":
        url = ensure_https(p["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )
    # CSV
    lines  = p["csv"].strip().splitlines()
    headers= lines[0].split(",") if lines else []
    rows   = [r.split(",") for r in lines[1:]]
    tbl    = "<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
    for r in rows:
        tbl += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    tbl += "</tbody></table>"
    return (
        f'<!--BLOCK_START:csv-->'
        f'<div style="color:{p["color"]};font-size:{p["size"]}px;">{tbl}</div>'
        f'<!--BLOCK_END-->'
    )

BLOCK_RGX = re.compile(
    r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S
)

def html_to_blocks(html: str) -> list[dict]:
    out = []
    for m in BLOCK_RGX.finditer(html or ""):
        t = m.group("type"); c = m.group("html")
        uid = str(uuid.uuid4())
        if t == "text":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>', c, re.S)
            if m2:
                col,size,txt = m2.groups()
                out.append({"uid":uid,"type":"text","payload":{"text":txt,"color":col,"size":int(size)}})
        elif t in ("youtube","image","embed"):
            url = re.search(r'src="([^"]+)"', c).group(1)
            if t=="youtube": url=url.replace("embed/","watch?v=")
            out.append({"uid":uid,"type":t,"payload":{"url":url}})
        elif t=="csv":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px', c, re.S)
            col,size = m2.groups() if m2 else ("#000000","16")
            out.append({"uid":uid,"type":"csv","payload":{"csv":"","color":col,"size":int(size)}})
    return out

# ───── Title parsing & load ─────
TITLE_RGX = re.compile(r'<h2 style="color:(#[0-9A-Fa-f]{6});font-size:(\d+)px;">(.*?)</h2>', re.S)
@st.cache_data
def load_row(table: str):
    row = engine.connect().execute(
        text(f"SELECT id,title,content FROM {table} ORDER BY id LIMIT 1")
    ).fetchone()
    return row

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = load_row(table)
        st.session_state["table"]      = table
        st.session_state["row_id"]     = row.id if row else None
        raw = row.title if row else ""
        m = TITLE_RGX.search(raw or "")
        if m:
            st.session_state["title_color"], st.session_state["title_size"], st.session_state["title_plain"] = (
                m.group(1), int(m.group(2)), m.group(3)
            )
            st.session_state["title_html"] = raw
        else:
            st.session_state["title_color"] = "#000000"
            st.session_state["title_size"]  = 24
            st.session_state["title_plain"] = raw
            st.session_state["title_html"]  = f'<h2 style="color:#000000;font-size:24px;">{raw}</h2>'
        st.session_state["blocks"] = html_to_blocks(row.content) if row else []

# ───── Save helpers ─────
def save_title():
    new_html = f'<h2 style="color:{st.session_state["new_title_color"]};' \
               f'font-size:{st.session_state["new_title_size"]}px;">' \
               f'{st.session_state["new_title_txt"]}</h2>'
    engine.begin().execute(
        text(f"UPDATE {st.session_state['table']} SET title=:t WHERE id=:id"),
        {"t": new_html, "id": st.session_state["row_id"]}
    )
    st.success("Title updated")
    safe_rerun()

def save_blocks():
    html = "".join(block_html(b) for b in st.session_state["blocks"])
    engine.begin().execute(
        text(f"UPDATE {st.session_state['table']} SET content=:c WHERE id=:id"),
        {"c": html, "id": st.session_state["row_id"]}
    )
    st.success("Blocks saved")
    safe_rerun()

# ───── Main ─────
st.set_page_config(layout="wide")
mode = navigation()

if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    # Title preview & edit
    st.subheader("Title Preview")
    st.write(st.session_state["title_plain"])

    with st.expander("🖉 Edit Title", expanded=False):
        st.session_state["new_title_txt"]   = st.text_input(
            "Text", st.session_state["title_plain"], key="new_title_txt"
        )
        st.session_state["new_title_color"] = st.color_picker(
            "Color", st.session_state["title_color"], key="new_title_color"
        )
        st.session_state["new_title_size"]  = st.number_input(
            "Size(px)", 8, 72, st.session_state["title_size"], key="new_title_size"
        )
        if st.button("⚙️ Update Title"):
            save_title()

    # Blocks
    st.subheader("🧩 Blocks")
    c1, c2 = st.columns([3,1])
    with c1:
        new_type = st.selectbox("Add block…", list(BLOCK_TYPES.keys()), key="new_type")
    with c2:
        if st.button("➕ Add"):
            uid = str(uuid.uuid4())
            t = BLOCK_TYPES[new_type]
            payload = {"text":"","color":"#000000","size":16} if t=="text" else (
                      {"url":""} if t in ("youtube","image","embed") else
                      {"csv":"col1,col2\nr1c1,r1c2","color":"#000000","size":16})
            st.session_state["blocks"].append({"uid":uid,"type":t,"payload":payload})

    for idx, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        with st.expander(f"Block {idx+1} – {blk['type']}", expanded=False):
            if blk["type"] == "text":
                blk["payload"]["text"]  = st.text_area("Text", blk["payload"]["text"], key=f"text_{uid}")
                blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{uid}")
                blk["payload"]["size"]  = st.slider("Size(px)", 8,48, blk["payload"]["size"], key=f"size_{uid}")
            elif blk["type"] in ("youtube","image","embed"):
                label = "Image URL" if blk["type"]=="image" else "URL"
                blk["payload"]["url"] = st.text_input(label, blk["payload"]["url"], key=f"url_{uid}")
            else:  # csv
                blk["payload"]["csv"]   = st.text_area("CSV", blk["payload"]["csv"], key=f"csv_{uid}")
                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                blk["payload"]["size"]  = st.slider("Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{uid}")

            col_del, col_upd = st.columns([1,1])
            if col_del.button("🗑️ Delete", key=f"del_{uid}"):
                st.session_state["blocks"].pop(idx)
                save_blocks()
            if col_upd.button("⚙️ Update", key=f"upd_{uid}"):
                save_blocks()

    st.markdown("---")
    if st.button("💾 Save All Blocks"):
        save_blocks()

    # Final preview
    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(st.session_state["title_html"], unsafe_allow_html=True)
    st.markdown("".join(block_html(b) for b in st.session_state["blocks"]), unsafe_allow_html=True)
