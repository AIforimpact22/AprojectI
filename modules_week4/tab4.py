import streamlit as st

def show():
    st.markdown('<h1 style="color: palegreen;">4.3 Geospatial Data</h1>', unsafe_allow_html=True)
    st.markdown("### Geospatial Data")
    st.image("photos/10.png", use_column_width=True)
    st.markdown(
        """
**What is it?**  
Geospatial data refers to information tied to specific geographic locations, defined by coordinates or spatial attributes such as polygons and elevation.

**Examples include:**  
- **Maps**
- **Elevation Models**
- **Shapefiles**

**Key Concepts Covered:**  
1. **Geospatial Attributes**
        """, unsafe_allow_html=True
    )
    st.image("photos/11.png", use_column_width=True)
    st.markdown(
        """
- **Coordinates:** Define a point's location.
- **Polygons:** Represent areas.
- **Layers:** Overlay multiple datasets.
- **Metadata:** Details about the dataset.

2. **Why is Geospatial Data Important?**  
- Enhanced spatial understanding.
- Data-driven decision making.
- Cross-industry applications.
- Accessibility through open-source tools.

**The Power of Google Earth Engine and Open Data**  

*Example Use Cases:*  
- Monitoring wildlife migration.
- Visualizing earthquake locations.
- Urban planning and logistics.

**Practical Tools:**  
- Google Earth Engine, Geopandas, Folium, Plotly.
        """, unsafe_allow_html=True
    )
    st.image("photos/12.png", use_column_width=True)
    st.markdown(
        """
**Google Earth Engine (GEE):**  
- Cloud-based analysis of global geospatial data.
- Example: Analyze deforestation trends.

**Geopandas:**  
- Combines Pandas with geospatial capabilities.

**Folium:**  
- Creates interactive maps.

**Plotly:**  
- Advanced 3D visualizations.

**Example Datasets:**  
- Wildlife Migration Dataset  
- Earthquake Data

**References:**  
- Google Earth Engine Overview  
- OpenStreetMap  
- NASA Earthdata  
- WWF  
- USGS Earthquake Hazards Program  

**Documentation:**  
- Geopandas: [Official Documentation](https://geopandas.org/en/stable/)  
- Folium: [Official Documentation](https://python-visualization.github.io/folium/)  
- Plotly: [Official Documentation](https://plotly.com/python/)
        """, unsafe_allow_html=True
    )
