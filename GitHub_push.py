import subprocess
import sys

# Provided GitHub token and repository details
token = "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"
repo = "AIforimpact22/AprojectI"

def push_changes(commit_message):
    try:
        # Stage all changes
        subprocess.check_call(["git", "add", "."])
        # Commit changes with the provided commit message
        subprocess.check_call(["git", "commit", "-m", commit_message])
        
        # Construct the remote URL with the token included for authentication
        remote_url = f"https://{token}@github.com/{repo}.git"
        # Push changes to the remote repository
        subprocess.check_call(["git", "push", remote_url])
        print("Pushed changes successfully.")
    except subprocess.CalledProcessError as e:
        print("An error occurred during the git operations:", e)

if __name__ == "__main__":
    # Use a commit message from the command line if provided, otherwise a default message
    commit_message = "Update from GitHub_push.py" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    push_changes(commit_message)
