import streamlit as st
import mysql.connector

# ──────────────────────────────────────────────────────────────────────────────
# DB helper – reads [mysql] block from secrets.toml
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
# Quiz content
# ──────────────────────────────────────────────────────────────────────────────
questions = [
    {
        "question": "Splitting a script into multiple smaller scripts helps make the code more manageable and easier to debug.",
        "points": 35,
        "answer": True
    },
    {
        "question": "The main.py script is responsible for importing and executing functions or modules stored in other scripts saved on Google Drive.",
        "points": 35,
        "answer": True
    },
    {
        "question": "Saving smaller scripts in Google Drive and importing them into Google Colab increases the risk of altering the main script when making changes.",
        "points": 30,
        "answer": False
    }
]

MAX_ATTEMPTS = 1

# ──────────────────────────────────────────────────────────────────────────────
# UI helpers
# ──────────────────────────────────────────────────────────────────────────────
def add_custom_css():
    st.markdown(
        """
        <style>
        .question-container{background-color:#FFEFD5;border:2px solid #007BFF;
            border-radius:12px;padding:24px;margin:16px 0;box-shadow:0 0 8px #007BFF;}
        .question-text{font-size:1.1em;color:#1f1f1f;line-height:1.5;margin-bottom:20px;}
        .stRadio>div{display:flex;gap:12px;}
        .stRadio>div>label{flex:1;background-color:#f8f9fa;border:2px solid #e9ecef;
            border-radius:8px;padding:12px 24px;text-align:center;transition:all .2s ease;
            cursor:pointer;font-weight:500;color:#495057;min-width:120px;}
        .stRadio>div>label:hover{background-color:#e9ecef;transform:translateY(-2px);
            box-shadow:0 4px 6px rgba(0,0,0,.05);}
        .stRadio input{position:absolute;opacity:0;cursor:pointer;}
        .stRadio>div>label[data-checked="true"]{background-color:#28a745;color:#fff;border-color:#28a745;}
        .stRadio>label{display:none!important;}
        .stRadio>div>div>span{display:none!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Validation & DB helpers
# ──────────────────────────────────────────────────────────────────────────────
def validate_username(username: str):
    """
    Check if the username exists and whether quiz2 was already submitted.
    Returns (is_valid, quiz_already_submitted).
    """
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT quiz2 FROM records WHERE username = %s", (username,))
            row = cur.fetchone()
        if row is None:
            return False, False
        return True, row[0] is not None
    except Exception as e:
        st.error(f"Error validating username: {e}")
        return False, False

def save_score(username: str, score: int):
    """
    Update quiz2 score for the given username.
    """
    try:
        with _get_conn() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE records SET quiz2 = %s WHERE username = %s", (score, username))
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        st.error(f"Error saving grade: {e}")
        return False

# ──────────────────────────────────────────────────────────────────────────────
# Main UI
# ──────────────────────────────────────────────────────────────────────────────
def show():
    add_custom_css()
    st.title("Quiz 2: Python and Script Management")

    # Step 1 · username
    st.markdown("<h2 style='color:#ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        username = st.text_input("Username", placeholder="Enter your username")
    with col2:
        verify = st.button("Verify Username")

    if verify:
        valid, submitted = validate_username(username)
        if not valid:
            st.error("❌ Invalid username. Please use a registered username.")
            st.session_state["validated_q2"] = False
        elif submitted:
            st.error("❌ You have already submitted this quiz.")
            st.session_state["validated_q2"] = False
        else:
            st.success("✅ Username validated. You can proceed with the quiz.")
            st.session_state["validated_q2"] = True
            st.session_state["username_q2"] = username

    # Ensure state keys exist
    st.session_state.setdefault("quiz2_attempts", 0)
    st.session_state.setdefault("user_answers_q2", [None] * len(questions))

    # Step 2 · questions
    if st.session_state.get("validated_q2", False):
        if st.session_state["quiz2_attempts"] >= MAX_ATTEMPTS:
            st.error("❌ You have reached the maximum number of attempts for this quiz.")
            return

        st.markdown("<h2 style='color:#ADD8E6;'>Step 2: Answer the Questions</h2>", unsafe_allow_html=True)
        for i, q in enumerate(questions):
            with st.container():
                st.markdown(
                    f"<div class='question-container'><div class='question-text'>Q{i+1}: {q['question']}</div></div>",
                    unsafe_allow_html=True,
                )
                ans = st.radio(
                    "",
                    options=["True", "False"],
                    key=f"quiz2_q{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
                st.session_state["user_answers_q2"][i] = ans == "True"

        # Submit
        col_mid = st.columns([1, 2, 1])[1]
        with col_mid:
            if st.button("Submit Quiz", use_container_width=True):
                if None in st.session_state["user_answers_q2"]:
                    st.error("❌ Please answer all questions before submitting.")
                    return

                score = sum(
                    q["points"] for i, q in enumerate(questions)
                    if st.session_state["user_answers_q2"][i] == q["answer"]
                )

                # Increment attempts
                st.session_state["quiz2_attempts"] += 1

                # Show result
                st.markdown("### Quiz Results")
                st.progress(score / 100)
                st.success(f"📊 Your score: {score}/100")

                # Save to DB
                if save_score(st.session_state["username_q2"], score):
                    st.success("Grade successfully saved.")
                else:
                    st.error("Grade update failed—please check username or database.")

if __name__ == "__main__":
    show()
