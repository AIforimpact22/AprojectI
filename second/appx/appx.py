import streamlit as st

def show():
    st.title("Advanced Machine Learning and Real-Time Deployment")
    st.write("Welcome to the second course! Here you can access all course materials and activities.")

    if st.button("Logout from Course 2"):
        st.session_state["course2_logged_in"] = False
        st.session_state["page"] = "offer"
        st.rerun()
