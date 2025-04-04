import streamlit as st

def show():
    st.markdown('<h1 style="color: palegreen;">4.6 Synthesizing...</h1>', unsafe_allow_html=True)
    st.write("Discover one of my completed projects, highlighting the practical application of Python and Streamlit:")
    st.markdown(
        """
- **Live Application:** [Clinic Dashboard](https://clinicdashboard.streamlit.app/)  
  **Access Key:** clinic2024

- **GitHub Repository:** [Clinic App Repository](https://github.com/habdulhaq87/clinicapp)

- **ChatGPT Prompt:** [View the prompt used to build this app](https://chatgpt.com/share/67389f5a-9410-800c-9fc6-f5698c26636a)

This project demonstrates Python's capability to create a dynamic, interactive dashboard for clinic management. Explore the source code, features, and functionality to see how Python can be applied to solve real-world challenges!
        """,
        unsafe_allow_html=True
    )
