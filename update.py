# update.py
from __future__ import annotations
import re, uuid, json

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
# 1. Database connection (Neon Postgres)
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
# 3. Block ↔ HTML serialization
# ──────────────────────────────────────────────────────────────
def ensure_proto(url: str) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url):
        return "https://" + url
    return url

def block_html(block: dict) -> str:
    t = block["type"]
    p = block["payload"]

    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p>'
            f'<!--BLOCK_END-->'
        )

    if t == "youtube":
        url = ensure_proto(p["url"]).replace("watch?v=", "embed/")
        return (
            f'<!--BLOCK_START:youtube-->'
            f'<iframe width="560" height="315" src="{url}" '
            f'frameborder="0" allowfullscreen></iframe>'
            f'<!--BLOCK_END-->'
        )

    if t == "image":
        src = ensure_proto(p["url"])
        return (
            f'<!--BLOCK_START:image-->'
            f'<img src="{src}" style="max-width:100%;">'
            f'<!--BLOCK_END-->'
        )

    if t == "embed":
        url = ensure_proto(p["url"])
        return (
            f'<!--BLOCK_START:embed-->'
            f'<iframe src="{url}" style="width:100%;height:420px;border:none;"></iframe>'
            f'<!--BLOCK_END-->'
        )

    # CSV → styled table
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
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px.*?>(.*?)</p>',
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
            u = re.search(r'src="([^"]+)"', content).group(1)
            u = u.replace("embed/", "watch?v=")
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "youtube",
                "payload": {"url": u}
            })

        elif t == "image":
            u = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "image",
                "payload": {"url": u}
            })

        elif t == "embed":
            u = re.search(r'src="([^"]+)"', content).group(1)
            blocks.append({
                "uid": str(uuid.uuid4()),
                "type": "embed",
                "payload": {"url": u}
            })

        elif t == "csv":
            m2 = re.search(
                r'color:(#[0-9A-Fa-f]{6});font-size:(\d+)px',
                content,
                re.S,
            )
            if m2:
                c, s = m2.groups()
                blocks.append({
                    "uid": str(uuid.uuid4()),
                    "type": "csv",
                    "payload": {"csv": "", "color": c, "size": int(s)}
                })
    return blocks

# ──────────────────────────────────────────────────────────────
# 4. Load & prime session_state
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_row(table: str):
    q = text(f"SELECT id, title, content FROM {table} ORDER BY id")
    with engine.connect() as conn:
        return conn.execute(q).fetchall()

def prime_state(table: str):
    rows = load_row(table)
    # pick the first as “current”
    row = rows[0] if rows else None
    st.session_state["table"]     = table
    st.session_state["row_id"]    = row.id if row else None
    st.session_state["title_raw"] = row.title if row else ""
    st.session_state["blocks"]    = html_to_blocks(row.content) if row else []

# ──────────────────────────────────────────────────────────────
# 5. UI – Page config + Sidebar
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

with st.sidebar:
    st.header("Navigate")
    chosen = st.selectbox("Edit table", TAB_NAMES)
    manage = st.button("🛠 Manage Tables")

prime_state(chosen)

# ──────────────────────────────────────────────────────────────
# 6. Manage Tables panel (if clicked)
# ──────────────────────────────────────────────────────────────
if manage:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Table Manager")
    table_to_manage = st.sidebar.selectbox("Which table?", TAB_NAMES, key="mg_table")
    rows = load_row(table_to_manage)
    for r in rows:
        st.sidebar.write(f"• ID {r.id} – {r.title}")
        if st.sidebar.button(f"Delete row {r.id}", key=f"del_{table_to_manage}_{r.id}"):
            with engine.begin() as conn:
                conn.execute(text(f"DELETE FROM {table_to_manage} WHERE id=:id"), {"id": r.id})
            st.sidebar.success(f"Deleted row {r.id}")
            safe_rerun()

# ──────────────────────────────────────────────────────────────
# 7. Title editor
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
c1, c2, c3 = st.columns([3,1,1])
with c1:
    title_txt = st.text_input("Text", value=st.session_state["title_raw"])
with c2:
    title_color = st.color_picker("Color", "#000000")
with c3:
    title_size = st.number_input("Size (px)", 8, 72, 24)
raw_html = st.checkbox("Raw HTML title", value=False)

title_html = (
    title_txt if raw_html
    else f'<h2 style="color:{title_color};font-size:{title_size}px;">{title_txt}</h2>'
)

# ──────────────────────────────────────────────────────────────
# 8. Content Blocks – add / edit / delete
# ──────────────────────────────────────────────────────────────
st.subheader("Content Blocks")
a1, a2 = st.columns([3,1])
with a1:
    new_type = st.selectbox("Add block type…", list(BLOCK_TYPES.keys()))
with a2:
    if st.button("➕ Add Block"):
        uid = str(uuid.uuid4())
        t = BLOCK_TYPES[new_type]
        if t == "text":
            payload = {"text":"", "color":"#000000", "size":16}
        elif t in ("youtube","image","embed"):
            payload = {"url":""}
        else:  # csv
            payload = {"csv":"col1,col2\nval1,val2", "color":"#000000", "size":16}
        st.session_state["blocks"].append({"uid":uid,"type":t,"payload":payload})

to_delete = None
for idx, blk in enumerate(st.session_state["blocks"]):
    with st.expander(f"Block {idx+1}: {blk['type']}"):
        if blk["type"] == "text":
            blk["payload"]["text"]  = st.text_area("Text", blk["payload"]["text"], key=f"text_{blk['uid']}")
            blk["payload"]["color"] = st.color_picker("Color", blk["payload"]["color"], key=f"col_{blk['uid']}")
            blk["payload"]["size"]  = st.slider("Size(px)", 8,48, blk["payload"]["size"], key=f"size_{blk['uid']}")
        elif blk["type"] in ("youtube","image","embed"):
            label = "URL" if blk["type"]!="image" else "Image URL"
            blk["payload"]["url"]   = st.text_input(label, blk["payload"]["url"], key=f"url_{blk['uid']}")
        else:  # csv
            blk["payload"]["csv"]   = st.text_area("CSV", blk["payload"]["csv"], key=f"csv_{blk['uid']}")
            blk["payload"]["color"] = st.color_picker("Text Color", blk["payload"]["color"], key=f"csv_col_{blk['uid']}")
            blk["payload"]["size"]  = st.slider("Font Size(px)", 8,48, blk["payload"]["size"], key=f"csv_size_{blk['uid']}")

        if st.button("🗑️ Delete this block", key=f"del_{blk['uid']}"):
            to_delete = idx

if to_delete is not None:
    st.session_state["blocks"].pop(to_delete)

# ──────────────────────────────────────────────────────────────
# 9. Save / Update
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save / Update"):
    full_html = "".join(block_html(b) for b in st.session_state["blocks"])
    with engine.begin() as conn:
        if st.session_state["row_id"]:
            conn.execute(
                text(f"UPDATE {chosen} SET title=:t, content=:c WHERE id=:id"),
                {"t": title_html, "c": full_html, "id": st.session_state["row_id"]}
            )
        else:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES (:t, :c)"),
                {"t": title_html, "c": full_html}
            )
    st.success("Saved ✔︎ – refreshing…")
    safe_rerun()

# ──────────────────────────────────────────────────────────────
# 10. Live Preview
# ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Live Preview")
st.markdown(title_html, unsafe_allow_html=True)
st.markdown("".join(block_html(b) for b in st.session_state["blocks"]), unsafe_allow_html=True)
