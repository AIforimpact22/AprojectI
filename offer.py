import streamlit as st

# Helper function to safely trigger a rerun
def safe_rerun():
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    elif hasattr(st, "rerun"):
        st.rerun()
    else:
        st.error("Streamlit rerun functionality is not available. Please update Streamlit.")

def show():
    # Custom CSS for styling
    st.markdown("""
    <style>
    /* Center the tabs */
    div[role="tablist"] {
        justify-content: center;
    }
    /* Style the tab buttons with pale blue */
    div[role="tablist"] button {
        color: #ADD8E6;
    }
    /* Digital font with soft shining for headers */
    .digital-header {
        font-family: 'Digital-7', sans-serif;
        font-size: 40px;
        text-align: center;
        text-shadow: 0 0 8px rgba(255, 255, 255, 0.8);
        margin: 10px 0;
    }
    /* Style for Course Chapters text */
    .course-chapters {
        color: #FFDAB9;
        font-weight: bold;
    }
    /* Style for Availability text */
    .availability {
        color: #98FB98;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Place the headers at the top of the page
    st.markdown('<div class="digital-header">AI for Impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="digital-header">What We Offer</div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "Course 1: Foundations of Python Programming and Applied Coding",
        "Course 2: Advanced Machine Learning and Real-Time Deployment"
    ])

    # Course 1 Tab
    with tabs[0]:
        st.markdown('<div style="color: #ADD8E6; text-align: center; font-size: 24px;">Course 1: Foundations of Python Programming and Applied Coding</div>', unsafe_allow_html=True)
        st.markdown("""\
Impact: Participants will gain foundational skills in Python programming and learn to create robust scripts, work with APIs, and utilize tools like Google Colab and GitHub. This course enables learners to automate tasks, process data, and build basic web applications.

<span class="course-chapters">Course Chapters:</span>
- Week 1: Introduction to Coding
- Week 2: Generate Comprehensive Codings
- Week 3: Deploy Apps with GitHub and Streamlit
- Week 4: Data Week

📌 <span class="availability">Availability:</span> ✅ Included in Basic, Pro, and VIP Plans
""", unsafe_allow_html=True)
        if st.button("Start Course 1"):
            st.session_state["page"] = "login"
            safe_rerun()  # using the helper function

    # Course 2 Tab
    with tabs[1]:
        st.markdown('<div style="color: #ADD8E6; text-align: center; font-size: 24px;">Course 2: Advanced Machine Learning and Real-Time Deployment</div>', unsafe_allow_html=True)
        st.markdown("""\
Impact: Participants will develop advanced skills in database management, machine learning, and real-time application deployment. This course focuses on practical implementations, enabling learners to create AI-driven solutions, deploy them in real-world scenarios, and integrate apps with cloud and database systems.

<span class="course-chapters">Course Chapters:</span>
- Week 1: Advanced SQL and Databases
- Week 2: Deploy Database
- Week 3: Unsupervised Machine Learning
- Week 4: Supervised Machine Learning
- Week 5: Processing Data in Real-Time for Decision-Making
- Week 6: Capstone Project

📌 <span class="availability">Availability:</span> ✅ Included in Pro and VIP Plans (Not available in Basic Plan)
""", unsafe_allow_html=True)
        if st.button("Start Course 2"):
            st.session_state["page"] = "loginx"
            safe_rerun()  # using the helper function
