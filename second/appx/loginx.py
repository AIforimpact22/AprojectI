
import streamlit as st

def show():
    st.title("Course 2 Login")
    st.write("Please log in to access the Advanced Machine Learning and Real-Time Deployment course.")

    username = st.text_input("Username", key="course2_username")
    password = st.text_input("Password", type="password", key="course2_password")

    if st.button("Login"):
        if username and password:
            # Here you can add your authentication logic.
            st.session_state["course2_logged_in"] = True
            st.session_state["page"] = "course2_app"
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Please enter both username and password.")
