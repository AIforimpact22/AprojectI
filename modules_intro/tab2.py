import streamlit as st

def show():
    st.markdown("<h1 style='color: gold;'>Course Instructions</h1>", unsafe_allow_html=True)
    st.markdown("""
    This course is designed to span **5 weeks**, structured to provide you with a comprehensive learning and hands-on experience:

    * **Weeks 1–3:** Focus on learning foundational concepts and developing your Python skills through tutorials, assignments, and guided exercises.
    * **Weeks 4–5:** Dedicated to working on your personalized project, applying what you've learned to create a meaningful and impactful application.

    <h2 style='color: #FFD3A3;'>Weekly Structure</h2>
    1. Each week begins with a video tutorial that introduces the core concepts.
    
    2. Follow up with related materials, assignments, and discussions to deepen your understanding.

    <h2 style='color: #FFD3A3;'>Online Sessions:</h2>
    * To schedule one-on-one sessions, stay in contact with the instructor for organizing a convenient time.
    
    * These sessions are designed to address your queries, provide feedback, and guide you through challenges.

    <h2 style='color: #FFD3A3;'>Assignment Submission:</h2>
    Submit assignments promptly and ensure all required files and links are included.
    
    * **For Google Colab projects**, ensure they are **set to public** so your peers and the instructor can access and review them.
    """, unsafe_allow_html=True)
