# as2.py  – MySQL edition (no local .db file)

import streamlit as st
import os
from grades.grade2 import grade_assignment
import mysql.connector
from mysql.connector import pooling

# ──────────────────────────────────────────────────────────────────────────────
# Initialize a MySQL connection pool once per session
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_conn_pool():
    cfg = st.secrets["mysql"]
    return pooling.MySQLConnectionPool(
        pool_name="mypool_as2",
        pool_size=5,
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )

def get_conn():
    return init_conn_pool().get_connection()

# ──────────────────────────────────────────────────────────────────────────────
# Cache username verification
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def username_exists(username: str) -> bool:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps old code alive even after removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github  # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):  # noqa: D401
        """No-op – all data now lives in MySQL."""
        return {"success": True}

# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    st.title("Assignment 2: Analyzing Real-Time Earthquake Data")

    # ────────────────── STEP 1 – username verification ──────────────────
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username = st.text_input("Enter Your Username")
    if st.button("Verify Username") and username:
        if username_exists(username):
            st.success("Username verified. Proceed to the next steps.")
            st.session_state["verified"] = True
        else:
            st.error("Username not found. Please enter a registered username.")
            st.session_state["verified"] = False

    # ────────────────── STEP 2 – assignment & grading details ──────────────────
    if st.session_state.get("verified", False):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
            unsafe_allow_html=True,
        )
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

        with tab1:
            st.markdown("""
            ### Objective
            In this assignment, you will write a Python script that fetches real-time earthquake data from the USGS Earthquake API, processes the data to filter earthquakes with a magnitude greater than 4.0, and plots the earthquake locations on a map. Additionally, you will calculate the number of earthquakes in different magnitude ranges and present the results visually.
            """)
            with st.expander("See More"):
                st.markdown("""
                **Task Requirements:**
                - **Fetch Earthquake Data** for January 2–9, 2025.
                - **Filter** magnitude > 4.0.
                - **Map** with folium: color-coded markers by magnitude range, popups with details.
                - **Bar Chart** (matplotlib) of counts by ranges: 4.0–4.5, 4.5–5.0, 5.0+.
                - **CSV Summary** with total count, avg/max/min magnitudes, counts per range.
                """)

        with tab2:
            st.markdown("### Detailed Grading Breakdown")
            st.markdown("""
            **Library Imports (10 Pts)**  
            **Code Quality (20 Pts)**  
            **Data Fetching (10 Pts)**  
            **Filtering (10 Pts)**  
            **Map Visualization (20 Pts)**  
            **Bar Chart (15 Pts)**  
            **Text Summary (15 Pts)**
            """)

        # ────────────────── STEP 3 – code entry ──────────────────
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        # ────────────────── STEP 4 – file uploads ──────────────────
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 4: Upload Your Outputs</h1>',
            unsafe_allow_html=True,
        )
        uploaded_html = st.file_uploader("Upload your HTML file (Map)", type=["html"])
        uploaded_png  = st.file_uploader("Upload your PNG file (Bar Chart)", type=["png"])
        uploaded_csv  = st.file_uploader("Upload your CSV file (Summary)", type=["csv"])

        all_uploaded = all([uploaded_html, uploaded_png, uploaded_csv])
        st.write("All files uploaded:", "✅ Yes" if all_uploaded else "❌ No")

        # ────────────────── SUBMIT button ──────────────────
        if all_uploaded and st.button("Submit Assignment"):
            try:
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                html_path = os.path.join(temp_dir, "uploaded_map.html")
                png_path  = os.path.join(temp_dir, "uploaded_chart.png")
                csv_path  = os.path.join(temp_dir, "uploaded_summary.csv")
                for path, file in [
                    (html_path, uploaded_html),
                    (png_path,  uploaded_png),
                    (csv_path,  uploaded_csv),
                ]:
                    with open(path, "wb") as f:
                        f.write(file.getvalue())

                grade = grade_assignment(code_input, html_path, png_path, csv_path)
                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                    return

                conn = get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET as2 = %s WHERE username = %s",
                    (grade, username),
                )
                conn.commit()
                updated = cur.rowcount
                cur.close()
                conn.close()

                if updated == 0:
                    st.error("No record updated—please check the username.")
                    return

                push_db_to_github(None)
                st.success(f"Your grade for Assignment 2: {grade}/100")
            except Exception as e:
                st.error(f"An error occurred during submission: {e}")
    else:
        st.warning("Please verify your username first.")

if __name__ == "__main__":
    show()
