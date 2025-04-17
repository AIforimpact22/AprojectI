# update.py
import streamlit as st
import psycopg2
from psycopg2 import sql

# --- Helpers ---
@st.cache_resource
def get_conn():
    creds = st.secrets["postgres"]
    return psycopg2.connect(
        host     = creds["host"],
        port     = creds["port"],
        user     = creds["user"],
        password = creds["password"],
        dbname   = creds["dbname"]
    )

def list_schemas_and_tabs(conn):
    """Return dict: { 'intro': [], 'week1': ['tab1','tab2',...], ... }"""
    cur = conn.cursor()
    # load week schemas
    cur.execute("""
      SELECT nspname
      FROM pg_namespace
      WHERE nspname LIKE 'modules_week%';
    """)
    weeks = [row[0] for row in cur.fetchall()]
    result = {"intro": []}
    for wk in weeks:
        cur.execute(sql.SQL(
          "SELECT tablename FROM pg_tables WHERE schemaname = %s ORDER BY tablename;"
        ), [wk])
        tabs = [r[0] for r in cur.fetchall()]
        result[wk.split('_')[-1]] = tabs
    cur.close()
    return result

def fetch_content(conn, schema, table):
    cur = conn.cursor()
    query = sql.SQL("SELECT title, video_url, content FROM {}.{};")\
            .format(sql.Identifier(schema), sql.Identifier(table))
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    return rows

def render(rows):
    for title, video_url, content in rows:
        st.title(title)
        if video_url:
            st.video(video_url)
        # allow HTML/markdown
        st.markdown(content, unsafe_allow_html=True)

# --- Main ---
def main():
    st.set_page_config(page_title="Course Updates", layout="wide")
    conn = get_conn()
    modules = list_schemas_and_tabs(conn)

    st.sidebar.header("Select Module")
    choice = st.sidebar.selectbox("Module", list(modules.keys()), index=0)

    if choice != "intro":
        tab = st.sidebar.selectbox("Tab", modules[choice])
        rows = fetch_content(conn, f"modules_week{choice}", tab)
    else:
        rows = fetch_content(conn, "public", "modules_intro")

    render(rows)

if __name__ == "__main__":
    main()
