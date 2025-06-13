import streamlit as st

def show():
    st.markdown(
        '<h1 style="color: #FFFFE0;">3.3 Building Interactive Data Apps with GitHub & Streamlit</h1>',
        unsafe_allow_html=True
    )
    st.markdown("### Presentation:")
    st.components.v1.html(
        """
        <iframe src="https://docs.google.com/presentation/d/1hqwNOAJWPXzT94nmALxz6pXYNtKB6c6EzBPsijJw8RY/embed?start=false&loop=false&delayms=3000" 
        frameborder="0" width="960" height="569" allowfullscreen="true" mozallowfullscreen="true" webkitallowfullscreen="true"></iframe>
        """,
        height=569,
    )

