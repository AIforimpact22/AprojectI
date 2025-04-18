import streamlit as st

# ──────────────────────────────────────────────────────────────
# 0️⃣  This must be the FIRST Streamlit command
# ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Tabbed CMS", layout="wide")

from sqlalchemy import create_engine, text

# ──────────────────────────────────────────────────────────────
# 1️⃣  Database connection (taken from .streamlit/secrets.toml)
# ──────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    """Create (and cache) the SQLAlchemy engine that talks to Neon."""
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

# ──────────────────────────────────────────────────────────────
# 2️⃣  Layout & navigation
# ──────────────────────────────────────────────────────────────
st.title("📑 Tabbed Content Manager")

TAB_NAMES = ["intro"] + [f"tab{i}" for i in range(1, 51)]
with st.sidebar:
    st.header("Select section")
    selected_tab = st.selectbox("Choose a table", TAB_NAMES)

# ──────────────────────────────────────────────────────────────
# 3️⃣  Helpers – fetch the first (and only) row per table
# ──────────────────────────────────────────────────────────────

def get_current_row(table_name: str):
    """Return (id, title, content) or None if the table is empty."""
    query = text(f"SELECT id, title, content FROM {table_name} ORDER BY id LIMIT 1")
    with engine.connect() as conn:
        return conn.execute(query).fetchone()

row   = get_current_row(selected_tab)
row_id = row.id      if row else None
curr_title_html   = row.title   if row else ""
curr_content_html = row.content if row else ""

# ──────────────────────────────────────────────────────────────
# 4️⃣  Title editor
# ──────────────────────────────────────────────────────────────
st.subheader("Title")

txt_col, col_col = st.columns([3, 1])
with txt_col:
    title_text = st.text_input("Title text", value=st.session_state.get("title_text", ""))
    st.session_state["title_text"] = title_text
with col_col:
    t_color = st.color_picker("Text color", value=st.session_state.get("title_color", "#000000"))
    st.session_state["title_color"] = t_color

t_size   = st.slider("Font size (px)", 8, 48, st.session_state.get("title_size", 18))
st.session_state["title_size"] = t_size

t_is_html = st.toggle("Interpret as raw HTML?", value=st.session_state.get("title_is_html", False))
st.session_state["title_is_html"] = t_is_html

stored_title = (
    title_text if t_is_html else f'<span style="color:{t_color};font-size:{t_size}px;">{title_text}</span>'
)

# ──────────────────────────────────────────────────────────────
# 5️⃣  Content blocks – add as many as you need
# ──────────────────────────────────────────────────────────────
st.subheader("Content blocks (fill any you need)")

content_parts: list[str] = []  # Collect snippets, then join

# 5‑A  Rich text / HTML
with st.expander("📝 Rich text / HTML"):
    rt_text  = st.text_area("Markdown / HTML", height=200, key="rt_text")
    rt_color = st.color_picker("Text color", "#000000", key="rt_color")
    rt_size  = st.slider("Font size (px)", 8, 48, 16, key="rt_size")
    if rt_text.strip():
        snippet = f'<div style="color:{rt_color};font-size:{rt_size}px;">{rt_text}</div>'
        content_parts.append(snippet)

# 5‑B  YouTube video
with st.expander("🎬 YouTube video"):
    yt_url = st.text_input("YouTube URL", key="yt_url")
    if yt_url.strip():
        embed_url = yt_url.replace("watch?v=", "embed/")
        snippet = (
            f'<iframe width="560" height="315" src="{embed_url}" '
            "frameborder=\"0\" allowfullscreen></iframe>"
        )
        content_parts.append(snippet)

# 5‑C  Generic embed
with st.expander("🌐 Embed URL"):
    em_url = st.text_input("Embeddable URL", key="em_url")
    if em_url.strip():
        snippet = (
            f'<iframe src="{em_url}" style="width:100%;height:400px;border:none;"></iframe>'
        )
        content_parts.append(snippet)

# 5‑D  CSV → HTML table
with st.expander("📊 CSV → HTML table"):
    csv_text = st.text_area("Paste CSV (first line = headers)", height=200, key="csv_text")
    if csv_text.strip():
        rows = [r.strip() for r in csv_text.strip().splitlines() if r.strip()]
        if rows:
            headers = rows[0].split(",")
            data_rows = [r.split(",") for r in rows[1:]]
            table_html = (
                "<table><thead><tr>"
                + "".join(f"<th>{h}</th>" for h in headers)
                + "</tr></thead><tbody>"
            )
            for r in data_rows:
                table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
            table_html += "</tbody></table>"
            content_parts.append(table_html)

# ──────────────────────────────────────────────────────────────
# 6️⃣  Compose final HTML for content
# ──────────────────────────────────────────────────────────────
stored_content = "<br>".join(content_parts) if content_parts else curr_content_html

# ──────────────────────────────────────────────────────────────
# 7️⃣  Save / update the database
# ──────────────────────────────────────────────────────────────
if st.button("💾 Save to database"):
    with engine.begin() as conn:
        if row_id:
            conn.execute(
                text(f"UPDATE {selected_tab} SET title=:t, content=:c WHERE id=:id"),
                {"t": stored_title, "c": stored_content, "id": row_id},
            )
        else:
            conn.execute(
                text(f"INSERT INTO {selected_tab} (title, content) VALUES (:t, :c)"),
                {"t": stored_title, "c": stored_content},
            )
    st.success("Saved!  ↻  Refreshing …")
    st.experimental_rerun()

# ──────────────────────────────────────────────────────────────
# 8️⃣  Live preview (what visitors will see)
# ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("Live preview")
st.markdown(stored_title or curr_title_html, unsafe_allow_html=True)
st.markdown(stored_content or curr_content_html, unsafe_allow_html=True)
