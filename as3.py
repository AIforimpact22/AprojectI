# as3.py  – MySQL edition (no local .db file)
import streamlit as st
import os
from grades.grade3 import grade_assignment
import mysql.connector
from mysql.connector import errorcode

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps old call sites alive after file removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op – data is already in MySQL."""
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
    st.title("Assignment 3: Data Processing and Visualization in Python")

    # inject widget-label CSS (unchanged)
    st.markdown(
        """
        <style>
        .stTextArea label, .stFileUploader label { color: white !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────────
    # Step 1 – username validation
    # ─────────────────────────────────────────────
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username = st.text_input("Enter Your Username", key="as3_username_input")
    if st.button("Verify Username", key="as3_verify_button") and username:
        try:
            conn = _get_conn()
            cur  = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username,))
            exists = cur.fetchone() is not None
            conn.close()

            if exists:
                st.success("Username verified. Proceed to the next steps.")
                st.session_state["verified_as3"]  = True
                st.session_state["username_as3"] = username
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["verified_as3"] = False
        except Exception as e:
            st.error(f"Error verifying username: {e}")
            st.session_state["verified_as3"] = False

    # ─────────────────────────────────────────────
    # Step 2 – assignment & grading details (UI unchanged)
    # ─────────────────────────────────────────────
    if st.session_state.get("verified_as3"):
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>',
            unsafe_allow_html=True,
        )
        tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
        with tab1:
            st.markdown("*(assignment description unchanged)*")
        with st.expander("See More"):
            st.markdown("*(full text unchanged)*")
        with tab2:
            st.markdown("*(grading rubric unchanged)*")

        # ─────────────────────────────────────────
        # Step 3 – code input
        # ─────────────────────────────────────────
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Submit Your Assignment</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as3_code_input")

        # ─────────────────────────────────────────
        # Step 4 – uploads
        # ─────────────────────────────────────────
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 4: Upload Your HTML and Excel Files</h1>',
            unsafe_allow_html=True,
        )
        uploaded_html  = st.file_uploader("Upload your HTML file (Map)",   type=["html"], key="as3_uploaded_html")
        uploaded_excel = st.file_uploader("Upload your Excel file",        type=["xlsx"], key="as3_uploaded_excel")
        all_uploaded = all([uploaded_html, uploaded_excel])
        st.write("All files uploaded:", "✅ Yes" if all_uploaded else "❌ No")

        # ─────────────────────────────────────────
        # Submit button
        # ─────────────────────────────────────────
        if all_uploaded and st.button("Submit Assignment", key="as3_submit_button"):
            try:
                # save uploads to a temp folder
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                html_path  = os.path.join(temp_dir, "uploaded_map.html")
                excel_path = os.path.join(temp_dir, "uploaded_sheet.xlsx")
                for path, file in [(html_path, uploaded_html), (excel_path, uploaded_excel)]:
                    with open(path, "wb") as f:
                        f.write(file.getvalue())

                # grade
                total_grade, breakdown = grade_assignment(code_input, html_path, excel_path)
                if total_grade < 70:
                    st.error(f"You got {total_grade}/100. Please try again.")
                    return

                # record grade in MySQL
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET as3 = %s WHERE username = %s",
                    (total_grade, st.session_state["username_as3"]),
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


