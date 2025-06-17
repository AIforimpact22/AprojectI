# as1.py  – MySQL version (no local .db file required)
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
from mysql.connector import errorcode

# --------------------------------------------------------------------------- #
# Optional GitHub‑push stub (keeps old code paths alive without changing them)
# --------------------------------------------------------------------------- #
try:
    from github_sync import push_db_to_github  # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):  # noqa: D401
        """No‑op stub – DB already lives in MySQL, nothing to push."""
        return {"success": True}

# --------------------------------------------------------------------------- #
# DB helper – centralise MySQL connection
# --------------------------------------------------------------------------- #

def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )

# --------------------------------------------------------------------------- #
# MAIN UI
# --------------------------------------------------------------------------- #

def show():
    # Apply custom styling
    set_page_style()

    # ───────────────────────── session defaults ────────────────────────────
    for key, default in {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username_entered": False,
        "username": "",
    }.items():
        st.session_state.setdefault(key, default)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ───────────────────────── Step 2 – details & grading ───────────────────
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    # ---------------- Assignment tab ----------------
    with tab1:
        st.markdown(
            """
            ### <span style="color:#FFD700;">Objective</span>
            In this assignment, you will write a Python script to plot three geographical coordinates on a map and calculate the distance between each pair of points in kilometers. This will help you practice working with geospatial data and Python libraries for mapping and calculations.

            **Assignment: Week 1 – Mapping Coordinates and Calculating Distances in Python**
            """,
            unsafe_allow_html=True,
        )

        with st.expander("See More"):
            st.markdown(
                """
                **<span style="color:#FFD700;">Task Requirements</span>:**
                1. **<span style="color:#FFD700;">Plot the Three Coordinates on a Map:</span>**
                   - The coordinates represent three locations in the Kurdistan Region.
                   - Use Python libraries to plot these points on a map.
                   - The map should visually display the exact locations of the coordinates.
                2. **<span style="color:#FFD700;">Calculate the Distance Between Each Pair of Points:</span>**
                   - Calculate the distances between the three points in kilometers.
                   - Specifically, calculate:
                     - The distance between Point 1 and Point 2.
                     - The distance between Point 2 and Point 3.
                     - The distance between Point 1 and Point 3.
                   - Add markers to the map for each coordinate.
                   - Add polylines to connect the points.
                   - Add popups to display distance information.

                **<span style="color:#FFD700;">Coordinates</span>:**
                - Point 1: Latitude 36.325735, Longitude 43.928414  
                - Point 2: Latitude 36.393432, Longitude 44.586781  
                - Point 3: Latitude 36.660477, Longitude 43.840174
                """,
                unsafe_allow_html=True,
            )

    # ---------------- Grading tab ----------------
    with tab2:
        st.markdown(
            """
            ### <span style="color:#FFD700;">Detailed Grading Breakdown</span>
            - **Code Structure and Implementation:** 30 points  
            - **Map Visualization:** 40 points  
            - **Distance Calculations:** 30 points
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            #### <span style="color:#FFD700;">1. Code Structure and Implementation (30 points)</span>
            - **Library Imports (5 points):**
                - Checks if the required libraries (folium, geopy, geodesic) are imported.
            - **Coordinate Handling (5 points):**
                - Checks if the correct coordinates are defined in the code.
            - **Code Execution (10 points):**
                - Checks if the code runs without errors.
            - **Code Quality (10 points):**
                - **Variable Naming:** 2 points (deducted if single‑letter variables are used).  
                - **Spacing:** 2 points (deducted if improper spacing is found).  
                - **Comments:** 2 points (deducted if no comments are present).  
                - **Code Organization:** 2 points (deducted if no blank lines are used for separation).
            """,
            unsafe_allow_html=True,
        )

        with st.expander("See More"):
            st.markdown(
                """
                #### <span style="color:#FFD700;">2. Map Visualization (40 points)</span>
                - **Map Generation (15 points):**
                    - Checks if the folium.Map is correctly initialized.
                - **Markers (15 points):**
                    - Checks if markers are added for each coordinate.
                - **Polylines (5 points):**
                    - Checks if polylines connect the points.
                - **Popups (5 points):**
                    - Checks if popups are added to the markers.

                #### <span style="color:#FFD700;">3. Distance Calculations (30 points)</span>
                - **Geodesic Implementation (10 points):**
                    - Checks if the geodesic function is used correctly.
                - **Distance Accuracy (20 points):**
                    - Checks if the calculated distances are accurate within a 100‑meter tolerance.
                """,
                unsafe_allow_html=True,
            )

    # ───────────────────────── Step 1 – username entry ───────────────────────
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        if not username_input:
            st.error("Please enter a username.")
        else:
            conn = _get_conn()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username_input,))
            exists = cur.fetchone() is not None
            conn.close()

            if exists:
                st.session_state["username_entered"] = True
                st.session_state["username"] = username_input
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False

    # ───────────────────────── Step 3 – code input / grading ─────────────────
    if st.session_state.get("username_entered"):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        if st.button("Run Code"):
            st.session_state.update(
                run_success=False,
                captured_output="",
                map_object=None,
                dataframe_object=None,
            )
            try:
                captured = StringIO()
                import sys
                sys_stdout_original = sys.stdout
                sys.stdout = captured

                local_context = {}
                exec(code_input, {}, local_context)

                sys.stdout = sys_stdout_original
                st.session_state["captured_output"] = captured.getvalue()

                for obj in local_context.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys_stdout_original
                st.error(f"Error while running code: {e}")

        if st.session_state["run_success"]:
            if st.session_state["captured_output"]:
                st.markdown("### 📄 Captured Output")
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;">{st.session_state["captured_output"].replace(chr(10), "<br>")}</pre>',
                    unsafe_allow_html=True,
                )
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code successfully before submitting.")
                return

            from grades
