import streamlit as st
import os
from grades.grade3 import grade_assignment
import sqlite3
from github_sync import push_db_to_github  # Assuming this is used to sync the database

def show():
    st.title("Assignment 3: Data Processing and Visualization in Python")
    
    # Inject CSS to style widget labels
    st.markdown(
        """
        <style>
        .stTextArea label, .stFileUploader label {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # ─────────────────────────────────────────────
    # Step 1: Validate Username
    # ─────────────────────────────────────────────
    st.markdown('<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username = st.text_input("Enter Your Username", key="as3_username_input")
    verify_button = st.button("Verify Username", key="as3_verify_button")
    
    if verify_button and username:
        try:
            db_path = st.secrets["general"]["db_path"]
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM records WHERE username = ?", (username,))
            user_record = cursor.fetchone()
            conn.close()

            if user_record:
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified_as3"] = True
                st.session_state["username_as3"] = username
            else:
                st.error("Invalid username. Please enter a valid, registered username.")
                st.session_state["verified_as3"] = False

        except Exception as e:
            st.error(f"An error occurred while verifying the username: {e}")
            st.session_state["verified_as3"] = False

    # ─────────────────────────────────────────────
    # Step 2: Review Assignment Details
    # ─────────────────────────────────────────────
    if st.session_state.get("verified_as3", False):
        st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
        
        with tab1:
            st.markdown("""
            ### Objective:
            In this assignment, students will work with geographical temperature data and apply Python programming to perform data manipulation and visualization. The task is broken into three stages, with each stage encapsulating a specific function. By the end of the assignment, students will merge the functions into one script to complete the task efficiently.
            """)
        with st.expander("See More"):
            st.markdown("""
        ### Stage 1: Filtering Data Below 25°C
        **Goal:** Create a new tab in the spreadsheet containing only the data points where the temperature is below 25°C.

        **Instructions:**
        - Load the provided Excel file containing longitude, latitude, and temperature data.
        - Write a Python script that filters out all the rows where the temperature is below 25°C.
        - Save this filtered data in a new sheet within the same Excel file, naming the new sheet "Below_25".

        **Deliverable:** A script that filters and saves the data in the "Below_25" tab of the Excel file.

        **File:** [Temperature Data](https://docs.google.com/spreadsheets/d/1EA4iram3ngYgTIuoKHCciKj1KBxpUqG1CwkyW71wUYU/edit?gid=1798066675#gid=1798066675)


        ### Stage 2: Filtering Data Above 25°C
        **Goal:** Create another tab in the spreadsheet containing only the data points where the temperature is above 25°C.

        **Instructions:**
        - Extend your script to filter out all the rows where the temperature is above 25°C.
        - Save this filtered data in a new sheet named "Above_25".

        **Deliverable:** A script that adds the "Above_25" tab to the Excel file.


        ### Stage 3: Visualizing Data on a Map
        **Goal:** Visualize the data points from both the "Below_25" and "Above_25" tabs on a geographical map.

        **Instructions:**
        - Using a Python mapping library (such as folium, matplotlib, or plotly), plot the data points from both the "Below_25" and "Above_25" tabs.
        - Use blue to represent the data points from the "Below_25" tab and red for the "Above_25" tab.
        - Ensure the map accurately displays the temperature data at the correct coordinates.

        **Deliverable:** A Python script that generates a map displaying the data points in blue and red.


        ### Final Task: Merging the Scripts
        **Goal:** Combine all three stages into one cohesive Python script that performs the filtering and visualization tasks in sequence.

        **Instructions:**
        - Encapsulate the functionality of the three scripts (Stage 1, Stage 2, and Stage 3) into distinct functions.
        - Write a master function that calls these functions in sequence:
            1. Filter the data below 25°C and save it to a new tab.
            2. Filter the data above 25°C and save it to another tab.
            3. Visualize both sets of data on a map.
        - Ensure that the final script runs all the steps seamlessly.

        **Deliverable:** A Python script that completes the entire task, from filtering the data to visualizing it on a map.
        """)
        
        with tab2:
            st.markdown("""
        ### Detailed Grading Breakdown:
        #### 1. Code Grading (40 Points Total)
        - **Library Imports (15 Points)**
        - **Code Quality (10 Points)**
        - **Sheet Creation (15 Points)**
        - Should create "Below_25" tab.
        - Should create "Above_25" tab.
    
        #### 2. HTML File Grading (20 Points Total)
    
        #### 3. Excel File Grading (40 Points Total)
        - **Correct Sheets (15 Points):**
        - The Excel file should have three sheets: "Sheet1", "Above_25", and "Below_25".
        - **Correct Columns (15 Points):**
        - Must include ("longitude", "latitude", "temperature").
        - **Row Count for "Above_25" (10 Points)**
        """)

        
        # ─────────────────────────────────────────────
        # Step 3: Submit Your Assignment
        # ─────────────────────────────────────────────
        st.markdown('<h1 style="color: #ADD8E6;">Step 3: Submit Your Assignment</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as3_code_input")
        
        st.markdown('<h1 style="color: #ADD8E6;">Step 4: Upload Your HTML and Excel Files</h1>', unsafe_allow_html=True)
        uploaded_html = st.file_uploader("Upload your HTML file (Map)", type=["html"], key="as3_uploaded_html")
        uploaded_excel = st.file_uploader("Upload your Excel file", type=["xlsx"], key="as3_uploaded_excel")
        all_uploaded = all([uploaded_html, uploaded_excel])
        # Removed key argument from st.write
        st.write("All files uploaded:", "✅ Yes" if all_uploaded else "❌ No")
        
        if all_uploaded:
            submit_button = st.button("Submit Assignment", key="as3_submit_button")
            if submit_button:
                try:
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    html_path = os.path.join(temp_dir, "uploaded_map.html")
                    excel_path = os.path.join(temp_dir, "uploaded_sheet.xlsx")
                    
                    with open(html_path, "wb") as f:
                        f.write(uploaded_html.getvalue())
                    with open(excel_path, "wb") as f:
                        f.write(uploaded_excel.getvalue())
                    
                    total_grade, grading_breakdown = grade_assignment(code_input, html_path, excel_path)
                    
                    if total_grade < 70:
                        st.error(f"You got {total_grade}/100. Please try again.")
                    else:
                        st.success(f"Your total grade: {total_grade}/100")
                        db_path = st.secrets["general"]["db_path"]
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        username = st.session_state.get("username_as3", None)
                        if not username:
                            st.error("Username not found in session. Please verify your username again.")
                            return
                        cursor.execute("UPDATE records SET as3 = ? WHERE username = ?", (total_grade, username))
                        conn.commit()
                        conn.close()
                        push_db_to_github(db_path)
                        
                except Exception as e:
                    st.error(f"An error occurred during submission: {e}")
        else:
            st.warning("Please upload all required files to proceed.")
            
if __name__ == "__main__":
    show()
