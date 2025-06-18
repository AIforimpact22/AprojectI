# home.py

import streamlit as st
import streamlit.components.v1 as components
from theme import apply_dark_theme
from style import apply_custom_styles

# ─────────────────────────────────────────────────────────────
# Cache the CSS injection so it only runs once
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def inject_static_css():
    css = """
    <style>
        /* Remove top padding from the main block container */
        .block-container { padding-top: 0; margin-top: 0; }
        /* Hide the Streamlit header */
        header { visibility: hidden; height: 0; }
        /* Remove body margin */
        body { margin: 0; padding: 0; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Cache rendering of the heavy SVG so it only injects once
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def render_svg():
    svg_code = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
      <!-- defs, filters, patterns omitted for brevity… use your full SVG here -->
      <rect width="800" height="400" fill="#000"/>
      <!-- … all the animated wave, neural network, code-snippets, text, particles … -->
    </svg>
    """
    wrapper = f"<div style='margin:0;padding:0'>{svg_code}</div>"
    components.html(wrapper, height=500)

def show_home():
    apply_dark_theme()      # ensures background is dark
    apply_custom_styles()   # ensures animated styles

    inject_static_css()     # run once per session
    render_svg()            # inject heavy SVG just once

if __name__ == "__main__":
    show_home()
