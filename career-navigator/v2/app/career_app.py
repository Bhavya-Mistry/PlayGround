import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit.components.v1 import html

# st.set_page_config(page_title="AI-Powered Career Navigator", layout="wide")

def run():
    # Load trained components
    model = joblib.load("v2/saved-models/career_model.pkl")
    mlb_dict = joblib.load("v2/saved-models/mlb_dict.pkl")
    label_encoder = joblib.load("v2/saved-models/label_encoder.pkl")

    st.markdown("""
        <style>
            .main-title {
                font-size: 3em;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            .intro-text {
                text-align: center;
                font-size: 1.2em;
                color: #34495e;
                margin-bottom: 50px;
            }
            .stButton>button {
                background-color: #2c3e50;
                color: white;
                border-radius: 8px;
                height: 3em;
                width: 100%;
                font-size: 1.1em;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""<div class='main-title'>🚀 AI-Powered Career Navigator</div>""", unsafe_allow_html=True)
    st.markdown("""<div class='intro-text'>Fill in your academic, technical, and personal interests to receive your personalized career prediction.</div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📝 Your Profile")

        multi_label_inputs = {}
        for col in mlb_dict.keys():
            options = mlb_dict[col].classes_
            selected = st.multiselect(f"{col.replace('_', ' ')}", options)
            multi_label_inputs[col] = selected

        preferred_style = st.selectbox("Preferred Work Style", ["Remote", "Hybrid", "Onsite"])
        problem_style = st.selectbox("Problem Solving Style", ["Analytical", "Creative", "Logical", "Experimental"])
        masters = st.radio("Do you want to go for Masters?", ["Yes", "No"])
        research = st.radio("Interested in Research?", ["Yes", "No"])
        cgpa = st.slider("Current CGPA", 2.0, 10.0, 7.5, 0.1)
        projects = st.number_input("Current Projects Count", min_value=0, step=1)
        internships = st.number_input("Internship Duration (in months)", min_value=0, step=1)

    with col2:
        st.header("📊 Results")

        def prepare_input():
            feature_parts = []
            for col, mlb in mlb_dict.items():
                selected_values = multi_label_inputs[col]
                encoded = mlb.transform([selected_values])
                df = pd.DataFrame(encoded, columns=[f"{col}_{c}" for c in mlb.classes_])
                feature_parts.append(df)

            other_features = pd.DataFrame([{
                "Preferred_Work_Style": {"Remote": 0, "Hybrid": 1, "Onsite": 2}.get(preferred_style, 0),
                "Problem_Solving_Style": {"Analytical": 0, "Creative": 1, "Logical": 2, "Experimental": 3}.get(problem_style, 0),
                "Wants_to_Go_for_Masters": 1 if masters.lower() == "yes" else 0,
                "Interested_in_Research": 1 if research.lower() == "yes" else 0,
                "CGPA": cgpa,
                "Current_Projects_Count": projects,
                "Internship_Experience": internships
            }])
            feature_parts.append(other_features)
            final_input = pd.concat(feature_parts, axis=1)
            for col in model.feature_names_in_:
                if col not in final_input:
                    final_input[col] = 0
            return final_input[model.feature_names_in_]

        if st.button("🎯 Predict My Career"):
            input_df = prepare_input()
            pred = model.predict(input_df)[0]
            proba = model.predict_proba(input_df)[0]
            career = label_encoder.inverse_transform([pred])[0]
            st.success(f"🎯 Based on your inputs, we recommend: **{career}**")

            st.subheader("📈 Top Career Probabilities")
            top_3_idx = np.argsort(proba)[::-1][:3]
            top_3_careers = label_encoder.inverse_transform(top_3_idx)
            top_3_scores = proba[top_3_idx]

            fig, ax = plt.subplots()
            ax.barh(top_3_careers[::-1], top_3_scores[::-1], color="#3498db")
            ax.set_xlabel("Probability")
            ax.set_xlim([0, 1])
            st.pyplot(fig)

            with st.expander("📋 Review Your Inputs"):
                st.write("### Your Selections:")
                for k, v in multi_label_inputs.items():
                    st.write(f"**{k.replace('_', ' ')}:**", ", ".join(v) if v else "None")
                st.write("**Preferred Work Style:**", preferred_style)
                st.write("**Problem Solving Style:**", problem_style)
                st.write("**Wants to go for Masters:**", masters)
                st.write("**Interested in Research:**", research)
                st.write("**CGPA:**", cgpa)
                st.write("**Projects Count:**", projects)
                st.write("**Internship Duration (months):**", internships)

            st.subheader("🎓 Recommended Resources")
            resource_map = {
                "Data Scientist": ["Coursera ML by Andrew Ng", "Kaggle Competitions", "fast.ai"],
                "Cybersecurity Analyst": ["TryHackMe", "HackTheBox", "Cybrary"],
                "DevOps Engineer": ["Docker Mastery", "Learn Kubernetes", "CI/CD with Jenkins"],
                "Software Developer (Backend)": ["System Design Primer", "LeetCode", "Build REST APIs"],
                "UI/UX Designer": ["Google UX Certification", "Figma Basics", "Design Thinking by IDEO"]
            }
            for role in top_3_careers:
                if role in resource_map:
                    st.markdown(f"**{role} Resources:**")
                    for item in resource_map[role]:
                        st.markdown(f"- {item}")
