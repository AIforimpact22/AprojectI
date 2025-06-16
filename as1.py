# as1.py  – MySQL version (no local .db file required)
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector

# --------------------------------------------------------------------------- #
# Optional GitHub-push stub (no-op now that DB is MySQL)
# --------------------------------------------------------------------------- #
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        return {"success": True}

# --------------------------------------------------------------------------- #
# DB helper
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

    # ──────────────────────────────────────────────────────────────
    # Session defaults
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
    # Step 2 – assignment details (always visible)
    # ──────────────────────────────────────────────────────────────
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    # TAB 1 ───────────────────────────────────────────────────────
    with tab1:
        st.markdown(
            """
            ### <span style="color:#FFD700;">Objective</span>
            In this assignment, you will write a Python script to plot three geographical
            coordinates on a map and calculate the distance between each pair of points
            in kilometres.
            
            **Assignment: Week 1 – Mapping Coordinates and Calculating Distances in Python**
            """,
            unsafe_allow_html=True,
        )

    with st.expander("See More"):
        st.markdown(
            """
            <span style="color:#FFD700;"><strong>Task Requirements:</strong></span>

            1. **<span style="color:#FFD700;">Plot the Three Coordinates on a Map:</span>**
               - The coordinates represent three locations in the Kurdistan Region.  
               - Use Python libraries to plot these points on a map.  
               - The map should visually display the exact locations of the coordinates.

            2. **<span style="color:#FFD700;">Calculate the Distance Between Each Pair of Points:</span>**
               - Calculate the distances between the three points in kilometres.  
                 - Point 1 ↔ Point 2  
                 - Point 2 ↔ Point 3  
                 - Point 1 ↔ Point 3  
               - Add markers to the map for each coordinate.  
               - Add polylines to connect the points.  
               - Add pop-ups to display distance information.

            <span style="color:#FFD700;"><strong>Coordinates:</strong></span>  
            • Point 1 – 36.325735, 43.928414  
            • Point 2 – 36.393432, 44.586781  
            • Point 3 – 36.660477, 43.840174
            """,
            unsafe_allow_html=True,
        )

    # TAB 2 ───────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            """
            ### <span style="color:#FFD700;">Detailed Grading Breakdown</span>
            - **<span style="color:#FFD700;">Code Structure and Implementation:</span>** 30 points  
            - **<span style="color:#FFD700;">Map Visualization:</span>** 40 points  
            - **<span style="color:#FFD700;">Distance Calculations:</span>** 30 points
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            #### <span style="color:#FFD700;">1.&nbsp;Code Structure and Implementation (30 points)</span>
            • Library Imports (5) • Coordinate Handling (5) • Code Execution (10) • Code Quality (10)  
            &nbsp;&nbsp;• Variable Naming (2) • Spacing (2) • Comments (2) • Organization (2)
            """,
            unsafe_allow_html=True,
        )

        with st.expander("See More"):
            st.markdown(
                """
                #### <span style="color:#FFD700;">2.&nbsp;Map Visualization (40 points)</span>
                Map Generation (15) • Markers (15) • Polylines (5) • Pop-ups (5)

                #### <span style="color:#FFD700;">3.&nbsp;Distance Calculations (30 points)</span>
                Geodesic Implementation (10) • Distance Accuracy (20 ≤ 100 m tolerance)
                """,
                unsafe_allow_html=True,
            )

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
            cur  = conn.cursor()
            cur.execute(
                "SELECT 1 FROM records WHERE username = %s LIMIT 1",
                (username_input,),
            )
            exists = cur.fetchone() is not None
            conn.close()

            if exists:
                st.session_state["username_entered"] = True
                st.session_state["username"]         = username_input
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False

    # ──────────────────────────────────────────────────────────────
    # Step 3 – code input / execution / grading
    # ──────────────────────────────────────────────────────────────
    if st.session_state.get("username_entered"):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        # Run Code
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

        # Show captured output / map / dataframe
        if st.session_state["run_success"]:
            if st.session_state["captured_output"]:
                st.markdown("### 📄 Captured Output")
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;">'
                    f'{st.session_state["captured_output"].replace(chr(10), "<br>")}'
                    "</pre>",
                    unsafe_allow_html=True,
                )
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # Submit
        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code successfully before submitting.")
                return

            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)
            if grade < 70:
                st.error(f"You got {grade}/100. Please try again.")
                return

            # Store grade in MySQL
            conn = _get_conn()
            cur  = conn.cursor()
            cur.execute(
                "UPDATE records SET as1 = %s WHERE username = %s",
                (grade, st.session_state["username"]),
            )
            conn.commit()
            updated = cur.rowcount
            conn.close()

            if updated == 0:
                st.error("No record updated—please check the username.")
                return

            push_db_to_github(None)  # no-op

            conn = _get_conn()
            cur  = conn.cursor()
            cur.execute(
                "SELECT as1 FROM records WHERE username = %s",
                (st.session_state["username"],),
            )
            new_grade = cur.fetchone()[0]
            conn.close()

            st.success(f"Submission successful! Your grade: {new_grade}/100")
            st.session_state["username_entered"] = False
            st.session_state["username"] = ""

# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    show()
