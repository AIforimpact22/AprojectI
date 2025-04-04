import streamlit as st

def show():
    st.header("2.3 Scale up your scripts Recorded Session")
    st.video("https://youtu.be/55VfpKxvp7s")
    st.markdown("### Presentation:")
    st.components.v1.html(
        """
        <iframe src="https://docs.google.com/presentation/d/1iOFdiLq3Wgpvnz1cjh_sEMSUZ68fngOCa5ShWFLA1OA/embed?start=false&loop=false&delayms=3000" 
        frameborder="0" width="800" height="600" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
        """,
        height=600,
    )
