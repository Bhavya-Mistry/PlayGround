import joblib
import numpy as np
import streamlit as st

# Load pipeline (includes scaler + model)
pipeline = joblib.load("E:/PlayGround/Pipeline_1/pipeline_model.pkl")

st.title("Iris Classifier")

sepal_length = st.number_input("Sepal Length", min_value=4.0, max_value=8.0, value=5.0)
sepal_width = st.number_input("Sepal Width", min_value=2.0, max_value=4.5, value=3.0)
petal_length = st.number_input("Petal Length", min_value=1.0, max_value=7.0, value=1.5)
petal_width = st.number_input("Petal Width", min_value=0.1, max_value=2.5, value=0.5)

features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
species = ["Setosa", "Versicolor", "Virginica"]

button = st.button("Predict")
if button:
    try:
        prediction = pipeline.predict(features)
        st.success(f"The predicted species is: **{species[prediction[0]]}**")
    except Exception as e:
        st.error(f"Prediction failed. Error: {str(e)}")
