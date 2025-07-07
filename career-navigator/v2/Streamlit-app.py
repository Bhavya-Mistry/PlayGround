import streamlit as st
from app import ats_app, career_app


st.set_page_config(page_title="Career Navigator", layout="wide")
st.sidebar.title("🧭 Choose a Tool")

page = st.sidebar.radio("Select a module:", ["🎓 Career Predictor", "📄 ATS Resume Evaluator"])

if page == "🎓 Career Predictor":
    career_app.run()
elif page == "📄 ATS Resume Evaluator":
    ats_app.run()
