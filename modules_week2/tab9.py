import streamlit as st

def show():
    st.markdown(
        '<h1 style="color: #FFA07A;">2.8 Accessing Google Sheets Data in Google Colab by API</h1>',
        unsafe_allow_html=True
    )
    st.write(
        "Learn to access and analyze data from Google Sheets within Google Colab by authenticating with a service account using a JSON key. "
        "Tutorial: Learn how to access and analyze data from Google Sheets using Google Colab by authenticating through a service account with a JSON key. "
        "[JSON Method](https://www.youtube.com/watch?v=H4-EIDxIhVE)"
    )
    st.video("https://youtu.be/H4-EIDxIhVE")
    st.markdown(
        """
**Steps:**

1. **Go to Google Cloud Console.**
   - Create a new project or select an existing project.
   - Navigate to the relevant section.
   - Search for the necessary services and click for both.

2. **In the Cloud Console, go to the Service Account section.**
   - Click on **Create Service Account**.
   - Give your service account a name and complete the steps to create it.
   - Under the section, click on **Create Key**, and select **JSON** format. This will download your key as a `.json` file.

3. **Open the Google Sheet you want to access.**
   - Click the **Share** button at the top-right.
   - Copy the service account email (it ends with `@<project>.iam.gserviceaccount.com`) from your Cloud Console.
   - Share the Google Sheet with this email, granting it access.

4. **Open a Colab notebook.**
   - Upload the downloaded JSON key by clicking on the folder icon in Colab, then using the upload button to select the file.
        """,
        unsafe_allow_html=True
    )
