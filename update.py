from __future__ import annotations
import re, uuid, io, urllib.parse

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

from updatesidbare import navigation
import tabledit
from streamlit_quill import st_quill
from streamlit_ace import st_ace

# ──────────────────────────────────────────────────────────────
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.rerun()

@st.cache_resource(show_spinner=False)
def get_engine():
    return create_engine(
        st.secrets["postgres"]["connection_string"],
        pool_pre_ping=True,
        isolation_level="AUTOCOMMIT",
    )

engine = get_engine()

TAB_NAMES = [
    "introtab1", "introtab2", "introtab3",
    # Week 1
    *[f"w1tab{i}" for i in range(1, 12)],
    # Week 2
    *[f"w2tab{i}" for i in range(1, 13)],
    # Week 3
    *[f"w3tab{i}" for i in range(1, 13)],
    # Week 4
    *[f"w4tab{i}" for i in range(1, 8)],
    # Week 5
    *[f"w5tab{i}" for i in range(1, 9)],
]
BLOCK_TYPES = {
    "Text":        "text",
    "Image URL":   "image",
    "CSV → Table": "csv",
    "Text/Rich":   "rich",
    "Text/HTML":   "html",
    "Video URL":   "video",
}

# Helper functions

def ensure_https(u: str) -> str:
    return u if u.startswith(("http://","https://")) else "https://" + u


def load_row(table: str):
    return engine.connect().execute(
        text(f"SELECT id, title, content FROM {table} ORDER BY id LIMIT 1")
    ).fetchone()


def update_content_db(chosen: str):
    parts = [block_html(b) for b in st.session_state.get("blocks", []) if block_html(b)]
    new_html = "<br>".join(parts)
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET content = :c WHERE id = :id"),
                {"c": new_html, "id": st.session_state["row_id"]},
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES ('', :c)"),
                {"c": new_html},
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None


def update_title_db(chosen: str, title_html: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = :t WHERE id = :id"),
                {"t": title_html, "id": st.session_state["row_id"]},
            )
    else:
        with engine.begin() as conn:
            conn.execute(
                text(f"INSERT INTO {chosen} (title, content) VALUES (:t, '')"),
                {"t": title_html},
            )
        row = load_row(chosen)
        st.session_state["row_id"] = row.id if row else None


def delete_title_db(chosen: str):
    if st.session_state.get("row_id"):
        with engine.begin() as conn:
            conn.execute(
                text(f"UPDATE {chosen} SET title = '' WHERE id = :id"),
                {"id": st.session_state["row_id"]},
            )


def get_video_embed_html(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    # YouTube
    if re.search(r'(youtu\.be|youtube\.com)', url, re.IGNORECASE):
        if "youtube.com/embed/" in url:
            embed_url = url
        else:
            m = re.search(r'(?:v=|be/)([^&?/]+)', url)
            vid = m.group(1) if m else url
            embed_url = f"https://www.youtube.com/embed/{vid}"
        return (
            f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'allowfullscreen></iframe>'
        )
    # Vimeo
    elif "vimeo.com" in url:
        if "player.vimeo.com/video/" in url:
            src = url
        else:
            m = re.search(r'vimeo\.com/(?:.*?/)?([0-9]+)', url)
            vid = m.group(1) if m else ""
            src = f"https://player.vimeo.com/video/{vid}"
        return (
            f'<iframe width="640" height="360" src="{src}" frameborder="0" '
            f'allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
        )
    # Direct video file
    elif url.lower().endswith((".mp4", ".webm", ".ogg", ".ogv", ".mov")):
        return (
            f'<video controls style="max-width:100%;height:auto;" src="{url}">'  
            "Sorry, your browser doesn't support embedded videos."
            "</video>"
        )
    # Fallback
    else:
        return (
            f'<video controls style="max-width:100%;height:auto;" src="{url}">'  
            "Sorry, your browser doesn't support embedded videos."
            "</video>"
        )

BLOCK_RGX = re.compile(r"<!--BLOCK_START:(?P<type>[a-z]+?)-->(?P<html>.*?)<!--BLOCK_END-->", re.S)

def block_html(block: dict) -> str:
    t, p = block["type"], block["payload"]
    if t == "text":
        return (
            f'<!--BLOCK_START:text-->'
            f'<p style="color:{p["color"]};font-size:{p["size"]}px;margin:0">'
            f'{p["text"]}</p><!--BLOCK_END-->'
        )
    if t == "image":
        url = ensure_https(p["url"])
        return f'<!--BLOCK_START:image--><img src="{url}" style="max-width:100%;"><!--BLOCK_END-->'
    if t == "csv":
        txt = (p.get("csv") or "").strip()
        if not txt:
            return ""
        try:
            df = pd.read_csv(io.StringIO(txt))
            raw = df.to_html(index=False, border=1)
        except Exception as e:
            return f'<!--BLOCK_START:csv--><p style="color:red;">⚠️ {e}</p><!--BLOCK_END-->'
        return (
            f'<!--BLOCK_START:csv-->
