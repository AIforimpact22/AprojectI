import streamlit as st
import os
import sqlite3
import re  # <--- Added for regex digit extraction
from grades.grade4 import grade_assignment
from github_sync import push_db_to_github  # Used to sync the updated database

def show():
    st.title("Assignment 4: Image Analysis and Rectangle Detection")
    
    # ─────────────────────────────────────────────
    # Step 1: Validate Username (instead of Password)
    # ─────────────────────────────────────────────
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    username = st.text_input("Enter Your Username", key="as4_username_input")
    verify_button = st.button("Verify Username", key="as4_verify_button")
    
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
                st.session_state["verified_as4"] = True
                st.session_state["username_as4"] = username
            else:
                st.error("Invalid username. Please use a registered username.")
                st.session_state["verified_as4"] = False
                
        except Exception as e:
            st.error(f"An error occurred while verifying your username: {e}")
            st.session_state["verified_as4"] = False

    # ─────────────────────────────────────────────
    # Step 2: Review Assignment Details
    # ─────────────────────────────────────────────
    if st.session_state.get("verified_as4", False):
        st.markdown("<h2 style='color:#ADD8E6;'>Step 2: Review Assignment Details</h2>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
        
        with tab1:
            st.markdown("""
            ### Objective:
            In this assignment, you will use Python image processing libraries to analyze a black-and-white image, detect rectangular shapes, and determine the coordinates of each rectangle.
            """)
        with st.expander("See More"):
            st.markdown("""
                #### Instructions:
                1. **Set Up Your Environment:**
                   - Open a new Google Colab notebook.
                   - Import the necessary libraries:
                     - `cv2` (OpenCV) for image processing
                     - `numpy` for numerical operations
                     - `matplotlib` for displaying images

                2. **Load the Image:**
                   - Download the provided image and upload it to Google Colab.
                   - Load the image using OpenCV.

                3. **Convert the Image to Grayscale and Apply Thresholding:**
                   - Convert the image to grayscale.
                   - Use binary thresholding to make it easier to detect the rectangular shapes. This will turn the rectangles into clear white shapes against a black background.

                4. **Detect Contours:**
                   - Use OpenCV’s `findContours` function to detect all contours in the image.
                   - Filter out contours that are not rectangular shapes.

                5. **Filter and Identify Rectangles:**
                   - For each contour, approximate its shape using `cv2.approxPolyDP`.
                   - If the contour has four points, consider it a rectangle.
                   - Calculate the bounding box coordinates of each rectangle using `cv2.boundingRect`.

                6. **Extract and Print the Coordinates:**
                   - For each detected rectangle, print the top-left and bottom-right coordinates.
                   - Display the original image with the rectangles outlined for verification.
                """)
            st.image("correct_files/BW.jpg")  # Local path instead of URL
                            
        with tab2:
            st.markdown("""
            ### Detailed Grading Breakdown:
            1. **Library Imports (20 Points)**
            2. **Code Quality (14 Points)**
            3. **Rectangle Coordinates (56 Points)**
            4. **Thresholded Image (5 Points)**
            5. **Image with Rectangles Outlined (5 Points)
            """)
        
        # ─────────────────────────────────────────────
        # Step 3: Submit Your Assignment
        # ─────────────────────────────────────────────
        st.markdown("<h2 style='color:#ADD8E6;'>Step 3: Submit Your Assignment</h2>", unsafe_allow_html=True)
        
        st.markdown("<p style='color:white; font-weight:bold;'>📝 Paste Your Code Here</p>", unsafe_allow_html=True)
        code_input = st.text_area("", height=300, key="as4_code_input")
        
        st.markdown("<h2 style='color:#ADD8E6;'>Step 4: Enter Rectangle Coordinates</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>Paste Rectangle Coordinates (Top-Left and Bottom-Right) Here</p>", unsafe_allow_html=True)
        rectangle_coordinates = st.text_area("", height=150, key="as4_rectangle_coordinates")
        
        st.markdown("<h2 style='color:#ADD8E6;'>Step 5: Upload Your Thresholded Image</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>Upload your thresholded image file</p>", unsafe_allow_html=True)
        uploaded_thresholded_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_thresholded_image")
        
        st.markdown("<h2 style='color:#ADD8E6;'>Step 6: Upload Image with Rectangles Outlined</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:white;'>Upload your image with rectangles outlined</p>", unsafe_allow_html=True)
        uploaded_outlined_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_outlined_image")
        
        submit_button = st.button("Submit Assignment", key="as4_submit_button")
        
        if submit_button:
            try:
                # Validate required file uploads
                if not uploaded_thresholded_image:
                    st.error("Please upload a thresholded image file.")
                    return
                if not uploaded_outlined_image:
                    st.error("Please upload an image with rectangles outlined.")
                    return
                    
                # Save uploaded files temporarily
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                
                thresholded_image_path = os.path.join(temp_dir, "as4_thresholded_image.png")
                with open(thresholded_image_path, "wb") as f:
                    f.write(uploaded_thresholded_image.getvalue())
                    
                outlined_image_path = os.path.join(temp_dir, "as4_outlined_image.png")
                with open(outlined_image_path, "wb") as f:
                    f.write(uploaded_outlined_image.getvalue())
                    
                # Parse rectangle coordinates using order-independent matching.
                # CHANGED HERE to simply detect all digits in each line.
                try:
                    import collections
                    correct_values = [
                        974, 768, 1190, 890,
                        270, 768, 486, 889,
                        37, 768, 253, 890,
                        1207, 768, 1423, 890,
                        740, 768, 955, 890,
                        505, 768, 720, 890,
                        92, 618, 234, 660,
                        206, 511, 349, 554,
                        367, 438, 509, 480,
                        523, 380, 665, 422,
                        629, 289, 772, 332,
                        788, 212, 930, 254,
                        37, 136, 471, 298,
                        1238, 98, 1380, 141
                    ]
                    
                    # Extract *all* digit sequences from each line
                    student_values = []
                    for line in rectangle_coordinates.splitlines():
                        found_nums = re.findall(r"\d+", line)
                        for num in found_nums:
                            student_values.append(int(num))
                    
                    correct_counter = collections.Counter(correct_values)
                    student_counter = collections.Counter(student_values)
                    
                    # Award 1 point per correct occurrence for each unique number.
                    rectangle_grade = sum(
                        min(correct_counter[num], student_counter.get(num, 0))
                        for num in correct_counter
                    )
                except Exception as e:
                    st.error(f"Invalid input format for rectangle coordinates: {e}")
                    return
                    
                # Grade the thresholded image (5 points for a valid image)
                thresholded_image_grade = 0
                try:
                    from PIL import Image
                    image_obj = Image.open(thresholded_image_path).convert("L")
                    if image_obj:
                        thresholded_image_grade = 5
                except Exception as e:
                    st.error(f"Error processing thresholded image: {e}")
                    
                # Grade the outlined image (5 points if file exists)
                outlined_image_grade = 0
                try:
                    outlined_image_grade = 5
                except Exception as e:
                    st.error(f"Error processing outlined image: {e}")
                    
                # Grade the assignment
                total_grade, grading_breakdown = grade_assignment(
                    code_input,
                    rectangle_grade,
                    thresholded_image_grade,
                    outlined_image_grade
                )
                
                # Display error if total grade is below 70
                if total_grade < 70:
                    st.error(f"You got {total_grade}/100. Please try again.")
                else:
                    st.success(f"Your total grade: {total_grade}/100")
                    
                    # Update the grade in the records table (save in as4 column)
                    db_path = st.secrets["general"]["db_path"]
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    username = st.session_state.get("username_as4", None)
                    if not username:
                        st.error("Username not found in session. Please verify your username again.")
                        return
                    cursor.execute("UPDATE records SET as4 = ? WHERE username = ?", (total_grade, username))
                    conn.commit()
                    conn.close()
                    
                    # Push the updated DB to GitHub
                    push_db_to_github(db_path)
                    
            except Exception as e:
                st.error(f"An error occurred during submission: {e}")

if __name__ == "__main__":
    show()
