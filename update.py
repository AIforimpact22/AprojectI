# update.py (modified version)
from __future__ import annotations
import re, uuid, io, urllib.parse, json
from typing import Optional, Dict, Any

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit

# Add new imports for rich text functionality
from htmldocx import HtmlToDocx
from markdown import markdown
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────────────────────
# Constants and Configuration
# ──────────────────────────────────────────────────────────────
TAB_NAMES = [
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
    "Text/Rich": "rich_text",
    "Text/HTML": "html_text",
    "YouTube URL": "youtube",
    "Image URL": "image",
    "Embed URL": "embed",
    "CSV → Table": "csv",
}

FONT_FAMILIES = {
    "Arial": "Arial, sans-serif",
    "Times New Roman": "'Times New Roman', serif",
    "Courier New": "'Courier New', monospace",
    "Georgia": "Georgia, serif",
    "Verdana": "Verdana, sans-serif",
    "Custom...": "custom"
}

FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32, 36, 42, 48]

# ──────────────────────────────────────────────────────────────
# Helper Functions
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
# Rich Text Editor Components
# ──────────────────────────────────────────────────────────────
def rich_text_toolbar(uid: str, payload: Dict[str, Any]):
    """Render the rich text formatting toolbar"""
    cols = st.columns([1,1,1,1,1,1,1,1,2,2])
    
    with cols[0]:
        payload["bold"] = st.toggle("B", value=payload.get("bold", False), 
                                  key=f"bold_{uid}", help="Bold (Ctrl+B)")
    with cols[1]:
        payload["italic"] = st.toggle("I", value=payload.get("italic", False), 
                                    key=f"italic_{uid}", help="Italic (Ctrl+I)")
    with cols[2]:
        payload["underline"] = st.toggle("U", value=payload.get("underline", False), 
                              key=f"underline_{uid}", help="Underline (Ctrl+U)")
    with cols[3]:
        payload["strikethrough"] = st.toggle("S", value=payload.get("strikethrough", False), 
                                           key=f"strikethrough_{uid}", help="Strikethrough")
    
    with cols[4]:
        align = st.selectbox("Align", ["left", "center", "right", "justify"],
                           index=["left", "center", "right", "justify"].index(
                               payload.get("align", "left")),
                           key=f"align_{uid}", label_visibility="collapsed")
        payload["align"] = align
    
    with cols[5]:
        payload["text_color"] = st.color_picker("Text", value=payload.get("text_color", "#000000"),
                                              key=f"text_color_{uid}", label_visibility="collapsed")
    
    with cols[6]:
        payload["bg_color"] = st.color_picker("BG", value=payload.get("bg_color", "transparent"),
                                            key=f"bg_color_{uid}", label_visibility="collapsed")
    
    with cols[7]:
        if st.button("❌", key=f"clear_{uid}"):
            payload.update({
                "bold": False,
                "italic": False,
                "underline": False,
                "strikethrough": False,
                "align": "left",
                "text_color": "#000000",
                "bg_color": "transparent",
                "font_family": "Arial",
                "font_size": 16
            })
    
    with cols[8]:
        font = st.selectbox("Font", list(FONT_FAMILIES.keys()),
                          index=list(FONT_FAMILIES.keys()).index(
                              payload.get("font_family", "Arial")),
                          key=f"font_{uid}", label_visibility="collapsed")
        payload["font_family"] = font
    
    with cols[9]:
        size = st.selectbox("Size", FONT_SIZES,
                          index=FONT_SIZES.index(
                              payload.get("font_size", 16)),
                          key=f"size_{uid}", label_visibility="collapsed")
        payload["font_size"] = size
    
    # List options
    list_cols = st.columns([1,1,2])
    with list_cols[0]:
        payload["list_type"] = st.radio("List", ["none", "bullet", "number"],
                                      index=["none", "bullet", "number"].index(
                                          payload.get("list_type", "none")),
                                      key=f"list_{uid}", horizontal=True,
                                      label_visibility="collapsed")
    
    # Link functionality
    with list_cols[2]:
        link_cols = st.columns([3,1])
        with link_cols[0]:
            payload["link_url"] = st.text_input("Link URL", value=payload.get("link_url", ""),
                                              key=f"link_url_{uid}", placeholder="https://...")
        with link_cols[1]:
            if st.button("🔗", key=f"apply_link_{uid}"):
                payload["has_link"] = bool(payload["link_url"])
    
    return payload

