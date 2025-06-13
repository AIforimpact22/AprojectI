import streamlit as st

def show():
    st.markdown('<h1 style="color: #FFFFE0;">3.4 Types of Databases You Can Use in Your Projects</h1>', unsafe_allow_html=True)
    
    st.markdown(
        """
**Content:**

In programming, databases are essential for storing, managing, and retrieving data. Depending on the scale and complexity of your project, you can use different types of databases to suit your needs. Below are the most commonly used databases, particularly in Python projects:

**<span style="color: #FFFFE0;">1. CSV (Comma-Separated Values)</span>**  
Description: A simple, lightweight format used to store tabular data in plain text, separated by commas.  
Use Case: Ideal for small datasets and data sharing across platforms.  
Example: Storing survey responses or sales records.

**<span style="color: #FFFFE0;">2. JSON (JavaScript Object Notation)</span>**  
Description: A lightweight format for storing structured data in a readable and flexible key-value format.  
Use Case: Perfect for API responses, configuration files, and hierarchical data.  
Example: Storing user profiles or settings for an application.

**<span style="color: #FFFFE0;">3. Google Sheets</span>**  
Description: A cloud-based spreadsheet tool that allows real-time collaboration and easy data sharing.  
Use Case: Great for projects requiring dynamic updates or shared access among team members.  
Example: Managing inventory data or collaborative project tracking.

**<span style="color: #FFFFE0;">4. SQL (Structured Query Language)</span>**  
Description: A powerful and standardized language used to interact with relational databases.  
Use Case: Best suited for complex queries and handling large datasets with defined relationships.  
Example: Storing and managing user accounts, transaction data, or website content.

**<span style="color: #FFFFE0;">Choosing the Right Database</span>**

The choice of database depends on your project requirements:

- For simplicity: Use CSV or JSON.
- For collaboration: Use Google Sheets.
- For large-scale applications: Use SQL.

Each of these databases has unique advantages, making them versatile tools for different projects. Start with one that fits your current needs and expand as your project grows!
        """,
        unsafe_allow_html=True
    )

