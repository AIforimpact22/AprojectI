import streamlit as st
import pandas as pd

def show():
    st.markdown('<h1 style="color: palegreen;">4.2 Numerical Data</h1>', unsafe_allow_html=True)
    st.markdown("### Numerical Data")
    st.image("photos/5.png", caption="Numerical Data")
    
    st.markdown("#### What is it?")
    st.write(
        """
Numerical data refers to information that is measurable and expressed in numbers. This type of data is essential for quantitative analysis and is prevalent across various fields:
- **Finance:** Analyzing metrics like sales figures, profit margins, and market trends.
- **Science:** Recording experimental outcomes such as temperature readings, reaction times, or growth rates.
- **Engineering:** Measuring parameters like stress levels, material thickness, or electrical currents.
- **Social Sciences:** Collecting data on population sizes, survey responses, or economic indicators.
        """
    )
    
    st.markdown("#### Types of Numerical Data")
    st.markdown("**1. Discrete Data:**")
    st.image("photos/6.png", caption="Discrete Data")
    st.markdown("**Numerical Data: Discrete Data**")
    
    discrete_data = {
        "Component ID": ["MC001", "MC002", "MC003", "MC004", "MC005", "MC006", "MC007", "MC008", "MC009", "MC010"],
        "Component Name": ["Bolt", "Washer", "Ball Bearing", "Hydraulic Cylinder", "Gear", "Nut", "Piston", "Valve", "Pulley", "Spring"],
        "Category": ["Fastener", "Fastener", "Rotational Support", "Actuator", "Transmission", "Fastener", "Engine Component", "Control Component", "Transmission", "Energy Storage"],
        "Quantity Available": [120, 300, 50, 25, 75, 200, 80, 37, 66, 79],
        "Batch Number": ["B001", "W003", "F073", "C080", "G903", "E703", "C608", "V405", "T008", "P732"],
        "Supplier ID": ["SUP101", "SUP102", "SUP103", "SUP104", "SUP105", "SUP106", "SUP107", "SUP108", "SUP109", "SUP110"]
    }
    df_discrete = pd.DataFrame(discrete_data)
    st.dataframe(df_discrete, height=200)
    
    st.markdown("**2. Continuous Data:**")
    st.image("photos/7.png", caption="Continuous Data")
    st.markdown("**Numerical Data: Continuous Data**")
    
    continuous_data = {
        "Timestamp": ["2024-12-01 0.00", "2024-12-01 1.00", "2024-12-01 2.00", "2024-12-01 3.00", "2024-12-01 4.00", 
                      "2024-12-01 5.00", "2024-12-01 6.00", "2024-12-01 7.00", "2024-12-01 8.00", "2024-12-01 9.00", "2024-12-01 10.00"],
        "PM2.5 (µg/m3)": [0.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 9.00, 10.00],
        "CO2 (ppm)": [96.55, 90.57, 88.58, 89.75, 56.55, 78.53, 86.34, 66.56, 76.75, 56.57, 79.85],
        "NO2 (ppb)": [78.4] * 11,
        "Additional": [330.4, 446.6, 380.7, 345.9, 389.8, 386.4, 378.0, 340.7, 360.7, 366.4, 345.5]
    }
    df_continuous = pd.DataFrame(continuous_data)
    st.dataframe(df_continuous, height=200)
    
    st.markdown("#### Why is it Important?")
    st.image("photos/8.png", caption="Importance of Numerical Data")
    st.write(
        """
Understanding and analyzing numerical data enables us to:
- **Identify Trends and Patterns:** For instance, a retail store analyzes monthly sales data to determine peak shopping periods.
- **Make Informed Decisions:** Healthcare professionals use patient vital statistics for diagnostics.
- **Perform Statistical Analysis:** Calculate averages, variances, and more.
- **Visualize Information:** Create charts and graphs to present data.
        """
    )
    
    st.markdown("#### Example Datasets")
    st.markdown("**1. Sales Data**")
    st.write(
        """
Date | Store ID | Product ID | Units Sold | Revenue (USD)
--- | --- | --- | --- | ---
2024-12-01 | 001 | A123 | 20 | 500.00  
2024-12-01 | 002 | B456 | 15 | 375.00  
2024-12-01 | 003 | C789 | 25 | 625.00  
        """
    )
    st.write(
        """
**Analysis:**
- **Total Revenue Calculation**
- **Performance Comparison**
- **Product Analysis**
        """
    )
    
    st.markdown("**2. Sensor Data**")
    st.write(
        """
Timestamp | Sensor ID | Measurement Type | Measurement Value
--- | --- | --- | ---
2024-12-01 12:30:00 | TEMP001 | Temperature | 25.6°C  
2024-12-01 12:35:00 | TEMP002 | Temperature | 26.3°C  
2024-12-01 12:40:00 | TEMP003 | Temperature | 24.9°C  
        """
    )
    st.write(
        """
**Analysis:**
- **Average Temperature**
- **Anomaly Detection**
        """
    )
    
    st.markdown("**3. Temperature Data**")
    st.write(
        """
Date | Location | Max Temp (°C) | Min Temp (°C) | Avg Temp (°C)
--- | --- | --- | --- | ---
2024-12-01 | New York | 30.5 | 15.2 | 22.8  
2024-12-01 | London   | 28.0 | 10.0 | 19.5  
2024-12-01 | Tokyo    | 32.1 | 20.3 | 26.2  
        """
    )
    st.write(
        """
**Analysis:**
- **Comparative Study**
- **Trend Analysis**
        """
    )
    
    st.markdown("#### How to Analyze Numerical Data")
    st.image("photos/9.png", caption="Analyzing Numerical Data")
    st.write(
        """
**Basic Calculations:**
- Sum, Mean, Median, Mode, Range

**Visualization:**
- Bar Charts, Line Graphs, Histograms, Scatter Plots

**Advanced Techniques:**
- Regression Analysis, Time-Series Analysis, Hypothesis Testing
        """
    )
    
    st.markdown("#### References")
    st.write(
        """
- [Statistics and Data Types, Khan Academy](https://www.khanacademy.org)
- [Applications of Quantitative Data, Investopedia](https://www.investopedia.com)
- [Retail Data Analytics Case Studies, Kaggle](https://www.kaggle.com)
- [IoT and Environmental Monitoring Data, ResearchGate](https://www.researchgate.net)
- [Global Temperature Dataset Analysis, NOAA](https://www.noaa.gov)
- [Data Visualization Best Practices, Tableau Public](https://public.tableau.com)
- [Statistics 101, Coursera](https://www.coursera.org)
- [Predictive Analytics for Beginners, Harvard Business Review](https://hbr.org)
- [How Companies Use Big Data, McKinsey & Company](https://www.mckinsey.com)
- [Climate Change Indicators: Temperature, EPA](https://www.epa.gov)
        """
    )
