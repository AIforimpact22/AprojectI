import streamlit as st
import sqlite3

DB_PATH = "updates.db"

def get_update_for_tab(tab_name="tab1"):
    """Retrieve update content for a given tab from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, video_url, content FROM updates WHERE tab_name = ?", (tab_name,))
    row = cursor.fetchone()
    conn.close()
    return row  # Returns a tuple (title, video_url, content) or None if not set

def show():
    # Try fetching the updated content for tab1.
    data = get_update_for_tab("tab1")
    if data:
        title, video_url, content = data
        st.header(title)
        if video_url:
            st.video(video_url)
        st.subheader("Content")
        st.write(content)
    else:
        # Fallback content if no update is in the database yet.
        st.header("1.1 Introduction to Python - Recorded Session")
        st.video("https://www.youtube.com/watch?v=Scem9sKTtJo")
        st.subheader("ChatGPT Prompts")
        st.markdown("[Links to an external site](https://chatgpt.com/share/6733c214-7ac4-8004-92f1-227d11b644ff)")
        st.subheader("Content:")
        st.write(
            "In this session, we’ll introduce you to the basics of Python and how it can be a powerful tool for enhancing personal impact, "
            "whether you're looking to automate tasks, analyze data, or create small projects. We will cover foundational topics such as "
            "setting up your Python environment, understanding Python syntax, and exploring the practical applications of Python in everyday scenarios."
        )

if __name__ == "__main__":
    show()
