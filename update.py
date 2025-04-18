import streamlit as st
from streamlit_quill import st_quill  # Quill text editor for rich text input

# Add to your existing BLOCK_TYPES dictionary
BLOCK_TYPES = {
    "Text":        "text",
    "Text/Rich":   "rich",
    "Text/HTML":   "html",
    "YouTube URL": "youtube",
    "Image URL":   "image",
    "Embed URL":   "embed",
    "CSV → Table": "csv",
}

# When adding a new block
if new_type == "Text/Rich":
    p = {"text": "", "color": "#000000", "size": 16}
elif new_type == "Text/HTML":
    p = {"html": ""}
else:
    p = {"url": ""} if new_type in ("youtube", "image", "embed") else {"csv": "", "color": "#000000", "size": 16}

# For rich text editing using Quill
if blk["type"] == "rich":
    blk["payload"]["text"] = st_quill(
        value=blk["payload"]["text"], 
        key=f"rich_{uid}", 
        height=200
    )

# For raw HTML input (text area for HTML content)
elif blk["type"] == "html":
    blk["payload"]["html"] = st.text_area(
        "HTML Code", 
        blk["payload"]["html"], 
        key=f"html_{uid}", 
        height=200
    )
