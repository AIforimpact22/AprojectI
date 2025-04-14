
import streamlit as st
import sqlite3
from github_sync import push_db_to_github  # Optional: if you use GitHub sync

# Quiz Questions and Answers remain unchanged
questions = [
    {
        "question": "What is the correct way to access a Google Sheet in Google Colab without using an API?",
        "options": [
            "By mounting Google Drive in Colab and accessing the file path directly.",
            "By sharing the Google Sheet link and importing it using a public URL.",
            "By using the gspread library with a service account key.",
            "By exporting the Google Sheet as a CSV file and uploading it to Google Colab"
        ],
        "answer": "By sharing the Google Sheet link and importing it using a public URL."
    },
    {
        "question": "How can ChatGPT be effectively used to assist in Python programming for processing Google Sheets?",
        "options": [
            "ChatGPT automatically integrates with Google Colab to process data.",
            "ChatGPT can write complete working scripts without any user input.",
            "ChatGPT can provide suggestions for improving your code, including optimization and error handling.",
            "ChatGPT replaces the need for learning Python syntax and programming logic."
        ],
        "answer": "ChatGPT can provide suggestions for improving your code, including optimization and error handling."
    },
    {
        "question": "Which of the following steps is required to save processed data back to Google Sheets using the Google Sheets API in Google Colab?",
        "options": [
            "Authenticating Colab with a personal Gmail account using gspread.",
            "Sharing the Google Sheet with a service account email.",
            "Both a and b.",
            "Using pandas to write data directly to the Google Sheet without authentication."
        ],
        "answer": "Both a and b."
    },
    {
        "question": "What is the first step to accessing Google Sheets using the Google Sheets API in Google Colab?",
        "options": [
            "Install the Google Sheets API client library and authenticate with an API key or service account credentials.",
            "Directly import the gspread library without any setup.",
            "Mount Google Drive and access the Google Sheet directly.",
            "Share the Google Sheet link publicly and download the file as a CSV."
        ],
        "answer": "Install the Google Sheets API client library and authenticate with an API key or service account credentials."
    },
    {
        "question": "How can ChatGPT assist in debugging Python code in your Google Colab workflow?",
        "options": [
            "By providing insights into error messages and suggesting corrections or improvements to the code.",
            "By connecting directly to your Colab instance to detect errors.",
            "By automatically fixing errors in real-time as you run the code.",
            "By generating new errors to help understand debugging techniques."
        ],
        "answer": "By providing insights into error messages and suggesting corrections or improvements to the code."
    },
    {
        "question": "What is the main advantage of mounting Google Drive in Google Colab for working with Google Sheets?",
        "options": [
            "It provides real-time synchronization between Google Sheets and Colab.",
            "It automatically processes data in Google Sheets without user intervention.",
            "It eliminates the need for authentication using the Google Sheets API.",
            "It allows direct access to all files stored in Google Drive."
        ],
        "answer": "It provides real-time synchronization between Google Sheets and Colab."
    },
    {
        "question": "Your code throws a KeyError when accessing a dictionary. What should you do?",
        "options": [
            "Blame Python for not understanding what you meant.",
            "Check if the key exists in the dictionary and handle the error appropriately.",
            "Write an angry email to Guido van Rossum demanding an explanation.",
            "Take a coffee break and hope the error fixes itself."
        ],
        "answer": "Check if the key exists in the dictionary and handle the error appropriately."
    }
]

MAX_ATTEMPTS = 1

