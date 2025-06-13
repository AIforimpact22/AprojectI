# theme.py – unified dark theme (Date-of-Joining picker shows BLACK date text)
import streamlit as st


def apply_dark_theme():
    st.markdown(
        """
        <style>
        /* ─────────── GLOBAL BACKGROUND & TEXT ─────────── */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
        .block-container, .stApp {
            background-color: #000000 !important;
            color: #ffffff !important;
        }

        /* ─────────── LABELS (orange & bold) ─────────── */
        .stTextInput > label,
        .stSelectbox > label,
        .stDateInput  > label,
        .stButton     > button {
            color: #FFA500 !important;
            font-weight: bold;
        }

        /* ─────────── COMMON INPUT BOX STYLE ─────────── */
        .stTextInput,
        .stSelectbox,
        .stButton > button {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #808080 !important;
            border-radius: 8px !important;
            padding: 10px;
            box-shadow: 0 0 5px rgba(128,128,128,0.5);
        }

        /* ─────────── DATE PICKER (light grey box, black text) ─────────── */
        .stDateInput > div {                     /* outer wrapper */
            background-color: #d3d3d3 !important;  /* light grey */
            color: #000000 !important;             /* black text */
            border: 1px solid #808080 !important;
            border-radius: 8px !important;
            padding: 10px;
            box-shadow: 0 0 5px rgba(128,128,128,0.5);
        }
        .stDateInput input {                     /* actual input element */
            background-color: transparent !important;
            color: #000000 !important;             /* black date */
            border: none !important;
        }

        /* ─────────── BUTTON HOVER ─────────── */
        .stButton > button:hover {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
            transition: 0.3s ease-in-out;
        }

        /* ─────────── TABS STYLE ─────────── */
        div[data-testid="stTabs"] button {
            border: 1px solid #808080 !important;
            border-radius: 50px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            color: #ffffff !important;
            background-color: #000000 !important;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
        }

        /* ─────────── ERROR TEXT ─────────── */
        .error-text {
            color: #FF0000 !important;
            font-weight: bold;
            font-size: 16px;
            padding: 5px;
        }

        /* ─────────── SIDEBAR ─────────── */
        [data-testid="stSidebar"], .sidebar-content {
            background-color: #000000 !important;
            color: #ffffff !important;
            border-right: 1px solid #808080 !important;
        }
        [data-testid="stSidebar"] div { color: #ffffff !important; }

        /* sidebar menu items */
        .css-1d391kg, .css-18e3th9 { color: #ffffff !important; }
        .css-1d391kg:hover, .css-18e3th9:hover {
            background-color: #d3d3d3 !important;
            color: #000000 !important;
            border-radius: 8px;
            transition: 0.3s ease-in-out;
        }

        /* ─────────── SCROLLBAR ─────────── */
        ::-webkit-scrollbar        { width: 8px; }
        ::-webkit-scrollbar-track  { background: #000000; }
        ::-webkit-scrollbar-thumb  { background-color: #808080; border-radius: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
