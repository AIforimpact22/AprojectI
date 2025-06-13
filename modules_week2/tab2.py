import streamlit as st

def show():
    st.header("2.1 Breaking Down Long Scripts and Using Google Drive with Google Colab")
    st.subheader("Purpose:")
    st.write(
        "Splitting long scripts into smaller, modular scripts improves code readability, reusability, and debugging efficiency. "
        "Google Drive acts as cloud storage for these scripts, making them accessible across devices and enabling integration with Google Colab for seamless execution."
    )
    st.video("https://youtu.be/d79b7IFY6dM")
    st.image("https://github.com/Hakari-Bibani/AprojectI/blob/main/workflow.png")
    st.subheader("Steps:")
    st.markdown(
        """
**<span style="color: #ADD8E6;">Break Down the Script:</span>**
- Identify distinct functionalities within the script (e.g., data processing, plotting, utilities).
- Save each functionality as a separate Python file (.py) with a clear, descriptive name.
**<span style="color: #ADD8E6;">Store in Google Drive:</span>**
- Create a folder in Google Drive to store these smaller scripts.
- Organize the scripts into folders if needed (e.g., utilities, visualizations).
**<span style="color: #ADD8E6;">Mount Google Drive in Colab:</span>**
- Mount Google Drive to access files directly from Colab.
- Append the script directory to the Python system path so the scripts can be imported as modules.
**<span style="color: #ADD8E6;">Use Scripts in Colab:</span>**
- Import the required scripts in Colab using Python's import statement.
- Reload any updated scripts dynamically without restarting the notebook.
**<span style="color: red;">Benefits:</span>**
- **Modularity:** Easier to manage, test, and debug smaller scripts.
- **Reusability:** Individual scripts can be reused across multiple projects.
- **Cloud Access:** Store scripts in Google Drive for persistent and cross-device availability.
- **Collaboration:** Allows multiple contributors to work on different parts of the code simultaneously.
- **Efficiency:** Faster updates and testing of specific functionalities without running the entire script.
        """,
        unsafe_allow_html=True
    )
