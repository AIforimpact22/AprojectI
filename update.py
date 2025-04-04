import streamlit as st
import os
import glob

# Set the admin password (as provided)
admin_password = "meer"

def check_admin():
    """Ask for the admin password and validate it."""
    password = st.sidebar.text_input("Enter admin password", type="password")
    if password != admin_password:
        st.sidebar.error("Incorrect password. Please try again.")
        return False
    return True

def get_tab_files():
    """Search for tab files (e.g. tab*.py) in the specified modules_week directories."""
    tab_files = []
    # List of directories where tab files are stored
    directories = ["modules_week1", "modules_week2", "modules_week3", "modules_week4", "modules_week5"]
    for d in directories:
        # Look for files that start with "tab" and end with ".py"
        pattern = os.path.join(d, "tab*.py")
        files = glob.glob(pattern)
        tab_files.extend(files)
    return tab_files

def load_file(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
        return ""

def save_file(file_path, content):
    """Write the provided content to a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        st.success(f"Saved changes to {file_path}")
    except Exception as e:
        st.error(f"Error saving {file_path}: {e}")

def main():
    st.title("Update Tabs")
    st.write("This page displays all tab files as HTML for editing purposes.")
    
    # Check admin password before proceeding
    if not check_admin():
        st.stop()
    
    # Get the list of tab files from the modules directories
    tab_files = get_tab_files()
    if not tab_files:
        st.write("No tab files found.")
        return

    # Allow selection of a tab file from a sidebar dropdown
    selected_file = st.sidebar.selectbox("Select a tab file to edit", tab_files)
    file_content = load_file(selected_file)
    
    # Display file content in a text area for editing (you could also use st.code() to display as code)
    edited_content = st.text_area(f"Editing {selected_file}", value=file_content, height=400)
    
    # Save changes button: write the edited content back to the file
    if st.button("Save Changes"):
        save_file(selected_file, edited_content)

if __name__ == "__main__":
    main()
