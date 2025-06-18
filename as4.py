# as4.py  – MySQL edition (no local .db file)
import streamlit as st
import os
import re
from grades.grade4 import grade_assignment
import mysql.connector
from mysql.connector import errorcode

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps call-sites alive after file removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op – data lives in MySQL."""
        return {"success": True}

# ──────────────────────────────────────────────────────────────────────────────
# Singleton cached MySQL connection helper
# ──────────────────────────────────────────────────────────────────────────────
@st.experimental_singleton
def _get_conn():
    """Return a persistent MySQL connection from Streamlit secrets."""
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host       = cfg["host"],
        port       = int(cfg.get("port", 3306)),
        user       = cfg["user"],
        password   = cfg["password"],
        database   = cfg["database"],
        autocommit = False,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Cache username verification to avoid repeat queries
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def username_exists_as4(username: str) -> bool:
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
    exists = cur.fetchone() is not None
    cur.close()
    return exists

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
        try:
            if username_exists_as4(username):
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified_as4"]  = True
                st.session_state["username_as4"]  = username
            else:
                st.error("Invalid username. Please use a registered username.")
                st.session_state["verified_as4"] = False
        except Exception as e:
            st.error(f"Error verifying username: {e}")
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
                <span style="color:#FFD700;"><strong>Set Up Your Environment:</strong></span>
                - Open a new Google Colab notebook.
                - Import the necessary libraries:
                  - `cv2` (OpenCV) for image processing
                  - `numpy` for numerical operations
                  - `matplotlib` for displaying images

                <span style="color:#FFD700;"><strong>Load the Image:</strong></span>
                - Download the provided image and upload it to Google Colab.
                - Load the image using OpenCV.

                <span style="color:#FFD700;"><strong>Convert the Image to Grayscale and Apply Thresholding:</strong></span>
                - Convert the image to grayscale.
                - Use binary thresholding to make it easier to detect the rectangular shapes. This will turn the rectangles into clear white shapes against a black background.

                <span style="color:#FFD700;"><strong>Detect Contours:</strong></span>
                - Use OpenCV’s `findContours` function to detect all contours in the image.
                - Filter out contours that are not rectangular shapes.

                <span style="color:#FFD700;"><strong>Filter and Identify Rectangles:</strong></span>
                - For each contour, approximate its shape using `cv2.approxPolyDP`.
                - If the contour has four points, consider it a rectangle.
                - Calculate the bounding box coordinates of each rectangle using `cv2.boundingRect`.

                <span style="color:#FFD700;"><strong>Extract and Print the Coordinates:</strong></span>
                - For each detected rectangle, print the top-left and bottom-right coordinates.
                - Display the original image with the rectangles outlined for verification.
                """, unsafe_allow_html=True)
                st.image("correct_files/BW.jpg")
        
        with tab2:
            st.markdown("""
            <span style="color:#FFD700;"><strong>Detailed Grading Breakdown:</strong></span>
            1. **Library Imports (20 Points)**
            2. **Code Quality (14 Points)**
            3. **Rectangle Coordinates (56 Points)**
            4. **Thresholded Image (5 Points)**
            5. **Image with Rectangles Outlined (5 Points)**
            """, unsafe_allow_html=True)

        # ─────────────────────────────────────────────
        # Step 3: Submit Your Assignment
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 3: Submit Your Assignment</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;font-weight:bold;'>📝 Paste Your Code Here</p>", unsafe_allow_html=True)
        code_input = st.text_area("", height=300, key="as4_code_input")

        # ─────────────────────────────────────────────
        # Step 4: Enter Rectangle Coordinates
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 4: Enter Rectangle Coordinates</h2>", unsafe_allow_html=True)
        rectangle_coordinates = st.text_area("", height=150, key="as4_rectangle_coordinates")

        # ─────────────────────────────────────────────
        # Step 5: Upload Your Thresholded Image
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 5: Upload Your Thresholded Image</h2>", unsafe_allow_html=True)
        uploaded_thresholded_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_thresholded_image")

        # ─────────────────────────────────────────────
        # Step 6: Upload Image with Rectangles Outlined
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 6: Upload Image with Rectangles Outlined</h2>", unsafe_allow_html=True)
        uploaded_outlined_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_outlined_image")

        if st.button("Submit Assignment", key="as4_submit_button"):
            try:
                # basic file checks
                if not uploaded_thresholded_image:
                    st.error("Please upload a thresholded image file.")
                    return
                if not uploaded_outlined_image:
                    st.error("Please upload an image with rectangles outlined.")
                    return

                # save uploads
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                th_path = os.path.join(temp_dir, "as4_thresholded.png")
                ol_path = os.path.join(temp_dir, "as4_outlined.png")
                with open(th_path, "wb") as f:
                    f.write(uploaded_thresholded_image.getvalue())
                with open(ol_path, "wb") as f:
                    f.write(uploaded_outlined_image.getvalue())

                # Rectangle-coordinate grading (logic unchanged)
                import collections
                correct_vals = [
                    974, 768, 1190, 890, 270, 768, 486, 889, 37, 768, 253, 890,
                    1207, 768, 1423, 890, 740, 768, 955, 890, 505, 768, 720, 890,
                    92, 618, 234, 660, 206, 511, 349, 554, 367, 438, 509, 480,
                    523, 380, 665, 422, 629, 289, 772, 332, 788, 212, 930, 254,
                    37, 136, 471, 298, 1238, 98, 1380, 141
                ]
                student_vals = []
                for line in rectangle_coordinates.splitlines():
                    student_vals += list(map(int, re.findall(r"\d+", line)))
                rec_grade = sum(
                    min(collections.Counter(correct_vals)[v], collections.Counter(student_vals)[v])
                    for v in set(correct_vals)
                )

                # Simple image-existence grades
                th_grade = 5 if uploaded_thresholded_image else 0
                ol_grade = 5 if uploaded_outlined_image else 0

                # Call existing grader
                total_grade, breakdown = grade_assignment(code_input, rec_grade, th_grade, ol_grade)

                if total_grade < 70:
                    st.error(f"You got {total_grade}/100. Please try again.")
                    return

                # store grade in MySQL
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET as4 = %s WHERE username = %s",
                    (total_grade, st.session_state["username_as4"]),
                )
                conn.commit()
                updated = cur.rowcount
                conn.close()

                if updated == 0:
                    st.error("No record updated—please check the username.")
                    return

                # optional GitHub push (no-op)
                push_db_to_github(None)

                st.success(f"Your total grade: {total_grade}/100")
            except Exception as e:
                st.error(f"An error occurred during submission: {e}")
    else:
        st.warning("Please verify your username first.")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":  # pragma: no cover
    show()
