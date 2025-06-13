import streamlit as st

def show():
    st.header("1.6 Top 10 Things to Know in Google Colab as a Beginner")
    st.write(
        "Google Colab is a beginner-friendly, free platform that allows you to write and run Python code in the cloud. "
        "If you're new to coding or data analysis, here are the top 10 things you should know about Google Colab to get started:"
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>1. Free Access to Powerful Computing</strong></p>', unsafe_allow_html=True)
    st.write(
        "Google Colab provides free access to powerful hardware like GPUs and TPUs, which are essential for tasks like "
        "machine learning and data analysis. You can use these resources without needing expensive hardware."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>2. No Installation Required</strong></p>', unsafe_allow_html=True)
    st.write(
        "With Google Colab, you don’t need to install Python or any software. You can run your code directly in your browser, "
        "making it easy to start coding from anywhere."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>3. Seamless Integration with Google Drive</strong></p>', unsafe_allow_html=True)
    st.write(
        "Colab integrates with Google Drive, so you can save your notebooks (files with .ipynb extensions) directly to your Drive. "
        "This ensures your work is safe, organized, and accessible across devices."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>4. Beginner-Friendly Interface</strong></p>', unsafe_allow_html=True)
    st.write(
        "Colab’s interface is straightforward:\n"
        "- **Code Cells:** Write and run Python code.\n"
        "- **Text Cells:** Add explanations, instructions, or notes using Markdown.\n\n"
        "This mix of code and text makes your projects more readable."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>5. Built-In Libraries</strong></p>', unsafe_allow_html=True)
    st.write(
        "Colab comes pre-installed with popular Python libraries like Pandas, NumPy, and Matplotlib. "
        "You can start analyzing data or creating visualizations without needing to install these libraries manually."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>6. Collaboration Made Easy</strong></p>', unsafe_allow_html=True)
    st.write(
        "Share your Colab notebook with others (just like a Google Doc). Collaborators can view or edit your code in real time, "
        "making it ideal for group projects or peer reviews."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>7. Data Integration</strong></p>', unsafe_allow_html=True)
    st.write(
        "Easily upload datasets or connect directly to Google Sheets, databases, or APIs. "
        "This is perfect for beginners working with small to medium-sized datasets."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>8. Visualization Tools</strong></p>', unsafe_allow_html=True)
    st.write(
        "Colab supports interactive visualizations with libraries like Matplotlib, Plotly, and Seaborn. "
        "You can quickly turn raw data into graphs and charts for better insights."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>9. Simple Debugging</strong></p>', unsafe_allow_html=True)
    st.write(
        "Colab provides error messages that help you debug your code step by step. "
        "It’s a great way to learn how Python works and fix common issues as you practice."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>10. Access to Tutorials and Demos</strong></p>', unsafe_allow_html=True)
    st.write(
        "Explore Colab’s built-in tutorials and code snippets. These resources guide you through common tasks like creating machine learning models or analyzing datasets, "
        "even if you’re just starting out."
    )

    st.markdown('<p style="color: #ADD8E6;"><strong>Bonus Tip: Keep Practicing!</strong></p>', unsafe_allow_html=True)
    st.write(
        "Google Colab is an excellent tool for hands-on learning. Start with small projects, such as analyzing a dataset, creating a simple graph, or automating tasks. "
        "With consistent practice, you’ll become comfortable coding in no time."
    )

