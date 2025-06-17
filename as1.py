import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector

# ──────────────────────────────────────────────────────────────
# GitHub push (No-op for MySQL users)
# ──────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github
except ModuleNotFoundError:
    def push_db_to_github(*args, **kwargs):
        return {"success": True}

# ──────────────────────────────────────────────────────────────
# DB Connection
# ──────────────────────────────────────────────────────────────
def get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"]
    )

# ──────────────────────────────────────────────────────────────
# Main App
# ──────────────────────────────────────────────────────────────
def show():
    set_page_style()

    for key, val in {
        "run_success": False,
        "map_object": None,
        "dataframe_object": None,
        "captured_output": "",
        "username": "",
        "username_entered": False,
    }.items():
        st.session_state.setdefault(key, val)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")
    st.markdown('<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username = st.text_input("Username", key="as1_username_input")

    if st.button("Enter"):
        if not username:
            st.error("Please enter a username.")
        else:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s", (username,))
            if cur.fetchone():
                st.session_state["username"] = username
                st.session_state["username_entered"] = True
                st.success(f"Welcome, {username}!")
            else:
                st.error("Username not found.")
            cur.close()
            conn.close()

    # ──────────────────────────────────────────────────────────────
    # Step 2: Instructions
    # ──────────────────────────────────────────────────────────────
    st.markdown('<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        In this assignment, you will write Python code to:
        1. Plot 3 coordinates on a map
        2. Calculate distances between them
        3. Display results with Folium + Pandas
        """)

    with tab2:
        st.markdown("""
        **Grading:**
        - Code Structure: 30
        - Map Display: 40
        - Distance Logic: 30
        """)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Code Execution
    # ──────────────────────────────────────────────────────────────
    if st.session_state["username_entered"]:
        st.markdown('<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code = st.text_area("📝 Paste Your Code Here", height=300)

        if st.button("Run Code"):
            st.session_state["run_success"] = False
            st.session_state["map_object"] = None
            st.session_state["dataframe_object"] = None
            st.session_state["captured_output"] = ""

            try:
                import sys
                from io import StringIO
                output = StringIO()
                sys_stdout = sys.stdout
                sys.stdout = output

                local_vars = {}
                exec(code, {}, local_vars)

                sys.stdout = sys_stdout
                st.session_state["captured_output"] = output.getvalue()
                for obj in local_vars.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
                st.success("✅ Code ran successfully.")
            except Exception as e:
                sys.stdout = sys_stdout
                st.error(f"❌ Error: {e}")

        # Show output
        if st.session_state["run_success"]:
            if st.session_state["captured_output"]:
                st.markdown("### 📄 Output")
                st.markdown(f'<pre style="color:white;">{st.session_state["captured_output"]}</pre>', unsafe_allow_html=True)
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # Submit code
        if st.button("Submit Code"):
            if not st.session_state["run_success"]:
                st.error("Run the code first before submitting.")
            else:
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code)

                conn = get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE records SET as1 = %s WHERE username = %s", (grade, st.session_state["username"]))
                conn.commit()
                cur.close()
                conn.close()

                push_db_to_github(None)
                st.success(f"🎉 Grade submitted successfully: {grade}/100")

                st.session_state["username_entered"] = False
                st.session_state["username"] = ""

# Entry point
if __name__ == "__main__":
    show()
