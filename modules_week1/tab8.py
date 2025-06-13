import streamlit as st

def show():
    st.header("1.8 Understanding APIs: The Key to Real-Time Data Integration")
    st.markdown("<h3 style='color: goldenrod;'>What is an API?</h3>", unsafe_allow_html=True)
    st.write(
        "An API (Application Programming Interface) is a set of rules and protocols that allows different software applications "
        "to communicate with each other. Think of it as a bridge that lets one piece of software request and retrieve data or services "
        "from another. APIs define how requests for information or actions are made, the format of these requests, and the expected responses, "
        "allowing applications to interact without needing to understand the inner workings of each other."
    )
    st.markdown("<h3 style='color: goldenrod;'>Why is an API Important?</h3>", unsafe_allow_html=True)
    st.write(
        "APIs are crucial because they enable software systems to share data and functionality, which is especially useful for developers "
        "and organizations. With APIs, applications can be made more powerful and flexible by integrating external data or services. "
        "This ability to pull in real-time data from other platforms, or let users perform specific tasks from different systems without leaving "
        "the primary application, enhances user experiences and broadens application capabilities."
    )
    st.markdown("<h3 style='color: goldenrod;'>How is an API Used? (Example)</h3>", unsafe_allow_html=True)
    st.write(
        "To use an API, you usually send a request to an endpoint URL with specific parameters that define what data or action you’re interested in. "
        "Let’s use the USGS Earthquake API as an example:"
    )
    st.code(
        "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=YYYY-MM-DD&endtime=YYYY-MM-DD",
        language="bash"
    )
    st.write("Here’s a breakdown of each part:")
    st.write("• **https://earthquake.usgs.gov/fdsnws/event/1/query:** This is the endpoint URL where the API is hosted.")
    st.write("• **format=geojson:** This parameter specifies that the response should be in GeoJSON format, a format for encoding geographical data.")
    st.write("• **starttime=YYYY-MM-DD and endtime=YYYY-MM-DD:** These parameters allow you to set a date range for the data, where YYYY-MM-DD should be replaced with actual dates (e.g., starttime=2024-01-01&endtime=2024-01-31 to get data for January 2024).")
    st.write(
        "When a request is sent with the filled-in parameters, the API returns data, often in JSON format, containing details about all recorded "
        "earthquakes within that time range. Each record includes information such as location, magnitude, depth, and time."
    )
    st.markdown("<h3 style='color: goldenrod;'>Why Use an API Like the USGS Earthquake API?</h3>", unsafe_allow_html=True)
    st.write(
        "Using APIs like the USGS Earthquake API allows developers to pull in constantly updated earthquake data directly into their applications "
        "without manually collecting, processing, and updating it themselves. This real-time data can be visualized on maps, used in alerts, "
        "or integrated into research dashboards."
    )

