# update.py
from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# ──────────────────────────────────────────────────────────────
# Helpers
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

TAB_NAMES   = ["intro"] + [f"tab{i}" for i in range(1, 51)]
BLOCK_TYPES = {
    "Text":   "text",
    "YouTube URL": "youtube",
    "Image URL":   "image",
    "Embed URL":   "embed",
    "CSV → Table": "csv",
}

def ensure_https(u: str) -> str:
    return u if u.startswith(("http://","https://")) else "https://" + u

def get_youtube_embed(raw_url: str) -> str:
    raw = raw_url.strip()
    if not raw.startswith(("http://","https://")):
        raw = "https://" + raw
    p = urllib.parse.urlparse(raw)
    vid = ""
    if "youtu.be" in p.netloc:
        vid = p.path.lstrip("/")
    elif "youtube.com" in p.netloc:
        qs = urllib.parse.parse_qs(p.query)
        vid = qs.get("v", [""])[0]
    return f"https://www.youtube-nocookie.com/embed/{vid}" if vid else raw

def load_row(table: str):
    return engine.connect().execute(
        text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    ).fetchone()

def update_content_db(chosen: str):
    parts = [block_html(b) for b in st.session_state["blocks"] if block_html(b)]
    new_html = "<br>".join(parts)
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET content = :c WHERE id = :id"),
                {"c": new_html, "id": st.session_state["row_id"]}
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES ('', :c)"),
                {"c": new_html}
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None

def update_title_db(chosen: str, title_html: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = :t WHERE id = :id"),
                {"t": title_html, "id": st.session_state["row_id"]}
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES (:t, '')"),
                {"t": title_html}
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None

def delete_title_db(chosen: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = '' WHERE id = :id"),
                {"id": st.session_state["row_id"]}
            )

# ──────────────────────────────────────────────────────────────
# Serialization (unchanged)
# ──────────────────────────────────────────────────────────────
def block_html(block: dict) -> str:
    t, pld = block["type"], block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{pld["color"]};font-size:{pld["size"]}px;margin:0">'
            f'{pld["text"]}</p><!--BLOCK_END-->'
        )
    if t == "youtube":
        emb = get_youtube_embed(pld["url"])
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{emb}" frameborder="0" '
            f'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen></iframe><!--BLOCK_END-->'
        )
    if t == "image":
        url = ensure_https(pld["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    if t == "embed":
        url = ensure_https(pld["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )
    # CSV
    csv_text = (pld.get("csv") or "").strip()
    if not csv_text:
        return ""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        raw = df.to_html(index=False, border=1)
    except Exception as e:
        return f'<!--BLOCK_START:csv--><p style="color:red;">⚠️ Invalid CSV: {e}</p><!--BLOCK_END-->'
    return (
        f'<!--BLOCK_START:csv-->'
        f'<div style="color:{pld["color"]};font-size:{pld["size"]}px;">{raw}</div><!--BLOCK_END-->'
    )

BLOCK_RGX = re.compile(r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S)

def html_to_blocks(html: str) -> list[dict]:
    blocks = []
    for m in BLOCK_RGX.finditer(html or ""):
        t, content = m.group("type"), m.group("html")
        uid = str(uuid.uuid4())
        if t == "text":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>', content, re.S)
            if m2:
                c, s, txt = m2.groups()
                blocks.append({"uid":uid,"type":"text","payload":{"text":txt,"color":c,"size":int(s)}})
        elif t == "youtube":
            src = re.search(r'src="([^"]+)"', content).group(1)
            vid = src.split("/")[-1]
            orig = f"https://www.youtube.com/watch?v={vid}"
            blocks.append({"uid":uid,"type":"youtube","payload":{"url":orig}})
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"image","payload":{"url":url}})
        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"embed","payload":{"url":url}})
        elif t == "csv":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px', content, re.S)
            if m2:
                c, s = m2.groups()
                blocks.append({"uid":uid,"type":"csv","payload":{"csv":"","color":c,"size":int(s)}})
    return blocks

# ──────────────────────────────────────────────────────────────
# Load & prime
# ──────────────────────────────────────────────────────────────
def prime_state(table: str):
    row = load_row(table)
    st.session_state["table"]     = table
    st.session_state["row_id"]    = row.id if row else None
    st.session_state["title_raw"] = re.sub(r"<[^>]*>", "", row.title or "") if row else ""
    st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()

