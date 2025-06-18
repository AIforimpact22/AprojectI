# as2.py  – MySQL edition (no local .db file)
import streamlit as st
import os
from grades.grade2 import grade_assignment
import mysql.connector
from mysql.connector import errorcode

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps old code alive even after removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op – all data now lives in MySQL."""
        return {"success": True}

# ──────────────────────────────────────────────────────────────────────────────
# MySQL connection helper
# ──────────────────────────────────────────────────────────────────────────────
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host     = cfg["host"],
        port     = int(cfg.get("port", 3306)),
        user     = cfg["user"],
        password = cfg["password"],
        database = cfg["database"],
        autocommit = False,
    )

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
        try:
            conn = _get_conn()
            cur  = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
            if cur.fetchone():
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified"] = True
            else:
                st.error("Username not found. Please enter a registered username.")
                st.session_state["verified"] = False
            conn.close()
        except Exception as e:
            st.error(f"Error verifying username: {e}")
            st.session_state["verified"] = False

    # ────────────────── STEP 2 – assignment & grading details ──────────────────
    if st.session_state.get("verified", False):
        # Step 2: Assignment and Grading Details
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
                <span style="color:#FFD700;"><strong>Task Requirements</strong></span>
                - <span style="color:#FFD700;"><strong>Fetch Earthquake Data:</strong></span>
                    - Use the USGS Earthquake API to fetch data for the date range **January 2nd, 2025, to January 9th, 2025**.
                    - The API URL is:  
                      https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=YYYY-MM-DD&endtime=YYYY-MM-DD  
                      Replace YYYY-MM-DD with the appropriate dates.
                - <span style="color:#FFD700;"><strong>Filter Data:</strong></span>
                    - Filter the data to include only earthquakes with a magnitude greater than 4.0.
                - <span style="color:#FFD700;"><strong>Map Visualization:</strong></span>
                    - Create an interactive map using folium to show the locations of the filtered earthquakes.
                    - Mark the earthquake locations with markers, using different colors based on their magnitude:
                        - <span style="color:#FFD700;"><strong>Green</strong></span> for magnitude 4.0–5.0  
                        - <span style="color:#FFD700;"><strong>Yellow</strong></span> for magnitude 5.0–5.5  
                        - <span style="color:#FFD700;"><strong>Red</strong></span> for magnitude 5.5+  
                    - Add popups to display additional information about each earthquake (magnitude, location, and time).
                - <span style="color:#FFD700;"><strong>Bar Chart:</strong></span>
                    - Create a bar chart using matplotlib or seaborn to visualize earthquake frequency by magnitude, within the following ranges:
                        - 4.0–4.5  
                        - 4.5–5.0  
                        - 5.0+
                - <span style="color:#FFD700;"><strong>Text Summary:</strong></span>
                    - Generate a CSV file containing:
                        - Total number of earthquakes with magnitude > 4.0.
                        - Average, maximum, and minimum magnitudes (rounded to 2 decimal places).
                        - Number of earthquakes in each magnitude range (4.0–4.5, 4.5–5.0, 5.0+).
                <span style="color:#FFD700;"><strong>Python Libraries You Will Use</strong></span>
                - folium for the map.  
                - matplotlib or seaborn for the bar chart.  
                - requests or urllib for API calls.  
                - pandas for data processing.  
                <span style="color:#FFD700;"><strong>Expected Output</strong></span>
                1. A map showing earthquake locations.  
                2. A bar chart showing earthquake frequency by magnitude.  
                3. A text summary in CSV format.
                """, unsafe_allow_html=True)

        with tab2:
            st.markdown("""
            ### Detailed Grading Breakdown
            """)
            st.markdown("""
            <span style="color:#FFD700;"><strong>1. Library Imports (10 Points)</strong></span>
            - Checks if the required libraries (folium, matplotlib, requests, pandas) are imported.
            """, unsafe_allow_html=True)
            with st.expander("See More"):
                st.markdown("""
                <span style="color:#FFD700;"><strong>2. Code Quality (20 Points)</strong></span>
                - **Variable Naming (5 Points)**: Deducted if non-descriptive variable names are used (e.g., x, y).  
                - **Spacing (5 Points)**: Deducted if improper spacing is found (e.g., no space after =, >, <).  
                - **Comments (5 Points)**: Deducted if no comments are present to explain major steps.  
                - **Code Organization (5 Points)**: Deducted if code blocks are not logically separated with blank lines.  
                <span style="color:#FFD700;"><strong>3. Fetching Data from the API (10 Points)</strong></span>
                - **Correct API URL (5 Points)**: Deducted if the URL is incorrect or the date range is invalid.  
                - **Successful Data Retrieval (5 Points)**: Deducted if the data is not fetched successfully or error handling is missing.  
                <span style="color:#FFD700;"><strong>4. Filtering Earthquakes (10 Points)</strong></span>
                - **Correct Filtering (5 Points)**: Deducted if earthquakes with magnitude ≤ 4.0 are included.  
                - **Data Extraction (5 Points)**: Deducted if relevant data (latitude, longitude, magnitude, time) is not extracted.  
                <span style="color:#FFD700;"><strong>5. Map Visualization (20 Points)</strong></span>
                - **Map Generation (5 Points)**: Deducted if the map is not generated or displayed.  
                - **Color-Coded Markers (9 Points)**: Deducted if markers are not color-coded based on magnitude.  
                - **Popups (6 Points)**: Deducted if popups do not display magnitude, location, and time.  
                <span style="color:#FFD700;"><strong>6. Bar Chart (15 Points)</strong></span>
                - **Chart Generation (5 Points)**: Deducted if the bar chart is not generated or displayed.  
                - **Magnitude Ranges (5 Points)**: Deducted if the magnitude ranges are incorrect.  
                - **Labeling (5 Points)**: Deducted if the chart is not properly labeled.  
                <span style="color:#FFD700;"><strong>7. Text Summary (15 Points)</strong></span>
                - **Total Earthquakes (3 Points)**: Deducted if the total number is incorrect.  
                - **Average Magnitude (3 Points)**: Deducted if not rounded to 2 decimal places.  
                - **Maximum Magnitude (3 Points)**: Deducted if not rounded to 2 decimal places.  
                - **Minimum Magnitude (3 Points)**: Deducted if not rounded to 2 decimal places.  
                - **Magnitude Ranges (3 Points)**: Deducted if the counts per range are incorrect.  
                """, unsafe_allow_html=True)

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
                # save uploads to a temp folder
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

                # grade
                grade = grade_assignment(code_input, html_path, png_path, csv_path)
                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                    return

                # store grade in MySQL
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET as2 = %s WHERE username = %s",
                    (grade, username),
                )
                conn.commit()
                updated = cur.rowcount
                conn.close()

                if updated == 0:
                    st.error("No record updated—please check the username.")
                    return

                # Optional GitHub push (now a no-op)
                push_db_to_github(None)

                st.success(f"Your grade for Assignment 2: {grade}/100")
            except Exception as e:
                st.error(f"An error occurred during submission: {e}")
    else:
        st.warning("Please verify your username first.")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":  # pragma: no cover
    show()
