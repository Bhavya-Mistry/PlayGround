import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run():
    # Load trained components
    model = joblib.load(r"v2\saved-models\career_model.pkl")
    mlb_dict = joblib.load(r"v2\saved-models\mlb_dict.pkl")
    label_encoder = joblib.load(r"v2\saved-models\label_encoder.pkl")

    st.title("AI-Powered Career Navigator")
    st.markdown("""
    Welcome to the Career Navigator tool powered by AI.

    Fill in your academic, technical, and personal interests, and our model will help predict your ideal career path and guide you with resources to get there.
    """)

    # --- Sidebar: User Details ---
    st.sidebar.header(" Enter Your Details")

    multi_label_inputs = {}
    for col in mlb_dict.keys():
        options = mlb_dict[col].classes_
        selected = st.sidebar.multiselect(f"{col.replace('_', ' ')}", options)
        multi_label_inputs[col] = selected

    preferred_style = st.sidebar.selectbox("Preferred Work Style", ["Remote", "Hybrid", "Onsite"])
    problem_style = st.sidebar.selectbox("Problem Solving Style", ["Analytical", "Creative", "Logical", "Experimental"])
    masters = st.sidebar.radio("Do you want to go for Masters?", ["Yes", "No"])
    research = st.sidebar.radio("Interested in Research?", ["Yes", "No"])
    cgpa = st.sidebar.slider("Current CGPA", 2.0, 10.0, 7.5, 0.1)
    projects = st.sidebar.number_input("Current Projects Count", min_value=0, step=1)
    internships = st.sidebar.number_input("Internship Duration (in months)", min_value=0, step=1)

    # Mapping for styles
    work_style_map = {"Remote": 0, "Hybrid": 1, "Onsite": 2}
    problem_style_map = {"Analytical": 0, "Creative": 1, "Logical": 2, "Experimental": 3}

    # --- Prepare Input Vector ---
    def prepare_input():
        feature_parts = []

        for col, mlb in mlb_dict.items():
            selected_values = multi_label_inputs[col]
            encoded = mlb.transform([selected_values])
            df = pd.DataFrame(encoded, columns=[f"{col}_{c}" for c in mlb.classes_])
            feature_parts.append(df)

        other_features = pd.DataFrame([{
            "Preferred_Work_Style": work_style_map.get(preferred_style, 0),
            "Problem_Solving_Style": problem_style_map.get(problem_style, 0),
            "Wants_to_Go_for_Masters": 1 if masters.lower() == "yes" else 0,
            "Interested_in_Research": 1 if research.lower() == "yes" else 0,
            "CGPA": cgpa,
            "Current_Projects_Count": projects,
            "Internship_Experience": internships
        }])

        feature_parts.append(other_features)
        final_input = pd.concat(feature_parts, axis=1)

        # Fill missing cols if any
        for col in model.feature_names_in_:
            if col not in final_input:
                final_input[col] = 0

        return final_input[model.feature_names_in_]

    # --- Predict Button ---
    if st.button("Predict My Career"):
        input_df = prepare_input()
        pred = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0]

        career = label_encoder.inverse_transform([pred])[0]
        st.success(f"\U0001F3AF Based on your inputs, we recommend: **{career}**")

        # --- Show Top 3 Probable Careers ---
        st.subheader("Top Career Probabilities")
        top_3_idx = np.argsort(proba)[::-1][:3]
        top_3_careers = label_encoder.inverse_transform(top_3_idx)
        top_3_scores = proba[top_3_idx]

        fig, ax = plt.subplots()
        ax.barh(top_3_careers[::-1], top_3_scores[::-1], color="skyblue")
        ax.set_xlabel("Probability")
        ax.set_xlim([0, 1])
        st.pyplot(fig)

        # --- Expandable Section: Your Input Summary ---
        with st.expander("Review Your Inputs"):
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

        # --- Show Resource Suggestions ---
        # st.sidebar.header("Enter Your Details")

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
