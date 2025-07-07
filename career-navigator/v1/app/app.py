import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load trained components
model = joblib.load(r"career-navigator\v1\saved-models\career_model.pkl")
mlb_dict = joblib.load(r"career-navigator\v1\saved-models\mlb_dict.pkl")
label_encoder = joblib.load(r"career-navigator\v1\saved-models\label_encoder.pkl")

st.set_page_config(page_title="Career Navigator", layout="centered")
st.title("🎓 AI-Powered Career Predictor")

st.markdown("Fill in your details below and we'll suggest the best-fit career path for you.")

# Multiselect inputs
multi_label_inputs = {}
for col in mlb_dict.keys():
    options = mlb_dict[col].classes_
    selected = st.multiselect(f"{col.replace('_', ' ')}", options)
    multi_label_inputs[col] = selected

# Single-select fields
preferred_style = st.selectbox("Preferred Work Style", ["Remote", "Hybrid", "Onsite"])
problem_style = st.selectbox("Problem Solving Style", ["Analytical", "Creative", "Logical", "Experimental"])
masters = st.radio("Do you want to go for Masters?", ["Yes", "No"])
research = st.radio("Interested in Research?", ["Yes", "No"])

# Numeric inputs
cgpa = st.slider("Current CGPA", 4.0, 10.0, 7.5, 0.1)
projects = st.number_input("Current Projects Count", min_value=0, step=1)
internships = st.number_input("Internship Duration (in months)", min_value=0, step=1)

# Mapping for styles
work_style_map = {"Remote": 0, "Hybrid": 1, "Onsite": 2}
problem_style_map = {"Analytical": 0, "Creative": 1, "Logical": 2, "Experimental": 3}

# Prepare input vector
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

# Prediction
if st.button("🚀 Predict My Career"):
    input_df = prepare_input()
    pred = model.predict(input_df)[0]
    career = label_encoder.inverse_transform([pred])[0]
    st.success(f"🎯 Based on your inputs, we recommend the career path: **{career}**")
