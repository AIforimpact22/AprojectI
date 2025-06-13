# theme.py - Manages black theme for the entire app, including sidebar
import streamlit as st

def apply_dark_theme():
    st.markdown(
        '''
        <style>
        /* Global background and text color */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
        .block-container, .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* ──────────── INPUT LABELS ──────────── */
        /* Added .stDateInput > label so the DoJ label is orange/bold too */
        .stTextInput > label,
        .stSelectbox > label,
        .stDateInput > label,
        .stButton > button {
            color: #FFA500 !important;  /* Orange */
            font-weight: bold;
        }

        /* ──────────── INPUT BOXES ──────────── */
        /* Common box styling (text, select, date) */
        .stTextInput,
        .stSelectbox,
        .stDateInput,
        .stButton > button {
            background-color: #000000 !important;  /* Black */
            color: white !important;
            border-radius: 8px !important;
            border: 1px solid #808080 !important;  /* Grey border */
            padding: 10px;
            box-shadow: 0px 0px 5px rgba(128, 128, 128, 0.5); /* Grey glow */
        }

        /* Ensure the internal date picker element inherits the dark theme */
        .stDateInput input {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: none !important;
        }

        /* Hover effect on buttons */
        .stButton > button:hover {
            background-color: #d3d3d3 !important;  /* Light gray */
            color: black !important;
            transition: 0.3s ease-in-out;
        }

        /* Styling for login and create-account tabs */
        div[data-testid="stTabs"] button {
            border-radius: 50px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            color: white !important;
            background-color: #000000 !important;
            border: 1px solid #808080 !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #d3d3d3 !important;  /* Light gray when selected */
            color: black !important;
        }

        /* Custom Error Message Styling */
        .error-text {
            color: #FF0000 !important;
            font-weight: bold !important;
            font-size: 16px !important;
            padding: 5px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"], .sidebar-content {
            background-color: #000000 !important;  /* Black */
            color: #ffffff !important;
            border-right: 1px solid #808080 !important;  /* Grey border */
        }
        [data-testid="stSidebar"] div {
            color: white !important;
        }

        /* Sidebar menu item styling */
        .css-1d391kg, .css-18e3th9 {
            color: white !important;
        }
        /* Sidebar menu hover effect */
        .css-1d391kg:hover, .css-18e3th9:hover {
            background-color: #d3d3d3 !important;  /* Light gray */
            color: black !important;
            border-radius: 8px;
            transition: 0.3s ease-in-out;
        }

        /* Scrollbar Customization */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #000000; }
        ::-webkit-scrollbar-thumb {
            background-color: #808080;
            border-radius: 10px;
        }
        </style>
        ''',
        unsafe_allow_html=True
    )
