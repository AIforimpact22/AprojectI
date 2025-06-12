
import streamlit as st
import os
from grades.grade2 import grade_assignment  # ensure this path is correct in your project
import sqlite3
from github_sync import push_db_to_github  # Assuming this is used to sync the database

def show():
    st.title("Assignment 2: Analyzing Real-Time Earthquake Data")

    # Step 1: Validate Username
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username = st.text_input("Enter Your Username")
    verify_button = st.button("Verify Username")

    if verify_button and username:
        try:
            db_path = st.secrets["general"]["db_path"]
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Check if the username exists in the records table
            cursor.execute("SELECT * FROM records WHERE username = ?", (username,))
            user_record = cursor.fetchone()

            if user_record:
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified"] = True
            else:
                st.error("Username not found. Please enter a valid registered username.")
                st.session_state["verified"] = False

            conn.close()

        except Exception as e:
            st.error(f"An error occurred while verifying username: {e}")
            st.session_state["verified"] = False

    if st.session_state.get("verified", False):
        # Step 2: Assignment and Grading Details
        st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

        with tab1:
            st.markdown("""
            ### Objective
            In this assignment, you will write a Python script that fetches real-time earthquake data from the USGS Earthquake API, processes the data to filter earthquakes with a magnitude greater than 4.0, and plots the earthquake locations on a map. Additionally, you will calculate the number of earthquakes in different magnitude ranges and present the results visually.
            """)
            # Add "See More" expandable section
            with st.expander("See More"):
                st.markdown("""
            ### Task Requirements
            - **Fetch Earthquake Data**:
                - Use the USGS Earthquake API to fetch data for the date range **January 2nd, 2025, to January 9th, 2025**.
                - The API URL is:  
                  https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=YYYY-MM-DD&endtime=YYYY-MM-DD.  
                  Replace YYYY-MM-DD with the appropriate dates.
            - **Filter Data**:
                - Filter the data to include only earthquakes with a magnitude greater than 4.0.
            - **Map Visualization**:
                - Create an interactive map using folium to show the locations of the filtered earthquakes.
                - Mark the earthquake locations with markers, using different colors based on their magnitude:
                    - **Green** for magnitude 4.0-5.0
                    - **Yellow** for magnitude 5.0-5.5
                    - **Red** for magnitude 5.5+
                - Add popups to display additional information about each earthquake (magnitude, location, and time).
            - **Bar Chart**:
                - Create a bar chart using matplotlib or seaborn to visualize earthquake frequency by magnitude, within the following ranges:
                    - 4.0-4.5
                    - 4.5-5.0
                    - 5.0+
            - **Text Summary**:
                - Generate a CSV file containing:
                    - Total number of earthquakes with magnitude > 4.0.
                    - Average, maximum, and minimum magnitudes (rounded to 2 decimal places).
                    - Number of earthquakes in each magnitude range (4.0-4.5, 4.5-5.0, 5.0+).
            ### Python Libraries You Will Use
            - folium for the map.
            - matplotlib or seaborn for the bar chart.
            - requests or urllib for API calls.
            - pandas for data processing.
            ### Expected Output
            1. A map showing earthquake locations.
            2. A bar chart showing earthquake frequency by magnitude.
            3. A text summary in CSV format.
            """)
        with tab2:
            st.markdown("""
            ### Detailed Grading Breakdown
            #### 1. Library Imports (10 Points)
            - Checks if the required libraries (folium, matplotlib, requests, pandas) are imported.
            """)
            # Add "See More" expandable section
            with st.expander("See More"):
                st.markdown("""
            #### 2. Code Quality (20 Points)
            - **Variable Naming (5 Points)**:
                - Deducted if non-descriptive variable names are used (e.g., x, y).
            - **Spacing (5 Points)**:
                - Deducted if improper spacing is found (e.g., no space after =, >, <).
            - **Comments (5 Points)**:
                - Deducted if no comments are present to explain major steps.
            - **Code Organization (5 Points)**:
                - Deducted if code blocks are not logically separated with blank lines.
            #### 3. Fetching Data from the API (10 Points)
            - **Correct API URL (5 Points)**:
                - Deducted if the URL is incorrect or the date range is invalid.
            - **Successful Data Retrieval (5 Points)**:
                - Deducted if the data is not fetched successfully or error handling is missing.
            #### 4. Filtering Earthquakes (10 Points)
            - **Correct Filtering (5 Points)**:
                - Deducted if earthquakes with magnitude ≤ 4.0 are included.
            - **Data Extraction (5 Points)**:
                - Deducted if relevant data (latitude, longitude, magnitude, time) is not extracted.
            #### 5. Map Visualization (20 Points)
            - **Map Generation (5 Points)**:
                - Deducted if the map is not generated or displayed.
            - **Color-Coded Markers (9 Points)**:
                - Deducted if markers are not color-coded based on magnitude:
                    - Green for 4.0-5.0: 3 points
                    - Yellow for 5.0-5.5: 3 points
                    - Red for 5.5+: 3 points
            - **Popups (6 Points)**:
                - Deducted if popups do not display:
                    - Magnitude: 2 points
                    - Latitude and Longitude: 2 points
                    - Time in readable format: 2 points
            #### 6. Bar Chart (15 Points)
            - **Chart Generation (5 Points)**:
                - Deducted if the bar chart is not generated or displayed.
            - **Magnitude Ranges (5 Points)**:
                - Deducted if the magnitude ranges are incorrect:
                    - 4.0-4.5
                    - 4.5-5.0
                    - 5.0+
            - **Labeling (5 Points)**:
                - Deducted if the chart is not properly labeled (title, x-axis, y-axis).
            #### 7. Text Summary (15 Points)
            - **Total Earthquakes (3 Points)**:
                - Deducted if the total number of earthquakes with magnitude > 4.0 is incorrect.
            - **Average Magnitude (3 Points)**:
                - Deducted if the average magnitude is not rounded to 2 decimal places.
            - **Maximum Magnitude (3 Points)**:
                - Deducted if the maximum magnitude is not rounded to 2 decimal places.
            - **Minimum Magnitude (3 Points)**:
                - Deducted if the minimum magnitude is not rounded to 2 decimal places.
            - **Magnitude Ranges (3 Points)**:
                - Deducted if the number of earthquakes in each range is incorrect:
                    - 4.0-4.5
                    - 4.5-5.0
                    - 5.0+
            """)
        
        # Step 3: Code Submission and Output
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("**📝 Paste Your Code Here**", height=300)

        # Step 4: Upload Files
        st.markdown('<h1 style="color: #ADD8E6;">Step 4: Upload Your Outputs</h1>', unsafe_allow_html=True)
        uploaded_html = st.file_uploader("Upload your HTML file (Map)", type=["html"])
        uploaded_png = st.file_uploader("Upload your PNG file (Bar Chart)", type=["png"])
        uploaded_csv = st.file_uploader("Upload your CSV file (Summary)", type=["csv"])

        all_uploaded = all([uploaded_html, uploaded_png, uploaded_csv])
        st.write("All files uploaded:", "✅ Yes" if all_uploaded else "❌ No")

        if all_uploaded:
            submit_button = st.button("Submit Assignment")

            if submit_button:
                try:
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    html_path = os.path.join(temp_dir, "uploaded_map.html")
                    png_path = os.path.join(temp_dir, "uploaded_chart.png")
                    csv_path = os.path.join(temp_dir, "uploaded_summary.csv")

                    with open(html_path, "wb") as f:
                        f.write(uploaded_html.getvalue())
                    with open(png_path, "wb") as f:
                        f.write(uploaded_png.getvalue())
                    with open(csv_path, "wb") as f:
                        f.write(uploaded_csv.getvalue())

                    # Grade the assignment
                    grade = grade_assignment(code_input, html_path, png_path, csv_path)

                    # Check if the grade is less than 70
                    if grade < 70:
                        st.error(f"You got {grade}/100. Please try again.")
                    else:
                        st.success(f"Your grade for Assignment 2: {grade}/100")

                        # Update the grade in the records table for this username (in as2 column)
                        db_path = st.secrets["general"]["db_path"]
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE records SET as2 = ? WHERE username = ?", (grade, username))
                        conn.commit()
                        conn.close()

                        # Push the updated DB to GitHub
                        push_db_to_github(db_path)

                except Exception as e:
                    st.error(f"An error occurred during submission: {e}")

        else:
            st.warning("Please upload all required files to proceed.")

if __name__ == "__main__":
    show()
