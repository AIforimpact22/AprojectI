# database.py
"""
Database helpers for a Streamlit app backed by MySQL.

🔄 2025-06-19 update
-------------------
Performance tweak (single change):
    • Replace per-call connect() with a global
      mysql.connector.pooling.MySQLConnectionPool,
      cached via @st.cache_resource.
"""

import streamlit as st
import mysql.connector
from mysql.connector import errorcode, pooling


# ---------------------------------------------------------------------------
# Connection handling
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _get_pool() -> pooling.MySQLConnectionPool:
    """
    Lazily create (and cache) a small connection-pool.

    • The pool persists across Streamlit script reruns, eliminating
      repeated handshakes.
    • Size 5 is plenty for a single-page Streamlit app; raise if needed.
    """
    cfg = st.secrets["mysql"]
    return pooling.MySQLConnectionPool(
        pool_name="st_pool",
        pool_size=5,
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,           # we still control commits manually
        connection_timeout=10,
        charset="utf8mb4",
        use_unicode=True,
    )


def _get_conn() -> mysql.connector.MySQLConnection:
    """Borrow a connection from the cached pool."""
    return _get_pool().get_connection()


# ---------------------------------------------------------------------------
# DDL helpers
# ---------------------------------------------------------------------------

def create_tables() -> None:
    """
    Ensure all required tables exist.

    We still use one connection/cursor for the whole batch, but now
    that connection comes from (and returns to) the shared pool.
    """
    ddl_statements = [
        # USERS table – TIMESTAMP default is CURRENT_TIMESTAMP
        """
        CREATE TABLE IF NOT EXISTS users (
            fullname         VARCHAR(100),
            email            VARCHAR(100),
            phone            BIGINT,
            username         VARCHAR(50)  PRIMARY KEY,
            password         VARCHAR(100),
            date_of_joining  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved         TINYINT       DEFAULT 0
        )
        """,
        # RECORDS table
        """
        CREATE TABLE IF NOT EXISTS records (
            username VARCHAR(50) PRIMARY KEY,
            as1      INT DEFAULT NULL,
            as2      INT DEFAULT NULL,
            as3      INT DEFAULT NULL,
            as4      INT DEFAULT NULL
        )
        """,
        # …add further CREATE TABLE statements here…
    ]

    conn = cur = None
    try:
        conn = _get_conn()
        cur = conn.cursor()
        for stmt in ddl_statements:
            cur.execute(stmt)
        conn.commit()
    except mysql.connector.Error as e:
        # Ignore “table already exists”; report everything else
        if e.errno not in (errorcode.ER_TABLE_EXISTS_ERROR,):
            st.warning(f"Error creating tables: {e.msg}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()        # returns the connection to the pool
