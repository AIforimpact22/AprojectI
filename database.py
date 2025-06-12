import sqlite3
import streamlit as st
import os

def create_tables():
    db_path = st.secrets["general"]["db_path"]

    # Only pull from GitHub if the local database file does not exist
    if not os.path.exists(db_path):
        try:
            from github_sync import pull_db_from_github
            pull_db_from_github(db_path)
        except Exception as e:
            st.error(f"Error pulling DB from GitHub: {e}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        fullname TEXT,
        email TEXT,
        phone INTEGER,
        username TEXT,
        password TEXT,
        approved INTEGER DEFAULT 0
    )
    ''')

    # Create the records table with UNIQUE constraint
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        username TEXT UNIQUE,
        fullname TEXT,
        as1 REAL DEFAULT 0,
        as2 REAL DEFAULT 0,
        as3 REAL DEFAULT 0,
        as4 REAL DEFAULT 0,
        quiz1 REAL DEFAULT NULL,
        quiz2 REAL DEFAULT NULL,
        total REAL GENERATED ALWAYS AS (as1 + as2 + as3 + as4 + IFNULL(quiz1, 0) + IFNULL(quiz2, 0)) STORED
    )
    ''')

    # Create the progress table with updated column names for tracking week progress
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        username TEXT UNIQUE,
        fullname TEXT,
        week1track INTEGER DEFAULT 0,
        week2track INTEGER DEFAULT 0,
        week3track INTEGER DEFAULT 0,
        week4track INTEGER DEFAULT 0,
        week5track INTEGER DEFAULT 0
    )
    ''')

    # Create trigger for automatic inserts when a new user is added
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS after_user_insert
    AFTER INSERT ON users
    FOR EACH ROW
    BEGIN
        INSERT OR IGNORE INTO records (username, fullname) VALUES (NEW.username, NEW.fullname);
        INSERT OR IGNORE INTO progress (username, fullname) VALUES (NEW.username, NEW.fullname);
    END;
    ''')

    conn.commit()
    conn.close()

def update_progress(username, week, tab_index):
    """
    Update the progress for a given username and week.
    week: an integer (1-5) corresponding to the week.
    tab_index: an integer representing the current unlocked tab.
    This function updates the highest unlocked tab number for the week.
    """
    db_path = st.secrets["general"]["db_path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    column = f"week{week}track"
    cursor.execute(f"UPDATE progress SET {column} = ? WHERE username = ?", (tab_index, username))
    conn.commit()
    conn.close()

def get_progress(username, week):
    """
    Retrieve the highest unlocked tab (1-indexed) for a given week.
    Returns 0 if no progress is recorded.
    """
    db_path = st.secrets["general"]["db_path"]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    col = f"week{week}track"
    cursor.execute(f"SELECT {col} FROM progress WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

if __name__ == "__main__":
    create_tables()
