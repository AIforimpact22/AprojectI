import streamlit as st
import sqlite3
from github_sync import push_db_to_github  # Optional: if you use GitHub sync

# Quiz Questions and Points remain unchanged
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

def add_custom_css():
    st.markdown("""
        <style>
        /* Modern container styling with blue shine border and pale orange background */
        .question-container {
            background-color: #FFEFD5; /* Pale orange background */
            border: 2px solid #007BFF; /* Blue border */
            border-radius: 12px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 0 8px #007BFF; /* Blue shine effect */
        }
        
        /* Question text styling */
        .question-text {
            font-size: 1.1em;
            color: #1f1f1f;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        
        /* Custom radio button styling */
        .stRadio > div {
            display: flex;
            gap: 12px;
        }
        
        .stRadio > div > label {
            flex: 1;
            background-color: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 12px 24px;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
            font-weight: 500;
            color: #495057;
            min-width: 120px;
        }
        
        .stRadio > div > label:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        /* Hide default radio button */
        .stRadio input {
            position: absolute;
            opacity: 0;
            cursor: pointer;
        }
        
        /* Selected state styling changed to green */
        .stRadio > div > label[data-checked="true"] {
            background-color: #28a745;
            color: white;
            border-color: #28a745;
        }
        
        /* Remove default streamlit label */
        .stRadio > label {
            display: none !important;
        }
        
        /* Hide default help text icon */
        .stRadio > div > div > span {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

def validate_username(username):
    """
    Validates that the username exists in the records table.
    Returns a tuple (is_valid, quiz_submitted, record) where:
      - is_valid is True if the user exists.
      - quiz_submitted is True if a grade is already recorded for quiz2.
      - record is the database record.
    """
    try:
        db_path = st.secrets["general"]["db_path"]
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT quiz2 FROM records WHERE username = ?", (username,))
        record = cursor.fetchone()
        conn.close()
        if record is None:
            return (False, False, None)
        # If quiz2 is not None, the quiz was already submitted.
        quiz_submitted = record[0] is not None
        return (True, quiz_submitted, record)
    except Exception as e:
        st.error(f"Error validating username: {e}")
        return (False, False, None)

def show():
    add_custom_css()
    
    st.title("Quiz 2: Python and Script Management")
    
    # Step 1: Enter Username with pale blue text
    with st.container():
        st.markdown("<h2 style='color: #ADD8E6;'>Step 1: Enter Your Username</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            username = st.text_input("Username", placeholder="Enter your username")
        with col2:
            verify_button = st.button("Verify Username")
    
    if "validated" not in st.session_state:
        st.session_state["validated"] = False
        
    if verify_button:
        is_valid, quiz_submitted, _ = validate_username(username)
        if is_valid:
            if quiz_submitted:
                st.error("❌ You have already submitted this quiz.")
                st.session_state["validated"] = False
            else:
                st.success("✅ Username validated. You can proceed with the quiz.")
                st.session_state["validated"] = True
                st.session_state["username"] = username
        else:
            st.error("❌ Invalid username. Please use a registered username.")
            st.session_state["validated"] = False

    # Check if user is validated and allowed to take the quiz
    if st.session_state.get("validated", False):
        # Use a separate session key for quiz2 attempts
        if "quiz2_attempts" not in st.session_state:
            st.session_state["quiz2_attempts"] = 0

        # Prevent multiple submissions per session
        if st.session_state["quiz2_attempts"] >= MAX_ATTEMPTS:
            st.error("❌ You have reached the maximum number of attempts for this quiz.")
            return

        # Step 2: Answer Questions with pale blue text
        st.markdown("<h2 style='color: #ADD8E6;'>Step 2: Answer the Questions</h2>", unsafe_allow_html=True)

        if "user_answers_quiz2" not in st.session_state:
            st.session_state["user_answers_quiz2"] = [None] * len(questions)

        # Display quiz questions with improved UI
        for i, question in enumerate(questions):
            with st.container():
                st.markdown(f"""
                    <div class="question-container">
                        <div class="question-text">
                            Q{i+1}: {question['question']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                answer = st.radio(
                    "",  # Empty label
                    options=["True", "False"],
                    key=f"question_quiz2_{i}",
                    horizontal=True,
                    label_visibility="collapsed"
                )
                st.session_state["user_answers_quiz2"][i] = answer == "True"

        # Submit Button with improved styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.button(
                "Submit Quiz",
                type="primary",
                use_container_width=True,
            )

        if submit_button:
            if None in st.session_state["user_answers_quiz2"]:
                st.error("❌ Please answer all questions before submitting.")
                return

            score = sum(
                question["points"]
                for i, question in enumerate(questions)
                if st.session_state["user_answers_quiz2"][i] == question["answer"]
            )

            st.session_state["quiz2_attempts"] += 1
            
            # Display score with progress bar
            st.markdown("### Quiz Results")
            st.progress(score / 100)
            st.success(f"📊 Your score: {score}/100")

            # Update grade in the database (quiz2 column) using the verified username
            db_path = st.secrets["general"]["db_path"]
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE records SET quiz2 = ? WHERE username = ?", (score, st.session_state["username"]))
                conn.commit()
                if cursor.rowcount == 0:
                    st.error("Grade update failed: No matching record found in the database. Please verify your username and database schema.")
                else:
                    st.success("Grade successfully saved.")
                    # Optional: push the updated DB to GitHub
                    push_db_to_github(db_path)
                conn.close()
            except Exception as e:
                st.error(f"Error saving grade: {e}")

if __name__ == "__main__":
    show()
