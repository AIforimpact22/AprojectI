import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
from mysql.connector import IntegrityError

# ──────────────────────────────────────────────────────────────────────────────
# DB helper – reads `[mysql]` block in secrets
# ──────────────────────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────────────────────
# Main UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    # Apply the custom page style
    set_page_style()

    # Initialize session state variables if not already set
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Review Assignment Details (always show)
    # ──────────────────────────────────────────────────────────────
    st.markdown(
        '<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>',
        unsafe_allow_html=True,
    )
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    # Add markdown content inside these tabs if needed

    # ──────────────────────────────────────────────────────────────
    # Step 1: Enter Username
    # ──────────────────────────────────────────────────────────────
    st.markdown(
        '<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s", (username_input,))
            user_exists = cur.fetchone() is not None

        if user_exists:
            st.session_state["username_entered"] = True
            st.session_state["username"] = username_input
            st.success(f"Welcome, {username_input}!")
        else:
            st.error("❌ Invalid username. Please enter a registered username.")
            st.session_state["username_entered"] = False

    # ──────────────────────────────────────────────────────────────
    # Step 3: Run and Submit Code (logged-in users)
    # ──────────────────────────────────────────────────────────────
    if st.session_state.get("username_entered", False):
        st.markdown(
            '<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="color: white;">📝 Paste Your Code Here</p>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("", height=300)

        # ───────── Run code
        if st.button("Run Code"):
            st.session_state["run_success"] = False
            st.session_state["captured_output"] = ""
            try:
                import sys

                captured = StringIO()
                sys.stdout = captured

                local_ctx = {}
                exec(code_input, {}, local_ctx)

                sys.stdout = sys.__stdout__
                st.session_state["captured_output"] = captured.getvalue()

                # Detect map / DataFrame
                st.session_state["map_object"] = next(
                    (o for o in local_ctx.values() if isinstance(o, folium.Map)), None
                )
                st.session_state["dataframe_object"] = next(
                    (o for o in local_ctx.values() if isinstance(o, pd.DataFrame)),
                    None,
                )

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys.__stdout__
                st.error(f"❌ An error occurred while running your code: {e}")

        # ───────── Show outputs
        if st.session_state["run_success"]:
            st.markdown(
                '<h3 style="color: white;">📄 Captured Output</h3>',
                unsafe_allow_html=True,
            )
            if st.session_state["captured_output"]:
                out_fmt = st.session_state["captured_output"].replace("\n", "<br>")
                st.markdown(
                    f'<pre style="color: white; white-space: pre-wrap; word-wrap: break-word;">{out_fmt}</pre>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<p style="color: white;">No text output captured.</p>',
                    unsafe_allow_html=True,
                )

            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)

            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # ───────── Submit code
        if st.button("Submit Code"):
            if not st.session_state.get("run_success", False):
                st.error("❌ Please run your code successfully before submitting.")
            else:
                from grades.grade1 import grade_assignment

                grade = grade_assignment(code_input)

                if grade < 70:
                    st.warning(f"⚠️ You got {grade}/100. Please try again.")
                else:
                    try:
                        with _get_conn() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "UPDATE records SET as1 = %s WHERE username = %s",
                                (grade, st.session_state["username"]),
                            )
                            conn.commit()
                            updated = cur.rowcount

                        if updated:
                            st.success(f"✅ Submission successful! Your grade: {grade}/100")
                        else:
                            st.error("⚠️ No record updated — please check username or database.")
                    except IntegrityError as e:
                        st.error(f"❌ Submission failed: {e}")

                    # Reset state after successful submit
                    st.session_state["username_entered"] = False
                    st.session_state["username"] = ""


if __name__ == "__main__":
    show()
