# update.py
from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
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
    "Text": "text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
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

def block_html(block: dict) -> str:
    t   = block["type"]
    pld = block["payload"]

    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{pld["color"]};font-size:{pld["size"]}px;margin:0">'
            f'{pld["text"]}</p>'
            f'<!--BLOCK_END-->'
        )

    if t == "youtube":
        emb = get_youtube_embed(pld["url"])
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{emb}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen></iframe>'
            f'<!--BLOCK_END-->'
        )

    if t == "image":
        url = ensure_https(pld["url"])
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{url}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )

    if t == "embed":
        url = ensure_https(pld["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )

    # CSV → DataFrame.to_html() with style
    csv_text = (pld.get("csv") or "").strip()
    if not csv_text:
        return ""

    try:
        df = pd.read_csv(io.StringIO(csv_text))
    except Exception as e:
        return (
            f'<!--BLOCK_START:csv-->'
            f'<p style="color:red;">⚠️ Invalid CSV: {e}</p>'
            f'<!--BLOCK_END-->'
        )

    raw = df.to_html(index=False, border=1)
    return (
        f'<!--BLOCK_START:csv-->'
        f'<div style="color:{pld["color"]};font-size:{pld["size"]}px;">'
        f'{raw}'
        f'</div><!--BLOCK_END-->'
    )

BLOCK_RGX = re.compile(r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S)

def html_to_blocks(html: str) -> list[dict]:
    blocks: list[dict] = []
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

@st.cache_data(show_spinner=False)
def load_row(table: str):
    with engine.connect() as conn:
        return conn.execute(text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")).fetchone()

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = load_row(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id if row else None
        st.session_state["title_raw"] = re.sub(r"<[^>]*>", "", row.title or "") if row else ""
        st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
mode = navigation()

if mode == "Table Editor":
    tabledit.main()

else:
    st.sidebar.header("📑 Content Manager")
    chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
    prime_state(chosen)

    # — Title editor + Delete Title —
    st.title("✏️ Edit Title")
    c1, c2, c3 = st.columns([3,1,1])
    with c1:
        title_txt = st.text_input("Text", st.session_state["title_raw"], key="title_txt")
    with c2:
        title_color = st.color_picker("Color", "#000000", key="title_color")
    with c3:
        title_size = st.number_input("Size(px)", 8,72,24, key="title_size")
    raw = st.checkbox("Treat as raw HTML", value=False, key="title_raw_html")
    title_html = title_txt if raw else f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_txt}</h2>'

    col_up, col_del = st.columns([1,1])
    with col_up:
        if st.button("🔄 Update Title", key="upd-title"):
            with engine.begin() as conn:
                if st.session_state["row_id"]:
                    conn.execute(text(f"UPDATE {chosen} SET title=:t WHERE id=:id"),
                                 {"t": title_html, "id": st.session_state["row_id"]})
                else:
                    conn.execute(text(f"INSERT INTO {chosen} (title,content) VALUES(:t,'')"),
                                 {"t": title_html})
            st.success("Title updated.")
            # force reload from DB
            st.session_state.pop("table", None)
            safe_rerun()
    with col_del:
        if st.button("🗑️ Delete Title", key="del-title"):
            with engine.begin() as conn:
                if st.session_state["row_id"]:
                    conn.execute(text(f"UPDATE {chosen} SET title='' WHERE id=:id"),
                                 {"id": st.session_state["row_id"]})
            st.success("Title deleted.")
            st.session_state.pop("table", None)
            safe_rerun()

    st.markdown("---")
    st.subheader("🧩 Content Blocks")
    a1, a2 = st.columns([3,1])
    with a1:
        new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
    with a2:
        if st.button("➕ Add Block", key="add"):
            uid = str(uuid.uuid4())
            t   = BLOCK_TYPES[new_type]
            payload = (
                {"text":"","color":"#000000","size":16}
                if t=="text"
                else {"url":""} if t in ("youtube","image","embed")
                else {"csv":"","color":"#000000","size":16}
            )
            st.session_state["blocks"].append({"uid":uid,"type":t,"payload":payload})

    # — Blocks list with instant delete & update —
    for idx, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        colA, colB, colC, colD = st.columns([5,1,1,1])
        colA.markdown(f"**Block {idx+1} – {blk['type']}**")

        if colB.button("🖉 Edit",   key=f"edit-{uid}"):
            st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}", False)

        if colC.button("🔄 Update", key=f"upd-{uid}"):
            new_html = "<br>".join(b for b in (block_html(b2) for b2 in st.session_state["blocks"]) if b)
            with engine.begin() as conn:
                conn.execute(text(f"UPDATE {chosen} SET content=:c WHERE id=:id"),
                             {"c": new_html, "id": st.session_state["row_id"]})
            st.success(f"Block {idx+1} updated.")
            st.session_state.pop("table", None)
            safe_rerun()

        if colD.button("🗑️ Delete", key=f"del-{uid}"):
            # remove from state
            st.session_state["blocks"].pop(idx)
            # persist
            new_html = "<br>".join(b for b in (block_html(b2) for b2 in st.session_state["blocks"]) if b)
            with engine.begin() as conn:
                conn.execute(text(f"UPDATE {chosen} SET content=:c WHERE id=:id"),
                             {"c": new_html, "id": st.session_state["row_id"]})
            st.success(f"Block {idx+1} deleted.")
            st.session_state.pop("table", None)
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
                tab1, tab2 = st.tabs(["Upload CSV","Paste CSV"])
                with tab1:
                    up = st.file_uploader("Choose CSV file", type=["csv"], key=f"file_{uid}")
                    if up:
                        try:
                            df = pd.read_csv(up)
                            st.dataframe(df)
                            blk["payload"]["csv"] = df.to_csv(index=False)
                        except Exception as e:
                            st.error(f"Invalid CSV file: {e}")
                with tab2:
                    txt = st.text_area("Paste CSV text", blk["payload"]["csv"], key=f"csv_{uid}")
                    blk["payload"]["csv"] = txt
                    try:
                        df = pd.read_csv(io.StringIO(txt))
                        st.dataframe(df)
                    except:
                        st.error("Invalid CSV text")

                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                blk["payload"]["size"]  = st.slider("Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{uid}")

        st.markdown("")  # one-line space

    # — Global fallback Save —
    if st.button("💾 Save / Update All", key="save-all"):
        full_html = "<br>".join(b for b in (block_html(b2) for b2 in st.session_state["blocks"]) if b)
        with engine.begin() as conn:
            if st.session_state["row_id"]:
                conn.execute(text(f"UPDATE {chosen} SET content=:c WHERE id=:id"),
                             {"c": full_html, "id": st.session_state["row_id"]})
            else:
                conn.execute(text(f"INSERT INTO {chosen} (title,content) VALUES('',:c)"),
                             {"c": full_html})
        st.success("All changes saved.")
        st.session_state.pop("table", None)
        safe_rerun()

    # — Live Preview with single <br> between blocks —
    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown( title_html, unsafe_allow_html=True )
    preview_html = "<br>".join(
        b for b in (block_html(b2) for b2 in st.session_state["blocks"]) if b
    )
    st.markdown(preview_html, unsafe_allow_html=True)
