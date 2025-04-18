from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit.components.v1 as components

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
    "Text": "text",
    "Text/HTML": "richtext",
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
    if t == "richtext":
        return (
            f'<!--BLOCK_START:richtext-->'
            f'<div style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["html"]}</div><!--BLOCK_END-->'
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
        elif t == "richtext":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</div>', content, re.S)
            if m2:
                c, s, html_content = m2.groups()
                blocks.append({"uid":uid,"type":"richtext","payload":{"html":html_content,"color":c,"size":int(s)}})
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
def prime_state(table: str):
    if "table" not in st.session_state or st.session_state["table"] != table:
        row = load_row(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id    if row else None
        st.session_state["title_raw"] = re.sub(r"<[^>]*>", "", row.title or "") if row else ""
        st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# Rich text editor component
def create_rich_text_editor(initial_value="", height=300):
    html = f"""
    <div style="margin-bottom:10px">
        <link href="https://cdn.quilljs.com/1.3.6/quill.snow.css" rel="stylesheet">
        <div id="editor" style="height:{height}px"></div>
        <script src="https://cdn.quilljs.com/1.3.6/quill.js"></script>
        <script>
            var quill = new Quill('#editor', {{
                theme: 'snow',
                modules: {{
                    toolbar: [
                        [{{ 'header': [1, 2, 3, false] }}],
                        ['bold', 'italic', 'underline', 'strike'],
                        [{{ 'color': [] }}, {{ 'background': [] }}],
                        ['link'],
                        [{{ 'list': 'ordered' }}, {{ 'list': 'bullet' }}],
                        ['clean']
                    ]
                }}
            }});
            quill.root.innerHTML = `{initial_value.replace('`', '\\`')}`;
            
            window.addEventListener('message', function(e) {{
                if (e.data.type === 'get_content') {{
                    window.parent.postMessage({{
                        type: 'quill_content',
                        content: quill.root.innerHTML,
                        id: e.data.id
                    }}, '*');
                }}
            }}, false);
        </script>
    </div>
    """
    return components.html(html, height=height+130)

def get_rich_text_content(key):
    import uuid
    import time
    import json
    
    request_id = str(uuid.uuid4())
    st.session_state[f"richtext_result_{key}"] = None
    
    components.html(
        f"""
        <script>
        window.parent.postMessage({{
            type: 'get_content',
            id: '{request_id}'
        }}, '*');
        
        window.addEventListener('message', function(e) {{
            if (e.data.type === 'quill_content' && e.data.id === '{request_id}') {{
                const data = JSON.stringify(e.data.content);
                const input = window.parent.document.getElementById('richtext_result_{key}');
                if (input) input.value = data;
                const button = window.parent.document.getElementById('richtext_submit_{key}');
                if (button) button.click();
            }}
        }}, false);
        </script>
        """,
        height=0
    )
    
    st.text_input(f"Hidden Result", key=f"richtext_result_{key}", label_visibility="collapsed")
    
    if st.button("Get Content", key=f"richtext_submit_{key}", style="display:none;"):
        pass
    
    result = st.session_state.get(f"richtext_result_{key}")
    if result:
        try:
            return json.loads(result)
        except:
            return result
    return None

# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Enhanced Tabbed CMS", layout="wide")
mode = navigation()

# Custom CSS for a nicer UI
st.markdown("""
<style>
    .block-container {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #eee;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .block-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
    }
    .stButton>button {
        width: 100%;
    }
    .main-actions {
        padding: 15px;
        background-color: #f5f5f5;
        border-radius: 5px;
        margin: 20px 0;
    }
    .preview-container {
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 5px;
        background-color: white;
    }
    .title-container {
        padding: 15px;
        background-color: #f5f5f5;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

if mode == "Table Editor":
    tabledit.main()
else:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.sidebar.header("📑 Content Manager")
        chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES, index=TAB_NAMES.index(st.session_state.get("table", "intro")) if "table" in st.session_state else 0)
        prime_state(chosen)
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Navigation")
        st.sidebar.info(f"Currently editing: **{chosen}**")
        
        # Show quick stats
        if st.session_state.get("blocks"):
            block_count = len(st.session_state["blocks"])
            block_types = {}
            for b in st.session_state["blocks"]:
                block_types[b["type"]] = block_types.get(b["type"], 0) + 1
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("Content Stats")
            st.sidebar.write(f"Total blocks: {block_count}")
            for bt, count in block_types.items():
                st.sidebar.write(f"- {bt.capitalize()}: {count}")
    
    with col2:
        st.title("📝 Enhanced Content Manager")
        
        # Title Section
        if st.session_state.get("clear_title_input"):
            for k in ("title_txt","title_color","title_size","title_raw_html","clear_title_input"):
                st.session_state.pop(k, None)

        with st.container():
            st.markdown('<div class="title-container">', unsafe_allow_html=True)
            st.subheader("📌 Title")
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.text_input("Text", st.session_state["title_raw"], key="title_txt")
            with c2:
                st.color_picker("Color", "#000000", key="title_color")
            with c3:
                st.number_input("Size(px)", 8, 72, 24, key="title_size")
            raw = st.checkbox("Raw HTML", value=False, key="title_raw_html")

            title_html = (
                st.session_state["title_txt"] if raw
                else f'<h2 style="color:{st.session_state["title_color"]};'
                    f'font-size:{st.session_state["title_size"]}px;">'
                    f'{st.session_state["title_txt"]}</h2>'
            )

            u_col, d_col = st.columns([1, 1])
            with u_col:
                if st.button("🔄 Update Title", use_container_width=True):
                    update_title_db(chosen, title_html)
                    st.success("Title updated.")
                    safe_rerun()
            with d_col:
                if st.button("🗑️ Delete Title", use_container_width=True):
                    delete_title_db(chosen)
                    st.session_state["clear_title_input"] = True
                    st.success("Title deleted.")
                    safe_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Content Blocks
        st.subheader("🧩 Content Blocks")
        
        with st.container():
            st.markdown('<div class="block-container">', unsafe_allow_html=True)
            colA, colB = st.columns([3, 1])
            with colA:
                new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
            with colB:
                if st.button("➕ Add Block", use_container_width=True):
                    uid = str(uuid.uuid4())
                    t = BLOCK_TYPES[new_type]
                    if t == "text":
                        p = {"text": "", "color": "#000000", "size": 16}
                    elif t == "richtext":
                        p = {"html": "", "color": "#000000", "size": 16}
                    elif t in ("youtube", "image", "embed"):
                        p = {"url": ""}
                    else:  # csv
                        p = {"csv": "", "color": "#000000", "size": 16}
                    st.session_state["blocks"].append({"uid": uid, "type": t, "payload": p})
                    safe_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Display blocks
        if not st.session_state.get("blocks"):
            st.info("No blocks yet. Add your first block using the selector above.")
        else:
            for i, blk in enumerate(st.session_state["blocks"]):
                uid = blk["uid"]
                with st.container():
                    st.markdown(f'<div class="block-container">', unsafe_allow_html=True)
                    
                    # Block header
                    st.markdown(f'<div class="block-header">', unsafe_allow_html=True)
                    a, e, u, d = st.columns([6, 1, 1, 1])
                    a.markdown(f"**Block {i+1}: {blk['type'].capitalize()}**")
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
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Block content editor
                    with st.expander("", expanded=st.session_state.get(f"exp_{uid}", False)):
                        if blk["type"] == "text":
                            blk["payload"]["text"] = st.text_area("Text", blk["payload"]["text"], key=f"text_{uid}", height=150)
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{uid}")
                            with col2:
                                blk["payload"]["size"] = st.slider("Size(px)", 8, 48, blk["payload"]["size"], key=f"size_{uid}")
                        elif blk["type"] == "richtext":
                            st.write("Rich Text Editor:")
                            # Show existing content in the editor
                            create_rich_text_editor(blk["payload"].get("html", ""), height=250)
                            
                            # Get the updated content when needed
                            new_content = get_rich_text_content(uid)
                            if new_content:
                                blk["payload"]["html"] = new_content
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"].get("color", "#000000"), key=f"rich_col_{uid}")
                            with col2:
                                blk["payload"]["size"] = st.slider("Font Size(px)", 8, 48, blk["payload"].get("size", 16), key=f"rich_size_{uid}")
                        elif blk["type"] in ("youtube", "image", "embed"):
                            lbl = "Image URL" if blk["type"] == "image" else "URL"
                            blk["payload"]["url"] = st.text_input(lbl, blk["payload"]["url"], key=f"url_{uid}")
                            
                            # Preview for image and YouTube
                            if blk["type"] == "image" and blk["payload"]["url"]:
                                st.image(ensure_https(blk["payload"]["url"]), use_column_width=True)
                            elif blk["type"] == "youtube" and blk["payload"]["url"]:
                                emb = get_youtube_embed(blk["payload"]["url"])
                                st.video(blk["payload"]["url"])
                        else:  # csv
                            tabs = st.tabs(["Upload CSV", "Paste CSV", "Preview"])
                            with tabs[0]:
                                up = st.file_uploader("Upload CSV file", type=["csv"], key=f"file_{uid}")
                                if up:
                                    try:
                                        df = pd.read_csv(up)
                                        st.dataframe(df)
                                        blk["payload"]["csv"] = df.to_csv(index=False)
                                    except Exception as e:
                                        st.error(f"Invalid CSV: {e}")
                            with tabs[1]:
                                txt = st.text_area("CSV text", blk["payload"]["csv"], key=f"csv_{uid}", height=150)
                                blk["payload"]["csv"] = txt
                            with tabs[2]:
                                try:
                                    if blk["payload"]["csv"]:
                                        df = pd.read_csv(io.StringIO(blk["payload"]["csv"]))
                                        st.dataframe(df)
                                except Exception as e:
                                    st.error(f"Invalid CSV: {e}")
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                            with col2:
                                blk["payload"]["size"] = st.slider("Font Size(px)", 8, 48, blk["payload"]["size"], key=f"csv_size_{uid}")
                    
                    # Show a small preview of the block content
                    if blk["type"] == "text":
                        preview = blk["payload"]["text"][:100] + ("..." if len(blk["payload"]["text"]) > 100 else "")
                        st.markdown(f"<p style='color:{blk['payload']['color']};font-size:{min(blk['payload']['size'], 16)}px;'>{preview}</p>", unsafe_allow_html=True)
                    elif blk["type"] == "richtext":
                        st.markdown(f"<div style='color:{blk['payload']['color']};font-size:{min(blk['payload']['size'], 16)}px;'>{blk['payload']['html'][:100] + ('...' if len(blk['payload']['html']) > 100 else '')}</div>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")  # spacing

        # Save all button
        with st.container():
            st.markdown('<div class="main-actions">', unsafe_allow_html=True)
            if st.button("💾 Save All", use_container_width=True):
                update_content_db(chosen)
                st.success("All content saved.")
                safe_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Preview section
        st.markdown("---")
        with st.container():
            st.subheader("🔍 Live Preview")
            st.markdown('<div class="preview-container">', unsafe_allow_html=True)
            st.markdown(title_html, unsafe_allow_html=True)
            live_html = "<br>".join(p for p in (block_html(b) for b in st.session_state["blocks"]) if p)
            st.markdown(live_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
