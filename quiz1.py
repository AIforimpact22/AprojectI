# quiz1.py – MySQL edition (no local .db file)
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
    {
        "question": "How can ChatGPT be effectively used to assist in Python programming for processing Google Sheets?",
        "options": [
            "ChatGPT automatically integrates with Google Colab to process data.",
            "ChatGPT can provide suggestions for improving your code, including optimization and error handling.",
            "ChatGPT replaces the need for learning Python syntax and programming logic.",
            "ChatGPT can write complete working scripts without any user input."
        ],
        "points": 15,
        "answer": 1  # Second option is correct
    },
    {
        "question": "Which of the following steps is required to save processed data back to Google Sheets using the Google Sheets API in Google Colab?",
        "options": [
            "Sharing the Google Sheet with a service account email.",
            "Authenticating Colab with a personal Gmail account using gspread.",
            "Using pandas to write data directly to the Google Sheet without authentication.",
            "Both a and b."
        ],
        "points": 15,
        "answer": 3  # Fourth option is correct
    },
    {
        "question": "What is the first step to accessing Google Sheets using the Google Sheets API in Google Colab?",
        "options": [
            "Install the Google Sheets API client library and authenticate with an API key or service account credentials.",
            "Directly import the gspread library without any setup.",
            "Mount Google Drive and access the Google Sheet directly.",
            "Share the Google Sheet link publicly and download the file as a CSV."
        ],
        "points": 15,
        "answer": 0  # First option is correct
    },
    {
        "question": "How can ChatGPT assist in debugging Python code in your Google Colab workflow?",
        "options": [
            "By generating new errors to help understand debugging techniques.",
            "By connecting directly to your Colab instance to detect errors.",
            "By automatically fixing errors in real-time as you run the code.",
            "By providing insights into error messages and suggesting corrections or improvements to the code."
        ],
        "points": 15,
        "answer": 3  # Fourth option is correct
    },
    {
        "question": "What is the main advantage of mounting Google Drive in Google Colab for working with Google Sheets?",
        "options": [
            "It automatically processes data in Google Sheets without user intervention.",
            "It eliminates the need for authentication using the Google Sheets API.",
            "It allows direct access to all files stored in Google Drive.",
            "It provides real-time synchronization between Google Sheets and Colab."
        ],
        "points": 15,
        "answer": 2  # Third option is correct
    },
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
            color: #FAFAFA;
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
            ans = st.radio(
                "", q["options"],
                key=f"q1_{i}", index=None, label_visibility="collapsed"
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
