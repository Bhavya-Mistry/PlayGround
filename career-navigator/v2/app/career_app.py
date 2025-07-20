import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit.components.v1 import html

# st.set_page_config(page_title="AI-Powered Career Navigator", layout="wide")

def run():
    # Load trained components
    model = joblib.load("../saved-models/career_model.pkl")
    mlb_dict = joblib.load("../saved-models/mlb_dict.pkl")
    label_encoder = joblib.load("../saved-models/label_encoder.pkl")

    from resume_parser import parse_resume
    from prompts import build_ats_prompt
    from gemini_handler import get_gemini_response
    import plotly.graph_objects as go

    st.set_page_config(page_title="Career Navigator", layout="wide", page_icon="🚀")
    st.markdown(
        """
        <style>
        body {background-color: #f5f7fa;}
        .main-title {
            font-size: 2.6em;
            font-weight: 700;
            color: #1a237e;
            text-align: center;
            margin-top: 10px;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        .section-header {
            font-size: 1.3em;
            color: #3949ab;
            font-weight: 600;
            margin-top: 1.2em;
            margin-bottom: 0.5em;
        }
        .stButton>button {
            background: linear-gradient(90deg, #3949ab 0%, #00c6ff 100%);
            color: white;
            border-radius: 8px;
            height: 2.8em;
            font-size: 1.1em;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(33,150,243,0.08);
            border: none;
        }
        .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div>input {
            border-radius: 6px;
            border: 1px solid #90caf9;
            background: #f7fbff;
        }
        .stMultiSelect>div>div>div>input {
            border-radius: 6px;
            border: 1px solid #90caf9;
            background: #f7fbff;
        }
        .stSlider>div>div>div>input {
            background: #e3f2fd;
        }
        .stRadio>div>div {
            background: #e3f2fd;
            border-radius: 6px;
            padding: 0.25em 0.5em;
        }
        .stExpanderHeader {
            font-size: 1.1em;
            color: #1976d2;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
        <div class='main-title'>🚀 Career Navigator & ATS</div>
        <p style='text-align:center; color:#374151; font-size:1.15em;'>
            Get personalized career recommendations and evaluate your resume for any job role.<br>
            <span style='color:#1976d2;'>AI-powered, modern, and user-friendly.</span>
        </p>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='section-header'>📝 Profile Information</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            multi_label_inputs = {}
            for col in mlb_dict.keys():
                options = mlb_dict[col].classes_
                selected = st.multiselect(f"{col.replace('_', ' ')}", options, help=f"Select your {col.replace('_', ' ')}")
                multi_label_inputs[col] = selected
            preferred_style = st.selectbox("Preferred Work Style", ["Remote", "Hybrid", "Onsite"], help="Where do you prefer to work?")
            problem_style = st.selectbox("Problem Solving Style", ["Analytical", "Creative", "Logical", "Experimental"], help="How do you approach problems?")
            masters = st.radio("Do you want to go for Masters?", ["Yes", "No"], horizontal=True)
            research = st.radio("Interested in Research?", ["Yes", "No"], horizontal=True)
        with col2:
            cgpa = st.slider("Current CGPA", 2.0, 10.0, 7.5, 0.1, help="Your latest CGPA")
            projects = st.number_input("Current Projects Count", min_value=0, step=1, help="How many projects have you done?")
            internships = st.number_input("Internship Duration (in months)", min_value=0, step=1, help="Total months of internship experience")

    st.markdown("<div class='section-header'>🎯 Career Prediction</div>", unsafe_allow_html=True)
    with st.container():
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

        pred_col, prob_col = st.columns([1, 1])
        with pred_col:
            if st.button("🔍 Predict My Career", use_container_width=True):
                input_df = prepare_input()
                pred = model.predict(input_df)[0]
                proba = model.predict_proba(input_df)[0]
                career = label_encoder.inverse_transform([pred])[0]
                st.success(f"🎯 We recommend: **{career}**", icon="🎯")
                st.markdown("<div style='margin-top:0.5em;'></div>", unsafe_allow_html=True)
                st.markdown("<b>Your Selections:</b>", unsafe_allow_html=True)
                for k, v in multi_label_inputs.items():
                    st.markdown(f"- <span style='color:#1976d2'><b>{k.replace('_', ' ')}:</b></span> {', '.join(v) if v else 'None'}", unsafe_allow_html=True)
                st.markdown(f"- <b>Preferred Work Style:</b> {preferred_style}", unsafe_allow_html=True)
                st.markdown(f"- <b>Problem Solving Style:</b> {problem_style}", unsafe_allow_html=True)
                st.markdown(f"- <b>Wants to go for Masters:</b> {masters}", unsafe_allow_html=True)
                st.markdown(f"- <b>Interested in Research:</b> {research}", unsafe_allow_html=True)
                st.markdown(f"- <b>CGPA:</b> {cgpa}", unsafe_allow_html=True)
                st.markdown(f"- <b>Projects Count:</b> {projects}", unsafe_allow_html=True)
                st.markdown(f"- <b>Internship Duration (months):</b> {internships}", unsafe_allow_html=True)
        with prob_col:
            if st.button("📈 Show Career Probabilities", use_container_width=True):
                input_df = prepare_input()
                proba = model.predict_proba(input_df)[0]
                top_3_idx = np.argsort(proba)[::-1][:3]
                top_3_careers = label_encoder.inverse_transform(top_3_idx)
                top_3_scores = proba[top_3_idx]
                fig = go.Figure(go.Bar(
                    x=top_3_scores[::-1],
                    y=top_3_careers[::-1],
                    orientation='h',
                    marker=dict(color=['#1976d2', '#00c6ff', '#3949ab'])
                ))
                fig.update_layout(
                    xaxis_title="Probability",
                    yaxis_title="Career",
                    template="simple_white",
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-header'>🎓 Recommended Resources</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("Get started with these resources for your top careers:")
        resource_map = {
            "Data Scientist": ["Coursera ML by Andrew Ng", "Kaggle Competitions", "fast.ai"],
            "Cybersecurity Analyst": ["TryHackMe", "HackTheBox", "Cybrary"],
            "DevOps Engineer": ["Docker Mastery", "Learn Kubernetes", "CI/CD with Jenkins"],
            "Software Developer (Backend)": ["System Design Primer", "LeetCode", "Build REST APIs"],
            "UI/UX Designer": ["Google UX Certification", "Figma Basics", "Design Thinking by IDEO"]
        }
        # This is just an example; you may want to use top_3_careers from prediction
        for role, resources in resource_map.items():
            with st.expander(f"{role} Resources", expanded=False):
                for item in resources:
                    st.markdown(f"- {item}")

    # --- ATS Resume Parsing & Scoring Section ---
    ats_col1, ats_col2, ats_col3 = st.columns([1,1,1])
    with ats_col2:
        show_ats = st.button("📝 ATS Resume Check", key="show_ats_button", use_container_width=True)
    if show_ats:
        st.header("ATS Resume Parsing & Score")
        st.markdown("Upload your resume and check how it performs against your target job role.")
        uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"], key="ats_resume")
        job_role = st.text_input("Target Job Role for ATS", value="Software Engineer", key="ats_job_role")
        if uploaded_file and st.button("Parse & Score Resume", key="ats_button", use_container_width=True):
            with st.spinner("Reading your resume..."):
                resume_text = parse_resume(uploaded_file)
            if resume_text.startswith("Unsupported"):
                st.error(resume_text)
            else:
                st.subheader("Extracted Resume Text")
                st.text_area("Preview", resume_text, height=250)
                with st.spinner("Sending to Gemini for evaluation..."):
                    prompt = build_ats_prompt(resume_text, job_role)
                    result = get_gemini_response(prompt)
                st.subheader("ATS Evaluation Result")
                st.markdown(result)

    # st.markdown("""<div class='main-title'>🚀 AI-Powered Career Navigator</div>""", unsafe_allow_html=True)
    # st.markdown("""<div class='intro-text'>Fill in your academic, technical, and personal interests to receive your personalized career prediction.</div>""", unsafe_allow_html=True)

    # col1, col2 = st.columns([1, 2])

    # with col1:
    #     st.header("📝 Your Profile")

    #     multi_label_inputs = {}
    #     for col in mlb_dict.keys():
    #         options = mlb_dict[col].classes_
    #         selected = st.multiselect(f"{col.replace('_', ' ')}", options)
    #         multi_label_inputs[col] = selected

    #     preferred_style = st.selectbox("Preferred Work Style", ["Remote", "Hybrid", "Onsite"])
    #     problem_style = st.selectbox("Problem Solving Style", ["Analytical", "Creative", "Logical", "Experimental"])
    #     masters = st.radio("Do you want to go for Masters?", ["Yes", "No"])
    #     research = st.radio("Interested in Research?", ["Yes", "No"])
    #     cgpa = st.slider("Current CGPA", 2.0, 10.0, 7.5, 0.1)
    #     projects = st.number_input("Current Projects Count", min_value=0, step=1)
    #     internships = st.number_input("Internship Duration (in months)", min_value=0, step=1)

    # with col2:
    #     st.header("📊 Results")

    #     def prepare_input():
    #         feature_parts = []
    #         for col, mlb in mlb_dict.items():
    #             selected_values = multi_label_inputs[col]
    #             encoded = mlb.transform([selected_values])
    #             df = pd.DataFrame(encoded, columns=[f"{col}_{c}" for c in mlb.classes_])
    #             feature_parts.append(df)

    #         other_features = pd.DataFrame([{
    #             "Preferred_Work_Style": {"Remote": 0, "Hybrid": 1, "Onsite": 2}.get(preferred_style, 0),
    #             "Problem_Solving_Style": {"Analytical": 0, "Creative": 1, "Logical": 2, "Experimental": 3}.get(problem_style, 0),
    #             "Wants_to_Go_for_Masters": 1 if masters.lower() == "yes" else 0,
    #             "Interested_in_Research": 1 if research.lower() == "yes" else 0,
    #             "CGPA": cgpa,
    #             "Current_Projects_Count": projects,
    #             "Internship_Experience": internships
    #         }])
    #         feature_parts.append(other_features)
    #         final_input = pd.concat(feature_parts, axis=1)
    #         for col in model.feature_names_in_:
    #             if col not in final_input:
    #                 final_input[col] = 0
    #         return final_input[model.feature_names_in_]

    #     if st.button("🎯 Predict My Career"):
    #         input_df = prepare_input()
    #         pred = model.predict(input_df)[0]
    #         proba = model.predict_proba(input_df)[0]
    #         career = label_encoder.inverse_transform([pred])[0]
    #         st.success(f"🎯 Based on your inputs, we recommend: **{career}**")

    #         st.subheader("📈 Top Career Probabilities")
    #         top_3_idx = np.argsort(proba)[::-1][:3]
    #         top_3_careers = label_encoder.inverse_transform(top_3_idx)
    #         top_3_scores = proba[top_3_idx]

    #         fig, ax = plt.subplots()
    #         ax.barh(top_3_careers[::-1], top_3_scores[::-1], color="#3498db")
    #         ax.set_xlabel("Probability")
    #         ax.set_xlim([0, 1])
    #         st.pyplot(fig)

    #         with st.expander("📋 Review Your Inputs"):
    #             st.write("### Your Selections:")
    #             for k, v in multi_label_inputs.items():
    #                 st.write(f"**{k.replace('_', ' ')}:**", ", ".join(v) if v else "None")
    #             st.write("**Preferred Work Style:**", preferred_style)
    #             st.write("**Problem Solving Style:**", problem_style)
    #             st.write("**Wants to go for Masters:**", masters)
    #             st.write("**Interested in Research:**", research)
    #             st.write("**CGPA:**", cgpa)
    #             st.write("**Projects Count:**", projects)
    #             st.write("**Internship Duration (months):**", internships)

    #         st.subheader("🎓 Recommended Resources")
    #         resource_map = {
    #             "Data Scientist": ["Coursera ML by Andrew Ng", "Kaggle Competitions", "fast.ai"],
    #             "Cybersecurity Analyst": ["TryHackMe", "HackTheBox", "Cybrary"],
    #             "DevOps Engineer": ["Docker Mastery", "Learn Kubernetes", "CI/CD with Jenkins"],
    #             "Software Developer (Backend)": ["System Design Primer", "LeetCode", "Build REST APIs"],
    #             "UI/UX Designer": ["Google UX Certification", "Figma Basics", "Design Thinking by IDEO"]
    #         }
    #         for role in top_3_careers:
    #             if role in resource_map:
    #                 st.markdown(f"**{role} Resources:**")
    #                 for item in resource_map[role]:
    #                     st.markdown(f"- {item}")

    # # --- ATS Resume Parsing & Scoring Section ---
    # show_ats = st.button("Show Resume Parsing & ATS Score Section", key="show_ats_button")
    # if show_ats:
    #     st.header("Resume Parsing & ATS Score")
    #     uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"], key="ats_resume")
    #     job_role = st.text_input("Target Job Role for ATS", value="Software Engineer", key="ats_job_role")
    #     if uploaded_file and st.button("Parse & Score Resume", key="ats_button"):
    #         with st.spinner("Reading your resume..."):
    #             resume_text = parse_resume(uploaded_file)
    #         if resume_text.startswith("Unsupported"):
    #             st.error(resume_text)
    #         else:
    #             st.subheader("Extracted Resume Text")
    #             st.text_area("Preview", resume_text, height=250)
    #             with st.spinner("Sending to Gemini for evaluation..."):
    #                 prompt = build_ats_prompt(resume_text, job_role)
    #                 result = get_gemini_response(prompt)
    #             st.subheader("ATS Evaluation Result")
    #             st.markdown(result)


if __name__ == "__main__":
    run()
