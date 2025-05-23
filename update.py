# update.py
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

def ensure_https(u: str) -> str:
    return u if u.startswith(("http://","https://")) else "https://" + u

def get_video_embed_html(url: str) -> str:
    """Return HTML to embed YouTube, Vimeo, or direct video files."""
    if not url:
        return ""
    url = url.strip()
    # YouTube
    if re.search(r'(youtu\.be|youtube\.com)', url, re.IGNORECASE):
        if "youtube.com/embed/" in url:
            embed_url = url
        else:
            m = re.search(r'(?:v=|be/)([^&?/]+)', url)
            vid = m.group(1) if m else url
            embed_url = f"https://www.youtube.com/embed/{vid}"
        return (
            f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe>'
        )
    # Vimeo
    elif "vimeo.com" in url:
        if "player.vimeo.com/video/" in url:
            src = url
        else:
            m = re.search(r'vimeo\.com/(?:.*?/)?([0-9]+)', url)
            vid = m.group(1) if m else ""
            src = f"https://player.vimeo.com/video/{vid}"
            hm = re.search(r'vimeo\.com/[0-9]+/([0-9A-Za-z]+)', url)
            if hm:
                h = hm.group(1)
                src += f"?h={h}" if not h.startswith("?") else h
        return (
            f'<iframe width="640" height="360" src="{src}" frameborder="0" '
            f'allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
        )
    # Direct video file
    elif url.lower().endswith((".mp4", ".webm", ".ogg", ".ogv", ".mov")):
        return (
            f'<video controls style="max-width:100%;height:auto;" src="{url}">'
            "Sorry, your browser doesn't support embedded videos."
            "</video>"
        )
    # Fallback
    else:
        return (
            f'<video controls style="max-width:100%;height:auto;" src="{url}">'
            "Sorry, your browser doesn't support embedded videos."
            "</video>"
        )

def block_html(block: dict) -> str:
    t, p = block["type"], block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p><!--BLOCK_END-->'
        )
    if t == "image":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    if t == "csv":
        txt = (p.get("csv") or "").strip()
        if not txt:
            return ""
        try:
            df = pd.read_csv(io.StringIO(txt))
            raw = df.to_html(index=False, border=1)
        except Exception as e:
            return f'<!--BLOCK_START:csv--><p style="color:red;">⚠️ {e}</p><!--BLOCK_END-->'
        return (
            f'<!--BLOCK_START:csv-->'
            f'<div style="color:{p["color"]};font-size:{p["size"]}px;">'
            f'{raw}</div><!--BLOCK_END-->'
        )
    if t == "rich":
        return f'<!--BLOCK_START:rich-->{p["content"]}<!--BLOCK_END-->'
    if t == "html":
        return f'<!--BLOCK_START:html--><pre>{p["content"]}</pre><!--BLOCK_END-->'
    if t == "video":
        embed = get_video_embed_html(p["url"])
        return f'<!--BLOCK_START:video-->{embed}<!--BLOCK_END-->'
    return ""

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
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"image","payload":{"url":url}})
        elif t == "csv":
            m2 = re.search(r'font-size:(\d+)px', content, re.S)
            c = re.search(r'color:(#[0-9A-Fa-f]{6})', content, re.S).group(1) if "color" in content else "#000"
            s = int(m2.group(1)) if m2 else 14
            blocks.append({"uid":uid,"type":"csv","payload":{"csv":"","color":c,"size":s}})
        elif t == "rich":
            blocks.append({"uid":uid,"type":"rich","payload":{"content":content}})
        elif t == "html":
            blocks.append({"uid":uid,"type":"html","payload":{"content":content}})
        elif t == "video":
            src = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"video","payload":{"url":src}})
    return blocks

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
                {"c": new_html, "id": st.session_state["row_id"]},
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES ('', :c)"),
                {"c": new_html},
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None

