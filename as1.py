import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector

# Apply the custom page style
def show():
    set_page_style()

    # Initialize session state variables if not already set
    for key in ["run_success", "map_object", "dataframe_object", "captured_output", "username_entered", "username"]:
        if key not in st.session_state:
            st.session_state[key] = False if key != "username" else ""

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # Step 2: Review Assignment Details
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        In this assignment, you will write a Python script to plot three geographical coordinates on a map and calculate the distance between each pair of points in kilometers.
        
        **Assignment: Week 1 – Mapping Coordinates and Calculating Distances in Python**
        """)
    with st.expander("See More"):
        st.markdown("""
        **Task Requirements:**
        1. Plot three coordinates on a map
        2. Calculate the distance between each pair
        **Coordinates:**
        - Point 1: 36.325735, 43.928414
        - Point 2: 36.393432, 44.586781
        - Point 3: 36.660477, 43.840174
        """)

    with tab2:
        st.markdown("""
        ### Grading Breakdown
        - Code Structure: 30
        - Map Visualization: 40
        - Distance Calculations: 30
        """)

    # Step 1: Enter Your Username
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter") and username_input:
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE username = %s", (username_input,))
        user_record = cursor.fetchone()
        conn.close()

        if user_record:
            st.session_state["username_entered"] = True
            st.session_state["username"] = username_input
            st.success(f"Welcome, {username_input}!")
        else:
            st.error("Invalid username.")
            st.session_state["username_entered"] = False

    if st.session_state.get("username_entered", False):
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: white;">📝 Paste Your Code Here</p>', unsafe_allow_html=True)
        code_input = st.text_area("", height=300)

        if st.button("Run Code") and code_input:
            st.session_state["run_success"] = False
            st.session_state["captured_output"] = ""
            try:
                captured_output = StringIO()
                import sys
                sys.stdout = captured_output
                local_context = {}
                exec(code_input, {}, local_context)
                sys.stdout = sys.__stdout__
                st.session_state["captured_output"] = captured_output.getvalue()
                st.session_state["map_object"] = next((v for v in local_context.values() if isinstance(v, folium.Map)), None)
                st.session_state["dataframe_object"] = next((v for v in local_context.values() if isinstance(v, pd.DataFrame)), None)
                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys.__stdout__
                st.error(f"Error running code: {e}")

        if st.session_state["run_success"]:
            st.markdown('<h3 style="color: white;">📄 Captured Output</h3>', unsafe_allow_html=True)
            out = st.session_state["captured_output"].replace('\n', '<br>')
            st.markdown(f'<pre style="color: white;">{out}</pre>', unsafe_allow_html=True)
            if st.session_state["map_object"]:
                st.markdown("### 🗌️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        if st.button("Submit Code"):
            if not st.session_state.get("run_success", False):
                st.error("Please run your code before submitting.")
            else:
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)
                if grade < 70:
                    st.error(f"You got {grade}/100. Try again.")
                else:
                    try:
                        conn = mysql.connector.connect(
                            host=st.secrets["mysql"]["host"],
                            port=st.secrets["mysql"]["port"],
                            user=st.secrets["mysql"]["user"],
                            password=st.secrets["mysql"]["password"],
                            database=st.secrets["mysql"]["database"]
                        )
                        cursor = conn.cursor()
                        cursor.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
                        conn.commit()
                        conn.close()
                        st.success(f"Submission successful! Your grade: {grade}/100")
                        st.session_state["username"] = ""
                        st.session_state["username_entered"] = False
                    except Exception as e:
                        st.error(f"Failed to update grade: {e}")

if __name__ == "__main__":
    show()
