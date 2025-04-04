import streamlit as st

def show():
    st.markdown(
        """
        <h1 style="color: palegreen;">Week 5: Your Personalized Project</h1>
        <h2 style="color: lightyellow;">Project Development Guideline</h2>
        <p>
            <strong>Objective:</strong> This week, focus on launching the foundation of your personalized project. Your goal is to build the core functionality and ensure the project is operational by the end of the week. By prioritizing functionality over aesthetics, you’ll be able to submit a draft that captures the project’s purpose and initial implementation.
        </p>
        <h3>Steps to Follow:</h3>
        
        <p><span style="color: #ADD8E6; font-weight: bold;">Define Your Project Concept:</span></p>
        <ul>
            <li><strong>Problem Statement:</strong> Identify the main problem your project will address.</li>
            <li><strong>Project Goals:</strong> Describe how the project will enhance productivity, save time, or contribute to a positive impact.</li>
            <li><strong>Ethics and Impact:</strong> Ensure your project aligns with ethical standards and serves community needs, supporting one or more UN Sustainable Development Goals (SDGs).</li>
        </ul>
        
        <p><span style="color: #ADD8E6; font-weight: bold;">Set Up on GitHub:</span></p>
        <ul>
            <li><strong>Repository Creation:</strong> Create a new GitHub repository to host your project files.</li>
            <li><strong>Organize the Structure:</strong> Set up folders for scripts, data, and documentation. <em>Example structure:</em>
                <ul>
                    <li>src/: main scripts</li>
                    <li>data/: datasets</li>
                    <li>docs/: project documentation</li>
                </ul>
            </li>
            <li><strong>README File:</strong> Add a README.md to introduce your project, its purpose, and key functionalities.</li>
        </ul>
        
        <p><span style="color: #ADD8E6; font-weight: bold;">Develop Core Functionality:</span></p>
        <ul>
            <li><strong>Focus on Core Scripts:</strong> Start by writing the essential scripts that form the backbone of your project’s functionality.</li>
            <li><strong>Avoid UI Details:</strong> Concentrate on the core features and data processing, and save layout and design refinements for later weeks.</li>
            <li><strong>Basic Streamlit Setup:</strong> Use Streamlit to test your core functionality. Display data and results with simple Streamlit functions (e.g., st.write, st.table, st.plot) to verify the script’s operations.</li>
        </ul>
        
        <p><span style="color: #ADD8E6; font-weight: bold;">Prepare for Feedback:</span></p>
        <ul>
            <li><strong>Document Key Insights:</strong> Take notes on any challenges or issues you encounter.</li>
            <li><strong>Write a Concept Summary:</strong> Prepare a brief summary explaining your project’s aim, functionality, and expected impact.</li>
        </ul>
        
        <p><span style="color: red; font-weight: bold;">End-of-Week Submission:</span></p>
        <ul>
            <li><strong>Submit as a Draft:</strong> Provide a GitHub link to your project repository.</li>
            <li><strong>Attach Concept Summary:</strong> Include a description of the project’s goals, functions, and benefits.</li>
        </ul>
        
        <p><span style="color: #FFA07A; font-weight: bold;">Guidelines for Future Weeks:</span></p>
        <p>
            For following weeks, focus on expanding features, refining the UI, and gathering feedback. A suggested timeline:
            <br><strong>Weeks 5-6:</strong> Add extra functionality, work on UI/UX with Streamlit.
            <br><strong>Weeks 7-8:</strong> Finalize testing, incorporate feedback, and polish for presentation.
        </p>
        """,
        unsafe_allow_html=True
    )
