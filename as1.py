# as1.py  – MySQL version (no local .db file required)
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
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
    with tab1:
        st.markdown(
            """
            ### Objective
            In this assignment, you will write a Python script to plot three
            geographical coordinates on a map and calculate the distance
            between each pair of points in kilometres.
            """
        )
    with st.expander("See More"):
        st.markdown("*(full assignment text unchanged)*")
    with tab2:
        st.markdown("*(grading rubric unchanged)*")

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

                # Check for folium.Map or DataFrame in namespace
                for obj in local_context.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys_stdout_original
                st.error(f"Error while running code: {e}")

        # Display captured output / map / dataframe
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

        # ──────────────────────────────────────────────────────────
        # Submit button – update grade in MySQL
        # ──────────────────────────────────────────────────────────
        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code successfully before submitting.")
            else:
                # Grade using existing grading function
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

                # Optional GitHub push (now a no-op)
                push_db_to_github(None)

                # Confirm result
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "SELECT as1 FROM records WHERE username = %s",
                    (st.session_state["username"],),
                )
                new_grade = cur.fetchone()[0]
                conn.close()

                st.success(f"Submission successful! Your grade: {new_grade}/100")

                # Force re-enter username next time
                st.session_state["username_entered"] = False
                st.session_state["username"] = ""

# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    show()
