# as1.py – MySQL version (no local .db file required)
# --------------------------------------------------------------------------- #
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector

# ─────────────────────────────────────────────────────────────────────────────
# Optional GitHub push stub (keeps legacy call-sites alive)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github          # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):          # noqa: D401
        """No-op – data already lives in MySQL."""
        return {"success": True}

# ─────────────────────────────────────────────────────────────────────────────
# DB helper
# ─────────────────────────────────────────────────────────────────────────────
def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host      = cfg["host"],
        port      = int(cfg.get("port", 3306)),
        user      = cfg["user"],
        password  = cfg["password"],
        database  = cfg["database"],
        use_pure  = True,      # ensures consistent cursor behaviour
    )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────────────────────
def show():
    # Apply custom styling
    set_page_style()

    # ------------------------------------------------------------
    # Session defaults
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # Step 2 – Assignment details (always visible)
    # ------------------------------------------------------------
    st.markdown('<h1 style="color:#ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])

    with tab1:
        st.markdown("""
        ### Objective
        In this assignment you’ll plot three coordinates on a map and
        calculate the distance between each pair.
        """)
    with st.expander("See More"):
        st.markdown("*(full task description unchanged)*")
    with tab2:
        st.markdown("*(grading rubric unchanged)*")

    # ------------------------------------------------------------
    # Step 1 – Username entry / validation
    # ------------------------------------------------------------
    st.markdown('<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>', unsafe_allow_html=True)
    username_in = st.text_input("Username", key="as1_username")
    if st.button("Enter"):
        if not username_in:
            st.error("Please enter a username.")
        else:
            with _get_conn() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM records WHERE username = %s", (username_in,))
                exists = cur.fetchone() is not None
            if exists:
                st.session_state["username_entered"] = True
                st.session_state["username"] = username_in
                st.success(f"Welcome, {username_in}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False

    # ------------------------------------------------------------
    # Step 3 – Run code, review outputs, submit
    # ------------------------------------------------------------
    if st.session_state.get("username_entered"):
        st.markdown('<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>', unsafe_allow_html=True)
        code_input = st.text_area("📝 Paste Your Code Here", height=300)

        # -------- Run code ---------------------------------------------------
        if st.button("Run Code"):
            st.session_state.update(
                run_success=False,
                captured_output="",
                map_object=None,
                dataframe_object=None,
            )
            try:
                captured = StringIO()
                import sys
                sys_stdout_orig = sys.stdout
                sys.stdout = captured

                local_ctx = {}
                exec(code_input, {}, local_ctx)

                sys.stdout = sys_stdout_orig
                st.session_state["captured_output"] = captured.getvalue()

                # Detect map / dataframe
                for obj in local_ctx.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
            except Exception as e:
                sys.stdout = sys_stdout_orig
                st.error(f"Error while running code: {e}")

        # -------- Show results ----------------------------------------------
        if st.session_state["run_success"]:
            if st.session_state["captured_output"]:
                st.markdown("### 📄 Captured Output")
                st.markdown(
                    f'<pre style="color:white;white-space:pre-wrap;">'
                    f'{st.session_state["captured_output"].replace(chr(10), "<br>")}'
                    "</pre>",
                    unsafe_allow_html=True,
                )
            if st.session_state["map_object"]:
                st.markdown("### 🗺️ Map Output")
                st_folium(st.session_state["map_object"], width=1000, height=500)
            if st.session_state["dataframe_object"] is not None:
                st.markdown("### 📊 DataFrame Output")
                st.dataframe(st.session_state["dataframe_object"])

        # -------- Submit code -----------------------------------------------
        if st.button("Submit Code"):
            if not st.session_state["run_success"]:
                st.error("Please run your code successfully before submitting.")
                return

            # 1 – grade
            from grades.grade1 import grade_assignment
            grade = grade_assignment(code_input)
            if grade < 70:
                st.error(f"You got {grade}/100. Please try again.")
                return

            # 2 – save grade
            try:
                conn = _get_conn()
                conn.autocommit = True
                cur = conn.cursor(buffered=True)
                cur.execute(
                    "UPDATE records SET as1 = %s WHERE username = %s",
                    (grade, st.session_state["username"]),
                )
                if cur.rowcount == 0:
                    st.error("No record updated — username not found.")
                    conn.close()
                    return
                st.toast("✅ Grade saved", icon="🎉")
            except mysql.connector.Error as e:
                st.error(f"MySQL error while saving grade: {e.msg}")
                return
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

            # 3 – confirm
            try:
                with _get_conn() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT as1 FROM records WHERE username = %s", (st.session_state["username"],))
                    new_grade = cur.fetchone()[0]
                st.success(f"Submission successful! Your grade: {new_grade}/100")
            except Exception as e:
                st.error(f"MySQL error while retrieving grade: {e}")

            # 4 – optional GitHub push (no-op)
            push_db_to_github(None)

            # reset
            st.session_state["username_entered"] = False
            st.session_state["username"] = ""

# --------------------------------------------------------------------------- #
if __name__ == "__main__":        # pragma: no cover
    show()
