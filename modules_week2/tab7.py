import streamlit as st

def show():
    st.header("2.6 Case Study: Using Google Colab to Transform Abandoned Hydrocarbon Fields into Heat Storage Solutions")
    st.markdown(
        """
**<span style="color: #FFA07A;">Case Study: Leveraging Google Colab for Advanced Geostatistical Analysis in Energy Storage Research</span>**

**Context:** In your research titled "Transforming Abandoned Hydrocarbon Fields into Heat Storage Solutions: A Hungarian Case Study Using Enhanced Multi-Criteria Decision Analysis–Analytic Hierarchy Process and Geostatistical Methods," you implemented a comprehensive methodology to assess the feasibility of repurposing depleted hydrocarbon reservoirs for underground thermal energy storage (UTES). Google Colab played a pivotal role in facilitating the computational and visualization aspects of this study.

**<span style="color: #FFA07A;">Key Utilizations of Google Colab:</span>**

**<span style="color: #ADD8E6;">Data Processing and Integration:</span>** 

- Google Colab was used to execute Python scripts for handling and processing vast datasets from 67 wells, including porosity, permeability, thickness, temperature, and other reservoir parameters.  
- Libraries like NumPy, pandas, and Matplotlib enabled efficient manipulation and visualization of data, including cumulative histograms and variograms.

**<span style="color: #ADD8E6;">Geostatistical Modeling:</span>**

- Sequential Gaussian Simulation (SGS) and Universal Kriging models were implemented and visualized within Colab, taking advantage of its GPU acceleration for complex calculations.  
- Colab's integration with cloud storage ensured seamless access to large datasets and geospatial models.

**<span style="color: #ADD8E6;">Multi-Criteria Decision Analysis (MCDA):</span>**

- The platform was used to automate the evaluation of reservoir suitability for high-temperature aquifer thermal energy storage (HT-ATES) using the Analytic Hierarchy Process (AHP).  
- Python-based visualization tools in Colab helped depict scoring distributions and identify optimal locations with heatmaps and grid-based analyses.

**<span style="color: #ADD8E6;">Collaboration and Transparency:</span>** 

- Colab's real-time collaboration features allowed team members to review and refine workflows and models simultaneously.  
- The reproducibility of results was ensured through shared Colab notebooks, aligning with scientific transparency standards.

**<span style="color: #ADD8E6;">Benefits of Using Google Colab in Your Research:</span>**

- **Accessibility and Cost-Effectiveness:** The browser-based nature of Colab eliminated the need for local installations or high-performance hardware, making advanced geostatistical methods accessible.  
- **Efficiency in Workflow:** By centralizing data processing and model execution, Colab reduced the time and effort required for iterative analyses.  
- **Enhanced Visualization:** The use of Colab for dynamic plots and geospatial representations improved the interpretability of complex datasets.  
- **Collaborative Development:** The integration of team contributions through Colab streamlined the review and decision-making process.
**Author to whom correspondence should be addressed.**  
_Energies 2024, 17(16), 3954; [https://doi.org/10.3390/en17163954](https://doi.org/10.3390/en17163954)_  
_Submission received: 6 June 2024 / Revised: 27 June 2024 / Accepted: 7 August 2024 / Published: 9 August 2024_  
_(This article belongs to the Special Issue Subsurface Energy and Environmental Protection)_
        """,
        unsafe_allow_html=True
    )
