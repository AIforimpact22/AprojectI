# database.py

import mysql.connector
from mysql.connector import errorcode, InterfaceError
import streamlit as st

def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host       = cfg["host"],
        port       = int(cfg.get("port", 3306)),
        user       = cfg["user"],
        password   = cfg["password"],
        database   = cfg["database"],
        autocommit = False,
        connection_timeout=10,
    )

def create_tables():
    """
    Ensure all necessary tables exist in the MySQL database.
    Safely pings and reconnects if needed to avoid IndexError in ping().
    """
    # 1) Establish or re-establish connection
    try:
        conn = _get_conn()
        # force a reconnect if the ping fails
        conn.ping(reconnect=True, attempts=3, delay=2)
    except InterfaceError:
        conn = _get_conn()

    cur = conn.cursor()
    # List your DDL statements here, one per string
    ddl = [
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
        # … add any other CREATE TABLE statements you need …
    ]

    # 2) Execute each DDL statement safely
    for stmt in ddl:
        try:
            cur.execute(stmt)
        except mysql.connector.Error as e:
            # log but continue on errors (e.g. “table already exists”)
            st.warning(f"Warning creating table: {e.msg}")
    conn.commit()
    cur.close()
    conn.close()