def update_title_db(chosen: str, title_html: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = :t WHERE id = :id"),
                {"t": title_html, "id": st.session_state["row_id"]},
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES (:t, '')"),
                {"t": title_html},
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None

def delete_title_db(chosen: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = '' WHERE id = :id"),
                {"id": st.session_state["row_id"]},
            )

def prime_state(table: str):
    if "table" not in st.session_state or st.session_state["table"] != table:
        row = load_row(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id    if row else None
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
    # Sidebar: list pages as buttons
    st.sidebar.header("📑 Content Manager")
    if "chosen" not in st.session_state:
        st.session_state["chosen"] = TAB_NAMES[0]
    for tbl in TAB_NAMES:
        if st.sidebar.button(tbl, key=f"btn_{tbl}"):
            st.session_state["chosen"] = tbl
            safe_rerun()

    chosen = st.session_state["chosen"]
    prime_state(chosen)

    # === Title section (unchanged) ===
    st.subheader("Title")
    if st.session_state.get("clear_title_input"):
        for k in ("title_txt","title_color","title_size","title_raw_html","clear_title_input"):
            st.session_state.pop(k, None)
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

    # ◾ Add block types via buttons instead of dropdown
    st.markdown("**➕ Add a new block:**")
    btn_cols = st.columns(len(BLOCK_TYPES))
    for idx, (label, t) in enumerate(BLOCK_TYPES.items()):
        if btn_cols[idx].button(label):
            uid = str(uuid.uuid4())
            if t in ("rich", "html"):
                p = {"content": ""}
            elif t == "video":
                p = {"url": ""}
            else:
                p = (
                    {"text": "", "color": "#000000", "size": 16}
                    if t == "text"
                    else {"csv": "", "color": "#000000", "size": 16}
                )
            st.session_state["blocks"].append({"uid": uid, "type": t, "payload": p})

    # ◾ Existing blocks
    for i, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        a, e, u, d = st.columns([6,1,1,1])
        a.markdown(f"**Block {i+1}: {blk['type']}**")
        if e.button("🖉 Edit", key=f"edit-{uid}"):
            st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}", False)
        if u.button("🔄 Update", key=f"upd-{uid}"):
            update_content_db(chosen)
            st.success(f"Block {i+1} saved.")
            safe_rerun()
        if d.button("🗑️ Delete", key=f"del-{uid}"):
            st.session_state["blocks"].pop(i)
            update_content_db(chosen)
            st.success(f"Block {i+1} deleted.")
            safe_rerun()

        with st.expander("", expanded=st.session_state.get(f"exp_{uid}", False)):
            if blk["type"] == "rich":
                blk["payload"]["content"] = st_quill(
                    value=blk["payload"]["content"], html=True, key=f"rich_{uid}"
                )
            elif blk["type"] == "html":
                blk["payload"]["content"] = st_ace(
                    value=blk["payload"]["content"], language="html", theme="dracula", key=f"html_{uid}"
                )
            elif blk["type"] == "video":
                blk["payload"]["url"] = st.text_input(
                    "Video URL", blk["payload"]["url"], key=f"video_{uid}"
                )
            elif blk["type"] == "text":
                blk["payload"]["text"] = st.text_area(
                    "Text", blk["payload"]["text"], key=f"text_{uid}"
                )
                blk["payload"]["color"] = st.color_picker(
                    "Color", "#000000", key=f"col_{uid}"
                )
                blk["payload"]["size"] = st.slider(
                    "Size(px)", 8,48, blk["payload"]["size"], key=f"size_{uid}"
                )
            else:  # csv
                t1, t2 = st.tabs(["Upload", "Paste"])
                with t1:
                    up = st.file_uploader("CSV", type=["csv"], key=f"file_{uid}")
                    if up:
                        try:
                            df = pd.read_csv(up)
                            st.dataframe(df)
                            blk["payload"]["csv"] = df.to_csv(index=False)
                        except Exception as e:
                            st.error(f"Invalid CSV: {e}")
                with t2:
                    txt = st.text_area("CSV text", blk["payload"]["csv"], key=f"csv_{uid}")
                    blk["payload"]["csv"] = txt
                    try:
                        pd.read_csv(io.StringIO(txt))
                        st.dataframe(pd.read_csv(io.StringIO(txt)))
                    except:
                        st.error("Invalid CSV")
                blk["payload"]["color"] = st.color_picker(
                    "Text Color", blk["payload"]["color"], key=f"csv_col_{uid}"
                )
                blk["payload"]["size"] = st.slider(
                    "Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{uid}"
                )

        st.markdown("")  # blank line

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
