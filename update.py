# update.py
import streamlit as st
import json
from handle import get_tab_content, update_tab_content

def main():
    st.title("Update Tab Content")
    
    # Allow admin to choose which tab to update.
    tab_name = st.selectbox("Select Tab to Update", ["tab1", "tab2", "tab3"])
    
    # Retrieve any existing content for the selected tab.
    existing_content = get_tab_content(tab_name)
    if existing_content:
        default_title = existing_content.get("title", "")
        default_video_url = existing_content.get("video_url", "")
        default_content = existing_content.get("content", "")
        default_formatting = existing_content.get("formatting_options", {})
    else:
        default_title = ""
        default_video_url = ""
        default_content = ""
        default_formatting = {}

    title = st.text_input("Title", value=default_title)
    video_url = st.text_input("Video URL", value=default_video_url)
    content = st.text_area("Content", value=default_content, height=300)

    st.markdown("### Formatting Options")
    colors = ["black", "blue", "red", "green", "gold", "pale blue"]
    default_color = default_formatting.get("color", "black")
    color = st.selectbox("Text Color", colors, index=colors.index(default_color) if default_color in colors else 0)
    
    font_weights = ["normal", "bold"]
    default_weight = default_formatting.get("font_weight", "normal")
    font_weight = st.selectbox("Font Weight", font_weights, index=font_weights.index(default_weight) if default_weight in font_weights else 0)
    
    formatting_options = {"color": color, "font_weight": font_weight}

    if st.button("Update Content"):
        update_tab_content(tab_name, title, video_url, content, formatting_options)
        st.success("Content updated successfully!")
        st.experimental_rerun()

if __name__ == "__main__":
    main()
