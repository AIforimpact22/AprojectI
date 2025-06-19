# database.py

import streamlit as st
import mysql.connector
from mysql.connector import errorcode

def _get_conn():
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
        allow_multi_statements=True,  # key change
    )

def create_tables():
    """
    Create tables using a single multi-statement transaction to improve speed.
    """
    ddl_multi_statement = """
    CREATE TABLE IF NOT EXISTS users (
        fullname         VARCHAR(100),
        email            VARCHAR(100),
        phone            BIGINT,
        username         VARCHAR(50) PRIMARY KEY,
        password         VARCHAR(100),
        date_of_joining  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        approved         TINYINT DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS records (
        username VARCHAR(50) PRIMARY KEY,
        as1      INT DEFAULT NULL,
        as2      INT DEFAULT NULL,
        as3      INT DEFAULT NULL,
        as4      INT DEFAULT NULL
    );
    """

    conn = cur = None
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(ddl_multi_statement, multi=True)

        # Consume results to complete multi-statement execution
        for _ in cur:
            pass

        conn.commit()

    except mysql.connector.Error as e:
        if e.errno != errorcode.ER_TABLE_EXISTS_ERROR:
            st.warning(f"Error creating tables: {e.msg}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
