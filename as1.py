# as1.py – MySQL version (no local .db file required)
import streamlit as st
import folium
import pandas as pd
from geopy.distance import geodesic
from io import StringIO
from streamlit_folium import st_folium
from utils.style1 import set_page_style
import mysql.connector
from mysql.connector import errorcode

# --------------------------------------------------------------------------- #
# Optional GitHub-push stub (keeps old code paths alive without changing them)
# --------------------------------------------------------------------------- #
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op stub – DB already lives in MySQL, nothing to push."""
        return {"success": True}

# --------------------------------------------------------------------------- #
# DB helper – centralise MySQL connection
# --------------------------------------------------------------------------- #
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

# --------------------------------------------------------------------------- #
# MAIN UI
# --------------------------------------------------------------------------- #
def show():
    set_page_style()

    for key, default in {
        "run_success":      False,
        "map_object":       None,
        "dataframe_object": None,
        "captured_output":  "",
        "username_entered": False,
        "username":         "",
    }.items():
        st.session_state.setdefault(key, default)

    st.title("Assignment 1: Mapping Coordinates and Calculating Distances")

    # ————————————————————————————— Tabs for details —————————————————————————————
    st.markdown('<h1 style="color: #ADD8E6;">Step 2: Review Assignment Details</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Assignment Details", "Grading Details"])
    # (… your existing markdown here …)

    # ————————————————————————————— Username entry —————————————————————————————
    st.markdown(
        '<h1 style="color:#ADD8E6;">Step 1: Enter Your Username</h1>',
        unsafe_allow_html=True,
    )
    username_input = st.text_input("Username", key="as1_username")
    if st.button("Enter", key="enter_user"):
        if not username_input:
            st.error("Please enter a username.")
        else:
            try:
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM records WHERE username = %s LIMIT 1",
                    (username_input,),
                )
                exists = cur.fetchone() is not None
            except Exception as e:
                st.error(f"Error checking username: {e}")
                exists = False
            finally:
                conn.close()
            if exists:
                st.session_state["username_entered"] = True
                st.session_state["username"]         = username_input
                st.success(f"Welcome, {username_input}!")
            else:
                st.error("Invalid username. Please enter a registered username.")
                st.session_state["username_entered"] = False

    # ————————————————————————————— Code execution & grading —————————————————————————————
    if st.session_state["username_entered"]:
        st.markdown(
            '<h1 style="color:#ADD8E6;">Step 3: Run and Submit Your Code</h1>',
            unsafe_allow_html=True,
        )
        code_input = st.text_area("📝 Paste Your Code Here", height=300, key="as1_code")

        # Run Code button
        if st.button("Run Code", key="run_code"):
            st.session_state.update(
                run_success=False,
                captured_output="",
                map_object=None,
                dataframe_object=None,
            )
            try:
                captured = StringIO()
                import sys
                old_stdout = sys.stdout
                sys.stdout = captured

                local_ctx = {}
                exec(code_input, {}, local_ctx)

                sys.stdout = old_stdout
                st.session_state["captured_output"] = captured.getvalue()

                # detect folium.Map or DataFrame
                for obj in local_ctx.values():
                    if isinstance(obj, folium.Map):
                        st.session_state["map_object"] = obj
                    elif isinstance(obj, pd.DataFrame):
                        st.session_state["dataframe_object"] = obj

                st.session_state["run_success"] = True
                st.success("✅ Code ran successfully!")
            except Exception as e:
                sys.stdout = old_stdout
                st.error(f"Error while running code: {e}")

        # show outputs if run succeeded
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

            # —————————————————————— Submit Code button ——————————————————————
            if st.button("Submit Code", key="submit_code"):
                # 1. Grade the code
                from grades.grade1 import grade_assignment
                grade = grade_assignment(code_input)
                st.write(f"**Calculated Grade:** {grade}/100")

                if grade < 70:
                    st.error(f"You got {grade}/100. Please revise and try again.")
                else:
                    # 2. Update the database
                    try:
                        conn = _get_conn()
                        cur  = conn.cursor()
                        cur.execute(
                            "UPDATE records SET as1 = %s WHERE username = %s",
                            (grade, st.session_state["username"]),
                        )
                        conn.commit()
                        if cur.rowcount == 0:
                            st.error("⚠️ No record updated—please check the username.")
                        else:
                            # 3. Optional GitHub push
                            push_db_to_github()

                            # 4. Fetch back to confirm
                            cur.execute(
                                "SELECT as1 FROM records WHERE username = %s",
                                (st.session_state["username"],),
                            )
                            new_grade = cur.fetchone()[0]
                            st.success(f"🎉 Submission successful! Your grade: {new_grade}/100")
                            # reset for next time
                            st.session_state["username_entered"] = False
                            st.session_state["username"] = ""
                    except Exception as e:
                        st.error(f"Database error: {e}")
                    finally:
                        conn.close()

if __name__ == "__main__":
    show()
