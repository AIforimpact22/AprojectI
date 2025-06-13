import streamlit as st
import pandas as pd

def show():
    st.header("1.5 Introduction to Python Libraries")
    st.write(
        "Python libraries extend the functionality of the language, making it easier to perform complex tasks with simple commands. "
        "Below is a polished overview of essential Python libraries, their primary purposes, and examples of projects where they can be applied."
    )

    # Data for the table
    data = {
        'Library': [
            'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Scikit-Learn', 'TensorFlow', 'Keras',
            'NLTK', 'SpaCy', 'OpenCV', 'BeautifulSoup', 'Requests', 'Flask', 'Django',
            'Streamlit', 'Pygame', 'PySpark', 'Plotly', 'SQLAlchemy'
        ],
        'Purpose': [
            'Data manipulation and analysis',
            'Numerical computations and matrix operations',
            'Creating static visualizations and charts',
            'Statistical data visualization and exploratory analysis',
            'Building machine learning models and data modeling',
            'Developing deep learning models and neural networks',
            'Simplified deep learning model prototyping',
            'Natural language processing (NLP) tasks and text analysis',
            'Advanced NLP for large-scale text processing',
            'Computer vision and image processing applications',
            'Web scraping to extract data from websites',
            'Sending HTTP requests to access and interact with APIs',
            'Lightweight web development and creating RESTful APIs',
            'Full-stack web development for large-scale applications',
            'Developing interactive data applications and dashboards',
            'Game development and interactive simulations',
            'Distributed data processing and large-scale analytics',
            'Interactive, web-based visualizations and dashboards',
            'Database management and object-relational mapping (ORM)'
        ],
        'Project Examples': [
            'Cleaning and analyzing CSV/Excel data, financial data processing, and generating reports.',
            'Scientific computing, handling large-scale datasets, and performing linear algebra operations.',
            'Plotting trends, creating line/bar/pie charts, and visualizing statistical data.',
            'Generating heatmaps, pair plots, and interactive visual reports for data insights.',
            'Building classification models, predictive analytics, clustering, and recommendation engines.',
            'Developing image recognition systems, object detection, and natural language processing models.',
            'Rapid prototyping for image recognition, text classification, and other deep learning projects.',
            'Chatbots, sentiment analysis, language translation, and text-based data mining projects.',
            'Entity recognition, document classification, and large-scale language modeling projects.',
            'Face recognition, object detection, and motion tracking for real-time image processing.',
            'Scraping news sites, aggregating data from multiple sources, and building data collection tools.',
            'Accessing weather data, stock market APIs, and automating data retrieval tasks.',
            'Building small web apps, dashboards, and RESTful services for rapid prototyping.',
            'Developing e-commerce platforms, content management systems (CMS), and large-scale websites.',
            'Creating interactive dashboards, data apps, and visualizations without extensive coding.',
            'Developing 2D games, educational simulations, and interactive entertainment projects.',
            'Handling big data tasks, real-time analytics, and processing large datasets efficiently.',
            'Building interactive graphs, 3D visualizations, and dynamic dashboards for data analysis.',
            'Managing databases, developing CRUD applications, and integrating backend services.'
        ]
    }

    df = pd.DataFrame(data)

    # Style the DataFrame: white text, blue borders, and a dark background for contrast.
    styled_df = (
        df.style
          .set_table_styles([
              {"selector": "th", "props": [("color", "white"), ("border", "2px solid blue"), ("background-color", "black")]},
              {"selector": "td", "props": [("color", "white"), ("border", "2px solid blue"), ("background-color", "black")]}
          ])
          .set_properties(**{'text-align': 'left'})
    )

    # Render the styled table.
    st.table(styled_df)

