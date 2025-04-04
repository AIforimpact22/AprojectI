import streamlit as st

def show():
    st.markdown(
        "<h2 style='color: #98FB98;'>Assignment: Submission of Draft Version for Your Personalized Project</h2>",
        unsafe_allow_html=True
    )
    st.subheader("Objective:")
    st.write(
        "The purpose of this assignment is to submit the first draft of your personalized project. "
        "This draft should include the core functionality and outline the project's purpose, impact, and operational concept. "
        "It’s a chance to receive feedback that will guide you in refining and expanding the project in future weeks."
    )
    st.markdown(
        """
**<span style="color: #ADD8E6;">Submission Requirements:</span>**

- **<span style="color: #FFA07A;">Project Repository on GitHub:</span>**  
  - **Link to Repository:** Create a GitHub repository dedicated to your project. Ensure that the repository is publicly accessible or shared with the instructor for review.
  - **Repository Structure:**  
    - Include a `README.md` file that provides a brief introduction to the project and explains its purpose and main functionalities.  
    - Organize folders such as:
      - `src/`: Core scripts
      - `data/`: Any necessary datasets (if applicable)
      - `docs/`: Additional documentation (if needed)

**<span style="color: #ADD8E6;">Project Concept Summary:</span>**

- **Project Description:** Provide a 2-3 paragraph summary of your project’s purpose, target problem, and expected impact. Explain how this project will save time, improve workflow, or contribute positively to your goals.
- **Core Features and Functionality:** Describe the main features implemented so far, even if they are still in a draft form. Focus on core operations rather than UI/UX at this stage.
- **Ethical Alignment:** Explain how your project aligns with ethical standards and contributes to community welfare, preferably supporting one or more UN Sustainable Development Goals (SDGs).

**<span style="color: #ADD8E6;">Basic Streamlit Setup:</span>**  

- Ensure that you have a basic Streamlit interface for testing and demonstrating core functionality.
- This could include displaying data, showing any initial visualizations, or outlining interactive features that have been implemented.

**<span style="color: #ADD8E6;">Steps for Submission:</span>**

- **<span style="color: #ADD8E6;">GitHub Link:</span>**  
  - Copy the link to your project repository on GitHub. Ensure that anyone with the link can view or access it.

- **<span style="color: #ADD8E6;">Concept Summary Document:</span>**  
  - Write your concept summary in a Word document or Google Doc.
  - Alternatively, you can include this summary in the `README.md` file within your GitHub repository.

- **<span style="color: #ADD8E6;">Streamlit Demonstration (Optional):</span>**  
  - If you’ve set up basic Streamlit functionality, provide a brief explanation of what is displayed and how it demonstrates the core of your project.

**<span style="color: red;">Evaluation Criteria:</span>**  

- **Core Functionality:** Does the project have essential features that align with the stated purpose?
- **Documentation and Concept:** Is the concept well-defined, and does it articulate the project’s value and impact?
- **Structure and Organization:** Is the GitHub repository organized with a clear structure and adequate documentation?
- **Alignment with Ethical Goals:** Does the project support ethical standards and potentially align with UN SDGs?
        """,
        unsafe_allow_html=True
    )
