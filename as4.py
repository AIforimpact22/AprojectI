import streamlit as st
import os
import re
import collections
import mysql.connector
from mysql.connector import IntegrityError


# ──────────────────────────────────────────────────────────────────────────────
# DB helper – pulls creds from [mysql] in secrets.toml
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
    st.title("Assignment 4: Image Analysis and Rectangle Detection")

    # ─────────────────────────────────────────────
    # Step 1 · Validate Username
    # ─────────────────────────────────────────────
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    username = st.text_input("Enter Your Username", key="as4_username_input")
    if st.button("Verify Username", key="as4_verify_button") and username:
        try:
            with _get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM records WHERE username = %s", (username,))
                user_exists = cur.fetchone() is not None

            if user_exists:
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
    # Step 2 · Review Assignment Details
    # (Markdown content unchanged)
    # ─────────────────────────────────────────────
    if st.session_state.get("verified_as4", False):
        # … full assignment & grading markdown unchanged for brevity …
        st.image("correct_files/BW.jpg")

        # ─────────────────────────────────────────────
        # Step 3 to 6 · Submit code, coordinates, and images
        # ─────────────────────────────────────────────
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as4_code_input")

        st.markdown("<h2 style='color:#ADD8E6;'>Step 4: Enter Rectangle Coordinates</h2>", unsafe_allow_html=True)
        rectangle_coordinates = st.text_area("", height=150, key="as4_rectangle_coordinates")

        st.markdown("<h2 style='color:#ADD8E6;'>Step 5: Upload Your Thresholded Image</h2>", unsafe_allow_html=True)
        uploaded_thresholded_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_thresholded_image")

        st.markdown("<h2 style='color:#ADD8E6;'>Step 6: Upload Image with Rectangles Outlined</h2>", unsafe_allow_html=True)
        uploaded_outlined_image = st.file_uploader("", type=["png", "jpg", "jpeg"], key="as4_outlined_image")

        if st.button("Submit Assignment", key="as4_submit_button"):
            try:
                # Validate uploads
                if not uploaded_thresholded_image:
                    st.error("Please upload a thresholded image file.")
                    return
                if not uploaded_outlined_image:
                    st.error("Please upload an image with rectangles outlined.")
                    return

                # Save uploads
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                thr_path = os.path.join(temp_dir, "as4_thresholded_image.png")
                out_path = os.path.join(temp_dir, "as4_outlined_image.png")
                with open(thr_path, "wb") as f: f.write(uploaded_thresholded_image.getvalue())
                with open(out_path, "wb") as f: f.write(uploaded_outlined_image.getvalue())

                # Parse rectangle coordinates (order-independent digit match)
                correct_vals = [
                    974, 768, 1190, 890, 270, 768, 486, 889, 37, 768, 253, 890,
                    1207, 768, 1423, 890, 740, 768, 955, 890, 505, 768, 720, 890,
                    92, 618, 234, 660, 206, 511, 349, 554, 367, 438, 509, 480,
                    523, 380, 665, 422, 629, 289, 772, 332, 788, 212, 930, 254,
                    37, 136, 471, 298, 1238, 98, 1380, 141
                ]
                student_vals = []
                for ln in rectangle_coordinates.splitlines():
                    student_vals.extend([int(x) for x in re.findall(r"\d+", ln)])

                c_counter = collections.Counter(correct_vals)
                s_counter = collections.Counter(student_vals)
                rectangle_grade = sum(min(c_counter[n], s_counter.get(n, 0)) for n in c_counter)

                # Simple 5-point grade if thresholded image loads
                threshold_grade = 0
                try:
                    from PIL import Image
                    Image.open(thr_path).convert("L")
                    threshold_grade = 5
                except Exception:
                    pass

                # 5 points just for having an outlined image
                outlined_grade = 5

                # Grade assignment
                total_grade, breakdown = grade_assignment(
                    code_input,
                    rectangle_grade,
                    threshold_grade,
                    outlined_grade,
                )

                if total_grade < 70:
                    st.error(f"You got {total_grade}/100. Please try again.")
                    return

                # Update DB
                uname = st.session_state.get("username_as4")
                if not uname:
                    st.error("Username missing—please verify again.")
                    return

                with _get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("UPDATE records SET as4 = %s WHERE username = %s", (total_grade, uname))
                    conn.commit()
                    updated = cur.rowcount

                if updated:
                    st.success(f"Your total grade: {total_grade}/100")
                else:
                    st.error("No record updated—please check username or database integrity.")

            except Exception as e:
                st.error(f"An error occurred during submission: {e}")


if __name__ == "__main__":
    show()
