import streamlit as st

def show():
    st.markdown(
        '<h1 style="color: palegreen;">3.11 Top 10 Prompt Engineering Techniques for ChatGPT to Optimize GitHub Scripting and Automation</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
**<span style="color: #ADD8E6;">1. Clarify Repository Structure and Setup</span>**  
Prompt: "Generate a script to set up a new GitHub repository, including folders for src, tests, and docs, with a basic README template."  
Tip: Define the repository structure and folder requirements to get a well-organized starting point.

**<span style="color: #ADD8E6;">2. Specify Code Documentation Needs</span>**  
Prompt: "Write a Python script for [specific task], and include detailed comments for each function and step."  
Tip: When documentation is a priority, prompt ChatGPT to add comments, making code more accessible for other collaborators.

**<span style="color: #ADD8E6;">3. Describe Automation Tasks for GitHub Actions</span>**  
Prompt: "Create a GitHub Actions YAML file that automates testing for a Python project on each pull request."  
Tip: Specify triggers (e.g., pull requests, pushes) to make GitHub Actions workflows effective for continuous integration (CI) and testing.

**<span style="color: #ADD8E6;">4. Request Code for Branch Management</span>**  
Prompt: "Write a script to automate branch creation and deletion for feature branches in a GitHub repo."  
Tip: Define naming conventions or branch rules to ensure GitHub branches are managed in an organized way.

**<span style="color: #ADD8E6;">5. Define Access and Permission Requirements</span>**  
Prompt: "Generate a script to add a list of users with read-only permissions to my repository."  
Tip: Clearly state permission levels (e.g., read, write) to ensure correct access control settings are applied.

**<span style="color: #ADD8E6;">6. Use Prompts for Repository Data Retrieval</span>**  
Prompt: "Create a Python script to retrieve a list of open issues and pull requests from a specified GitHub repository."  
Tip: Specify desired fields, such as issue titles, descriptions, or statuses, to retrieve precise information.

**<span style="color: #ADD8E6;">7. Seek Git Commands for Version Control</span>**  
Prompt: "Provide a list of essential Git commands for managing commits, branches, and merges."  
Tip: Use ChatGPT to clarify complex Git workflows, like branching and merging, with easy-to-follow commands.

**<span style="color: #ADD8E6;">8. Outline GitHub Project Board Automation</span>**  
Prompt: "Write a script to automate adding issues to a GitHub Project Board and assigning them based on tags."  
Tip: Define conditions for automation, like tagging issues, to streamline project management in GitHub.

**<span style="color: #ADD8E6;">9. Get Guidance for Issue and PR Templates</span>**  
Prompt: "Generate a GitHub issue template for bug reporting and a pull request template for code reviews."  
Tip: Specify the template content (e.g., bug details, testing instructions) to standardize reporting and review processes.

**<span style="color: #ADD8E6;">10. Generate Workflow for Code Review and Approval</span>**  
Prompt: "Create a GitHub Actions workflow that requires code review and approval before merging to the main branch."  
Tip: Define review steps or conditions, ensuring that code quality standards are upheld before integration.
        """,
        unsafe_allow_html=True,
    )

