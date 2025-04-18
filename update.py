# update.py
from __future__ import annotations
import re, uuid, json, urllib.parse

import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 0. Safe rerun helper
# ──────────────────────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()

# ──────────────────────────────────────────────────────────────
# 1. DB connection (Neon)
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
# 3. Serialization helpers
# ──────────────────────────────────────────────────────────────
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
        raw = p["url"].strip()
        if not raw.startswith("http"):
            raw = "https://" + raw
        # extract video ID
        vid = ""
        if "youtu.be/" in raw:
            vid = raw.split("/")[-1]
        else:
            q = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query)
            vid = q.get("v", [""])[0]
        embed_url = f"https://www.youtube.com/embed/{vid}"
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{embed_url}" '
            f'frameborder="0" allowfullscreen></iframe>'
            f'<!--BLOCK_END-->'
        )

    if t == "image":
        raw = p["url"].strip()
        if not raw.startswith("http"):
            raw = "https://" + raw
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{raw}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )

    if t == "embed":
        raw = p["url"].strip()
        if not raw.startswith("http"):
            raw = "https://" + raw
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{raw}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )

    # CSV → styled div
    lines = p["csv"].strip().splitlines()
    headers = lines[0].split(",") if lines else []
    rows = [r.split(",") for r in lines[1:]]
    table = "<table><thead><tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>"
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
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*)</p>',
                content,
                re.S,
            )
            if m2:
                c, s, txt = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "text",
                    "payload": {"text": txt, "color": c, "size": int(s)}
                })

        elif t == "youtube":
            # round-trip via video ID
            src = re.search(r'src="([^"]+)"', content).group(1)
            vid = src.split("/")[-1]
            url = f"https://www.youtube.com/watch?v={vid}"
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "youtube",
                "payload": {"url": url}
            })

        elif t == "image":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "image",
                "payload": {"url": url}
            })

        elif t == "embed":
            url = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "embed",
                "payload": {"url": url}
            })

        elif t == "csv":
            m2 = re.search(
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</div>',
                content,
                re.S,
            )
            if m2:
                c, s, _ = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "csv",
                    "payload": {"csv": "", "color": c, "size": int(s)}
                })
    return blocks

# ──────────────────────────────────────────────────────────────
# 4. Load & prime session state
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_row(table: str):
    q = text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(q).fetchone()

def prime_state(table: str):
    if st.session_state.get("table") != table:
        row = load_row(table)
        st.session_state["table"]     = table
        st.session_state["row_id"]    = row.id if row else None
        st.session_state["title_raw"] = row.title if row else ""
        st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# 5. UI – Sidebar & Title
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

with st.sidebar:
    st.header("Section")
    chosen = st.selectbox("Table", TAB_NAMES)
prime_state(chosen)

st.subheader("Title")
col1, col2, col3 = st.columns([3,1,1])
with col1:
    title_txt = st.text_input("Text", st.session_state["title_raw"], key="title_txt")
with col2:
    title_color = st.color_picker("Color", "#000000", key="title_color")
with col3:
    title_size = st.number_input("Size(px)", 8,72,24, key="title_size")
raw_html = st.checkbox("Raw HTML?", value=False, key="title_raw_html")

title_html = title_txt if raw_html else f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_txt}</h2>'

# ──────────────────────────────────────────────────────────────
# 6. Content Blocks – Add / Edit / Delete
# ──────────────────────────────────────────────────────────────
st.subheader("Content Blocks")
add_c, add_btn = st.columns([3,1])
with add_c:
    new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()), key="new_type")
with add_btn:
    if st.button("➕ Add Block", key="add"):
        uid = str(uuid.uuid4())
        t = BLOCK_TYPES[new_type]
        payload = {}
        if t == "text":
            payload = {"text": "", "color": "#000000", "size": 16}
        elif t in ("youtube","image","embed"):
            payload = {"url": ""}
        else:  # csv
            payload = {"csv": "col1,col2\nval1,val2", "color": "#000000", "size": 16}
        st.session_state["blocks"].append({"uid":uid,"type":t,"payload":payload})

to_delete = None
for idx, blk in enumerate(st.session_state["blocks"]):
    uid = blk["uid"]
    cols = st.columns([8,1,1])
    cols[0].markdown(f"**Block {idx+1} – {blk['type']}**")
    if cols[1].button("🖉 Edit", key=f"edit_{uid}"):
        st.session_state[f"exp_{uid}"] = not st.session_state.get(f"exp_{uid}", False)
    if cols[2].button("🗑️ Delete", key=f"del_{uid}"):
        to_delete = idx

    with st.expander("Edit block", expanded=st.session_state.get(f"exp_{uid}", False)):
        if blk["type"] == "text":
            blk["payload"]["text"]  = st.text_area("Text", blk["payload"]["text"], key=f"text_{uid}")
            blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{uid}")
            blk["payload"]["size"]  = st.slider("Size(px)", 8,48, blk["payload"]["size"], key=f"size_{uid}")
        elif blk["type"] in ("youtube","image","embed"):
            lbl = "Image URL" if blk["type"]=="image" else "URL"
            blk["payload"]["url"] = st.text_input(lbl, blk["payload"]["url"], key=f"url_{uid}")
        else:  # csv
            blk["payload"]["csv"]   = st.text_area("CSV", blk["payload"]["csv"], key=f"csv_{uid}")
            blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{uid}")
            blk["payload"]["size"]  = st.slider("Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{uid}")
    st.markdown("---")

if to_delete is not None:
    st.session_state["blocks"].pop(to_delete)

# ──────────────────────────────────────────────────────────────
# 7. Save / Update
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save / Update", key="save"):
    full_html = "".join(block_html(b) for b in st.session_state["blocks"])
    with engine.begin() as conn:
        if st.session_state["row_id"]:
            conn.execute(
                text(f"UPDATE {chosen} SET title=:t, content=:c WHERE id=:id"),
                {"t": title_html, "c": full_html, "id": st.session_state["row_id"]},
            )
        else:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES (:t, :c)"),
                {"t": title_html, "c": full_html},
            )
    st.success("Saved ✔︎ – refreshing…")
    safe_rerun()

# ──────────────────────────────────────────────────────────────
# 8. Live Preview
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Live Preview")
st.markdown(title_html, unsafe_allow_html=True)
st.markdown("".join(block_html(b) for b in st.session_state["blocks"]), unsafe_allow_html=True)
