import json
from github import Github
import streamlit as st

def load_github_progress():
    """
    Loads the user_progress.json file from the repository.
    If the file is not found (404), creates an empty progress file and returns it.
    Returns a tuple: (progress_data, contents) where contents is a ContentFile object.
    """
    token = st.secrets["github"]["token"]
    repo_name = st.secrets["github"]["repository"]
    file_path = st.secrets["github"]["file_path"]

    g = Github(token)
    repo = g.get_repo(repo_name)
    
    try:
        contents = repo.get_contents(file_path)
        progress_data = json.loads(contents.decoded_content.decode())
    except Exception as e:
        if "Not Found" in str(e):
            # File does not exist: create an empty progress file.
            progress_data = {}
            commit_message = "Create initial progress file"
            new_content = json.dumps(progress_data, indent=4)
            repo.create_file(file_path, commit_message, new_content)
            # Retrieve the newly created file.
            contents = repo.get_contents(file_path)
        else:
            st.error(f"Error loading progress file: {e}")
            progress_data = {}
            contents = None
    return progress_data, contents

def save_github_progress(progress_data, contents):
    """
    Commits the updated progress_data (a Python dict) back to the repository.
    """
    token = st.secrets["github"]["token"]
    repo_name = st.secrets["github"]["repository"]
    file_path = st.secrets["github"]["file_path"]

    g = Github(token)
    repo = g.get_repo(repo_name)

    new_content = json.dumps(progress_data, indent=4)
    commit_message = "Update user progress"
    try:
        repo.update_file(contents.path, commit_message, new_content, contents.sha)
    except Exception as e:
        st.error(f"Error saving progress file: {e}")

def get_user_progress(username):
    """
    Returns the progress dictionary for the given username.
    If the user doesn't exist, initializes with default values.
    Example: { "week1": 1, "week2": 0, "week3": 0, "week4": 0, "week5": 0 }
    """
    progress_data, _ = load_github_progress()
    if username not in progress_data:
        progress_data[username] = {"week1": 1, "week2": 0, "week3": 0, "week4": 0, "week5": 0}
        # Save the new default progress immediately.
        _, contents = load_github_progress()
        save_github_progress(progress_data, contents)
    return progress_data[username]

def update_user_progress(username, week, new_tab_index):
    """
    Update the progress for the user in the specified week.
    Only updates if new_tab_index is greater than the current value.
    """
    progress_data, contents = load_github_progress()
    user_prog = progress_data.get(username, {"week1": 1, "week2": 0, "week3": 0, "week4": 0, "week5": 0})
    key = f"week{week}"
    if new_tab_index > user_prog.get(key, 0):
        user_prog[key] = new_tab_index
    progress_data[username] = user_prog
    save_github_progress(progress_data, contents)
