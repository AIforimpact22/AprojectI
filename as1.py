import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
from database import get_connection  # MySQL connection
from grades.grade1 import grade_assignment

def show():
    set_page_style()

    # Session variables
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Review Assignment Details (ALWAYS SHOW)
    # ──────────────────────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        You will plot three coordinates in the Kurdistan Region and calculate distances.
        """)

    with st.expander("See More"):
        st.markdown("""
        **Coordinates:**
        - Point 1: 36.325735, 43.928414
        - Point 2: 36.393432, 44.586781
        - Point 3: 36.660477, 43.840174
        """)

    with tab2:
        st.markdown("""
        ### Detailed Grading Breakdown
        - Code, Map, Distance: up to 100 points
        """)

    # ──────────────────────────────────────────────────────────────
    # Step 1: Enter Your Username
    # ──────────────────────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    enter_username = st.button("Enter")
    if enter_username and username_input:
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
            st.error("Invalid username.")

    # ──────────────────────────────────────────────────────────────
    # Step 3: Run and Submit Your Code
    # ──────────────────────────────────────────────────────────────
    if st.session_state.get("username_entered", False):
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        run_button = st.button("Run Code", key="run_code_button")
        if run_button and code_input:
            st.session_state["run_success"] = False
            st.session_state["captured_output"] = ""
            try:
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
                st.error(f"Error running your code: {e}")

        if st.session_state["run_success"]:
            st.markdown("### 📄 Output")
            if st.session_state["captured_output"]:
                st.markdown(f"<pre>{st.session_state['captured_output']}</pre>", unsafe_allow_html=True)

            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)

            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        submit_button = st.button("Submit Code", key="submit_code_button")
        if submit_button:
            if not st.session_state.get("run_success", False):
                st.error("Please run your code before submitting.")
            else:
                username = st.session_state["username"]
                grade = grade_assignment(code_input)

                if grade < 70:
                    st.error(f"❌ You got {grade}/100. Please try again.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, username))
                    conn.commit()
                    cursor.execute("SELECT as1 FROM records WHERE username = %s", (username,))
                    result = cursor.fetchone()
                    conn.close()

                    if result:
                        st.success(f"✅ Submission successful! Your grade: {result[0]}/100")
                    else:
                        st.error("❌ Grade not found after submission.")

                    st.session_state["username_entered"] = False
                    st.session_state["username"] = ""

if __name__ == "__main__":
    show()
