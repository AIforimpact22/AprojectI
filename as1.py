# as1.py – MySQL version (no local .db file required)

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
# Cached connection (avoids reconnect on every rerun)
# --------------------------------------------------------------------------- #
@st.cache(allow_output_mutation=True)
def get_cached_conn():
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
# Cache username‐exists check
# --------------------------------------------------------------------------- #
@st.cache(allow_output_mutation=True, show_spinner=False)
def user_exists(username: str) -> bool:
    conn = get_cached_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
    found = cur.fetchone() is not None
    cur.close()
    return found

# --------------------------------------------------------------------------- #
# Cache exec+capture logic so reruns with the same code string are fast
# --------------------------------------------------------------------------- #
@st.cache(allow_output_mutation=True, show_spinner=False)
def run_and_capture(code_str: str):
    captured = StringIO()
    import sys
    old_stdout = sys.stdout
    sys.stdout = captured

    local_ctx = {}
    exec(code_str, {}, local_ctx)

    sys.stdout = old_stdout

    map_obj = None
    df_obj = None
    for obj in local_ctx.values():
        if isinstance(obj, folium.Map):
            map_obj = obj
        elif isinstance(obj, pd.DataFrame):
            df_obj = obj

    return captured.getvalue(), map_obj, df_obj

# --------------------------------------------------------------------------- #
# Optional GitHub-push stub (keeps old code paths alive without changing them)
# --------------------------------------------------------------------------- #
try:
    from github_sync import push_db_to_github  # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):  # noqa: D401
        """No-op stub – DB already lives in MySQL, nothing to push."""
        return {"success": True}

# --------------------------------------------------------------------------- #
# MAIN UI
# --------------------------------------------------------------------------- #
def show():
    set_page_style()

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

    # ————————————————————————————— Tabs for details —————————————————————————————
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        In this assignment, you will write a Python script to plot three geographical coordinates on a map and calculate the distance between each pair of points in kilometers. This will help you practice working with geospatial data and Python libraries for mapping and calculations.
        
        **Assignment: Week 1 – Mapping Coordinates and Calculating Distances in Python**
        """, unsafe_allow_html=True)
        with st.expander("See More"):
            st.markdown("""
            <span style="color: #FFD700;"><strong>Task Requirements:</strong></span>
            1. <span style="color: #FFD700;"><strong>Plot the Three Coordinates on a Map:</strong></span>
               - The coordinates represent three locations in the Kurdistan Region.
               - Use Python libraries to plot these points on a map.
               - The map should visually display the exact locations of the coordinates.
            2. <span style="color: #FFD700;"><strong>Calculate the Distance Between Each Pair of Points:</strong></span>
               - Calculate the distances between the three points in kilometers.
               - Specifically, calculate:
                 - The distance between Point 1 and Point 2.
                 - The distance between Point 2 and Point 3.
                 - The distance between Point 1 and Point 3.
               - Add markers to the map for each coordinate.
               - Add polylines to connect the points.
               - Add popups to display distance information.

            <span style="color: #FFD700;"><strong>Coordinates:</strong></span>
            - Point 1: Latitude: 36.325735, Longitude: 43.928414
            - Point 2: Latitude: 36.393432, Longitude: 44.586781
            - Point 3: Latitude: 36.660477, Longitude: 43.840174
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        ### Detailed Grading Breakdown
        - **Code Structure and Implementation:** 30 points
        - **Map Visualization:** 40 points
        - **Distance Calculations:** 30 points
        """, unsafe_allow_html=True)
        st.markdown("""
        #### 1. Code Structure and Implementation (30 points)
        - **Library Imports (5 points):**
            - Checks if the required libraries (folium, geopy, geodesic) are imported.
        - **Coordinate Handling (5 points):**
            - Checks if the correct coordinates are defined in the code.
        - **Code Execution (10 points):**
            - Checks if the code runs without errors.
        - **Code Quality (10 points):**
            - **Variable Naming:** 2 points (deducted if single-letter variables are used).
            - **Spacing:** 2 points (deducted if improper spacing is found).
            - **Comments:** 2 points (deducted if no comments are present).
            - **Code Organization:** 2 points (deducted if no blank lines are used for separation).
        """, unsafe_allow_html=True)
        with st.expander("See More"):
            st.markdown("""
            #### 2. Map Visualization (40 points)
            - **Map Generation (15 points):**
                - Checks if the folium.Map is correctly initialized.
            - **Markers (15 points):**
                - Checks if markers are added for each coordinate.
            - **Polylines (5 points):**
                - Checks if polylines connect the points.
            - **Popups (5 points):**
                - Checks if popups are added to the markers.
            #### 3. Distance Calculations (30 points)
            - **Geodesic Implementation (10 points):**
                - Checks if the geodesic function is used correctly.
            - **Distance Accuracy (20 points):**
                - Checks if the calculated distances are accurate within a 100-meter tolerance.
            """, unsafe_allow_html=True)

    # ————————————————————————————— Username entry —————————————————————————————
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter", key="enter_user"):
        if not username_input:
            st.error("Please enter a username.")
        else:
            if user_exists(username_input):
                st.session_state["username_entered"] = True
                st.session_state["username"]         = username_input
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False

    # ————————————————————————————— Code execution & grading —————————————————————————————
    if st.session_state["username_entered"]:
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as1_code")

        # Run Code button
        if st.button("Run Code", key="run_code"):
            st.session_state.update(
                run_success=False,
                captured_output="",
                map_object=None,
                dataframe_object=None,
            )
            out, mobj, dfobj = run_and_capture(code_input)
            st.session_state["captured_output"] = out
            st.session_state["map_object"]       = mobj
            st.session_state["dataframe_object"] = dfobj
            st.session_state["run_success"]      = True

            if out:
                st.markdown("### 📄 Captured Output")
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;">'
                    f'{out.replace(chr(10), "<br>")}</pre>',
                    unsafe_allow_html=True,
                )
            if mobj:
                st.markdown("### 🗺️ Map Output")
                st_folium(mobj, width=1000, height=500)
            if dfobj is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(dfobj)

        # Submit Code button
        if st.session_state["run_success"] and st.button("Submit Code", key="submit_code"):
            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)
            st.write(f"**Calculated Grade:** {grade}/100")

            if grade < 70:
                st.error(f"You got {grade}/100. Please revise and try again.")
            else:
                try:
                    conn = get_cached_conn()
                    cur  = conn.cursor()
                    cur.execute(
                        "UPDATE records SET as1 = %s WHERE username = %s",
                        (grade, st.session_state["username"]),
                    )
                    conn.commit()
                    if cur.rowcount == 0:
                        st.error("⚠️ No record updated—please check the username.")
                    else:
                        push_db_to_github()
                        cur.execute(
                            "SELECT as1 FROM records WHERE username = %s",
                            (st.session_state["username"],),
                        )
                        new_grade = cur.fetchone()[0]
                        st.success(f"🎉 Submission successful! Your grade: {new_grade}/100")
                        st.session_state["username_entered"] = False
                        st.session_state["username"] = ""
                except Exception as e:
                    st.error(f"Database error: {e}")
                finally:
                    conn.close()

if __name__ == "__main__":
    show()
