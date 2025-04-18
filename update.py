from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

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
    "intro",
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
    "Text/Rich":   "textrich",
    "Text/HTML":   "texthtml",
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

# ──────────────────────────────────────────────────────────────
def block_html(block: dict) -> str:
    t, p = block["type"], block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p><!--BLOCK_END-->'
        )
    if t == "textrich":
        return (
            f'<!--BLOCK_START:textrich-->'
            f'{p["rich_content"]}'
            f'<!--BLOCK_END-->'
        )
    if t == "texthtml":
        return (
            f'<!--BLOCK_START:texthtml-->'
            f'{p["html_content"]}'
            f'<!--BLOCK_END-->'
        )
    if t == "youtube":
        emb = get_youtube_embed(p["url"])
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{emb}" frameborder="0" '
            f'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen></iframe><!--BLOCK_END-->'
        )
    if t == "image":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    if t == "embed":
        url = ensure_https(p["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe><!--BLOCK_END-->'
        )
    # CSV
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
        elif t == "textrich":
            blocks.append({"uid":uid,"type":"textrich","payload":{"rich_content":content}})
        elif t == "texthtml":
            blocks.append({"uid":uid,"type":"texthtml","payload":{"html_content":content}})
        elif t == "youtube":
            src = re.search(r'src="([^"]+)"', content).group(1)
            vid = src.split("/")[-1]
            url = f"https://www.youtube.com/watch?v={vid}"
            blocks.append({"uid":uid,"type":"youtube","payload":{"url":url}})
        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"image","payload":{"url":url}})
        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({"uid":uid,"type":"embed","payload":{"url":url}})
        elif t == "csv":
            m2 = re.search(r'font-size:(\d+)px', content, re.S)
            c = re.search(r'color:(#[0-9A-Fa-f]{6})', content, re.S).group(1) if "color" in content else "#000"
            s = int(m2.group(1)) if m2 else 14
            blocks.append({"uid":uid,"type":"csv","payload":{"csv":"","color":c,"size":s}})
    return blocks

