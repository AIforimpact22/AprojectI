import streamlit as st

def show():
    st.markdown(
        """
        <h1 style="color: #ADD8E6; font-size: 2.5em;">2.7 Understanding the Limitations of Google Colab: Why Professional Developers Choose GitHub</h1>
        <p>
        Google Colab is a fantastic tool for beginners and researchers to learn and experiment with Python programming, especially for data analysis and machine learning. However, when moving towards professional projects, Colab has certain limitations that may hinder more advanced workflows. Let’s break it down in simple terms:
        </p>
        
        <h2 style="color: #FFA07A;">1. User Interface (UI) and User Experience (UX)</h2>
        <p>
        <strong>Limitations in UI Design:</strong> Google Colab is primarily designed for running code and displaying outputs, not for building user-friendly apps. You can’t create polished graphical interfaces or dashboards for users.<br>
        <strong>Basic UX:</strong> It’s not ideal for someone interacting with your project beyond running code. There are no easy buttons, forms, or custom-designed elements for users to interact with.
        </p>
        
        <h2 style="color: #FFA07A;">2. Database Integration</h2>
        <p>
        <strong>Temporary Storage:</strong> Data saved in Colab is temporary. Once you close your session, the data disappears unless you save it to Google Drive or download it. This makes handling large or permanent datasets difficult.<br>
        <strong>Limited Database Features:</strong> While you can connect Colab to databases (like SQL), it’s not optimized for managing real-time, scalable database systems.
        </p>
        
        <h2 style="color: #FFA07A;">3. Real-Time Applications</h2>
        <p>
        <strong>No Real-Time Interactivity:</strong> Colab is designed to execute code on demand. It doesn’t support real-time updates or dynamic interactions, which are critical for applications like live dashboards or collaborative platforms.<br>
        <strong>Delayed Execution:</strong> Colab doesn’t allow users to interact with an app in real-time (e.g., clicking buttons to instantly update charts).
        </p>
        
        <h2 style="color: #FFA07A;">4. Deployment Challenges</h2>
        <p>
        <strong>No Direct Deployment:</strong> Colab notebooks are not meant to be deployed as standalone applications. You can share your code, but users need to know how to run the notebook themselves.<br>
        <strong>Temporary Environment:</strong> The environment resets every time you restart Colab, which means any libraries or files you’ve added will need to be re-installed or re-uploaded.
        </p>
        
        <h2 style="color: #FFA07A;">5. Why Professionals Use GitHub</h2>
        <p>
        GitHub is a platform specifically designed for professional coding and project management. Here’s why it’s recommended:<br>
        <strong>Version Control:</strong> GitHub tracks every change you make to your code, so you never lose your progress. It’s like having a backup system for your code.<br>
        <strong>Collaboration:</strong> You can work with teams, get feedback, and manage projects easily. It’s a go-to tool for professionals worldwide.<br>
        <strong>Deployment:</strong> Many developers use GitHub to host and deploy their apps directly, making it easy to share with users.<br>
        <strong>Integration with Other Tools:</strong> GitHub works seamlessly with tools like Streamlit, which lets you create interactive apps, and Heroku or AWS for deployment.
        </p>
        
        <h2 style="color: #FF0000;">Bottom Line</h2>
        <p>
        Google Colab is excellent for learning and prototyping ideas quickly, especially if you’re just starting with Python. However, for professional-level coding and app development, tools like GitHub offer more robust features, scalability, and real-world usability. As you grow in your coding journey, understanding these tools will help you take your projects to the next level!
        </p>
        """,
        unsafe_allow_html=True
    )
