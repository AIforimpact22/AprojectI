import streamlit as st
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# ──────────────────────────────────────────────────────────────
# 1. Database connection
#    The connection string lives in .streamlit/secrets.toml
# ──────────────────────────────────────────────────────────────
@st.cache_resource  # keeps the pool warm across reruns
def get_engine():
    conn_str = st.secrets["postgres"]["connection_string"]
    return create_engine(conn_str, pool_pre_ping=True, isolation_level="AUTOCOMMIT")

engine = get_engine()

# ──────────────────────────────────────────────────────────────
# 2. Page setup
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

# All 51 table names
TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]

with st.sidebar:
    st.header("Select section")
    selected_tab = st.selectbox("Choose a table", TAB_NAMES)

# ──────────────────────────────────────────────────────────────
# 3. Fetch existing row (we treat row id=1 as “current content”)
# ──────────────────────────────────────────────────────────────
def get_current_row(table: str):
    query = text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as conn:
        row = conn.execute(query).fetchone()
    return row

row = get_current_row(selected_tab)
current_title  = row.title   if row else ""
current_html   = row.content if row else ""
row_id         = row.id if row else None

# ──────────────────────────────────────────────────────────────
# 4. UI – Title block
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
col1, col2 = st.columns([3, 1])
with col1:
    title_text = st.text_input("Text", value=current_title)
with col2:
    t_color = st.color_picker("Color", "#000000")
t_size   = st.slider("Font size (px)", 8, 48, 18)
t_is_html = st.toggle("Interpret title as raw HTML?", value=False)

# Build the stored title value
if t_is_html:
    stored_title = title_text  # take verbatim
else:
    stored_title = f'<span style="color:{t_color};font-size:{t_size}px;">{title_text}</span>'

# ──────────────────────────────────────────────────────────────
# 5. UI – Content block
# ──────────────────────────────────────────────────────────────
st.subheader("Content")
c_type = st.selectbox(
    "Content type",
    ["Rich text / HTML", "YouTube URL", "Embed URL", "CSV → Table"],
    index=0,
)

if c_type == "Rich text / HTML":
    content_raw = st.text_area("Markdown / HTML", value=current_html, height=200)
    c_color = st.color_picker("Text color", "#000000")
    c_size  = st.slider("Font size (px)", 8, 48, 16, key="csize")
    stored_content = (
        f'<div style="color:{c_color};font-size:{c_size}px;">{content_raw}</div>'
    )

elif c_type == "YouTube URL":
    yt_url = st.text_input("YouTube full URL (https://…)", value="")
    stored_content = f'<iframe width="560" height="315" src="{yt_url.replace("watch?v=", "embed/")}" frameborder="0" allowfullscreen></iframe>'

elif c_type == "Embed URL":
    em_url = st.text_input("Any embeddable URL (maps, another video…)", value="")
    stored_content = f'<iframe src="{em_url}" style="width:100%;height:400px;border:none;"></iframe>'

else:  # CSV → Table
    csv_text = st.text_area("Paste CSV (first line = headers)", height=200)
    rows = [r.split(",") for r in csv_text.strip().splitlines() if r.strip()]
    headers, data = rows[0], rows[1:]
    table_html = "<table><thead><tr>" + "".join(
        f"<th>{h}</th>" for h in headers
    ) + "</tr></thead><tbody>"
    for r in data:
        table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    table_html += "</tbody></table>"
    stored_content = table_html

# ──────────────────────────────────────────────────────────────
# 6. Save / Update
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save to database"):
    with engine.begin() as conn:
        if row_id:  # update
            q = text(
                f"UPDATE {selected_tab} SET title=:title, content=:content WHERE id=:id"
            )
            conn.execute(q, {"title": stored_title, "content": stored_content, "id": row_id})
        else:       # insert
            q = text(
                f"INSERT INTO {selected_tab} (title, content) VALUES (:title, :content)"
            )
            conn.execute(q, {"title": stored_title, "content": stored_content})
    st.success("Saved!  ↻  Page will refresh.")
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 7. Live preview
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live preview")
st.markdown(stored_title, unsafe_allow_html=True)
st.markdown(stored_content, unsafe_allow_html=True)
