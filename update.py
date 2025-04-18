import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1. DATABASE POOL
# ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

# ──────────────────────────────────────────────────────────────
# 2. PAGE ‑ BASICS
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]

with st.sidebar:
    st.header("Select section")
    selected_tab = st.selectbox("Choose a table", TAB_NAMES)

# ──────────────────────────────────────────────────────────────
# 3. LOAD EXISTING RECORD (id = 1)
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_row(tab: str):
    with engine.connect() as cn:
        r = cn.execute(
            text(f"SELECT id, title, content FROM {tab} ORDER BY id LIMIT 1")
        ).fetchone()
    return r

row = fetch_row(selected_tab)
row_id = row.id if row else None
initial_title = row.title if row else ""
initial_content = row.content if row else ""

# ──────────────────────────────────────────────────────────────
# 4. SESSION STATE FOR MULTI‑BLOCK CONTENT
# ──────────────────────────────────────────────────────────────
if "loaded_tab" not in st.session_state or st.session_state.loaded_tab != selected_tab:
    # First visit or tab switch → initialise
    st.session_state.loaded_tab = selected_tab
    st.session_state.content_blocks = (
        [initial_content] if initial_content else []
    )

# ──────────────────────────────────────────────────────────────
# 5. TITLE EDITOR
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
tl, tr = st.columns([3, 1])
with tl:
    title_text = st.text_input("Text", value=initial_title, key="title_text")
with tr:
    title_color = st.color_picker("Color", "#000000", key="title_color")
title_size = st.slider("Font size (px)", 8, 48, 18, key="title_size")
title_is_html = st.toggle("Interpret title as raw HTML?", value=False)

stored_title = (
    title_text
    if title_is_html
    else f'<span style="color:{title_color};font-size:{title_size}px;">{title_text}</span>'
)

# ──────────────────────────────────────────────────────────────
# 6. BLOCK‑BY‑BLOCK CONTENT BUILDER
# ──────────────────────────────────────────────────────────────
st.subheader("➕ Add a new content block")

with st.form("block_form", clear_on_submit=True):
    block_type = st.selectbox(
        "Block type",
        ["Plain text / HTML", "YouTube URL", "Embed URL", "CSV → Table"],
    )

    # DYNAMIC INPUTS -----------------------------------------------------------
    if block_type == "Plain text / HTML":
        txt = st.text_area("Markdown / HTML", height=150)
        txt_color = st.color_picker("Text color", "#000000")
        txt_size = st.slider("Font size (px)", 8, 48, 16)
        snippet = (
            f'<div style="color:{txt_color};font-size:{txt_size}px;">{txt}</div>'
        )

    elif block_type == "YouTube URL":
        yt = st.text_input("Paste a full YouTube URL (https://…)")
        embed = yt.replace("watch?v=", "embed/")
        snippet = f'<iframe width="560" height="315" src="{embed}" frameborder="0" allowfullscreen></iframe>'

    elif block_type == "Embed URL":
        url = st.text_input("Any embeddable URL (maps, video, chart…)")
        snippet = f'<iframe src="{url}" style="width:100%;height:400px;border:none;"></iframe>'

    else:  # CSV → Table
        csv_raw = st.text_area("Paste CSV (first row = headers)", height=150)
        rows = [r.split(",") for r in csv_raw.strip().splitlines() if r.strip()]
        if rows:
            hdr, data = rows[0], rows[1:]
            table = "<table><thead><tr>" + "".join(
                f"<th>{h}</th>" for h in hdr
            ) + "</tr></thead><tbody>"
            for r in data:
                table += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            table += "</tbody></table>"
            snippet = table
        else:
            snippet = ""

    # SUBMIT BUTTON ------------------------------------------------------------
    add_it = st.form_submit_button("Add block ➜")
    if add_it and snippet:
        st.session_state.content_blocks.append(snippet)
        st.success("Block added!")

# OPTION TO CLEAR ALL BLOCKS ---------------------------------------------------
if st.button("🗑️ Clear ALL blocks"):
    st.session_state.content_blocks = []

# ──────────────────────────────────────────────────────────────
# 7. LIVE PREVIEW OF COMBINED CONTENT
# ──────────────────────────────────────────────────────────────
combined_content = "\n".join(st.session_state.content_blocks)

st.divider()
st.subheader("Live preview")
st.markdown(stored_title, unsafe_allow_html=True)
st.markdown(combined_content, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 8. SAVE / UPDATE TO DATABASE
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save to database"):
    with engine.begin() as cn:
        if row_id:
            cn.execute(
                text(
                    f"UPDATE {selected_tab} SET title=:ti, content=:co WHERE id=:id"
                ),
                {"ti": stored_title, "co": combined_content, "id": row_id},
            )
        else:
            cn.execute(
                text(
                    f"INSERT INTO {selected_tab} (title, content) VALUES (:ti, :co)"
                ),
                {"ti": stored_title, "co": combined_content},
            )
    st.success("Saved! Reloading…")
    st.experimental_rerun()
