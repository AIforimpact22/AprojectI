# database.py
"""
Database helpers for a Streamlit app backed by MySQL.

🔄 2025-06-19 update
--------------------
Performance tweak (single change requested):
    • create_tables() now opens **one** connection/cursor,
      runs all DDL statements, then commits & closes.
"""

import streamlit as st
import mysql.connector
from mysql.connector import errorcode


def _get_conn():
    """Return a fresh MySQL connection using Streamlit secrets."""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
        connection_timeout=10,
    )


def create_tables():
    """
    Ensure required tables exist.

    Key change for speed:
        • Use **one** connection/cursor for all DDL statements
          instead of opening a new socket per statement.
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
        # …add additional CREATE TABLE statements here as needed…
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
