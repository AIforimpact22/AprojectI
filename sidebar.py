import streamlit as st

def show_sidebar():
    # Custom CSS for sidebar styling (removed animated title CSS)
    st.markdown("""
        <style>
        /* Sidebar container padding */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: #f0f2f6;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
        
        /* Button styling */
        .stButton button {
            background-color: transparent;
            border: 1px solid #4ECDC4;
            color: #4ECDC4;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background-color: #4ECDC4;
            color: white;
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)

    with st.sidebar:
        # Display logo above the sidebar content.
        st.image("logo.jpg", use_container_width=True)

        # Home section
        with st.expander("🏠 HOME", expanded=False):
            if st.button("Home Page", key="home", use_container_width=True):
                st.session_state["page"] = "home"

        # Modules section
        with st.expander("📘 MODULES", expanded=False):
            if st.button("Introduction", key="modules_intro", use_container_width=True):
                st.session_state["page"] = "modules_intro"
            if st.button("Week 1: Introduction to Coding", key="modules_week1", use_container_width=True):
                st.session_state["page"] = "modules_week1"
            if st.button("Week 2: Generate Comprehensive Codings", key="modules_week2", use_container_width=True):
                st.session_state["page"] = "modules_week2"
            if st.button("Week 3: Deploy App through Github and Streamlit", key="modules_week3", use_container_width=True):
                st.session_state["page"] = "modules_week3"
            if st.button("Week 4: Data Week", key="modules_week4", use_container_width=True):
                st.session_state["page"] = "modules_week4"
            if st.button("Week 5: Finalizing and Showcasing Your Personalized Project", key="modules_week5", use_container_width=True):
                st.session_state["page"] = "modules_week5"

        # Help section
        with st.expander("❓ HELP", expanded=False):
            if st.button("Help Center", key="help", use_container_width=True):
                st.session_state["page"] = "help"

        # Logout section
        with st.expander("🚪 LOGOUT", expanded=False):
            if st.button("Logout", key="logout", use_container_width=True):
                st.session_state["page"] = "logout"

    # Return the currently selected page or default to "home"
    return st.session_state.get("page", "home")