# ──────────────────────────────────────────────────────────────
# prime_state now only runs on table change
# ──────────────────────────────────────────────────────────────
def prime_state(table: str):
    if "table" not in st.session_state or st.session_state["table"] != table:
        row = load_row(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id    if row else None
        st.session_state["title_raw"] = re.sub(r"<[^>]*>", "", row.title or "") if row else ""
        st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# Rich Text Editor Component
# ──────────────────────────────────────────────────────────────
def rich_text_editor(initial_content="", key=None):
    """Custom component for rich text editing with formatting options"""
    container = st.container()
    
    # Create toolbar with formatting options
    cols = container.columns(8)
    
    # Bold button
    if cols[0].button("**B**", key=f"bold_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + "<strong></strong>"
    
    # Italic button
    if cols[1].button("*I*", key=f"italic_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + "<em></em>"
    
    # Underline button
    if cols[2].button("_U_", key=f"underline_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + "<u></u>"
    
    # Link button
    if cols[3].button("🔗", key=f"link_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + '<a href=""></a>'
    
    # Header button
    if cols[4].button("H", key=f"header_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + "<h3></h3>"
    
    # List button
    if cols[5].button("•", key=f"list_{key}"):
        st.session_state[f"content_{key}"] = st.session_state.get(f"content_{key}", initial_content) + "<ul><li></li></ul>"
    
    # Color selector
    text_color = cols[6].color_picker("T", "#000000", key=f"text_color_{key}")
    
    # Background color selector
    bg_color = cols[7].color_picker("BG", "#ffffff", key=f"bg_color_{key}")
    
    # Apply color button
    if container.button("Apply Colors", key=f"apply_colors_{key}"):
        selected_content = st.session_state.get(f"content_{key}", initial_content)
        st.session_state[f"content_{key}"] = f'<span style="color:{text_color};background-color:{bg_color};">{selected_content}</span>'
    
    # Main content area with preview
    tab1, tab2 = container.tabs(["Edit", "Preview"])
    
    with tab1:
        content = st.text_area(
            "HTML Content", 
            value=st.session_state.get(f"content_{key}", initial_content),
            height=200,
            key=f"content_{key}"
        )
    
    with tab2:
        st.markdown(content, unsafe_allow_html=True)
    
    return content

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

    # Title
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
    colA, colB = st.columns([3,1])
    with colA:
        new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
    with colB:
        if st.button("➕ Add Block"):
            uid = str(uuid.uuid4()); t = BLOCK_TYPES[new_type]
            p = ({"text":"","color":"#000000","size":16}
                if t=="text" 
                else {"rich_content":"<p>Edit this rich text</p>"} if t=="textrich"
                else {"html_content":"<!-- Edit your HTML here -->"} if t=="texthtml"
                else {"url":""} if t in ("youtube","image","embed")
                else {"csv":"","color":"#000000","size":16})
            st.session_state["blocks"].append({"uid":uid,"type":t,"payload":p})

    for i, blk in enumerate(st.session_state["blocks"]):
        uid = blk["uid"]
        a,e,u,d = st.columns([6,1,1,1])
        a.markdown(f"**Block {i+1}: {blk['type']}**")
        if e.button("🖉 Edit",   key=f"edit-{uid}"):
            st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}",False)
        if u.button("🔄 Update", key=f"upd-{uid}"):
            update_content_db(chosen)
            st.success(f"Block {i+1} saved.")
            safe_rerun()
        if d.button("🗑️ Delete", key=f"del-{uid}"):
            st.session_state["blocks"].pop(i)
            update_content_db(chosen)
            st.success(f"Block {i+1} deleted.")
            safe_rerun()

        with st.expander("", expanded=st.session_state.get(f"exp_{uid}",False)):
            if blk["type"]=="text":
                blk["payload"]["text"]  = st.text_area("Text",blk["payload"]["text"],key=f"text_{uid}")
                blk["payload"]["color"] = st.color_picker("Color",blk["payload"]["color"],key=f"col_{uid}")
                blk["payload"]["size"]  = st.slider("Size(px)",8,48,blk["payload"]["size"],key=f"size_{uid}")
            elif blk["type"]=="textrich":
                # Rich text editor with formatting options
                blk["payload"]["rich_content"] = rich_text_editor(
                    initial_content=blk["payload"]["rich_content"],
                    key=f"rich_{uid}"
                )
            elif blk["type"]=="texthtml":
                # HTML editor with preview
                html_tabs = st.tabs(["HTML Code", "Preview"])
                with html_tabs[0]:
                    blk["payload"]["html_content"] = st.text_area(
                        "HTML Content", 
                        blk["payload"]["html_content"], 
                        height=300,
                        key=f"html_{uid}"
                    )
                with html_tabs[1]:
                    st.markdown(blk["payload"]["html_content"], unsafe_allow_html=True)
            elif blk["type"] in ("youtube","image","embed"):
                lbl = "Image URL" if blk["type"]=="image" else "URL"
                blk["payload"]["url"] = st.text_input(lbl,blk["payload"]["url"],key=f"url_{uid}")
            else: # csv
                t1,t2=st.tabs(["Upload","Paste"])
                with t1:
                    up=st.file_uploader("CSV",type=["csv"],key=f"file_{uid}")
                    if up:
                        try:
                            df=pd.read_csv(up); st.dataframe(df)
                            blk["payload"]["csv"]=df.to_csv(index=False)
                        except Exception as e:
                            st.error(f"Invalid CSV: {e}")
                with t2:
                    txt=st.text_area("CSV text",blk["payload"]["csv"],key=f"csv_{uid}")
                    blk["payload"]["csv"]=txt
                    try:
                        pd.read_csv(io.StringIO(txt)); st.dataframe(pd.read_csv(io.StringIO(txt)))
                    except:
                        st.error("Invalid CSV")
                blk["payload"]["color"]=st.color_picker("Text Color",blk["payload"]["color"],key=f"csv_col_{uid}")
                blk["payload"]["size"]=st.slider("Font Size(px)",8,48,blk["payload"]["size"],key=f"csv_size_{uid}")

        st.markdown("")  # exactly one blank line

    if st.button("💾 Save All"):
        update_content_db(chosen)
        st.success("All content saved.")
        safe_rerun()

    st.markdown("---")
    st.subheader("🔍 Live Preview")
    st.markdown(title_html, unsafe_allow_html=True)
    live_html = "<br>".join(p for p in (block_html(b) for b in st.session_state["blocks"]) if p)
    st.markdown(live_html, unsafe_allow_html=True)
