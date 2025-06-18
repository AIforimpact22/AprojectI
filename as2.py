# as2.py  – MySQL edition (no local .db file)
import streamlit as st
import os
from grades.grade2 import grade_assignment
import mysql.connector
from mysql.connector import errorcode

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps old code paths alive even after removal)
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

    # ────────────────── STEP 2 – assignment details (unchanged) ──────────────────
    if st.session_state.get("verified"):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
            unsafe_allow_html=True,
        )
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
        with tab1:
            st.markdown("*(assignment text unchanged)*")
            with st.expander("See More"):
                st.markdown("*(full task description unchanged)*")
        with tab2:
            st.markdown("*(grading rubric unchanged)*")
            with st.expander("See More"):
                st.markdown("*(full rubric unchanged)*")

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
