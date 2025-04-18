# update.py
from __future__ import annotations
import re, uuid, json
from urllib.parse import urlparse, parse_qs

import streamlit as st
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# 0. Safe rerun helper
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# 1. DB connection\ n@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )
engine = get_engine()

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {"Text": "text", "YouTube URL": "youtube", "Image URL": "image", "Embed URL": "embed", "CSV → Table": "csv"}

def strip_html_tags(raw: str) -> str:
    return re.sub(r'<[^>]+>', '', raw)

def ensure_https(url: str) -> str:
    return url if url.startswith(("http://", "https://")) else "https://" + url

def youtube_embed(url: str) -> str:
    u = ensure_https(url)
    p = urlparse(u)
    if "youtu.be" in p.netloc:
        vid = p.path.lstrip("/")
    else:
        params = parse_qs(p.query)
        vid = params.get("v", [None])[0]
    return f"https://www.youtube.com/embed/{vid}" if vid else u

def block_html(block: dict) -> str:
    t = block["type"]
    p = block["payload"]
    if t == "text":
        return f'<!--BLOCK_START:text--><p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">{p["text"]}</p><!--BLOCK_END-->'
    if t == "youtube":
        emb = youtube_embed(p["url"])
        return f'<!--BLOCK_START:youtube--><iframe width="560" height="315" src="{emb}" frameborder="0" allowfullscreen></iframe><!--BLOCK_END-->'
    if t == "image":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    if t == "embed":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:embed--><iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe><!--BLOCK_END-->'
    # CSV
    lines = p["csv"].strip().splitlines()
    headers = lines[0].split(",") if lines else []
    rows = [r.split(",") for r in lines[1:]]
    table_html = "<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
    for r in rows:
        table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    table_html += "</tbody></table>"
    return f'<!--BLOCK_START:csv--><div style="color:{p["color"]};font-size:{p["size"]}px;">{table_html}</div><!--BLOCK_END-->'

BLOCK_RGX = re.compile(r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S)

def html_to_blocks(html: str) -> list[dict]:
    blocks: list[dict] = []
    for m in BLOCK_RGX.finditer(html or ""):
        t = m.group("type")
        content = m.group("html")
        if t == "text":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>', content, re.S)
            if m2:
                c, s, txt = m2.groups()
                blocks.append({"uid": str(uuid.uuid4()), "type": "text", "payload": {"text": txt, "color": c, "size": int(s)}})
        elif t == "youtube":
            url = re.search(r'src="([^"]+)"', content).group(1).replace("embed/", "watch?v=")
            blocks.append({"uid": str(uuid.uuid4()), "type": "youtube", "payload": {"url": url}})
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid": str(uuid.uuid4()), "type": "image", "payload": {"url": url}})
        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid": str(uuid.uuid4()), "type": "embed", "payload": {"url": url}})
        elif t == "csv":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</div>', content, re.S)
            if m2:
                c, s, _ = m2.groups()
                blocks.append({"uid": str(uuid.uuid4()), "type": "csv", "payload": {"csv": "", "color": c, "size": int(s)}})
    return blocks

@st.cache_data(show_spinner=False)
def load_row(table: str):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")).fetchone()

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = load_row(table)
        st.session_state["table"] = table
        st.session_state["row_id"] = row.id if row else None
        st.session_state["title_raw"] = strip_html_tags(row.title) if row else ""
        st.session_state["title_html"] = row.title if row else ""
        st.session_state["blocks"] = html_to_blocks(row.content) if row else []

# Main
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()
if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    # Title Section
    st.subheader("📝 Title")
    st.markdown(f"**Current Title:** {st.session_state['title_raw']}")
    if st.button("🖉 Edit Title"):
        st.session_state['edit_title'] = True
    if st.session_state.get('edit_title', False):
        new_txt = st.text_input("Title Text", value=st.session_state['title_raw'], key="title_edit_txt")
        new_color = st.color_picker("Color", "#000000", key="title_edit_color")
        new_size = st.number_input("Size (px)", 8,72,24, key="title_edit_size")
        new_raw = st.checkbox("Treat as raw HTML", value=False, key="title_edit_raw")
        if st.button("⚙️ Update Title"):
            html_val = new_txt if new_raw else f'<h2 style="color:{new_color};font-size:{new_size}px;">{new_txt}</h2>'
            with engine.begin() as conn:
                if st.session_state['row_id']:
                    conn.execute(text(f"UPDATE {chosen} SET title=:t WHERE id=:id"), {"t": html_val, "id": st.session_state['row_id']})
                else:
                    conn.execute(text(f"INSERT INTO {chosen} (title,content) VALUES (:t,'')"), {"t": html_val})
            safe_rerun()

    # Block Editor
    st.subheader("🧩 Content Blocks")
    c1,c2 = st.columns([3,1])
    new_bt = c1.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_bt")
    if c2.button("➕ Add Block", key="add_blk"):
        uid = str(uuid.uuid4()); bt = BLOCK_TYPES[new_bt]
        payload = {"text":"","color":"#000000","size":16} if bt=="text" else ({"url":""} if bt in ("youtube","image","embed") else {"csv":"header1,header2\nrow1,row2","color":"#000000","size":16})
        st.session_state['blocks'].append({"uid":uid,"type":bt,"payload":payload})

    del_idx = None
    for i,blk in enumerate(st.session_state['blocks']):
        uid = blk['uid']
        colA,colB,colC,colD = st.columns([5,1,1,1])
        colA.markdown(f"**Block {i+1} – {blk['type']}**")
        if colB.button("🖉 Edit", key=f"ed_{uid}"):
            st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}", False)
        if colC.button("🗑️ Delete", key=f"del_{uid}"):
            del_idx = i
        if colD.button("⚙️ Update", key=f"upd_{uid}"):
            all_html = "".join(block_html(b) for b in st.session_state['blocks'])
            with engine.begin() as conn:
                if st.session_state['row_id']:
                    conn.execute(text(f"UPDATE {chosen} SET content=:c WHERE id=:id"), {"c":all_html,"id":st.session_state['row_id']})
                else:
                    conn.execute(text(f"INSERT INTO {chosen} (title,content) VALUES ('',:c)"), {"c":all_html})
            safe_rerun()
        with st.expander("Edit Block", expanded=st.session_state.get(f"exp_{uid}", False)):
            if blk['type']=="text":
                blk['payload']['text'] = st.text_area("Text", blk['payload']['text'], key=f"txt_{uid}")
                blk['payload']['color'] = st.color_picker("Color", blk['payload']['color'], key=f"col_{uid}")
                blk['payload']['size']  = st.slider("Size(px)",8,48,blk['payload']['size'], key=f"sz_{uid}")
            elif blk['type'] in ("youtube","image","embed"):
                lbl = "Image URL" if blk['type']=="image" else "URL"
                blk['payload']['url'] = st.text_input(lbl, blk['payload']['url'], key=f"url_{uid}")
            else:
                blk['payload']['csv']   = st.text_area("CSV", blk['payload']['csv'], key=f"csv_{uid}")
                blk['payload']['color'] = st.color_picker("Text Color", blk['payload']['color'], key=f"ccol_{uid}")
                blk['payload']['size']  = st.slider("Font Size(px)",8,48,blk['payload']['size'], key=f"csz_{uid}")
        st.markdown("---")
    if del_idx is not None:
        st.session_state['blocks'].pop(del_idx)

    # Live Preview
    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(st.session_state.get('title_html',''), unsafe_allow_html=True)
    st.markdown("".join(block_html(b) for b in st.session_state['blocks']), unsafe_allow_html=True)
