
# github_sync.py
import requests
import base64
import streamlit as st
from datetime import datetime
import time
import os
import fcntl

def push_db_to_github(db_file: str):
    repo = st.secrets["general"]["repo"]
    token = st.secrets["general"]["token"]
    branch = "main"  # Adjust if your default branch is different
    file_path = db_file  # Ensure this path matches your repo structure
    api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
def acquire_lock(lock_file):
    """Acquire a file lock to prevent concurrent database access"""
    lock_fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_fd
    except IOError:
        os.close(lock_fd)
        return None

def release_lock(lock_fd):
    """Release the file lock"""
    if lock_fd is not None:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)

def push_db_to_github(db_file: str):
    """Push database to GitHub with file locking"""
    lock_file = f"{db_file}.lock"
    lock_fd = None
    
    try:
        # Acquire lock with retry
        max_retries = 5
        for _ in range(max_retries):
            lock_fd = acquire_lock(lock_file)
            if lock_fd is not None:
                break
            time.sleep(1)
        
        if lock_fd is None:
            return {"success": False, "error": "Could not acquire database lock"}

        repo = st.secrets["general"]["repo"]
        token = st.secrets["general"]["token"]
        branch = "main"
        file_path = db_file
        api_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

        # Read file while holding lock
        with open(db_file, "rb") as f:
            content = f.read()
        encoded_content = base64.b64encode(content).decode("utf-8")

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Get the current file's SHA (if it exists)
        # Get current SHA
        get_response = requests.get(api_url, headers=headers)
        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
        else:
            sha = None
        if get_response.status_code != 200:
            return {"success": False, "error": "Failed to get current file SHA"}
        
        current_sha = get_response.json()["sha"]

        # Push update
        commit_message = f"Database update: {datetime.now().isoformat()}"
        data = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch,
            "sha": current_sha,
            "branch": branch
        }
        if sha is not None:
            data["sha"] = sha

        put_response = requests.put(api_url, headers=headers, json=data)
        if put_response.status_code in [200, 201]:
            return {"success": True}
        else:
            return {"success": False, "error": put_response.json()}
        return {"success": put_response.status_code in [200, 201]}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        release_lock(lock_fd)
