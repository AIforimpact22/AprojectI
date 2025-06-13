# GitHub_push.py  –  pushes the whole repo with a single function call
import subprocess
import sys
import streamlit as st  # only needed when called from Streamlit

def push_changes(commit_message: str = "Update via GitHub_push.py") -> None:
    """
    Stage everything, commit, and push using the token in secrets.
    """
    token = st.secrets["github"]["token"]        # <-- moved out of code
    repo  = st.secrets["github"]["repository"]   # e.g. "AIforimpact22/AprojectI"

    try:
        subprocess.check_call(["git", "add", "."])
        subprocess.check_call(["git", "commit", "-m", commit_message])
        remote_url = f"https://{token}@github.com/{repo}.git"
        subprocess.check_call(["git", "push", remote_url])
        print("Pushed changes successfully.")
    except subprocess.CalledProcessError as e:
        print("Git push failed:", e)

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Update via GitHub_push.py"
    push_changes(msg)
