# style.py - Extra custom styles (animations, text, etc.)
import streamlit as st

def apply_custom_styles():
    # Existing custom CSS for animated title, footer, etc.
    st.markdown(
        """
        <style>
        /* Animation for moving text */
        @keyframes move {
            0% { transform: translateX(0); }
            50% { transform: translateX(10px); }
            100% { transform: translateX(0); }
        }

        /* Title style */
        .title {
            color: #ff4757;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            animation: move 2s infinite;
            margin-bottom: 1rem;
        }
        
        /* Footer polished text styles */
        .footer {
            text-align: center;
            font-size: 1.2rem;
            font-weight: bold;
        }

        /* Specific styles for footer messages */
        .footer-assignments {
            color: #FFA500 !important; /* Orange color for assignments message */
            font-size: 1.3rem;
        }

        .footer-partner {
            color: #00CED1 !important; /* Turquoise color for partner message */
            font-size: 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def show_footer():
    footer_html = """
    <style>
    .global-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        text-align: center;
        color: palegreen;
        font-size: 1rem;
        padding: 0.5rem;
        z-index: 100;
    }
    </style>
    <div class="global-footer">
        💡 AI For Impact © 2025 - Your Partner in Academic Success
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
