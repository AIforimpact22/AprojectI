# tab1.py
import streamlit as st
import json
from handle import get_tab_content

def show():
    # Load the content for "tab1" from the database.
    content_data = get_tab_content("tab1")
    if content_data:
        st.header(content_data.get("title", "No Title"))
        st.video(content_data.get("video_url", ""))
        # Read formatting options and apply them in a Markdown container.
        formatting_options = content_data.get("formatting_options")
        try:
            if isinstance(formatting_options, str):
                options = json.loads(formatting_options)
            else:
                options = formatting_options
        except Exception:
            options = {}
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
