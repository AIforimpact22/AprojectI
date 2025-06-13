# github_progress.py  – now backed by MySQL, no GitHub token needed
import streamlit as st
import mysql.connector
from mysql.connector import IntegrityError


# ──────────────────────────────────────────────────────────────────────────────
# DB helper                                                                    │
# ──────────────────────────────────────────────────────────────────────────────
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Compatibility stubs (load/save no longer needed)                            │
# ──────────────────────────────────────────────────────────────────────────────
def load_github_progress():
    """Stub kept for backward-compat imports; returns (None, None)."""
    return {}, None


def save_github_progress(progress_data, contents):
    """Stub kept for backward-compat imports; now a no-op."""
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Core API (same signatures as before)                                         │
# ──────────────────────────────────────────────────────────────────────────────
def get_user_progress(username):
    """
    Returns a dict like
      { "week1": int, "week2": int, ..., "week5": int }
    creating a fresh row with defaults if the user isn't present.
    """
    conn = _get_conn()
    cur  = conn.cursor(dictionary=True)

    cur.execute(
        """
        SELECT week1track, week2track, week3track, week4track, week5track
        FROM progress
        WHERE username = %s
        """,
        (username,),
    )
    row = cur.fetchone()

    if row is None:
        # Insert a new progress row with week1 unlocked (1) and others 0
        try:
            cur.execute(
                """
                INSERT INTO progress
                    (username, fullname, week1track, week2track, week3track, week4track, week5track)
                VALUES (%s, %s, 1, 0, 0, 0, 0)
                """,
                (username, username),   # fullname fallback = username
            )
            conn.commit()
            row = {
                "week1track": 1,
                "week2track": 0,
                "week3track": 0,
                "week4track": 0,
                "week5track": 0,
            }
        except IntegrityError:
            conn.rollback()
            # retry select in rare race condition
            cur.execute(
                """
                SELECT week1track, week2track, week3track, week4track, week5track
                FROM progress
                WHERE username = %s
                """,
                (username,),
            )
            row = cur.fetchone()

    conn.close()

    # Map DB column names → original keys expected by calling code
    return {
        "week1": row["week1track"],
        "week2": row["week2track"],
        "week3": row["week3track"],
        "week4": row["week4track"],
        "week5": row["week5track"],
    }


def update_user_progress(username, week, new_tab_index):
    """
    Update progress if new_tab_index is greater than the stored value.
    `week` is 1-5.
    """
    column = f"week{week}track"
    conn   = _get_conn()
    cur    = conn.cursor()

    # Check current value first
    cur.execute(
        f"SELECT {column} FROM progress WHERE username = %s",
        (username,),
    )
    row = cur.fetchone()
    current = row[0] if row else 0

    if new_tab_index > current:
        cur.execute(
            f"UPDATE progress SET {column} = %s WHERE username = %s",
            (new_tab_index, username),
        )
        conn.commit()

    conn.close()
