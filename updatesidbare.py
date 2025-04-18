# updatesidbare.py
import streamlit as st
from streamlit.components.v1 import html

def navigation() -> str:
    # Custom CSS for stylish buttons
    st.markdown("""
    <style>
    .nav-button {
        border: none;
        padding: 0.5rem 1rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 8px;
        width: 100%;
    }
    .nav-button.active {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .nav-button.inactive {
        background-color: #f0f2f6;
        color: #31333F;
    }
    .nav-button.inactive:hover {
        background-color: #e0e2e6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state for active tab
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Content Manager"

    st.sidebar.header("📂 Admin Panel")

    # Button creation with visual feedback
    col1, col2 = st.sidebar.columns(2)
    with col1:
        content_active = "active" if st.session_state.active_tab == "Content Manager" else "inactive"
        if st.button(
            "📝 Content Manager",
            key="content_btn",
            help="Manage content and blocks"
        ):
            st.session_state.active_tab = "Content Manager"
        html(f"""
        <script>
            document.querySelector('[data-testid="content_btn"]').className = "nav-button {content_active}";
        </script>
        """, height=0)

    with col2:
        table_active = "active" if st.session_state.active_tab == "Table Editor" else "inactive"
        if st.button(
            "🔧 Table Editor",
            key="table_btn",
            help="Manage database tables and entries"
        ):
            st.session_state.active_tab = "Table Editor"
        html(f"""
        <script>
            document.querySelector('[data-testid="table_btn"]').className = "nav-button {table_active}";
        </script>
        """, height=0)

    # Add some spacing
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    return st.session_state.active_tab
