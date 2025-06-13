import streamlit as st

def show():
    st.markdown("<h1 style='color: palegreen;'>4.4 Image Data</h1>", unsafe_allow_html=True)
    st.image("photos/13.png")
    st.markdown(
        """
**What is it?**  
Image data represents visual content such as photographs, satellite imagery, and medical images.

**Why It Matters:**  
- Pattern detection  
- Enhanced decision-making  
- Innovative applications

**Applications:**  
1. Environmental Monitoring  
2. AI-Powered Enhancements  
3. Medical Imaging  
        """, unsafe_allow_html=True
    )
    st.image("photos/14.png")
    st.markdown(
        """
1. **Environmental Monitoring:**  
   - Analyze satellite imagery to detect deforestation.
   - Tools: Google Earth Engine, OpenCV.

2. **AI-Powered Enhancements:**  
   - Remove noise, adjust brightness, crop images.
   - Tools: Pillow, OpenCV.

3. **Medical Imaging:**  
   - Detect anomalies in X-rays or MRIs.
   - Tools: TensorFlow, PyTorch.
        """, unsafe_allow_html=True
    )
    st.image("photos/15.png")
    st.markdown(
        """
**Image Processing Tools:**  
1. **OpenCV:** Advanced image processing (object detection, edge detection).  
2. **Pillow (PIL):** Image manipulation (resizing, cropping).  
3. **TensorFlow and PyTorch:** AI frameworks for image classification.
        """, unsafe_allow_html=True
    )
    st.image("photos/16.png")
    st.markdown(
        """
**Example Datasets and Workflow:**  

*Satellite Imagery* and *Medical Imaging* examples with tables, data acquisition, preprocessing, model building, and visualization.

**References:**  
- OpenCV, NASA EarthData, NIH, TensorFlow, Pillow, Google Open Images.
        """, unsafe_allow_html=True
    )
