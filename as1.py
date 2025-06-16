import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style

# ▶ NEW: use the shared MySQL connection helper
from database import get_connection

def show():
    # ───────────────────────────────────────────────
    # Page Style & session-state initialisation
    # ───────────────────────────────────────────────
    set_page_style()

    defaults = {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username_entered": False,
        "username": "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ───────────────────────────────────────────────
    # STEP 2 – Review Assignment Details  (always visible)
    # ───────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
    # … <unchanged markdown content> …

    # ───────────────────────────────────────────────
    # STEP 1 – Enter Username (now verified via MySQL)
    # ───────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE username = %s", (username_input,))
        user_record = cursor.fetchone()
        conn.close()

        if user_record:
            st.session_state.update(username_entered=True, username=username_input)
            st.success(f"Welcome, {username_input}!")
        else:
            st.error("Invalid username. Please enter a registered username.")
            st.session_state["username_entered"] = False

    # ───────────────────────────────────────────────
    # STEP 3 – Run & Submit Code  (only after login)
    # ───────────────────────────────────────────────
    if st.session_state["username_entered"]:
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: white;">📝 Paste Your Code Here</p>', unsafe_allow_html=True)
        code_input = st.text_area("", height=300)

        # Run Code
        if st.button("Run Code"):
            st.session_state.update(run_success=False, captured_output="", map_object=None, dataframe_object=None)
            try:
                capture = StringIO()
                import sys
                sys.stdout = capture
                local_ctx = {}
                exec(code_input, {}, local_ctx)
                sys.stdout = sys.__stdout__

                st.session_state["captured_output"] = capture.getvalue()
                st.session_state["map_object"] = next((o for o in local_ctx.values() if isinstance(o, folium.Map)), None)
                st.session_state["dataframe_object"] = next((o for o in local_ctx.values() if isinstance(o, pd.DataFrame)), None)
                st.session_state["run_success"] = True

            except Exception as e:
                sys.stdout = sys.__stdout__
                st.error(f"Error while running your code: {e}")

        # Display results
        if st.session_state["run_success"]:
            st.markdown('<h3 style="color: white;">📄 Captured Output</h3>', unsafe_allow_html=True)
            if st.session_state["captured_output"]:
                st.markdown(
                    f'<pre style="color: white; white-space: pre-wrap;">{st.session_state["captured_output"].replace(chr(10), "<br>")}</pre>',
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

        # Submit Code → grade + store in MySQL
        if st.button("Submit Code"):
            if not st.session_state["run_success"]:
                st.error("Run your code successfully before submitting.")
                return

            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)

            if grade < 70:
                st.error(f"You scored {grade}/100. Please try again.")
                return

            # Update grade in MySQL
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
            conn.commit()
            cursor.close()
            conn.close()

            st.success(f"Submission successful! Your grade: {grade}/100")
            # Reset for next submission
            st.session_state.update(username_entered=False, username="", run_success=False)

if __name__ == "__main__":
    show()
