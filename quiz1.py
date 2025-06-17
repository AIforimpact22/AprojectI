# quiz1.py – MySQL edition (no local .db file) with selectbox answers
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
# Quiz questions
# ──────────────────────────────────────────────────────────────────────────────
questions = [
    {
        "question": "What is the correct way to access a Google Sheet in Google Colab without using an API?",
        "options": [
            "By mounting Google Drive in Colab and accessing the file path directly.",
            "By exporting the Google Sheet as a CSV file and uploading it to Google Colab.",
            "By sharing the Google Sheet link and importing it using a public URL.",
            "By using the gspread library with a service account key."
        ],
        "points": 15,
        "answer": 0  # First option is correct
    },
    # ... (other questions remain the same as before)
    {
        "question": "Your code throws a KeyError when accessing a dictionary. What should you do?",
        "options": [
            "Write an angry email to Guido van Rossum demanding an explanation.",
            "Blame Python for not understanding what you meant.",
            "Take a coffee break and hope the error fixes itself.",
            "Check if the key exists in the dictionary and handle the error appropriately."
        ],
        "points": 10,
        "answer": 3  # Fourth option is correct
    }
]
MAX_ATTEMPTS = 1

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def add_custom_css():
    st.markdown("""<style>
        .question-container {
            background-color: #0E1117;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .question-text {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #FFD700;  /* Yellow-gold color for questions */
        }
        /* Style for selectbox options */
        .stSelectbox > div > div {
            color: white !important;
            background-color: #0E1117 !important;
        }
        .stSelectbox > div > div:hover {
            background-color: #1E293B !important;
        }
        .stSelectbox > div > div[data-baseweb="select"] > div {
            color: white !important;
            background-color: #0E1117 !important;
        }
    </style>""", unsafe_allow_html=True)


def validate_username(username):
    """
    Return (is_valid, quiz_submitted) using MySQL.
    """
    try:
        conn = _get_conn()
        cur  = conn.cursor()
        cur.execute("SELECT quiz1 FROM records WHERE username = %s", (username,))
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
    st.title("Quiz 1: Google Colab and Google Sheets Integration")

    # ─── Step 1: username entry ───────────────────────────────────────────
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("Username", placeholder="Enter your username", key="quiz1_username")
    with col2:
        verify_btn = st.button("Verify Username", key="quiz1_verify")

    if verify_btn:
        ok, already = validate_username(username)
        if not ok:
            st.error("❌ Invalid username. Please use a registered username.")
            st.session_state["validated_q1"] = False
        elif already:
            st.error("❌ You have already submitted this quiz.")
            st.session_state["validated_q1"] = False
        else:
            st.success("✅ Username validated. You can proceed with the quiz.")
            st.session_state["validated_q1"] = True
            st.session_state["username_q1"] = username

    # ─── Step 2: quiz questions ──────────────────────────────────────────
    if st.session_state.get("validated_q1"):
        if "quiz1_attempts" not in st.session_state:
            st.session_state["quiz1_attempts"] = 0
        if st.session_state["quiz1_attempts"] >= MAX_ATTEMPTS:
            st.error("❌ You have reached the maximum number of attempts for this quiz.")
            return

        st.markdown("<h2 style='color:#ADD8E6;'>Step 2: Answer the Questions</h2>", unsafe_allow_html=True)
        st.session_state.setdefault("user_answers_q1", [None] * len(questions))

        for i, q in enumerate(questions):
            st.markdown(
                f"""<div class="question-container">
                       <div class="question-text">Q{i+1}: {q['question']}</div>
                   </div>""",
                unsafe_allow_html=True,
            )
            ans = st.selectbox(
                "Select your answer:",
                options=q["options"],
                key=f"q1_{i}",
                index=None,
                placeholder="Choose an option...",
            )
            if ans is not None:
                st.session_state["user_answers_q1"][i] = q["options"].index(ans)

        # Submit
        if st.button("Submit Quiz", type="primary", use_container_width=True, key="quiz1_submit"):
            if None in st.session_state["user_answers_q1"]:
                st.error("❌ Please answer all questions before submitting.")
                return

            score = sum(
                q["points"]
                for i, q in enumerate(questions)
                if st.session_state["user_answers_q1"][i] == q["answer"]
            )

            st.session_state["quiz1_attempts"] += 1
            st.markdown("### Quiz Results")
            st.progress(score / 100)
            st.success(f"📊 Your score: {score}/100")

            # Store grade in MySQL
            try:
                conn = _get_conn()
                cur  = conn.cursor()
                cur.execute(
                    "UPDATE records SET quiz1 = %s WHERE username = %s",
                    (score, st.session_state["username_q1"]),
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
