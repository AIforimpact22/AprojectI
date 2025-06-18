import streamlit as st

def show_sidebar():
    # ────────────────────────────────────────────────────────────────────────────
    # Any CSS tweaks here—this will not hide or collapse the sidebar itself.
    # ────────────────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        .streamlit-expanderHeader {
            background-color: #f0f2f6;
            border-radius: 5px;
            margin-bottom: 0.5rem;
        }
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
        """,
        unsafe_allow_html=True,
    )

    # ────────────────────────────────────────────────────────────────────────────
    # Explicitly use st.sidebar.* calls so Streamlit knows these widgets belong there
    # ────────────────────────────────────────────────────────────────────────────
    st.sidebar.image("logo.jpg", use_container_width=True)

    # Home
    if st.sidebar.expander("🏠 HOME", expanded=False).button("Home Page", key="home", use_container_width=True):
        st.session_state["page"] = "home"

    # Modules
    modules = st.sidebar.expander("📘 MODULES", expanded=False)
    if modules.button("Introduction", key="modules_intro", use_container_width=True):
        st.session_state["page"] = "modules_intro"
    if modules.button("Week 1: Introduction to Coding", key="modules_week1", use_container_width=True):
        st.session_state["page"] = "modules_week1"
    if modules.button("Week 2: Generate Comprehensive Codings", key="modules_week2", use_container_width=True):
        st.session_state["page"] = "modules_week2"
    if modules.button("Week 3: Deploy App through Github and Streamlit", key="modules_week3", use_container_width=True):
        st.session_state["page"] = "modules_week3"
    if modules.button("Week 4: Data Week", key="modules_week4", use_container_width=True):
        st.session_state["page"] = "modules_week4"
    if modules.button("Week 5: Finalizing and Showcasing Your Personalized Project", key="modules_week5", use_container_width=True):
        st.session_state["page"] = "modules_week5"

    # Help
    if st.sidebar.expander("❓ HELP", expanded=False).button("Help Center", key="help", use_container_width=True):
        st.session_state["page"] = "help"

    # Logout
    if st.sidebar.expander("🚪 LOGOUT", expanded=False).button("Logout", key="logout", use_container_width=True):
        st.session_state["page"] = "logout"
