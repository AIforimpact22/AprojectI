import streamlit as st
import sqlite3

def get_update(tab):
    """Fetch update data for a specific tab."""
    conn = sqlite3.connect("updates.db")
    c = conn.cursor()
    c.execute("SELECT title, video_url, content FROM updates WHERE tab = ?", (tab,))
    row = c.fetchone()
    conn.close()
    return row

def upsert_update(tab, title, video_url, content):
    """Insert a new update record or update an existing one."""
    conn = sqlite3.connect("updates.db")
    c = conn.cursor()
    # Check if a record for the tab exists.
    c.execute("SELECT COUNT(*) FROM updates WHERE tab = ?", (tab,))
    count = c.fetchone()[0]
    if count == 0:
        # Insert a new record.
        c.execute(
            "INSERT INTO updates (tab, title, video_url, content) VALUES (?, ?, ?, ?)",
            (tab, title, video_url, content)
        )
    else:
        # Update the existing record; last_updated is auto-updated.
        c.execute(
            "UPDATE updates SET title = ?, video_url = ?, content = ?, last_updated = CURRENT_TIMESTAMP WHERE tab = ?",
            (title, video_url, content, tab)
        )
    conn.commit()
    conn.close()

def main():
    st.title("Update Tab Content")
    st.write("Enter details to update the content for a specific tab.")

    # Dropdown to choose a tab.
    tab_choice = st.selectbox("Select Tab to Update", 
                              ["tab1", "tab2", "tab3", "tab4", "tab5", "tab6", "tab7", "tab8", "tab9", "tab10", "tab11"])
    
    # Preload existing data for the selected tab (if available).
    current_data = get_update(tab_choice)
    if current_data:
        current_title, current_video_url, current_content = current_data
    else:
        current_title, current_video_url, current_content = "", "", ""
    
    title = st.text_input("Title", value=current_title)
    video_url = st.text_input("Video URL", value=current_video_url)
    content = st.text_area("Content", value=current_content, height=300)
    
    if st.button("Update"):
        upsert_update(tab_choice, title, video_url, content)
        st.success(f"Update for {tab_choice} saved successfully.")
        # Automatic refresh if available.
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.warning("Automatic refresh is not available. Please refresh the page manually.")

if __name__ == "__main__":
    main()
