# handle.py
import streamlit as st
import psycopg2
import json

def get_connection():
    try:
        DATABASE_URL = st.secrets["DATABASE_URL"]
    except KeyError as e:
        raise KeyError("DATABASE_URL not found in st.secrets. Check your secrets.toml or Streamlit Cloud settings.") from e

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is empty in st.secrets.")
    return psycopg2.connect(DATABASE_URL)

def get_tab_content(tab_name):
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
