import streamlit as st
import sqlite3

# Path to the SQLite database
DB_PATH = "updates.db"

def get_update(tab_name):
    """Fetch the current update details for the selected tab."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, video_url, content FROM updates WHERE tab_name = ?", (tab_name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row
    else:
        # Return empty values if nothing is saved yet.
        return ("", "", "")

def update_update(tab_name, title, video_url, content):
    """Insert or update the update record for a given tab."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Check if this tab already has an update
    cursor.execute("SELECT id FROM updates WHERE tab_name = ?", (tab_name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE updates 
            SET title = ?, video_url = ?, content = ? 
            WHERE tab_name = ?
        """, (title, video_url, content, tab_name))
    else:
        cursor.execute("""
            INSERT INTO updates (tab_name, title, video_url, content)
            VALUES (?, ?, ?, ?)
        """, (tab_name, title, video_url, content))
    conn.commit()
    conn.close()

def main():
    st.title("Update Tab Content")
    st.write("Select a tab to update its content details.")

    # Dropdown to select the tab. Update the options if you have more/less tabs.
    tab_options = ["tab1", "tab2", "tab3", "tab4", "tab5", "tab6", "tab7", "tab8", "tab9", "tab10", "tab11"]
    selected_tab = st.selectbox("Select Tab", tab_options)

    # Fetch current update details for the selected tab
    current_title, current_video_url, current_content = get_update(selected_tab)

    # Input fields for title, video URL, and text content.
    new_title = st.text_input("Title", value=current_title)
    new_video_url = st.text_input("Video URL", value=current_video_url)
    new_content = st.text_area("Content", value=current_content, height=300)

    # Button to save the changes.
    if st.button("Save"):
        update_update(selected_tab, new_title, new_video_url, new_content)
        st.success(f"Content for {selected_tab} has been updated.")

if __name__ == "__main__":
    main()
