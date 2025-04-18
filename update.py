import streamlit as st
from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1.  DB connection (taken from secrets.toml)
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
# 2.  Page layout
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")
st.title("📑 Tabbed Content Manager")

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
with st.sidebar:
    st.header("Select section")
    selected_tab = st.selectbox("Choose a table", TAB_NAMES)

# ──────────────────────────────────────────────────────────────
# 3.  Fetch current row (first row = active content)
# ──────────────────────────────────────────────────────────────
def get_current_row(table):
    q = text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    with engine.connect() as c:
        return c.execute(q).fetchone()

row = get_current_row(selected_tab)
curr_title   = row.title   if row else ""
curr_content = row.content if row else ""
row_id       = row.id      if row else None

# ──────────────────────────────────────────────────────────────
# 4.  Title editor
# ──────────────────────────────────────────────────────────────
st.subheader("Title")
t_col1, t_col2 = st.columns([3, 1])
with t_col1:
    title_text = st.text_input("Text", value=curr_title, key="title_txt")
with t_col2:
    t_color = st.color_picker("Color", "#000000", key="tcol")
t_size   = st.slider("Font size (px)", 8, 48, 18, key="tsize")
t_is_html = st.toggle("Interpret title as raw HTML?", value=False)

stored_title = (
    title_text
    if t_is_html
    else f'<span style="color:{t_color};font-size:{t_size}px;">{title_text}</span>'
)

# ──────────────────────────────────────────────────────────────
# 5.  CONTENT BLOCKS – mix & match as many as you like
# ──────────────────────────────────────────────────────────────
st.subheader("Content blocks (fill any you need)")

content_parts = []  # collect blocks, then join ↓↓↓

# 📝 Rich text / HTML
with st.expander("📝 Rich text / HTML"):
    rt_text  = st.text_area("Markdown / HTML", height=200, key="rt_text")
    rt_color = st.color_picker("Text color", "#000000", key="rt_col")
    rt_size  = st.slider("Font size (px)", 8, 48, 16, key="rt_size")
    if rt_text.strip():
        content_parts.append(
            f'<div style="color:{rt_color};font-size:{rt_size}px;">{rt_text}</div>'
        )

# 🎬 YouTube
with st.expander("🎬 YouTube video"):
    yt_url = st.text_input("Full YouTube URL (https://…)", key="yt_url")
    if yt_url.strip():
        embed = yt_url.replace("watch?v=", "embed/")
        content_parts.append(
            f'<iframe width="560" height="315" src="{embed}" frameborder="0" allowfullscreen></iframe>'
        )

# 🌐 Generic embed
with st.expander("🌐 Embed any URL (maps, other videos…)"):
    em_url = st.text_input("Embeddable URL", key="em_url")
    if em_url.strip():
        content_parts.append(
            f'<iframe src="{em_url}" style="width:100%;height:400px;border:none;"></iframe>'
        )

# 📊 CSV → table
with st.expander("📊 CSV → HTML table"):
    csv_text = st.text_area("Paste CSV (first line = headers)", height=200, key="csv")
    if csv_text.strip():
        rows = [r.split(",") for r in csv_text.strip().splitlines() if r.strip()]
        if len(rows) >= 2:
            headers, data = rows[0], rows[1:]
            table_html = (
                "<table><thead><tr>"
                + "".join(f"<th>{h}</th>" for h in headers)
                + "</tr></thead><tbody>"
            )
            for r in data:
                table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            table_html += "</tbody></table>"
            content_parts.append(table_html)

# ──────────────────────────────────────────────────────────────
# 6.  Final composed content
# ──────────────────────────────────────────────────────────────
stored_content = "<br>".join(content_parts) if content_parts else curr_content

# ──────────────────────────────────────────────────────────────
# 7.  Save / update DB
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save to database"):
    with engine.begin() as conn:
        if row_id:  # UPDATE
            q = text(
                f"UPDATE {selected_tab} SET title=:t, content=:c WHERE id=:id"
            )
            conn.execute(q, {"t": stored_title, "c": stored_content, "id": row_id})
        else:       # INSERT
            q = text(f"INSERT INTO {selected_tab} (title, content) VALUES (:t, :c)")
            conn.execute(q, {"t": stored_title, "c": stored_content})
    st.success("Saved! ↻ Refreshing…")
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 8.  Live preview
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live preview")
st.markdown(stored_title,   unsafe_allow_html=True)
st.markdown(stored_content, unsafe_allow_html=True)
