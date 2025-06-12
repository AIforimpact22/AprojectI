

import streamlit as st

def show():
    custom_css = """
    <style>
    h1 {color: #add8e6 !important;}
    .orange-header {color: #FFA500 !important;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Help & Support")
    st.write("If you need assistance, we're here to help. Please check the options below to find a solution to your problem.")

    st.markdown("### How to Get Help:")
    st.markdown("1. **Check the FAQ section below**\n2. **Contact support**")

    # FAQ Section
    st.markdown('<h3 class="orange-header">Frequently Asked Questions (FAQ)</h3>', unsafe_allow_html=True)
    with st.expander("Can I resubmit assignments?"):
        st.write("Yes, you can resubmit assignments until the deadline for the next assignment. After that, resubmissions for previous assignments will no longer be accepted.")
    with st.expander("Can I resubmit quizzes?"):
        st.write("No, quizzes can only be submitted once.")
    with st.expander("What if I forget my password?"):
        st.write("If you forget your password, please email [meermiro299@gmail.com](mailto:meermiro299@gmail.com) to request assistance.")

    # Contact Section
    st.markdown('<h3 class="orange-header">Need More Help?</h3>', unsafe_allow_html=True)
    st.markdown("If you have any further questions or concerns, feel free to reach out to us via email at [meermiro299@gmail.com](mailto:meermiro299@gmail.com)")

if __name__ == "__main__":
    st.set_page_config(page_title="Help & Support", page_icon=":question:", layout="wide")
    show()
