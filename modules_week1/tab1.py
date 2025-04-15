# tab1.py
import streamlit as st
import json
from handle import get_tab_content

def show():
    # Retrieve the latest content for "tab1"
    content_data = get_tab_content("tab1")
    if content_data:
        st.header(content_data.get("title", "No Title"))
        st.video(content_data.get("video_url", ""))
        
        # Fetch and parse formatting options
        formatting_options = content_data.get("formatting_options")
        options = {}
        if formatting_options:
            if isinstance(formatting_options, str):
                try:
                    options = json.loads(formatting_options)
                except Exception:
                    options = {}
            else:
                options = formatting_options
        
        # Build inline CSS style string
        style = ""
        if options.get("color"):
            style += f"color: {options['color']};"
        if options.get("font_weight"):
            style += f" font-weight: {options['font_weight']};"
        
        st.markdown(
            f"<div style='{style}'>{content_data.get('content')}</div>",
            unsafe_allow_html=True
        )
    else:
        st.warning("No content found for this tab. Please update content from the update page.")

if __name__ == "__main__":
    show()
