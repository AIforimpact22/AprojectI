
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import sqlite3
from github_sync import push_db_to_github  # , pull_db_from_github  # Uncomment if needed

def show():
    # Apply the custom page style
    set_page_style()

    # Initialize session state variables if not already set
    if "run_success" not in st.session_state:
        st.session_state["run_success"] = False
    if "map_object" not in st.session_state:
        st.session_state["map_object"] = None
    if "dataframe_object" not in st.session_state:
        st.session_state["dataframe_object"] = None
    if "captured_output" not in st.session_state:
        st.session_state["captured_output"] = ""
    if "username_entered" not in st.session_state:
        st.session_state["username_entered"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = ""

    # Define the database path from secrets (ensure this points to your updated database file)
    db_path = st.secrets["general"]["db_path"]

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ──────────────────────────────────────────────────────────────
    # Step 2: Review Assignment Details (ALWAYS SHOW)
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
        **Task Requirements:**
        1. **Plot the Three Coordinates on a Map:**
           - The coordinates represent three locations in the Kurdistan Region.
           - Use Python libraries to plot these points on a map.
           - The map should visually display the exact locations of the coordinates.
        2. **Calculate the Distance Between Each Pair of Points:**
           - Calculate the distances between the three points in kilometers.
           - Specifically, calculate:
             - The distance between Point 1 and Point 2.
             - The distance between Point 2 and Point 3.
             - The distance between Point 1 and Point 3.
           - Add markers to the map for each coordinate.
           - Add polylines to connect the points.
           - Add popups to display distance information.
        
        **Coordinates:**
        - Point 1: Latitude: 36.325735, Longitude: 43.928414
        - Point 2: Latitude: 36.393432, Longitude: 44.586781
        - Point 3: Latitude: 36.660477, Longitude: 43.840174
        """)
    with tab2:
        st.markdown("""
        ### Detailed Grading Breakdown
        - **Code Structure and Implementation:** 30 points
        - **Map Visualization:** 40 points
        - **Distance Calculations:** 30 points
        """)
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
        """)
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
            """)

    # ──────────────────────────────────────────────────────────────
    # Step 1: Enter Your Username
    # ──────────────────────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    enter_username = st.button("Enter")
    if enter_username and username_input:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE username = ?", (username_input,))
        user_record = cursor.fetchone()
        conn.close()

        if user_record:
            st.session_state["username_entered"] = True
            st.session_state["username"] = username_input
            st.success(f"Welcome, {username_input}!")
        else:
            st.error("Invalid username. Please enter a registered username.")
            st.session_state["username_entered"] = False

    # ──────────────────────────────────────────────────────────────
    # Step 3: Run and Submit Your Code (only if user is logged in)
    # ──────────────────────────────────────────────────────────────
    if st.session_state.get("username_entered", False):
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: white;">📝 Paste Your Code Here</p>', unsafe_allow_html=True)
        code_input = st.text_area("", height=300)

        # Run Code Button
        run_button = st.button("Run Code", key="run_code_button")
        if run_button and code_input:
            st.session_state["run_success"] = False
            st.session_state["captured_output"] = ""
            try:
                from io import StringIO
                import sys

                captured_output = StringIO()
                sys.stdout = captured_output

                # Execute the user's code in a controlled environment
                local_context = {}
                exec(code_input, {}, local_context)

                # Restore stdout
                sys.stdout = sys.__stdout__

                # Capture printed output
                st.session_state["captured_output"] = captured_output.getvalue()

                # Look for specific outputs (folium.Map, pandas.DataFrame)
                map_object = next((obj for obj in local_context.values() if isinstance(obj, folium.Map)), None)
                dataframe_object = next((obj for obj in local_context.values() if isinstance(obj, pd.DataFrame)), None)

                st.session_state["map_object"] = map_object
                st.session_state["dataframe_object"] = dataframe_object

                st.session_state["run_success"] = True

            except Exception as e:
                sys.stdout = sys.__stdout__
                st.error(f"An error occurred while running your code: {e}")

        if st.session_state["run_success"]:
            st.markdown('<h3 style="color: white;">📄 Captured Output</h3>', unsafe_allow_html=True)
            if st.session_state["captured_output"]:
                formatted_output = st.session_state["captured_output"].replace('\n', '<br>')
                st.markdown(
                    f'<pre style="color: white; white-space: pre-wrap; word-wrap: break-word;">{formatted_output}</pre>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<p style="color: white;">No text output captured.</p>', unsafe_allow_html=True)

            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)

            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # ──────────────────────────────────────────────────────────────
        # Submit Code Button (updates grade and pushes DB)
        # ──────────────────────────────────────────────────────────────
        submit_button = st.button("Submit Code", key="submit_code_button")
        if submit_button:
            if not st.session_state.get("run_success", False):
                st.error("Please run your code successfully before submitting.")
            elif st.session_state.get("username", "").strip():
                # Grade the submission using your grading function
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)

                # Check if grade is less than 70. If so, do not update DB or push changes.
                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                else:
                    # Update the grade in the records table (OVERWRITING the existing row's as1 column)
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE records SET as1 = ? WHERE username = ?", (grade, st.session_state["username"]))
                    conn.commit()
                    updated_rows = cursor.rowcount
                    conn.close()

                    if updated_rows == 0:
                        st.error("No record updated. Please check the username or database integrity.")
                    else:
                        st.info("Grade updated locally. Pushing changes to GitHub...")

                        try:
                            # First push
                            push_db_to_github(db_path)
                            # Check after first push
                            conn = sqlite3.connect(db_path)
                            cursor = conn.cursor()
                            cursor.execute("SELECT as1 FROM records WHERE username = ?", (st.session_state["username"],))
                            result = cursor.fetchone()
                            conn.close()
                            if result:
                                new_grade = result[0]
                                st.success(f"Submission successful! Your grade: {new_grade}/100")

                            # Second push (original logic retained)
                            response = push_db_to_github(db_path)
                            if response.get("success"):
                                # Re-check the updated grade
                                conn = sqlite3.connect(db_path)
                                cursor = conn.cursor()
                                cursor.execute("SELECT as1 FROM records WHERE username = ?", (st.session_state["username"],))
                                result = cursor.fetchone()
                                conn.close()
                                if result:
                                    new_grade = result[0]
                                    st.success(f"Submission successful! Your grade: {new_grade}/100")
                                else:
                                    st.error("Error retrieving the updated grade after push.")
                            else:
                                st.error("Error retrieving the updated grade.")
                                st.error(f"GitHub push failed: {response.get('error')}")
                        except Exception as e:
                            st.error(f"GitHub sync error: {str(e)}")

                    # Clear username so the user must re-enter it on the next submission
                    st.session_state["username_entered"] = False
                    st.session_state["username"] = ""
            else:
                st.error("Please enter your username to submit.")

if __name__ == "__main__":
    show()
