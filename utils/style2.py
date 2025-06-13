
# style2.py
def set_page_style():
    import streamlit as st

    st.markdown(
        """
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #121212;
                color: #ffffff;
            }
            .stButton > button {
                background-color: #007BFF;
                color: white;
                font-size: 16px;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .stButton > button:hover {
                background-color: #0056b3;
            }
            .stTextInput > div > input {
                background-color: #333333;
                color: white;
                border: 1px solid #007BFF;
                border-radius: 4px;
                padding: 10px;
            }
            .stTextArea > div > textarea {
                background-color: #333333;
                color: white;
                border: 1px solid #007BFF;
                border-radius: 4px;
                padding: 10px;
            }
            .stFileUploader > div {
                background-color: #333333;
                color: white;
                border: 1px solid #007BFF;
                border-radius: 4px;
                padding: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
