# as1.py – MySQL version (no local .db file required)
import streamlit as st
import folium
import pandas as pd
import sys  # Added missing import
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
from mysql.connector import errorcode

# --------------------------------------------------------------------------- #
# Optional GitHub-push stub (keeps old code paths alive without changing them)
# --------------------------------------------------------------------------- #
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op stub – DB already lives in MySQL, nothing to push."""
        return {"success": True}

# --------------------------------------------------------------------------- #
# DB helper – centralise MySQL connection
# --------------------------------------------------------------------------- #
def _get_conn():
    try:
        cfg = st.secrets["mysql"]
        return mysql.connector.connect(
            host=cfg["host"],
            port=int(cfg.get("port", 3306)),
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            autocommit=False,
        )
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# --------------------------------------------------------------------------- #
# MAIN UI
# --------------------------------------------------------------------------- #
def show():
    # Apply custom styling
    set_page_style()

    # ──────────────────────────────────────────────────────────────
    # Streamlit session defaults
    # ──────────────────────────────────────────────────────────────
    for key, default in {
        "run_success":      False,
        "map_object":       None,
        "dataframe_object": None,
        "captured_output":  "",
        "username_entered": False,
        "username":         "",
    }.items():
        st.session_state.setdefault(key, default)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ──────────────────────────────────────────────────────────────
    # Step 2 (always visible) – assignment details
    # ──────────────────────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        In this assignment, you will write a Python script to plot three geographical coordinates on a map and calculate the distance between each pair of points in kilometers. This will help you practice working with geospatial data and Python libraries for mapping and calculations.
        
        **Assignment: Week 1 – Mapping Coordinates and Calculating Distances in Python**
        """)
        with st.expander("See More"):
            st.markdown("""
            <h3 style="color: #FFD700;">Task Requirements:</h3>
            <ol>
            <li><strong style="color: #FFD700;">Plot the Three Coordinates on a Map:</strong>
               <ul>
               <li>The coordinates represent three locations in the Kurdistan Region.</li>
               <li>Use Python libraries to plot these points on a map.</li>
               <li>The map should visually display the exact locations of the coordinates.</li>
               </ul>
            </li>
            <li><strong style="color: #FFD700;">Calculate the Distance Between Each Pair of Points:</strong>
               <ul>
               <li>Calculate the distances between the three points in kilometers.</li>
               <li>Specifically, calculate:
                 <ul>
                 <li>The distance between Point 1 and Point 2.</li>
                 <li>The distance between Point 2 and Point 3.</li>
                 <li>The distance between Point 1 and Point 3.</li>
                 </ul>
               </li>
               <li>Add markers to the map for each coordinate.</li>
               <li>Add polylines to connect the points.</li>
               <li>Add popups to display distance information.</li>
               </ul>
            </li>
            </ol>
            
            <h3 style="color: #FFD700;">Coordinates:</h3>
            <ul>
            <li>Point 1: Latitude: 36.325735, Longitude: 43.928414</li>
            <li>Point 2: Latitude: 36.393432, Longitude: 44.586781</li>
            <li>Point 3: Latitude: 36.660477, Longitude: 43.840174</li>
            </ul>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <h3 style="color: #FFD700;">Detailed Grading Breakdown</h3>
        <ul>
        <li><strong>Code Structure and Implementation:</strong> 30 points</li>
        <li><strong>Map Visualization:</strong> 40 points</li>
        <li><strong>Distance Calculations:</strong> 30 points</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("""
        <h4 style="color: #FFD700;">1. Code Structure and Implementation (30 points)</h4>
        <ul>
        <li><strong>Library Imports (5 points):</strong>
            <ul><li>Checks if the required libraries (folium, geopy, geodesic) are imported.</li></ul>
        </li>
        <li><strong>Coordinate Handling (5 points):</strong>
            <ul><li>Checks if the correct coordinates are defined in the code.</li></ul>
        </li>
        <li><strong>Code Execution (10 points):</strong>
            <ul><li>Checks if the code runs without errors.</li></ul>
        </li>
        <li><strong>Code Quality (10 points):</strong>
            <ul>
            <li><strong>Variable Naming:</strong> 2 points (deducted if single-letter variables are used).</li>
            <li><strong>Spacing:</strong> 2 points (deducted if improper spacing is found).</li>
            <li><strong>Comments:</strong> 2 points (deducted if no comments are present).</li>
            <li><strong>Code Organization:</strong> 2 points (deducted if no blank lines are used for separation).</li>
            </ul>
        </li>
        </ul>
        """, unsafe_allow_html=True)
        with st.expander("See More"):
            st.markdown("""
            <h4 style="color: #FFD700;">2. Map Visualization (40 points)</h4>
            <ul>
            <li><strong>Map Generation (15 points):</strong>
                <ul><li>Checks if the folium.Map is correctly initialized.</li></ul>
            </li>
            <li><strong>Markers (15 points):</strong>
                <ul><li>Checks if markers are added for each coordinate.</li></ul>
            </li>
            <li><strong>Polylines (5 points):</strong>
                <ul><li>Checks if polylines connect the points.</li></ul>
            </li>
            <li><strong>Popups (5 points):</strong>
                <ul><li>Checks if popups are added to the markers.</li></ul>
            </li>
            </ul>
            <h4 style="color: #FFD700;">3. Distance Calculations (30 points)</h4>
            <ul>
            <li><strong>Geodesic Implementation (10 points):</strong>
                <ul><li>Checks if the geodesic function is used correctly.</li></ul>
            </li>
            <li><strong>Distance Accuracy (20 points):</strong>
                <ul><li>Checks if the calculated distances are accurate within a 100-meter tolerance.</li></ul>
            </li>
            </ul>
            """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────
    # Step 1 – username entry / validation
    # ──────────────────────────────────────────────────────────────
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
            if conn is None:
                st.error("Could not connect to database.")
                return
            
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM records WHERE username = %s LIMIT 1",
                    (username_input,),
                )
                exists = cur.fetchone() is not None
                cur.close()
                conn.close()

                if exists:
                    st.session_state["username_entered"] = True
                    st.session_state["username"] = username_input
                    st.success(f"Welcome, {username_input}!")
                else:
                    st.error("Invalid username. Please enter a registered username.")
                    st.session_state["username_entered"] = False
            except Exception as e:
                st.error(f"Database query error: {str(e)}")
                conn.close()

    # ──────────────────────────────────────────────────────────────
    # Step 3 – code input / execution / grading
    # ──────────────────────────────────────────────────────────────
    if st.session_state.get("username_entered"):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        st.markdown('<p style="color: white;">📝 Paste Your Code Here</p>', unsafe_allow_html=True)
        code_input = st.text_area("", height=300)

        if st.button("Run Code"):
            st.session_state.update({
                "run_success": False,
                "captured_output": "",
                "map_object": None,
                "dataframe_object": None,
            })
            
            if not code_input.strip():
                st.error("Please enter some code to run.")
                return
                
            try:
                captured = StringIO()
                sys_stdout_original = sys.stdout
                sys.stdout = captured

                local_context = {}
                exec(code_input, {}, local_context)

                sys.stdout = sys_stdout_original
                st.session_state["captured_output"] = captured.getvalue()

                # Check for folium.Map or DataFrame in namespace
                for obj in local_context.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys_stdout_original
                st.error(f"Error while running code: {str(e)}")

        # Display captured output / map / dataframe
        if st.session_state["run_success"]:
            st.markdown('<h3 style="color: white;">📄 Captured Output</h3>', unsafe_allow_html=True)
            if st.session_state["captured_output"]:
                formatted_output = st.session_state["captured_output"].replace('\n', '<br>')
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;word-wrap:break-word;">'
                    f'{formatted_output}'
                    "</pre>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown('<p style="color: white;">No text output captured.</p>', unsafe_allow_html=True)
            
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # ──────────────────────────────────────────────────────────
        # Submit button – update grade in MySQL
        # ──────────────────────────────────────────────────────────
        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code successfully before submitting.")
                return
            
            if not code_input.strip():
                st.error("Please enter some code to submit.")
                return

            try:
                # Grade using existing grading function
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)

                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                    return

                # Store grade in MySQL
                conn = _get_conn()
                if conn is None:
                    st.error("Could not connect to database for submission.")
                    return

                cur = conn.cursor()
                cur.execute(
                    "UPDATE records SET as1 = %s WHERE username = %s",
                    (grade, st.session_state["username"]),
                )
                conn.commit()
                updated = cur.rowcount
                
                if updated == 0:
                    cur.close()
                    conn.close()
                    st.error("No record updated—please check the username.")
                    return

                # Confirm result
                cur.execute(
                    "SELECT as1 FROM records WHERE username = %s",
                    (st.session_state["username"],),
                )
                result = cur.fetchone()
                cur.close()
                conn.close()
                
                if result:
                    new_grade = result[0]
                    st.success(f"Submission successful! Your grade: {new_grade}/100")
                else:
                    st.error("Error retrieving the updated grade.")

                # Optional GitHub push (now a no-op)
                push_db_to_github(None)

                # Force re-enter username next time
                st.session_state["username_entered"] = False
                st.session_state["username"] = ""
                
            except Exception as e:
                st.error(f"Error during submission: {str(e)}")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    show()
