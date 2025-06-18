"""
database.py  – MySQL helper layer + schema bootstrap
====================================================

Public functions (unchanged):
    ▸ create_tables()
    ▸ update_progress(username, week:int, tab_index:int)
    ▸ get_progress(username, week:int) -> int
"""

import streamlit as st
import mysql.connector
from mysql.connector import errorcode, pooling

# ─────────────────────────────────────────────────────────────────────────────
# Connection Pool (singleton via Streamlit session_state)
# ─────────────────────────────────────────────────────────────────────────────
def _get_pool():
    """Return a singleton connection pool, created from Streamlit secrets."""
    if "mysql_pool" not in st.session_state:
        cfg = st.secrets["mysql"]
        st.session_state.mysql_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=8,  # adjust as needed, 8 is a good default
            host=cfg["host"],
            port=int(cfg.get("port", 3306)),
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            autocommit=False,
            use_pure=True,
        )
    return st.session_state.mysql_pool

def _get_conn():
    """Get a pooled MySQL connection."""
    return _get_pool().get_connection()

# ─────────────────────────────────────────────────────────────────────────────
# Schema bootstrap (idempotent)
# ─────────────────────────────────────────────────────────────────────────────
def create_tables() -> None:
    """Ensure tables + trigger exist; safe to call repeatedly."""
    ddl = [
        # users ----------------------------------------------------------------
        """
        CREATE TABLE IF NOT EXISTS users (
            fullname        VARCHAR(100),
            email           VARCHAR(100),
            phone           BIGINT,
            username        VARCHAR(50)  UNIQUE,
            password        VARCHAR(100),
            date_of_joining DATE,
            approved        TINYINT      DEFAULT 0
        )
        """,
        # records --------------------------------------------------------------
        """
        CREATE TABLE IF NOT EXISTS records (
            username VARCHAR(50)  UNIQUE,
            fullname VARCHAR(100),
            as1      FLOAT        DEFAULT 0,
            as2      FLOAT        DEFAULT 0,
            as3      FLOAT        DEFAULT 0,
            as4      FLOAT        DEFAULT 0,
            quiz1    FLOAT        DEFAULT NULL,
            quiz2    FLOAT        DEFAULT NULL,
            total    FLOAT GENERATED ALWAYS AS (
                       as1 + as2 + as3 + as4 +
                       IFNULL(quiz1,0) + IFNULL(quiz2,0)
                     ) STORED
        )
        """,
        # progress -------------------------------------------------------------
        """
        CREATE TABLE IF NOT EXISTS progress (
            username   VARCHAR(50)  UNIQUE,
            fullname   VARCHAR(100),
            week1track INT          DEFAULT 0,
            week2track INT          DEFAULT 0,
            week3track INT          DEFAULT 0,
            week4track INT          DEFAULT 0,
            week5track INT          DEFAULT 0
        )
        """,
        # drop + recreate trigger ---------------------------------------------
        "DROP TRIGGER IF EXISTS after_user_insert",
        """
        CREATE TRIGGER after_user_insert
        AFTER INSERT ON users
        FOR EACH ROW
        BEGIN
            INSERT IGNORE INTO records  (username, fullname)
            VALUES (NEW.username, NEW.fullname);
            INSERT IGNORE INTO progress (username, fullname)
            VALUES (NEW.username, NEW.fullname);
        END
        """,
    ]

    conn = _get_conn()
    cur  = conn.cursor()

    for stmt in ddl:
        try:
            cur.execute(stmt)
            while cur.nextset():
                pass
        except mysql.connector.Error as e:
            if e.errno not in (errorcode.ER_TRG_ALREADY_EXISTS,):
                st.error(f"DDL error: {e.msg}")

    conn.commit()
    cur.close()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# Progress helpers
# ─────────────────────────────────────────────────────────────────────────────
def update_progress(username: str, week: int, tab_index: int) -> None:
    """Set the highest unlocked tab number for a given user/week."""
    column = f"week{week}track"
    conn   = _get_conn()
    cur    = conn.cursor()
    try:
        cur.execute(
            f"UPDATE progress SET {column} = %s WHERE username = %s",
            (tab_index, username),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_progress(username: str, week: int) -> int:
    """Return the current unlocked tab for user/week (0 if none)."""
    column = f"week{week}track"
    conn   = _get_conn()
    cur    = conn.cursor()
    try:
        cur.execute(
            f"SELECT {column} FROM progress WHERE username = %s",
            (username,),
        )
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
    finally:
        cur.close()
        conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# CLI helper – run `python database.py` locally to bootstrap the schema
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":  # pragma: no cover
    # Don't use st.secrets in CLI context, use your own config loading for local testing
    print("WARNING: st.secrets only available in Streamlit. Use with Streamlit.")
