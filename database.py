# database.py

import streamlit as st
import mysql.connector
from mysql.connector import errorcode

def _get_conn():
    """Return a brand‐new MySQL connection from Streamlit secrets."""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host       = cfg["host"],
        port       = int(cfg.get("port", 3306)),
        user       = cfg["user"],
        password   = cfg["password"],
        database   = cfg["database"],
        autocommit = False,
        connection_timeout = 10,
    )

def create_tables():
    """
    Ensure all required tables exist. Opens a new connection for each CREATE
    statement to avoid stale‐socket ping errors.
    """
    # List your CREATE statements here, one per entry
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            fullname VARCHAR(100),
            email VARCHAR(100),
            phone BIGINT,
            username VARCHAR(50) PRIMARY KEY,
            password VARCHAR(100),
            date_of_joining DATE DEFAULT CURRENT_DATE,
            approved TINYINT DEFAULT 0
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS records (
            username VARCHAR(50) PRIMARY KEY,
            as1 INT DEFAULT NULL,
            as2 INT DEFAULT NULL,
            as3 INT DEFAULT NULL,
            as4 INT DEFAULT NULL
        )
        """,
        # … add any additional CREATE TABLE statements here …
    ]

    for stmt in ddl_statements:
        conn = None
        cur  = None
        try:
            conn = _get_conn()
            cur  = conn.cursor()
            cur.execute(stmt)
            conn.commit()
        except mysql.connector.Error as e:
            # Ignore "table already exists" errors, warn on others
            if e.errno not in (errorcode.ER_TABLE_EXISTS_ERROR,):
                st.warning(f"Error creating table: {e.msg}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
