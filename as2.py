import streamlit as st
import os
from grades.grade2 import grade_assignment  # keep your existing path
import mysql.connector
from mysql.connector import IntegrityError


# ──────────────────────────────────────────────────────────────────────────────
# DB helper – reads `[mysql]` block in secrets
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
# Main UI                                                                   │
# ──────────────────────────────────────────────────────────────────────────────
def show():
    st.title("Assignment 2: Analyzing Real-Time Earthquake Data")

    # ─────────────────────────
    # Step 1 · Validate Username
    # ─────────────────────────
    st.markdown(
        '<h1 style="color: #ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username = st.text_input("Enter Your Username")
    if st.button("Verify Username") and username:
        try:
            with _get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM records WHERE username = %s", (username,))
                user_exists = cur.fetchone() is not None

            if user_exists:
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified"] = True
            else:
                st.error("Username not found. Please enter a valid registered username.")
                st.session_state["verified"] = False

        except Exception as e:
            st.error(f"An error occurred while verifying username: {e}")
            st.session_state["verified"] = False

    # ─────────────────────────
    # Step 2 · Assignment & Grading Details
    # ─────────────────────────
    if st.session_state.get("verified", False):
        st.markdown(
            '<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>',
            unsafe_allow_html=True,
        )
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

        # (Markdown descriptions remain unchanged) …

        # ─────────────────────────
        # Step 3 · Code Submission
        # ─────────────────────────
        st.markdown(
            '<h1 style="color: #ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("**📝 Paste Your Code Here**", height=300)

        # ─────────────────────────
        # Step 4 · Upload Outputs
        # ─────────────────────────
        st.markdown(
            '<h1 style="color: #ADD8E6;">Step 4: Upload Your Outputs</h1>',
            unsafe_allow_html=True,
        )
        uploaded_html = st.file_uploader("Upload your HTML file (Map)", type=["html"])
        uploaded_png  = st.file_uploader("Upload your PNG file (Bar Chart)", type=["png"])
        uploaded_csv  = st.file_uploader("Upload your CSV file (Summary)", type=["csv"])

        all_uploaded = all([uploaded_html, uploaded_png, uploaded_csv])
        st.write("All files uploaded:", "✅ Yes" if all_uploaded else "❌ No")

        if all_uploaded and st.button("Submit Assignment"):
            try:
                # Save uploads to temp dir
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                html_path = os.path.join(temp_dir, "uploaded_map.html")
                png_path  = os.path.join(temp_dir, "uploaded_chart.png")
                csv_path  = os.path.join(temp_dir, "uploaded_summary.csv")

                with open(html_path, "wb") as f:
                    f.write(uploaded_html.getvalue())
                with open(png_path, "wb") as f:
                    f.write(uploaded_png.getvalue())
                with open(csv_path, "wb") as f:
                    f.write(uploaded_csv.getvalue())

                # Grade
                grade = grade_assignment(code_input, html_path, png_path, csv_path)

                if grade < 70:
                    st.error(f"You got {grade}/100. Please try again.")
                else:
                    st.success(f"Your grade for Assignment 2: {grade}/100")

                    # Update MySQL
                    with _get_conn() as conn:
                        cur = conn.cursor()
                        cur.execute(
                            "UPDATE records SET as2 = %s WHERE username = %s",
                            (grade, username),
                        )
                        conn.commit()

            except Exception as e:
                st.error(f"An error occurred during submission: {e}")
        elif not all_uploaded:
            st.warning("Please upload all required files to proceed.")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    show()