def rich_text_editor(uid: str, payload: Dict[str, Any]):
    """Render the rich text editor interface"""
    # First render the toolbar
    payload = rich_text_toolbar(uid, payload)
    
    # Then the text area
    payload["content"] = st.text_area("Content", value=payload.get("content", ""),
                                    key=f"content_{uid}", height=200,
                                    label_visibility="collapsed")
    
    return payload

def html_text_editor(uid: str, payload: Dict[str, Any]):
    """Render the HTML text editor with dual view"""
    tab1, tab2 = st.tabs(["Visual Editor", "HTML Source"])
    
    with tab1:
        payload["html_content"] = st.text_area("HTML Content", 
                                             value=payload.get("html_content", ""),
                                             key=f"html_visual_{uid}", 
                                             height=200)
        
        # Basic HTML formatting buttons
        btn_cols = st.columns(6)
        with btn_cols[0]:
            if st.button("Bold", key=f"html_bold_{uid}"):
                payload["html_content"] = f"<b>{payload['html_content']}</b>"
        with btn_cols[1]:
            if st.button("Italic", key=f"html_italic_{uid}"):
                payload["html_content"] = f"<i>{payload['html_content']}</i>"
        with btn_cols[2]:
            if st.button("Link", key=f"html_link_{uid}"):
                url = st.text_input("Enter URL:", key=f"html_link_url_{uid}")
                if url:
                    payload["html_content"] = f'<a href="{url}">{payload["html_content"]}</a>'
        with btn_cols[3]:
            if st.button("Paragraph", key=f"html_para_{uid}"):
                payload["html_content"] = f"<p>{payload['html_content']}</p>"
        with btn_cols[4]:
            if st.button("Div", key=f"html_div_{uid}"):
                payload["html_content"] = f'<div style="margin:10px 0">{payload["html_content"]}</div>'
        with btn_cols[5]:
            if st.button("Clear", key=f"html_clear_{uid}"):
                payload["html_content"] = ""
    
    with tab2:
        payload["html_content"] = st.text_area("HTML Source", 
                                             value=payload.get("html_content", ""),
                                             key=f"html_source_{uid}", 
                                             height=200)
    
    # Preview
    with st.expander("Preview"):
        st.markdown(payload.get("html_content", ""), unsafe_allow_html=True)
    
    return payload

