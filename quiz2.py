# quiz2.py  – MySQL edition (no local .db file)
import streamlit as st
import mysql.connector
from mysql.connector import errorcode

# ──────────────────────────────────────────────────────────────────────────────
# Optional GitHub-push stub (keeps call-sites alive after file removal)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from github_sync import push_db_to_github        # noqa: F401
except ModuleNotFoundError:
    def push_db_to_github(*_args, **_kwargs):        # noqa: D401
        """No-op – data already lives in MySQL."""
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
# Quiz questions (unchanged)
# ──────────────────────────────────────────────────────────────────────────────
questions = [
    {
        "question": "Splitting a script into multiple smaller scripts helps make the code more manageable and easier to debug.",
        "points": 35,
        "answer": True,
    },
    {
        "question": "The main.py script is responsible for importing and executing functions or modules stored in other scripts saved on Google Drive.",
        "points": 35,
        "answer": True,
    },
    {
        "question": "Saving smaller scripts in Google Drive and importing them into Google Colab increases the risk of altering the main script when making changes.",
        "points": 30,
        "answer": False,
    },
]
MAX_ATTEMPTS = 1

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def add_custom_css():
    st.markdown("""<style>
        /* (CSS block unchanged) */
    </style>""", unsafe_allow_html=True)


def validate_username(username):
    """
    Return (is_valid, quiz_submitted) using MySQL.
    """
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("SELECT quiz2 FROM records WHERE username = %s", (username,))
        row = cur.fetchone()
        conn.close()
        if row is None:
            return False, False
        return True, row[0] is not None
    except Exception as e:
        st.error(f"Error validating username: {e}")
        return False, False

# ──────────────────────────────────────────────────────────────────────────────
# MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    add_custom_css()
    st.title("Quiz 2: Python and Script Management")

    # ─── Step 1: username entry ───────────────────────────────────────────
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("Username", placeholder="Enter your username")
    with col2:
        verify_btn = st.button("Verify Username")

    if verify_btn:
        ok, already = validate_username(username)
        if not ok:
            st.error("❌ Invalid username. Please use a registered username.")
            st.session_state["validated_q2"] = False
        elif already:
            st.error("❌ You have already submitted this quiz.")
            st.session_state["validated_q2"] = False
        else:
            st.success("✅ Username validated. You can proceed with the quiz.")
            st.session_state["validated_q2"] = True
            st.session_state["username_q2"]  = username

    # ─── Step 2: quiz questions ──────────────────────────────────────────
    if st.session_state.get("validated_q2"):
        if "quiz2_attempts" not in st.session_state:
            st.session_state["quiz2_attempts"] = 0
        if st.session_state["quiz2_attempts"] >= MAX_ATTEMPTS:
            st.error("❌ You have reached the maximum number of attempts for this quiz.")
            return

        st.markdown("<h2 style='color:#ADD8E6;'>Step 2: Answer the Questions</h2>", unsafe_allow_html=True)
        st.session_state.setdefault("user_answers_q2", [None] * len(questions))

        for i, q in enumerate(questions):
            st.markdown(
                f"""<div class="question-container">
                       <div class="question-text">Q{i+1}: {q['question']}</div>
                   </div>""",
                unsafe_allow_html=True,
            )
            ans = st.radio(
                "", ["True", "False"],
                key=f"q2_{i}", horizontal=True, label_visibility="collapsed"
            )
            st.session_state["user_answers_q2"][i] = (ans == "True")

        # Submit
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            if None in st.session_state["user_answers_q2"]:
                st.error("❌ Please answer all questions before submitting.")
                return

            score = sum(
                q["points"]
                for i, q in enumerate(questions)
                if st.session_state["user_answers_q2"][i] == q["answer"]
            )

            st.session_state["quiz2_attempts"] += 1
            st.markdown("### Quiz Results")
            st.progress(score / 100)
            st.success(f"📊 Your score: {score}/100")

            # Store grade in MySQL
            try:
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET quiz2 = %s WHERE username = %s",
                    (score, st.session_state["username_q2"]),
                )
                conn.commit()
                rows = cur.rowcount
                conn.close()

                if rows == 0:
                    st.error("Grade update failed – user not found.")
                else:
                    st.success("Grade successfully saved.")
                    push_db_to_github(None)   # now a no-op
            except Exception as e:
                st.error(f"Error saving grade: {e}")

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":  # pragma: no cover
    show()
