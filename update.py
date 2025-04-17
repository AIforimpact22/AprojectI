# update.py
import streamlit as st
import psycopg2
from psycopg2 import sql

# ————————————————
# 1) Connect (use a single secret: "db_url")
@st.cache_resource
def get_connection():
    # Put your full connection string in Secrets as: db_url = "postgres://user:pass@host:port/dbname"
    return psycopg2.connect(st.secrets["db_url"])

# ————————————————
# 2) Discover all modules & tabs
def get_modules(conn):
    cur = conn.cursor()
    # find all "modules_weekX" schemas
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
        tabs = [r[0] for r in cur.fetchall()]
        modules[week] = tabs
    cur.close()
    return modules

# ————————————————
# 3) Fetch content for one table
def fetch_content(conn, schema, table):
    cur = conn.cursor()
    q = sql.SQL("SELECT title, video_url, content FROM {}.{};")\
           .format(sql.Identifier(schema), sql.Identifier(table))
    cur.execute(q)
    rows = cur.fetchall()
    cur.close()
    return rows

# ————————————————
# 4) Render rows
def render(rows):
    for title, video_url, content in rows:
        st.markdown(f"## {title}")
        if video_url:
            st.video(video_url)
        st.markdown(content, unsafe_allow_html=True)

# ————————————————
# 5) Main app
def main():
    st.set_page_config(page_title="Course Content", layout="wide")
    conn    = get_connection()
    modules = get_modules(conn)

    choice = st.sidebar.selectbox("Module", list(modules.keys()))

    if choice == "intro":
        rows = fetch_content(conn, "public", "modules_intro")
    else:
        tab   = st.sidebar.selectbox("Tab", modules[choice])
        rows  = fetch_content(conn, f"modules_{choice}", tab)

    render(rows)

if __name__ == "__main__":
    main()
