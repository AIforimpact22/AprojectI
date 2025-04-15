# update.py
import streamlit as st
import json
from handle import get_tab_content, update_tab_content

def main():
    st.title("Update Tab Content")

    # Select which tab content you want to update.
    tab_name = st.selectbox("Select Tab to Update", ["tab1", "tab2", "tab3"])

    # Fetch existing content from the database (if any)
    existing_content = get_tab_content(tab_name)
    if existing_content:
        default_title = existing_content.get("title", "")
        default_video_url = existing_content.get("video_url", "")
        default_content = existing_content.get("content", "")
        # For formatting_options, convert JSON/dict to a JSON string for display if needed.
        default_options = existing_content.get("formatting_options", {})
    else:
        default_title = ""
        default_video_url = ""
        default_content = ""
        default_options = {}

    # Input elements for content update.
    title = st.text_input("Title", value=default_title)
    video_url = st.text_input("Video URL", value=default_video_url)
    content = st.text_area("Content", value=default_content, height=300)

    st.markdown("### Formatting Options")
    # Dropdowns for text color and font weight.
    color = st.selectbox("Text Color", ["black", "blue", "red", "green", "gold", "pale blue"],
                         index=["black", "blue", "red", "green", "gold", "pale blue"].index(default_options.get("color", "black")))
    font_weight = st.selectbox("Font Weight", ["normal", "bold"],
                               index=["normal", "bold"].index(default_options.get("font_weight", "normal")))
    formatting_options = {"color": color, "font_weight": font_weight}

    if st.button("Update Content"):
        update_tab_content(tab_name, title, video_url, content, formatting_options)
        st.success("Content updated successfully!")

if __name__ == "__main__":
    main()
