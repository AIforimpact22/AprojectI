import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
from database import get_connection            # ← NEW

def show():
    # ───────── Init page style & session state ─────────
    set_page_style()

    defaults = {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username_entered": False,
        "username": ""
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    st.title("Assignment 1 – Mapping Coordinates & Distances")

    # ───────── Step 2 : Always-visible assignment details ─────────
    st.markdown('<h1 style="color:#ADD8E6;">Step 2 : Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
    with tab1:
        st.markdown("### Objective …")           # (kept content shortened)
    #  … existing Markdown for details / grading unchanged …

    # ───────── Step 1 : Username entry ─────────
    st.markdown('<h1 style="color:#ADD8E6;">Step 1 : Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM records WHERE username = %s", (username_input,))
        exists = cursor.fetchone()
        conn.close()

        if exists:
            st.session_state.update(username_entered=True, username=username_input)
            st.success(f"Welcome, {username_input}!")
        else:
            st.error("Invalid username. Please enter a registered username.")
            st.session_state["username_entered"] = False

    # ───────── Step 3 : Paste / run / grade code ─────────
    if st.session_state["username_entered"]:
        st.markdown('<h1 style="color:#ADD8E6;">Step 3 : Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste your code here", height=300)

        if st.button("Run Code"):
            from io import StringIO
            import sys, traceback

            captured = StringIO()
            sys.stdout, orig_stdout = captured, sys.stdout
            try:
                local_ctx = {}
                exec(code_input, {}, local_ctx)      # Run user code

                st.session_state["map_object"]       = next((o for o in local_ctx.values() if isinstance(o, folium.Map)), None)
                st.session_state["dataframe_object"] = next((o for o in local_ctx.values() if isinstance(o, pd.DataFrame)), None)
                st.session_state["captured_output"]  = captured.getvalue()
                st.session_state["run_success"]      = True
            except Exception:
                st.error(f"Error running code:\n{traceback.format_exc()}")
                st.session_state["run_success"] = False
            finally:
                sys.stdout = orig_stdout

        # ───────── Show outputs if run succeeded ─────────
        if st.session_state["run_success"]:
            st.markdown("#### 📄 Captured Output")
            if st.session_state["captured_output"]:
                st.code(st.session_state["captured_output"])
            else:
                st.info("No text output captured.")

            if st.session_state["map_object"]:
                st.markdown("#### 🗺 Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)

            if st.session_state["dataframe_object"] is not None:
                st.markdown("#### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # ───────── Submit / grade ─────────
        if st.button("Submit Code"):
            if not st.session_state["run_success"]:
                st.error("Please run your code successfully before submitting.")
                return

            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)

            if grade < 70:
                st.error(f"You got {grade}/100. Please try again.")
                return

            # Write grade to MySQL
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
            conn.commit()
            rows = cursor.rowcount
            conn.close()

            if rows:
                st.success(f"Submission successful! Your grade: {grade}/100")
            else:
                st.error("Grade update failed. Check username or DB integrity.")

            st.session_state.update(username_entered=False, username="")

if __name__ == "__main__":
    show()
