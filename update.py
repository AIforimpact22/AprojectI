# update.py

import streamlit as st
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from github_sync import push_update_to_github

# 1) Helper to force a rerun after saving
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun not available.")

# 2) Cached DB connection
@st.cache_resource
def get_conn():
    # expects a [postgres] section in .streamlit/secrets.toml
    db = st.secrets["postgres"]
    conn = psycopg2.connect(
        host=db["host"],
        port=db.get("port", 5432),
        dbname=db["dbname"],
        user=db["user"],
        password=db["password"],
    )
    conn.autocommit = True
    return conn

# 3) Ensure the scripts table exists
def init_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scripts (
                id SERIAL PRIMARY KEY,
                module_name TEXT NOT NULL,
                file_name   TEXT NOT NULL,
                content     TEXT NOT NULL,
                last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
                UNIQUE(module_name, file_name)
            );
        """)

# 4) Fetch all scripts
def fetch_scripts(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM scripts ORDER BY module_name, file_name;")
        return cur.fetchall()

# 5) Update a single script row
def update_script(conn, script_id, new_content):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE scripts SET content=%s, last_updated=NOW() WHERE id=%s;",
            (new_content, script_id),
        )

# --- main Streamlit app ---
st.set_page_config(page_title="Script Updater", layout="wide")
st.title("📄 Update Your Module Scripts")

# initialize
conn = get_conn()
init_db(conn)
scripts = fetch_scripts(conn)

if not scripts:
    st.warning(
        "No scripts found in the database.  \n"
        "Populate the `scripts` table with one row per file (`module_name`, `file_name`, `content`) first."
    )
    st.stop()

# build editors
edited_contents = {}
for script in scripts:
    # show path like "modules_week1/tab1.py" or just "modules_intro.py"
    path = (
        f"{script['module_name']}/{script['file_name']}"
        if script["module_name"]
        else script["file_name"]
    )
    edited_contents[path] = st.text_area(
        path,
        value=script["content"],
        height=400,
        key=path,
    )

# save button
if st.button("💾 Save Changes"):
    for script in scripts:
        path = (
            f"{script['module_name']}/{script['file_name']}"
            if script["module_name"]
            else script["file_name"]
        )
        new_txt = edited_contents[path]
        if new_txt != script["content"]:
            # 1) update DB
            update_script(conn, script["id"], new_txt)
            # 2) push to GitHub
            push_update_to_github(path, new_txt)
            st.success(f"✔️ Updated `{path}` in DB & GitHub.")
    st.info("All done – reloading editor…")
    safe_rerun()
