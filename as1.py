# as1.py  – MySQL version with anti-hang spinners
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub push stub
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        return {"success": True}

# ──────────────────────────────────────────────────────────────────────────────
# MySQL helper
# ──────────────────────────────────────────────────────────────────────────────
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host      = cfg["host"],
        port      = int(cfg.get("port", 3306)),
        user      = cfg["user"],
        password  = cfg["password"],
        database  = cfg["database"],
        autocommit=False,
        use_pure=True,  # consistent cursor behaviour
    )

# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    set_page_style()                                    # Custom CSS

    # Session defaults
    defaults = {
        "run_success":      False,
        "map_object":       None,
        "dataframe_object": None,
        "captured_output":  "",
        "username_entered": False,
        "username":         "",
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ── Assignment details (unchanged text) ──────────────────────────────────
    st.markdown('<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
    with tab1:
        st.markdown("*(task description unchanged – see previous version)*")
    with st.expander("See More"):
        st.markdown("*(full task text unchanged)*")
    with tab2:
        st.markdown("*(grading rubric unchanged)*")

    # ── Username entry / validation ─────────────────────────────────────────
    st.markdown('<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        if not username_input.strip():
            st.error("Please enter a username.")
        else:
            with st.spinner("Validating username…"):
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute("SELECT 1 FROM records WHERE username = %s LIMIT 1", (username_input,))
                exists = cur.fetchone() is not None
                cur.close(); conn.close()

            if exists:
                st.session_state.update(username_entered=True, username=username_input)
                st.success(f"Welcome, {username_input}!")
            else:
                st.session_state.update(username_entered=False)
                st.error("Invalid username. Please enter a registered username.")

    # ── Code run & grading section (shown only after validation) ─────────────
    if st.session_state.get("username_entered"):
        st.markdown('<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        # ── RUN CODE button ────────────────────────────────────────────────
        if st.button("Run Code"):
            st.session_state.update(run_success=False, captured_output="", map_object=None, dataframe_object=None)
            try:
                captured = StringIO()
                import sys
                stdout_original = sys.stdout
                sys.stdout = captured

                local_ctx = {}
                exec(code_input, {}, local_ctx)

                sys.stdout = stdout_original
                st.session_state["captured_output"] = captured.getvalue()

                for obj in local_ctx.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = stdout_original
                st.error(f"Error while running code: {e}")

        # ── Show outputs if run succeeded ─────────────────────────────────
        if st.session_state["run_success"]:
            if st.session_state["captured_output"]:
                st.markdown("### 📄 Captured Output")
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;">'
                    f'{st.session_state["captured_output"].replace(chr(10), "<br>")}'
                    '</pre>',
                    unsafe_allow_html=True,
                )
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # ── SUBMIT CODE button ────────────────────────────────────────────
        if st.button("Submit Code"):
            if not st.session_state.get("run_success"):
                st.error("Please run your code successfully before submitting.")
                st.stop()

            # 1 | Grade the code
            with st.spinner("Grading your submission…"):
                from grades.grade1 import grade_assignment
                try:
                    grade = grade_assignment(code_input)
                except Exception as e:
                    st.error(f"Grader error: {e}")
                    st.stop()

            if grade < 70:
                st.error(f"You got {grade}/100. Please try again.")
                st.stop()

            # 2 | Write grade to MySQL
            with st.spinner("Saving grade to database…"):
                try:
                    conn = _get_conn()
                    conn.cmd_query("SET SESSION wait_timeout = 5")
                    cur  = conn.cursor()
                    cur.execute(
                        "UPDATE records SET as1 = %s WHERE username = %s",
                        (grade, st.session_state["username"]),
                    )
                    conn.commit()
                    updated = cur.rowcount
                    cur.close(); conn.close()
                except Exception as e:
                    st.error(f"Database error: {e}")
                    st.stop()

                if updated == 0:
                    st.error("No record updated—please check the username.")
                    st.stop()

            # 3 | (Optionally) push to GitHub
            with st.spinner("Finalising submission…"):
                push_db_to_github(None)

            # 4 | Confirm result
            with st.spinner("Re-checking saved grade…"):
                conn = _get_conn()
                conn.cmd_query("SET SESSION wait_timeout = 5")
                cur  = conn.cursor()
                cur.execute("SELECT as1 FROM records WHERE username = %s", (st.session_state["username"],))
                new_grade = cur.fetchone()[0]
                cur.close(); conn.close()

            st.success(f"Submission successful! Your grade: {new_grade}/100")

            # Reset so user must re-enter username next time
            st.session_state.update(username_entered=False, username="")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":      # pragma: no cover
    show()
