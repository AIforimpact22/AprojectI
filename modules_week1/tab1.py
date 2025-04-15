import streamlit as st
from sqlalchemy import create_engine, text

# Load the connection string from your secrets file.
DATABASE_URL = st.secrets["postgres"]["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

def get_tab_update(tab_name: str):
    """Fetch the latest update record for the given tab."""
    query = text("""
        SELECT title, video_url, content 
        FROM tab_updates 
        WHERE tab_name = :tab_name 
        ORDER BY updated_at DESC LIMIT 1
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"tab_name": tab_name}).fetchone()
        return result

def show():
    # Try to fetch an update for "tab1"
    update = get_tab_update("tab1")
    if update:
        st.header(update.title)
        if update.video_url:
            st.video(update.video_url)
        st.markdown(update.content, unsafe_allow_html=True)
    else:
        # Default content if no update exists.
        st.header("1.1 Introduction to Python - Recorded Session")
        st.video("https://www.youtube.com/watch?v=Scem9sKTtJo")
        st.subheader("**ChatGPT Prompts**")
        st.markdown("[Links to an external site](https://chatgpt.com/share/6733c214-7ac4-8004-92f1-227d11b644ff)")
        st.subheader("**Content**:")
        st.write(
            "In this session, we’ll introduce you to the basics of Python and how it can be a powerful tool for enhancing personal impact, "
            "whether you're looking to automate tasks, analyze data, or create small projects. We will cover foundational topics such as "
            "setting up your Python environment, understanding Python syntax, and exploring the practical applications of Python in everyday scenarios."
        )

if __name__ == "__main__":
    show()
