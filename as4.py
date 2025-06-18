# as4.py  – MySQL edition (no local .db file)

import streamlit as st
import os
import re
from grades.grade4 import grade_assignment
import mysql.connector
from mysql.connector import pooling

# ──────────────────────────────────────────────────────────────────────────────
# Initialize a MySQL connection pool once per session
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_conn_pool():
    cfg = st.secrets["mysql"]
    return pooling.MySQLConnectionPool(
        pool_name="mypool_as4",
        pool_size=5,
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )

def get_conn():
    """Get a fresh connection from the pool."""
    return init_conn_pool().get_connection()


# ──────────────────────────────────────────────────────────────────────────────
# Cache username verification to avoid repeated DB hits
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def username_exists_as4(username: str) -> bool:
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps call-sites alive after file removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github  # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*args, **kwargs):
        return {"success": True}


# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    st.title("Assignment 4: Image Analysis and Rectangle Detection")

    # ─────────────────────────────────────────────
    # Step 1 – username validation
    # ─────────────────────────────────────────────
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    username = st.text_input("Enter Your Username", key="as4_username_input")
    if st.button("Verify Username", key="as4_verify_button") and username:
        if username_exists_as4(username):
            st.success("Username verified. Proceed to the next steps.")
            st.session_state["verified_as4"]  = True
            st.session_state["username_as4"] = username
        else:
            st.error("Invalid username. Please use a registered username.")
            st.session_state["verified_as4"] = False

    # ─────────────────────────────────────────────
    # Step 2: Review Assignment Details & Grading
    # ─────────────────────────────────────────────
    if st.session_state.get("verified_as4", False):
        st.markdown("<h2 style='color:#ADD8E6;'>Step 2: Review Assignment Details</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
        
        with tab1:
            st.markdown("""
            <span style="color:#FFD700;"><strong>Objective:</strong></span>
            In this assignment, you will use Python image processing libraries to analyze a black-and-white image, detect rectangular shapes, and determine the coordinates of each rectangle.
            """, unsafe_allow_html=True)
            with st.expander("See More"):
                st.markdown("""
                **Set Up Your Environment:**
                - Open a new Google Colab notebook.
                - Import `cv2`, `numpy`, and `matplotlib`.

                **Load and Threshold:**
                - Load the provided image with OpenCV.
                - Convert to grayscale and apply binary thresholding.

                **Contour Detection:**
                - Use `cv2.findContours`, filter for 4-point contours via `cv2.approxPolyDP`.
                - Compute bounding boxes with `cv2.boundingRect`.

                **Extract Coordinates:**
                - Print top-left and bottom-right coords for each rectangle.
                - Display the image with rectangles outlined for verification.
                """, unsafe_allow_html=True)
                st.image("correct_files/BW.jpg")
        
        with tab2:
            st.markdown("""
            **Detailed Grading Breakdown:**
            1. Library Imports (20 pts)  
            2. Code Quality (14 pts)  
            3. Rectangle Coordinates (56 pts)  
            4. Thresholded Image (5 pts)  
            5. Outlined Image (5 pts)
            """, unsafe_allow_html=True)

        # ─────────────────────────────────────────────
        # Step 3: Submit Your Assignment
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 3: Submit Your Assignment</h2>", unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as4_code_input")

        # ─────────────────────────────────────────────
        # Step 4: Enter Rectangle Coordinates
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 4: Enter Rectangle Coordinates</h2>", unsafe_allow_html=True)
        rectangle_coordinates = st.text_area("", height=150, key="as4_rectangle_coordinates")

        # ─────────────────────────────────────────────
        # Step 5: Upload Your Thresholded Image
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 5: Upload Your Thresholded Image</h2>", unsafe_allow_html=True)
        uploaded_thresholded = st.file_uploader("", type=["png","jpg","jpeg"], key="as4_thresholded_image")

        # ─────────────────────────────────────────────
        # Step 6: Upload Outlined Image
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 6: Upload Image with Rectangles Outlined</h2>", unsafe_allow_html=True)
        uploaded_outlined = st.file_uploader("", type=["png","jpg","jpeg"], key="as4_outlined_image")

        if st.button("Submit Assignment", key="as4_submit_button"):
            # Validate files
            if not uploaded_thresholded:
                st.error("Please upload a thresholded image.")
                return
            if not uploaded_outlined:
                st.error("Please upload the outlined image.")
                return

            # Save uploads
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            th_path = os.path.join(temp_dir, "th.png")
            ol_path = os.path.join(temp_dir, "ol.png")
            with open(th_path, "wb") as f: f.write(uploaded_thresholded.getvalue())
            with open(ol_path, "wb") as f: f.write(uploaded_outlined.getvalue())

            # Grade coordinates
            import collections
            correct_vals = [974,768,1190,890,270,768,486,889,37,768,253,890,
                            1207,768,1423,890,740,768,955,890,505,768,720,890,
                            92,618,234,660,206,511,349,554,367,438,509,480,
                            523,380,665,422,629,289,772,332,788,212,930,254,
                            37,136,471,298,1238,98,1380,141]
            student_vals = []
            for line in rectangle_coordinates.splitlines():
                student_vals += list(map(int, re.findall(r"\d+", line)))
            rec_grade = sum(min(collections.Counter(correct_vals)[v],
                                collections.Counter(student_vals)[v])
                            for v in set(correct_vals))

            th_grade = 5 if uploaded_thresholded else 0
            ol_grade = 5 if uploaded_outlined else 0

            # Call grader
            total_grade, breakdown = grade_assignment(code_input, rec_grade, th_grade, ol_grade)
            if total_grade < 70:
                st.error(f"You got {total_grade}/100. Please try again.")
                return

            # Update DB
            conn = get_conn()
            cur  = conn.cursor()
            cur.execute("UPDATE records SET as4 = %s WHERE username = %s",
                        (total_grade, st.session_state["username_as4"]))
            conn.commit()
            updated = cur.rowcount
            cur.close()
            conn.close()

            if updated == 0:
                st.error("No record updated—please check the username.")
                return

            push_db_to_github()
            st.success(f"Your total grade: {total_grade}/100")

    else:
        st.warning("Please verify your username first.")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    show()
