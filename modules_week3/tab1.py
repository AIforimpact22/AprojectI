import streamlit as st

def show():
    st.markdown(
        '<h1 style="color: #FFA07A;">3.1 Getting Started with GitHub for Writing Your Codes and Creating Your App</h1>',
        unsafe_allow_html=True
    )
    st.write(
        "GitHub is an essential tool for modern programming and project management. Whether you are building simple Python scripts or creating full-fledged applications, GitHub helps you collaborate, version-control your work, and deploy your projects seamlessly."
    )
    st.video("https://youtu.be/pPZI3zbXlMw")

