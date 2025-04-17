# update.py
import os
import streamlit as st
import psycopg2
from psycopg2 import sql

# ——————————————————————————————————————————
# 1) Connection helper (single secret: db_url)
@st.cache_resource
def get_connection():
    # Try secret first, then env var
    db_url = st.secrets.get("db_url") or os.getenv("DB_URL")
    if not db_url:
        st.error(
            "❌ No database URL found.\n\n"
            "Please set `db_url` in your Streamlit secrets or the DB_URL env var."
        )
        st.stop()
    return psycopg2.connect(db_url)

# ——————————————————————————————————————————
# 2) Discover modules & tabs
def get_modules(conn):
    cur = conn.cursor()
    # all schemas named modules_weekX
    cur.execute("""
      SELECT nspname
        FROM pg_namespace
       WHERE nspname LIKE 'modules_week%';
    """)
    schemas = [row[0] for row in cur.fetchall()]
    modules = {"intro": []}
    for schema in schemas:
        week = schema.split("_")[-1]
        cur.execute(
          "SELECT tablename FROM pg_tables WHERE schemaname = %s ORDER BY tablename;",
          (schema,)
        )
        modules[week] = [r[0] for r in cur.fetchall()]
    cur.close()
    return modules

# ——————————————————————————————————————————
# 3) Fetch rows from one table
def fetch_content(conn, schema, table):
    cur = conn.cursor()
    q = sql.SQL("SELECT title, video_url, content FROM {}.{};")\
         .format(sql.Identifier(schema), sql.Identifier(table))
    cur.execute(q)
    rows = cur.fetchall()
    cur.close()
    return rows

# ——————————————————————————————————————————
# 4) Render each row: title, video, markdown/HTML
def render(rows):
    for title, video_url, content in rows:
        st.markdown(f"## {title}")
        if video_url:
            st.video(video_url)
        st.markdown(content, unsafe_allow_html=True)

# ——————————————————————————————————————————
# 5) Main
def main():
    st.set_page_config(page_title="Course Content", layout="wide")
    conn    = get_connection()
    modules = get_modules(conn)

    choice = st.sidebar.selectbox("Module", list(modules.keys()))
    if choice == "intro":
        rows = fetch_content(conn, "public", "modules_intro")
    else:
        tab  = st.sidebar.selectbox("Tab", modules[choice])
        rows = fetch_content(conn, f"modules_{choice}", tab)

    render(rows)

if __name__ == "__main__":
    main()
