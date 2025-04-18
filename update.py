import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1. DB connection (taken from .streamlit/secrets.toml)
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
# 2. Page + sidebar
# ──────────────────────────────────────────────────────────────
st.set_page_config("Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager (multi‑segment)")

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
with st.sidebar:
    st.header("Select section")
    selected_tab = st.selectbox("Choose a table", TAB_NAMES)

# ──────────────────────────────────────────────────────────────
# 3. Load or initialise title + segments for this tab
# ──────────────────────────────────────────────────────────────
def fetch_row(table):
    q = text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as c:
        return c.execute(q).fetchone()

row = fetch_row(selected_tab)
if "current_tab" not in st.session_state or st.session_state.current_tab != selected_tab:
    st.session_state.current_tab = selected_tab
    st.session_state.row_id = row.id if row else None
    st.session_state.title_raw = (
        row.title if row else ""
    )  # raw HTML already stored
    st.session_state.segments = [row.content] if (row and row.content) else []

# ──────────────────────────────────────────────────────────────
# 4. TITLE editor
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
col1, col2 = st.columns([3, 1])
with col1:
    title_text = st.text_input("Text", st.session_state.title_raw, key="title_input")
with col2:
    title_color = st.color_picker("Color", "#000000")
title_size = st.slider("Font size (px)", 8, 48, 18)
is_html = st.toggle("Interpret title as raw HTML", False)
stored_title = (
    title_text
    if is_html
    else f'<span style="color:{title_color};font-size:{title_size}px;">{title_text}</span>'
)

# ──────────────────────────────────────────────────────────────
# 5. ADD‑SEGMENT UI
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("➕ Add a content segment")

c_type = st.selectbox(
    "Segment type",
    ["Plain text", "Rich text / HTML", "YouTube URL", "Embed URL", "CSV → Table"],
)

def make_segment_html():
    if c_type == "Plain text":
        txt = st.text_area("Text", height=120, key="plain")
        return f"<p>{txt}</p>"

    if c_type == "Rich text / HTML":
        raw = st.text_area("Markdown / raw HTML", height=180, key="rich")
        color = st.color_picker("Text color", "#000000", key="c1")
        size = st.slider("Font size (px)", 8, 48, 16, key="c2")
        return f'<div style="color:{color};font-size:{size}px;">{raw}</div>'

    if c_type == "YouTube URL":
        url = st.text_input("https://…", key="yt")
        return (
            f'<iframe width="560" height="315" src="{url.replace("watch?v=", "embed/")}"'
            ' frameborder="0" allowfullscreen></iframe>'
        )

    if c_type == "Embed URL":
        url = st.text_input("Embeddable URL", key="em")
        h = st.number_input("Height (px)", 200, 1000, 400, key="emh")
        return f'<iframe src="{url}" style="width:100%;height:{h}px;border:none;"></iframe>'

    # CSV -> HTML table
    csv_text = st.text_area("Paste CSV (first row = headings)", height=200, key="csv")
    rows = [r.split(",") for r in csv_text.strip().splitlines() if r.strip()]
    if not rows:
        return ""
    head, data = rows[0], rows[1:]
    html = (
        "<table><thead><tr>"
        + "".join(f"<th>{h}</th>" for h in head)
        + "</tr></thead><tbody>"
    )
    for r in data:
        html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    html += "</tbody></table>"
    return html

segment_html = make_segment_html()

if st.button("➕ Add segment"):
    if segment_html.strip():
        st.session_state.segments.append(segment_html)
        st.success("Segment added!")

# ──────────────────────────────────────────────────────────────
# 6. Segment list with delete + drag‑to‑reorder (Streamlit‑sortable‑elements)
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Current segments")
if st.session_state.segments:
    # simple delete buttons
    for idx, seg in enumerate(st.session_state.segments):
        colA, colB = st.columns([9, 1])
        with colA:
            st.markdown(seg, unsafe_allow_html=True)
        with colB:
            if st.button("🗑️", key=f"del{idx}"):
                st.session_state.segments.pop(idx)
                st.experimental_rerun()
else:
    st.info("No segments yet. Add one above!")

# ──────────────────────────────────────────────────────────────
# 7. SAVE
# ──────────────────────────────────────────────────────────────
full_content = "".join(st.session_state.segments)
st.divider()
if st.button("💾 Save to database"):
    with engine.begin() as conn:
        if st.session_state.row_id:  # UPDATE
            q = text(
                f"UPDATE {selected_tab} SET title=:t, content=:c WHERE id=:id"
            )
            conn.execute(
                q,
                {"t": stored_title, "c": full_content, "id": st.session_state.row_id},
            )
        else:  # INSERT
            q = text(f"INSERT INTO {selected_tab} (title, content) VALUES (:t, :c)")
            conn.execute(q, {"t": stored_title, "c": full_content})
    st.success("Saved – reloading.")
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 8. LIVE PREVIEW
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live preview")
st.markdown(stored_title, unsafe_allow_html=True)
st.markdown(full_content, unsafe_allow_html=True)
