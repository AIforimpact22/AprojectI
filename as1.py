# as1.py – Fixed MySQL + Map Version
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
import sys

# GitHub push stub
try:
    from github_sync import push_db_to_github
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):
        return {"success": True}

# MySQL connection
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

# MAIN APP
def show():
    set_page_style()

    for key, val in {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username_entered": False,
        "username": ""
    }.items():
        st.session_state.setdefault(key, val)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    st.markdown('<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    with st.expander("Assignment Details"):
        st.markdown("""
        **Coordinates:**
        - Point 1: (36.325735, 43.928414)
        - Point 2: (36.393432, 44.586781)
        - Point 3: (36.660477, 43.840174)
        """)

    st.markdown('<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username = st.text_input("Username", key="as1_username")

    if st.button("Enter Username"):
        if not username:
            st.error("Username is required.")
        else:
            try:
                conn = _get_conn()
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM records WHERE username = %s", (username,))
                if cur.fetchone():
                    st.session_state["username_entered"] = True
                    st.session_state["username"] = username
                    st.success(f"Welcome {username}!")
                else:
                    st.error("Username not found.")
                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"MySQL Error: {e}")

    if st.session_state.get("username_entered"):
        st.markdown('<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste your code here", height=300)

        if st.button("Run Code"):
            st.session_state.update(run_success=False, captured_output="", map_object=None, dataframe_object=None)
            try:
                buffer = StringIO()
                sys.stdout = buffer

                local_ctx = {}
                exec(code_input, {}, local_ctx)

                sys.stdout = sys.__stdout__
                st.session_state["captured_output"] = buffer.getvalue()

                for val in local_ctx.values():
                    if isinstance(val, folium.Map):
                        st.session_state["map_object"] = val
                    elif isinstance(val, pd.DataFrame):
                        st.session_state["dataframe_object"] = val

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys.__stdout__
                st.error(f"Execution Error: {e}")

        if st.session_state["run_success"]:
            st.subheader("📄 Output")
            if st.session_state["captured_output"]:
                st.markdown(
                    f'<pre style="color:white;">{st.session_state["captured_output"].replace(chr(10), "<br>")}</pre>',
                    unsafe_allow_html=True,
                )
            if st.session_state["map_object"]:
                st.subheader("🗺️ Map Output")
                try:
                    st_folium(st.session_state["map_object"], width=1000, height=500)
                except Exception as e:
                    st.error(f"Map render failed: {e}")
            if st.session_state["dataframe_object"] is not None:
                st.subheader("📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code before submitting.")
            else:
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)

                if grade < 70:
                    st.error(f"You got {grade}/100. Try again.")
                else:
                    try:
                        conn = _get_conn()
                        cur = conn.cursor()
                        cur.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
                        conn.commit()
                        cur.execute("SELECT as1 FROM records WHERE username = %s", (st.session_state["username"],))
                        result = cur.fetchone()
                        cur.close()
                        conn.close()

                        if result:
                            st.success(f"Submission successful! Your grade: {result[0]}/100")
                            push_db_to_github(None)
                        else:
                            st.error("Grade update failed.")
                    except Exception as e:
                        st.error(f"MySQL Submit Error: {e}")
                st.session_state["username_entered"] = False
                st.session_state["username"] = ""

if __name__ == "__main__":
    show()
