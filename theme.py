# theme.py – Dark theme for the entire app (date-picker fully matched)
import streamlit as st

def apply_dark_theme():
    st.markdown(
        '''
        <style>
        /* ─────────────────────────── GLOBAL COLORS ─────────────────────────── */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
        .block-container, .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* ────────────────────────── INPUT LABELS ───────────────────────────── */
        .stTextInput > label,
        .stSelectbox > label,
        [data-testid="stDateInput"] > label,
        .stButton > button {
            color: #FFA500 !important;          /* Orange */
            font-weight: bold;
        }

        /* ───────────────────── COMMON INPUT CONTAINERS ────────────────────── */
        .stTextInput, .stSelectbox, .stButton > button,
        /* Date picker outer container */
        [data-testid="stDateInput"] > div {
            background-color: #000000 !important;      /* Black */
            color: #ffffff !important;
            border: 1px solid #808080 !important;      /* Grey border */
            border-radius: 8px !important;
            padding: 10px !important;
            box-shadow: 0 0 5px rgba(128,128,128,0.5); /* Grey glow */
        }

        /* ─────── Inner <input> of the date picker (text in the box) ───────── */
        [data-testid="stDateInput"] input {
            background-color: transparent !important;
            color: #ffffff !important;
            border: none !important;
        }

        /* ─────────── Calendar-icon button inside the date picker ──────────── */
        [data-testid="stDateInput"] button {
            background-color: #000000 !important;
            border: none !important;
            color: #ffffff !important;
        }
        [data-testid="stDateInput"] button:hover {
            background-color: #d3d3d3 !important;  /* Light gray */
            color: #000000 !important;
            transition: 0.3s ease-in-out;
        }

        /* ───────────────────────── BUTTON HOVER (other buttons) ───────────── */
        .stButton > button:hover {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
            transition: 0.3s ease-in-out;
        }

        /* ────────────────────────── TABS STYLING ──────────────────────────── */
        div[data-testid="stTabs"] button {
            border-radius: 50px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            color: #ffffff !important;
            background-color: #000000 !important;
            border: 1px solid #808080 !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
        }

        /* ─────────────────────── ERROR TEXT STYLE ─────────────────────────── */
        .error-text {
            color: #FF0000 !important;
            font-weight: bold !important;
            font-size: 16px !important;
            padding: 5px;
        }

        /* ─────────────────────── SIDEBAR THEME ────────────────────────────── */
        [data-testid="stSidebar"], .sidebar-content {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-right: 1px solid #808080 !important;
        }
        [data-testid="stSidebar"] div {
            color: #ffffff !important;
        }

        /* Sidebar menu items */
        .css-1d391kg, .css-18e3th9 { color: #ffffff !important; }
        .css-1d391kg:hover, .css-18e3th9:hover {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
            border-radius: 8px;
            transition: 0.3s ease-in-out;
        }

        /* ───────────────────── CUSTOM SCROLLBAR ───────────────────────────── */
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
