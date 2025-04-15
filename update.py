import streamlit as st
from sqlalchemy import create_engine, text
import datetime

# Configure the database connection using the secret (adjust the key names accordingly)
DATABASE_URL = st.secrets["postgres"]["DATABASE_URL"]

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

def update_tab_in_db(tab_name: str, title: str, video_url: str, content: str):
    """Insert a new update record for the given tab."""
    query = text("""
        INSERT INTO tab_updates (tab_name, title, video_url, content, updated_at)
        VALUES (:tab_name, :title, :video_url, :content, :updated_at)
    """)
    with engine.connect() as connection:
        connection.execute(query, {
            "tab_name": tab_name,
            "title": title,
            "video_url": video_url,
            "content": content,
            "updated_at": datetime.datetime.now()
        })

def update_form():
    st.header("Update a Tab")
    
    # You can define the list of available tab names
    available_tabs = [
        "tab1", "tab2", "tab3", "tab4", "tab5", 
        "tab6", "tab7", "tab8", "tab9", "tab10", "tab11"
    ]
    selected_tab = st.selectbox("Select Tab to Update", available_tabs)

    # Inputs: Title, Video URL, and rich text (Markdown supported)
    new_title = st.text_input("New Title (can include HTML/Markdown for styling)")
    new_video_url = st.text_input("New Video URL")
    new_content = st.text_area("New Content (Supports Markdown - for bold, colored text, etc.)")

    if st.button("Update Tab"):
        # Basic validation could be added here.
        if new_title:
            update_tab_in_db(selected_tab, new_title, new_video_url, new_content)
            st.success(f"{selected_tab} updated successfully!")
        else:
            st.error("Please provide a title to update.")

if __name__ == "__main__":
    update_form()
