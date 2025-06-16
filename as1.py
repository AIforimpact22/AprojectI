import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
from github_sync import push_db_to_github  # Optional
from database import get_connection  # ✅ MySQL connection function

def show():
    # Apply the custom page style
    set_page_style()

    # Initialize session state
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

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # Step 2: Review Assignment Details
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        In this assignment, you will write a Python script to plot three geographical coordinates...
        """)
    with st.expander("See More"):
        st.markdown("""
        **Task Requirements:**
        ...
        """)

    with tab2:
        st.markdown("""
        ### Detailed Grading Breakdown
        ...
        """)
        with st.expander("See More"):
            st.markdown("""
            #### 2. Map Visualization (40 points)
            ...
            """)

    # Step 1: Enter Username
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    enter_username = st.button("Enter")
    if enter_username and username_input:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM records WHERE username = %s", (username_input,))
            user_record = cursor.fetchone()
            conn.close()

            if user_record:
                st.session_state["username_entered"] = True
                st.session_state["username"] = username_input
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False
        except Exception as e:
            st.error(f"MySQL Error: {e}")

    if st.session_state.get("username_entered", False):
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: white;">📝 Paste Your Code Here</p>', unsafe_allow_html=True)
        code_input = st.text_area("", height=300)

        if st.button("Run Code", key="run_code_button") and code_input:
            st.session_state["run_success"] = False
            st.session_state["captured_output"] = ""
            try:
                from io import StringIO
                import sys
                captured_output = StringIO()
                sys.stdout = captured_output
                local_context = {}
                exec(code_input, {}, local_context)
                sys.stdout = sys.__stdout__
                st.session_state["captured_output"] = captured_output.getvalue()
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
                st.markdown(f'<pre style="color: white;">{st.session_state["captured_output"].replace("\n", "<br>")}</pre>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color: white;">No text output captured.</p>', unsafe_allow_html=True)

            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)

            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        if st.button("Submit Code", key="submit_code_button"):
            if not st.session_state.get("run_success", False):
                st.error("Please run your code successfully before submitting.")
            elif st.session_state.get("username", "").strip():
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)
                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                else:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
                        conn.commit()
                        updated_rows = cursor.rowcount
                        conn.close()

                        if updated_rows == 0:
                            st.error("No record updated. Please check the username or database integrity.")
                        else:
                            st.info("Grade updated. Pushing changes to GitHub...")
                            try:
                                response = push_db_to_github("mydatabase.db")  # This path isn't used anymore if you're not pushing .db files
                                st.success(f"Submission successful! Your grade: {grade}/100")
                            except Exception as e:
                                st.error(f"GitHub sync error: {str(e)}")
                        st.session_state["username_entered"] = False
                        st.session_state["username"] = ""
                    except Exception as e:
                        st.error(f"MySQL Error: {e}")
            else:
                st.error("Please enter your username to submit.")

if __name__ == "__main__":
    show()