if mode == "Table Editor":
    tabledit.main()
else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    # Title section
    st.subheader("Title")
    t1, t2, t3 = st.columns([3,1,1])
    with t1:
        st.text_input("Text", st.session_state["title_raw"], key="title_txt")
    with t2:
        st.color_picker("Color", "#000000", key="title_color")
    with t3:
        st.number_input("Size(px)", 8,72,24, key="title_size")
    raw = st.checkbox("Raw HTML", value=False, key="title_raw_html")
    title_html = (
        st.session_state["title_txt"]
        if raw
        else f'<h2 style="color:{st.session_state["title_color"]};'
             f'font-size:{st.session_state["title_size"]}px;">'
             f'{st.session_state["title_txt"]}</h2>'
    )

    c_upd, c_del = st.columns([1,1])
    with c_upd:
        if st.button("🔄 Update Title"):
            update_title_db(chosen, title_html)
            st.success("Title updated.")
            safe_rerun()
    with c_del:
        if st.button("🗑️ Delete Title"):
            delete_title_db(chosen)
            # pop keys so the widget is recreated blank on rerun
            for k in ("title_txt","title_color","title_size","title_raw_html"):
                st.session_state.pop(k, None)
            st.success("Title deleted.")
            safe_rerun()

    st.markdown("---")
    st.subheader("🧩 Content Blocks")
    a1, a2 = st.columns([3,1])
    with a1:
        new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
    with a2:
        if st.button("➕ Add Block"):
            uid = str(uuid.uuid4())
            t   = BLOCK_TYPES[new_type]
            payload = (
                {"text":"","color":"#000000","size":16}
                if t == "text"
                else {"url":""} if t in ("youtube","image","embed")
                else {"csv":"","color":"#000000","size":16}
            )
            st.session_state["blocks"].append({"uid":uid,"type":t,"payload":payload})

    for idx, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        colA, colE, colU, colD = st.columns([6,1,1,1])
        colA.markdown(f"**Block {idx+1}: {blk['type']}**")
        if colE.button("🖉 Edit", key=f"edit-{uid}"):
            st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}", False)
        if colU.button("🔄 Update", key=f"upd-{uid}"):
            update_content_db(chosen)
            st.success(f"Block {idx+1} updated.")
            safe_rerun()
        if colD.button("🗑️ Delete", key=f"del-{uid}"):
            st.session_state["blocks"].pop(idx)
            update_content_db(chosen)
            st.success(f"Block {idx+1} deleted.")
            safe_rerun()

        with st.expander("", expanded=st.session_state.get(f"exp_{uid}", False)):
            if blk["type"] == "text":
                blk["payload"]["text"]  = st.text_area("Text", blk["payload"]["text"], key=f"text_{uid}")
                blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{uid}")
                blk["payload"]["size"]  = st.slider("Size(px)", 8,48, blk["payload"]["size"], key=f"size_{uid}")
            elif blk["type"] in ("youtube","image","embed"):
                lbl = "Image URL" if blk["type"]=="image" else "URL"
                blk["payload"]["url"]   = st.text_input(lbl, blk["payload"]["url"], key=f"url_{uid}")
            else:  # CSV
                tab1, tab2 = st.tabs(["Upload","Paste"])
                with tab1:
                    up = st.file_uploader("CSV file", type=["csv"], key=f"file_{uid}")
                    if up:
                        try:
                            df = pd.read_csv(up); st.dataframe(df)
                            blk["payload"]["csv"] = df.to_csv(index=False)
                        except Exception as e:
                            st.error(f"Invalid CSV: {e}")
                with tab2:
                    txt = st.text_area("CSV text", blk["payload"]["csv"], key=f"csv_{uid}")
                    blk["payload"]["csv"] = txt
                    try:
                        df = pd.read_csv(io.StringIO(txt)); st.dataframe(df)
                    except:
                        st.error("Invalid CSV")
                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                blk["payload"]["size"]  = st.slider("Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{uid}")
        st.markdown("")  # single blank line

    if st.button("💾 Save All"):
        update_content_db(chosen)
        st.success("All content saved.")
        safe_rerun()

    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(title_html, unsafe_allow_html=True)
    html = "<br>".join(p for p in (block_html(b) for b in st.session_state["blocks"]) if p)
    st.markdown(html, unsafe_allow_html=True)