def add_custom_css():
    st.markdown("""
        <style>
        /* Modern container styling for each question with blue shine border and pale orange background */
        .question-container {
            background-color: #FFF3E0 !important; /* pale orange background */
            border-radius: 12px !important;
            padding: 24px !important;
            margin: 20px 0 !important;
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.5) !important; /* blue shine border effect */
            border: 2px solid #007BFF !important; /* blue border */
        }
        
        .question-text {
            font-size: 1.1em;
            color: #1f1f1f;
            line-height: 1.6;
            margin-bottom: 20px;
            font-weight: 500;
        }
        
        /* Custom radio button styling */
        .stRadio > div {
            gap: 12px;
        }
        
        .stRadio > div > label {
            background-color: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 8px 0;
            transition: all 0.2s ease;
            cursor: pointer;
            font-weight: 400;
            color: #495057;
            width: 100%;
            display: block;
            position: relative;
            padding-right: 50px; /* extra space for the custom indicator */
        }
        
        .stRadio > div > label:hover {
            background-color: #e9ecef;
            transform: translateX(5px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Pseudo-element for custom option indicator */
        .stRadio > div > label::after {
            content: "";
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            width: 20px;
            height: 20px;
            border: 2px solid #e9ecef;
            border-radius: 4px;  /* square with slightly rounded corners */
            transition: all 0.2s ease;
        }
        
        /* Selected state styling for the option and its indicator */
        .stRadio > div > label[data-checked="true"] {
            background-color: #0066cc;
            color: white;
            border-color: #0066cc;
        }
        
        .stRadio > div > label[data-checked="true"]::after {
            content: "✔";
            background-color: #0066cc;
            border-color: #0066cc;
            color: white;
            text-align: center;
            line-height: 20px;
            border-radius: 4px;
        }
        
        /* Progress indicator */
        .progress-indicator {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }
        
        /* Password input container */
        .student-id-container {
            background-color: #ffffff;
            padding: 24px;
            border-radius: 12px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

def validate_password(password):
    try:
        db_path = st.secrets["general"]["db_path"]
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE password = ?", (password,))
        record = cursor.fetchone()
        conn.close()
        return record is not None
    except Exception as e:
        st.error(f"Error validating password: {e}")
        return False

def show():
    add_custom_css()
    
    st.title("Quiz 1: Python and Google Sheets")
    
    # Step 1: Enter Password
    with st.container():
        st.markdown('<h2 style="color: #ADD8E6;">Step 1: Enter Your Password</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            password = st.text_input("Password", placeholder="Enter your password", type="password")
        with col2:
            verify_button = st.button("Verify Password", type="primary", use_container_width=True)

    if "attempts" not in st.session_state:
        st.session_state["attempts"] = 0

    if verify_button:
        if validate_password(password):
            st.success("✅ Password validated. You can proceed with the quiz.")
            st.session_state["validated"] = True
        else:
            st.error("❌ Invalid password. Please ensure your password is registered.")
            st.session_state["validated"] = False

    if st.session_state.get("validated", False):
        st.markdown('<h2 style="color: #ADD8E6;">Step 2: Answer the Questions</h2>', unsafe_allow_html=True)

        if "user_answers" not in st.session_state:
            st.session_state["user_answers"] = [None] * len(questions)

        # Progress indicator
        answered_questions = sum(1 for answer in st.session_state["user_answers"] if answer is not None)
        st.markdown(f"""
            <div class="progress-indicator">
                Questions answered: {answered_questions}/{len(questions)}
            </div>
        """, unsafe_allow_html=True)

        # Quiz questions with improved UI
        for i, question in enumerate(questions):
            with st.container():
                st.markdown(f"""
                    <div class="question-container">
                        <div class="question-text">
                            Q{i+1}: {question['question']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Radio buttons for options without pre-selection
                answer = st.radio(
                    "",  # Empty label
                    options=question["options"],
                    key=f"question_{i}",
                    label_visibility="collapsed",
                    index=None  # Ensures no option is pre-selected
                )
                
                if answer:
                    st.session_state["user_answers"][i] = answer

        # Submit Button with improved styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.button(
                "Submit Quiz",
                type="primary",
                use_container_width=True,
                disabled=None in st.session_state["user_answers"]  # Disable if not all answered
            )

        if submit_button:
            if st.session_state["attempts"] >= MAX_ATTEMPTS:
                st.error("❌ You have reached the maximum number of attempts for this quiz.")
                return

            # Calculate Score
            score = sum(
                1 for i, question in enumerate(questions)
                if st.session_state["user_answers"][i] == question["answer"]
            )

            st.session_state["attempts"] += 1
            total_score = (score / len(questions)) * 100
            
            # Display score with progress bar
            st.markdown("### Quiz Results")
            st.progress(total_score/100)
            st.success(f"📊 Your score: {total_score:.1f}/100")

            # Update grade in the database (quiz1 column)
            db_path = st.secrets["general"]["db_path"]
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE records SET quiz1 = ? WHERE password = ?", (total_score, password))
                conn.commit()
                conn.close()
                st.success("Grade successfully saved.")
                # Optional: push the updated DB to GitHub
                push_db_to_github(db_path)
            except Exception as e:
                st.error(f"Error saving grade: {e}")

if __name__ == "__main__":
    show()
