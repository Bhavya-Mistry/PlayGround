import streamlit as st

st.title("Hello, This is Bhavya Mistry")
st.write("A simple app that shows some info about me")

# Scores
with st.expander("SSC Score"):
    st.success("My SSC Score is 75%")

with st.expander("HSC Score"):
    st.success("My HSC Score is 57%")

with st.expander("CGPA"):
    st.success("My CGPA is 9.55")

# Skills
with st.expander("Skills"):
    st.markdown("""
- Python
- SQL
- pandas
- NumPy
- matplotlib
- seaborn
""")

# Tech Skills
with st.expander("Tech Skills"):
    st.markdown("""
**Exploring:** OpenCV, FastAPI, Keras  
**Tools:** Google Colab / Jupyter Notebook, Git, GitHub  
**Soft Skills:** Communication, Time Management, Teamwork  
**Languages Spoken:** English, Hindi, Gujarati  
""")

# Certifications
with st.expander("Certifications"):
    st.markdown("""
- AI - Indus University (2024)  
- Getting Started With Machine Learning Algorithms - Simplilearn (2024)  
- Introduction to SQL - Simplilearn (2024)  
""")

# Experience
with st.expander("Experience"):
    st.markdown("""
**Prodigy Infotech**  
*Data Science Intern*  
May 1, 2025 – Present  
- Working on data analysis and machine learning projects.
""")

# Projects
with st.expander("Projects"):
    st.markdown("""
1. **Flight Price Prediction [Regression]**  
   - Used Linear and Decision Tree Regression  
   - Applied feature engineering on multiple data types  

2. **SmartHealth Predictive Analyzer [Classification]**  
   - Built model using Decision Tree & Logistic Regression  
   - Predicted diabetes using clinical inputs  

3. **Customer Segmentation using K-Means [Unsupervised]**  
   - Performed RFM and K-Means clustering  
   - Visualized clusters and deployed a basic web app with Streamlit  

4. **Single Image Dehazing [Computer Vision Basics]**  
   - Implemented Dark Channel Prior + Guided Filter  
   - Enhanced visibility by refining transmission maps  
""")

# Contact Me
with st.expander("Contact Me"):
    st.markdown("""
📧 **Email:** mistrybhavya9@gmail.com  
📱 **Phone:** 6352181842  
💻 **GitHub:** [Bhavya-Mistry](https://github.com/Bhavya-Mistry)  
🔗 **LinkedIn:** [Bhavya Mistry](https://www.linkedin.com/in/bhavya-mistry-5b5a57293/)  
""")
