import streamlit as st
import mysql.connector
from mysql.connector import errorcode

# ---------- internal helper ---------------------------------------------------
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,   # we’ll handle commits manually
    )

# ---------- schema creation ----------------------------------------------------
def create_tables():
    """
    Ensure the three core tables (users, records, progress) and the trigger
    exist in the target MySQL database.  Safe to call repeatedly.
    """
    ddl_statements = [
        # users ---------------------------------------------------------------
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
        # records -------------------------------------------------------------
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
                       as1 + as2 + as3 + as4 + IFNULL(quiz1,0) + IFNULL(quiz2,0)
                     ) STORED
        )
        """,
        # progress ------------------------------------------------------------
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
        # trigger -------------------------------------------------------------
        """
        DROP TRIGGER IF EXISTS after_user_insert
        """,
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
    for stmt in ddl_statements:
        try:
            cur.execute(stmt)
        except mysql.connector.Error as e:
            # Ignore “trigger already exists” after race or permissions issues
            if e.errno not in (errorcode.ER_TRG_ALREADY_EXISTS,):
                st.error(f"DDL error: {e.msg}")
    conn.commit()
    cur.close()
    conn.close()

# ---------- progress helpers ---------------------------------------------------
def update_progress(username: str, week: int, tab_index: int) -> None:
    """
    Update the highest unlocked tab number for a given user/week.
    """
    column = f"week{week}track"
    conn   = _get_conn()
    cur    = conn.cursor()
    cur.execute(
        f"UPDATE progress SET {column} = %s WHERE username = %s",
        (tab_index, username),
    )
    conn.commit()
    cur.close()
    conn.close()

def get_progress(username: str, week: int) -> int:
    """
    Return the current highest unlocked tab for a given user/week (0 if none).
    """
    column = f"week{week}track"
    conn   = _get_conn()
    cur    = conn.cursor()
    cur.execute(
        f"SELECT {column} FROM progress WHERE username = %s",
        (username,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    return int(row[0]) if row and row[0] is not None else 0

# -------------------------------------------------------------------------------
if __name__ == "__main__":
    create_tables()
