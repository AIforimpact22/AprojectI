import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
from database import get_connection   # <— central helper

def show():
    # style & state
    set_page_style()
    for k, v in {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username_entered": False,
        "username": "",
    }.items():
        st.session_state.setdefault(k, v)

    st.title("Assignment 1 – Mapping Coordinates & Distances")

    # (Markdown for assignment + grading unchanged) …

    # ── Step 1 : Enter username ───────────────────────────
    st.subheader("Step 1 – Enter Your Username")
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s", (username_input,))
            if cur.fetchone():
                st.session_state.update(username_entered=True, username=username_input)
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username.")
                st.session_state["username_entered"] = False

    # ── Step 3 – Run & Submit code ───────────────────────
    if st.session_state["username_entered"]:
        st.subheader("Step 3 – Run and Submit Your Code")
        code_input = st.text_area("📝 Paste your code here", height=300)

        if st.button("Run Code"):
            st.session_state["run_success"] = False
            try:
                import sys, traceback
                captured = StringIO(); sys.stdout, old = captured, sys.stdout
                local_ctx = {}; exec(code_input, {}, local_ctx)
                sys.stdout = old
                st.session_state["captured_output"]  = captured.getvalue()
                st.session_state["map_object"]       = next((o for o in local_ctx.values() if isinstance(o, folium.Map)), None)
                st.session_state["dataframe_object"] = next((o for o in local_ctx.values() if isinstance(o, pd.DataFrame)), None)
                st.session_state["run_success"]      = True
            except Exception as e:
                sys.stdout = old
                st.error(f"Error running code:\n{traceback.format_exc()}")

        if st.session_state["run_success"]:
            st.code(st.session_state["captured_output"] or "No text output.")
            if st.session_state["map_object"]:
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.dataframe(st.session_state["dataframe_object"])

        if st.button("Submit Code"):
            if not st.session_state["run_success"]:
                st.error("Run your code first.")
                return
            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)
            if grade < 70:
                st.error(f"You got {grade}/100. Please try again.")
                return
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE records SET as1 = %s WHERE username = %s",
                    (grade, st.session_state["username"])
                )
                conn.commit()
            st.success(f"Submission successful! Your grade: {grade}/100")
            st.session_state.update(username_entered=False, username="")

if __name__ == "__main__":
    show()
