import csv
from io import StringIO
from pathlib import Path

import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1.  Database connection (pulled from .streamlit/secrets.toml)
# ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    conn_str = st.secrets["postgres"]["connection_string"]
    return create_engine(conn_str, pool_pre_ping=True, isolation_level="AUTOCOMMIT")

engine = get_engine()

# ──────────────────────────────────────────────────────────────
# 2.  App skeleton
# ──────────────────────────────────────────────────────────────
st.set_page_config("Tabbed CMS – Blocks", layout="wide")
st.title("📑 Tabbed Content Manager – Block Edition")

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]

with st.sidebar:
    chosen = st.selectbox("Choose section", TAB_NAMES, key="chosen_tab")

# Reset the block editor when the user switches table
if "active_tab" not in st.session_state or st.session_state.active_tab != chosen:
    st.session_state.active_tab = chosen
    st.session_state.blocks = []            # list of block dictionaries
    st.session_state.title_text = ""        # raw title
    st.session_state.title_color = "#000000"
    st.session_state.title_size = 18
    st.session_state.title_is_html = False

blocks = st.session_state.blocks  # shorthand

# ──────────────────────────────────────────────────────────────
# 3.  TITLE editor (same idea as before)
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
c1, c2, c3 = st.columns([3, 1.2, 1])
st.session_state.title_text = c1.text_input(
    "Text", value=st.session_state.title_text, placeholder="Page headline here..."
)
st.session_state.title_color = c2.color_picker(
    "Colour", st.session_state.title_color
)
st.session_state.title_size = c3.slider(
    "Size (px)", 8, 48, st.session_state.title_size
)
st.session_state.title_is_html = st.toggle(
    "Interpret title as raw HTML?", st.session_state.title_is_html
)

def make_title_html():
    if st.session_state.title_is_html:
        return st.session_state.title_text
    return (
        f'<span style="color:{st.session_state.title_color};'
        f'font-size:{st.session_state.title_size}px;">'
        f'{st.session_state.title_text}</span>'
    )

# ──────────────────────────────────────────────────────────────
# 4.  ADD‑A‑BLOCK wizard
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a content block")

with st.expander("➕  New block"):
    kind = st.selectbox(
        "Block type",
        ["Text", "Rich text / HTML", "YouTube URL", "Image URL",
         "Embed URL", "CSV → Table"],
        key="new_kind",
    )

    if kind == "Text":
        txt = st.text_area("Text", key="new_txt")
        colA, colB = st.columns(2)
        txt_col = colA.color_picker("Colour", "#000000", key="new_txt_col")
        txt_size = colB.slider("Size (px)", 8, 48, 16, key="new_txt_size")
        if st.button("Add block", key="add_txt"):
            blocks.append(
                {"type": "text", "text": txt, "color": txt_col, "size": txt_size}
            )
            st.experimental_rerun()

    elif kind == "Rich text / HTML":
        html_src = st.text_area("Raw HTML / Markdown", key="new_html_src")
        if st.button("Add block", key="add_html"):
            blocks.append({"type": "html", "html": html_src})
            st.experimental_rerun()

    elif kind == "YouTube URL":
        yt = st.text_input("Full YouTube URL", key="new_yt")
        if st.button("Add block", key="add_yt"):
            blocks.append({"type": "youtube", "url": yt})
            st.experimental_rerun()

    elif kind == "Image URL":
        img = st.text_input("Image URL", key="new_img")
        if st.button("Add block", key="add_img"):
            blocks.append({"type": "image", "url": img})
            st.experimental_rerun()

    elif kind == "Embed URL":
        em = st.text_input("Embeddable URL (maps, loom, …)", key="new_embed")
        if st.button("Add block", key="add_embed"):
            blocks.append({"type": "embed", "url": em})
            st.experimental_rerun()

    else:  # CSV → Table
        csv_text = st.text_area("Paste CSV here", key="new_csv")
        if st.button("Add block", key="add_csv"):
            blocks.append({"type": "csv", "csv": csv_text})
            st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 5.  LIST, PREVIEW & DELETE blocks
# ──────────────────────────────────────────────────────────────
def block_to_html(b: dict) -> str:
    t = b["type"]
    if t == "text":
        return (
            f'<div style="color:{b["color"]};font-size:{b["size"]}px;">'
            f'{b["text"]}</div>'
        )
    if t == "html":
        return b["html"]
    if t == "youtube":
        embed = b["url"].replace("watch?v=", "embed/")
        return (
            f'<iframe width="560" height="315" '
            f'src="{embed}" frameborder="0" allowfullscreen></iframe>'
        )
    if t == "image":
        return f'<img src="{b["url"]}" style="max-width:100%;">'
    if t == "embed":
        return (
            f'<iframe src="{b["url"]}" '
            f'style="width:100%;height:400px;border:none;"></iframe>'
        )
    if t == "csv":
        f = StringIO(b["csv"])
        rdr = list(csv.reader(f))
        if not rdr:
            return ""
        head, rows = rdr[0], rdr[1:]
        h = "<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"
        for r in rows:
            h += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
        h += "</tbody></table>"
        return h
    return ""

st.divider()
st.subheader("Current blocks")

delete_indices = []
for i, b in enumerate(blocks):
    with st.container(border=True):
        st.markdown(f"**Block {i+1} – {b['type'].upper()}**")
        st.markdown(block_to_html(b), unsafe_allow_html=True)
        if st.button("🗑 Delete", key=f"del_{i}"):
            delete_indices.append(i)

# actually remove after iteration (avoids list‑size shift)
for idx in sorted(delete_indices, reverse=True):
    blocks.pop(idx)
if delete_indices:
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 6.  SAVE to Neon
# ──────────────────────────────────────────────────────────────
full_html = make_title_html() + "".join(block_to_html(b) for b in blocks)

st.divider()
if st.button("💾 Save page"):
    # Merge / upsert into table: one row (id=1) per section
    with engine.begin() as conn:
        row = conn.execute(
            text(f"SELECT id FROM {chosen} ORDER BY id LIMIT 1")
        ).fetchone()
        if row:
            conn.execute(
                text(
                    f"UPDATE {chosen} SET title=:title, content=:content "
                    f"WHERE id=:id"
                ),
                {"title": make_title_html(), "content": full_html, "id": row.id},
            )
        else:
            conn.execute(
                text(
                    f"INSERT INTO {chosen} (title, content) "
                    f"VALUES (:title, :content)"
                ),
                {"title": make_title_html(), "content": full_html},
            )
    st.success("Saved! (content overwrites previous version)")
    st.balloons()

# ──────────────────────────────────────────────────────────────
# 7.  LIVE PREVIEW
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live preview")
st.markdown(full_html, unsafe_allow_html=True)
