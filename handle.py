# handle.py
import streamlit as st
import psycopg2
import json

def get_connection():
    # Retrieve the connection string from Streamlit secrets.
    # If you stored it under a section, access it appropriately.
    # Here we assume the key is: st.secrets["database"]["DATABASE_URL"]
    DATABASE_URL = st.secrets["database"]["DATABASE_URL"]
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in Streamlit secrets.")
    return psycopg2.connect(DATABASE_URL)

def get_tab_content(tab_name):
    """Fetch content for a given tab from the database."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
      SELECT title, video_url, content, formatting_options 
      FROM tab_content 
      WHERE tab_name = %s;
    """
    cur.execute(query, (tab_name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {
            "title": row[0],
            "video_url": row[1],
            "content": row[2],
            "formatting_options": row[3],
        }
    return None

def update_tab_content(tab_name, title, video_url, content, formatting_options):
    """Insert new content or update the existing content for a given tab."""
    conn = get_connection()
    cur = conn.cursor()
    query = """
      INSERT INTO tab_content (tab_name, title, video_url, content, formatting_options)
      VALUES (%s, %s, %s, %s, %s)
      ON CONFLICT (tab_name) DO UPDATE SET
          title = EXCLUDED.title,
          video_url = EXCLUDED.video_url,
          content = EXCLUDED.content,
          formatting_options = EXCLUDED.formatting_options,
          updated_at = NOW();
    """
    cur.execute(query, (tab_name, title, video_url, content, json.dumps(formatting_options)))
    conn.commit()
    cur.close()
    conn.close()
