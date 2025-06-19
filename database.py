# database.py
"""
Database helpers for a Streamlit app backed by MySQL.

🔄 2025-06-19 performance update
--------------------------------
Change focus:
    • Add carefully chosen secondary INDEXes so look-ups
      on frequent search columns use B-trees instead of scans.

Tip: adjust or add more indexes if your real workloads
often `WHERE` by other columns.
"""

import streamlit as st
import mysql.connector
from mysql.connector import errorcode


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def _get_conn() -> mysql.connector.MySQLConnection:
    """
    Open a fresh MySQL connection from Streamlit secrets.

    (If you preferred the earlier pooling version, just
    paste that pool code back in—indexing is orthogonal.)
    """
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
# DDL with performance-critical indexes
# ---------------------------------------------------------------------------

def create_tables() -> None:
    """
    Ensure all required tables—and their performance indexes—exist.

    Each CREATE has `IF NOT EXISTS`, so re-running is harmless.
    """
    ddl_statements = [
        # USERS table
        """
        CREATE TABLE IF NOT EXISTS users (
            fullname         VARCHAR(100),
            email            VARCHAR(100),
            phone            BIGINT,
            username         VARCHAR(50)  PRIMARY KEY,
            password         VARCHAR(100),
            date_of_joining  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
            approved         TINYINT       DEFAULT 0,
            -- 🔑 performance indexes
            INDEX idx_email  (email),
            INDEX idx_phone  (phone)
        ) ENGINE=InnoDB
        """,
        # RECORDS table – index on username for joins; FK keeps data consistent
        """
        CREATE TABLE IF NOT EXISTS records (
            username VARCHAR(50) PRIMARY KEY,
            as1      INT DEFAULT NULL,
            as2      INT DEFAULT NULL,
            as3      INT DEFAULT NULL,
            as4      INT DEFAULT NULL,
            CONSTRAINT fk_records_user
                FOREIGN KEY (username) REFERENCES users (username)
                ON DELETE CASCADE
        ) ENGINE=InnoDB
        """
        # …add more CREATE TABLE statements here, giving each column
        #    you filter/join on its own INDEX (or composite INDEX)…
    ]

    conn = cur = None
    try:
        conn = _get_conn()
        cur = conn.cursor()
        for stmt in ddl_statements:
            cur.execute(stmt)
        conn.commit()
    except mysql.connector.Error as e:
        # Ignore “table already exists”; surface everything else
        if e.errno not in (errorcode.ER_TABLE_EXISTS_ERROR,):
            st.warning(f"Error creating tables: {e.msg}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
