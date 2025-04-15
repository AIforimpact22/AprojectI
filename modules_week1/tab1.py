import streamlit as st
import sqlite3

def get_update(tab):
    """Fetch update data for the specified tab from the database."""
    conn = sqlite3.connect("updates.db")
    c = conn.cursor()
    c.execute("SELECT title, video_url, content FROM updates WHERE tab = ?", (tab,))
    row = c.fetchone()
    conn.close()
    return row

def show():
    # Try to load update data for tab1 from the database.
    update_data = get_update("tab1")
    if update_data:
        title, video_url, content = update_data
        st.header(title if title else "1.1 Introduction to Python - Recorded Session")
        if video_url:
            st.video(video_url)
        else:
            st.info("No video URL provided. Please update this field in the update section.")
        st.subheader("Content:")
        st.write(content if content else "No content available. Please update accordingly.")
    else:
        # Fallback to original static content.
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