# ──────────────────────────────────────────────────────────────
# Block Rendering and Conversion
# ──────────────────────────────────────────────────────────────
def block_html(block: dict) -> str:
    t, p = block["type"], block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p><!--BLOCK_END-->'
        )
    elif t == "rich_text":
        styles = []
        if p.get("bold"): styles.append("font-weight:bold")
        if p.get("italic"): styles.append("font-style:italic")
        if p.get("underline"): styles.append("text-decoration:underline")
        if p.get("strikethrough"): styles.append("text-decoration:line-through")
        if p.get("align"): styles.append(f"text-align:{p['align']}")
        if p.get("text_color"): styles.append(f"color:{p['text_color']}")
        if p.get("bg_color") and p["bg_color"] != "transparent": 
            styles.append(f"background-color:{p['bg_color']}")
        if p.get("font_family"): styles.append(f"font-family:{FONT_FAMILIES[p['font_family']]}")
        if p.get("font_size"): styles.append(f"font-size:{p['font_size']}px")
        
        content = p.get("content", "")
        if p.get("list_type") == "bullet":
            content = f"<ul><li>{content}</li></ul>"
        elif p.get("list_type") == "number":
            content = f"<ol><li>{content}</li></ol>"
        
        if p.get("has_link") and p.get("link_url"):
            content = f'<a href="{p["link_url"]}">{content}</a>'
        
        return (
            f'<!--BLOCK_START:rich_text-->'
            f'<div style="{";".join(styles)};margin:10px 0;padding:5px;">'
            f'{content}</div><!--BLOCK_END-->'
        )
    elif t == "html_text":
        return (
            f'<!--BLOCK_START:html_text-->'
            f'{p.get("html_content", "")}'
            f'<!--BLOCK_END-->'
        )
    elif t == "youtube":
        emb = get_youtube_embed(p["url"])
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{emb}" frameborder="0" '
            f'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen></iframe><!--BLOCK_END-->'
        )
    elif t == "image":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    elif t == "embed":
        url = ensure_https(p["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe><!--BLOCK_END-->'
        )
    elif t == "csv":
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
    return ""

BLOCK_RGX = re.compile(r"<!--BLOCK_START:(?P<type>[a-z_]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S)

def html_to_blocks(html: str) -> list[dict]:
    blocks = []
    for m in BLOCK_RGX.finditer(html or ""):
        t, content = m.group("type"), m.group("html")
        uid = str(uuid.uuid4())
        
        if t == "text":
            m2 = re.search(r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>', content, re.S)
            if m2:
                c, s, txt = m2.groups()
                blocks.append({
                    "uid": uid,
                    "type": "text",
                    "payload": {
                        "text": txt,
                        "color": c,
                        "size": int(s)
                    }
                })
        elif t == "rich_text":
            soup = BeautifulSoup(content, 'html.parser')
            div = soup.find('div')
            if div:
                style = div.get('style', '')
                styles = {s.split(':')[0]: s.split(':')[1] 
                         for s in style.split(';') if ':' in s}
                
                # Extract content - handle lists
                list_type = "none"
                content_text = div.get_text()
                if div.find('ul'):
                    list_type = "bullet"
                    content_text = div.find('li').get_text() if div.find('li') else ""
                elif div.find('ol'):
                    list_type = "number"
                    content_text = div.find('li').get_text() if div.find('li') else ""
                
                # Extract link if exists
                link = div.find('a')
                has_link = link is not None
                link_url = link.get('href') if link else ""
                
                blocks.append({
                    "uid": uid,
                    "type": "rich_text",
                    "payload": {
                        "content": content_text,
                        "bold": "font-weight:bold" in style,
                        "italic": "font-style:italic" in style,
                        "underline": "text-decoration:underline" in style,
                        "strikethrough": "text-decoration:line-through" in style,
                        "align": styles.get("text-align", "left"),
                        "text_color": styles.get("color", "#000000"),
                        "bg_color": styles.get("background-color", "transparent"),
                        "font_family": next((k for k, v in FONT_FAMILIES.items() 
                                           if v in styles.get("font-family", "")), "Arial"),
                        "font_size": int(styles.get("font-size", "16px").replace('px', '')),
                        "list_type": list_type,
                        "has_link": has_link,
                        "link_url": link_url
                    }
                })
        elif t == "html_text":
            blocks.append({
                "uid": uid,
                "type": "html_text",
                "payload": {
                    "html_content": content
                }
            })
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
# State Management
# ──────────────────────────────────────────────────────────────
def prime_state(table: str):
    if "table" not in st.session_state or st.session_state["table"] != table:
        row = load_row(table)
        st.session_state["table"] = table
        st.session_state["row_id"] = row.id if row else None
        st.session_state["title_raw"] = re.sub(r"<[^>]*>", "", row.title or "") if row else ""
        st.session_state["blocks"] = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Enhanced Tabbed CMS", layout="wide")
    mode = navigation()

    if mode == "Table Editor":
        tabledit.main()
    else:
        st.sidebar.header("📑 Enhanced Content Manager")
        chosen = st.sidebar.selectbox("Pick a table", TAB_NAMES)
        prime_state(chosen)

        # Title Editor (unchanged from original)
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
        st.subheader("🧩 Enhanced Content Blocks")
        
        # Add Block Interface
        colA, colB = st.columns([3,1])
        with colA:
            new_type = st.selectbox("Add block type...", list(BLOCK_TYPES.keys()), key="new_type")
        with colB:
            if st.button("➕ Add Block"):
                uid = str(uuid.uuid4())
                t = BLOCK_TYPES[new_type]
                p = {
                    "text": {"text":"","color":"#000000","size":16},
                    "rich_text": {
                        "content": "",
                        "bold": False,
                        "italic": False,
                        "underline": False,
                        "strikethrough": False,
                        "align": "left",
                        "text_color": "#000000",
                        "bg_color": "transparent",
                        "font_family": "Arial",
                        "font_size": 16,
                        "list_type": "none",
                        "has_link": False,
                        "link_url": ""
                    },
                    "html_text": {"html_content": ""},
                    "youtube": {"url": ""},
                    "image": {"url": ""},
                    "embed": {"url": ""},
                    "csv": {"csv":"","color":"#000000","size":16}
                }.get(t, {})
                
                st.session_state["blocks"].append({
                    "uid": uid,
                    "type": t,
                    "payload": p
                })

        # Block Management
        for i, blk in enumerate(st.session_state["blocks"]):
            uid = blk["uid"]
            
            # Block header with controls
            a, e, u, d = st.columns([6, 1, 1, 1])
            a.markdown(f"**Block {i+1}: {blk['type'].replace('_', ' ').title()}**")
            
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

            # Block content editor
            with st.expander("", expanded=st.session_state.get(f"exp_{uid}", False)):
                if blk["type"] == "text":
                    blk["payload"]["text"] = st.text_area(
                        "Text", blk["payload"]["text"], key=f"text_{uid}")
                    blk["payload"]["color"] = st.color_picker(
                        "Color", blk["payload"]["color"], key=f"col_{uid}")
                    blk["payload"]["size"] = st.slider(
                        "Size(px)", 8, 48, blk["payload"]["size"], key=f"size_{uid}")
                
                elif blk["type"] == "rich_text":
                    blk["payload"] = rich_text_editor(uid, blk["payload"])
                
                elif blk["type"] == "html_text":
                    blk["payload"] = html_text_editor(uid, blk["payload"])
                
                elif blk["type"] in ("youtube", "image", "embed"):
                    lbl = "Image URL" if blk["type"] == "image" else "URL"
                    blk["payload"]["url"] = st.text_input(
                        lbl, blk["payload"]["url"], key=f"url_{uid}")
                
                elif blk["type"] == "csv":
                    t1, t2 = st.tabs(["Upload", "Paste"])
                    with t1:
                        up = st.file_uploader(
                            "CSV", type=["csv"], key=f"file_{uid}")
                        if up:
                            try:
                                df = pd.read_csv(up)
                                st.dataframe(df)
                                blk["payload"]["csv"] = df.to_csv(index=False)
                            except Exception as e:
                                st.error(f"Invalid CSV: {e}")
                    with t2:
                        txt = st.text_area(
                            "CSV text", blk["payload"]["csv"], key=f"csv_{uid}")
                        blk["payload"]["csv"] = txt
                        try:
                            pd.read_csv(io.StringIO(txt))
                            st.dataframe(pd.read_csv(io.StringIO(txt)))
                        except:
                            st.error("Invalid CSV")
                    blk["payload"]["color"] = st.color_picker(
                        "Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
                    blk["payload"]["size"] = st.slider(
                        "Font Size(px)", 8, 48, blk["payload"]["size"], key=f"csv_size_{uid}")

            st.markdown("")  # Spacer

        # Save All button
        if st.button("💾 Save All"):
            update_content_db(chosen)
            st.success("All content saved.")
            safe_rerun()

        # Preview section
        st.markdown("---")
        st.subheader("🔍 Live Preview")
        st.markdown(title_html, unsafe_allow_html=True)
        live_html = "<br>".join(p for p in (block_html(b) for b in st.session_state["blocks"]) if p)
        st.markdown(live_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
