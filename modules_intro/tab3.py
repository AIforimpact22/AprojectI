import streamlit as st

def show():
    st.markdown(
        "<h1 style='color: #FFD700;'>Stay Connected: Join Our Discord Server!</h1>", 
        unsafe_allow_html=True
    )
    
    st.markdown(
        "<div style='color: #ADD8E6; font-weight: bold; font-size: 24px;'>Why Join Our Discord Server?</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    **Enhance your learning experience by joining our Discord server**, a dedicated space for collaboration, support, and community engagement.

    * **Stay Updated:** Get instant updates about the course, assignments, and materials.
    * **Connect with Peers:** Engage with fellow learners, ask questions, and share your progress.
    * **Exclusive Opportunities:** Be the first to know about new projects, learning resources, and events.
    * **Direct Support:** Reach out for help from the instructor or peers in real-time.

    Discord is a powerful platform for building an active learning community. It's simple to use and ensures you're always in the loop.

    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='color: #ADD8E6; font-weight: bold; font-size: 24px;'>Join Now</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    Become part of the conversation today! 

    **Discord Invite Link:** [Click to Join](https://discord.gg/JnybQncM)
    """, unsafe_allow_html=True)
