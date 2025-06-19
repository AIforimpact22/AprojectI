# database.py
"""
Database helpers for a Streamlit app backed by MySQL.

🔄 2025-06-19 performance update
-------------------------------
Single change:
    • `create_tables()` is now wrapped in `@st.cache_resource`, so
      table creation happens only once per session.  Subsequent calls
      return instantly, eliminating repeated connection overhead.
"""

import streamlit as st
import mysql.connector
from mysql.connector import errorcode


# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

def _get_conn() -> mysql.connector.MySQLConnection:
    """Return a fresh MySQL connection from Streamlit secrets."""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
        connection_timeout=10,
        charset="utf8mb4",
        use_unicode=True,
    )


# ---------------------------------------------------------------------------
# Schema creation — now cached
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def create_tables() -> bool:
    """
    Ensure all required tables exist.

    Thanks to @st.cache_resource, this body executes only once per
    Streamlit session.  Later calls return the cached `True` immediately.
    """
    ddl_statements = [
        # USERS
        """
        CREATE TABLE IF NOT EXISTS users (
            fullname         VARCHAR(100),
            email            VARCHAR(100),
            phone            BIGINT,
            username         VARCHAR(50)  PRIMARY KEY,
            password         VARCHAR(100),
            date_of_joining  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved         TINYINT       DEFAULT 0
        ) ENGINE=InnoDB
        """,
        # RECORDS
        """
        CREATE TABLE IF NOT EXISTS records (
            username VARCHAR(50) PRIMARY KEY,
            as1      INT DEFAULT NULL,
            as2      INT DEFAULT NULL,
            as3      INT DEFAULT NULL,
            as4      INT DEFAULT NULL
        ) ENGINE=InnoDB
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
        return True          # value cached by Streamlit
    except mysql.connector.Error as e:
        # Ignore “table already exists”; surface everything else
        if e.errno not in (errorcode.ER_TABLE_EXISTS_ERROR,):
            st.warning(f"Error creating tables: {e.msg}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
