import streamlit as st
import requests

st.title("Iris Species Predictor")

st.write("Enter Flower's measurements below to predict its species")

sepal_length = st.number_input("Sepal Length (cm)", min_value=0.0, max_value=10.0, value=5.0)
sepal_width = st.number_input("Sepal width (cm)", min_value=0.0, max_value=10.0, value=5.0)
petal_length = st.number_input("Petal_length (cm)", min_value=0.0, max_value=10.0, value=5.0)
petal_width = st.number_input("Petal Width (cm)", min_value=0.0, max_value=10.0, value=5.0)

if (st.button("Predict Species")):
    payload = {
        "SepalLengthCm" : sepal_length,
        "SepalWidthCm" : sepal_width,
        "PetalLengthCm" : petal_length,
        "PetalWidthCm" : petal_width
    }
    try:
        res = requests.post("http://127.0.0.1:8000/predict", json=payload)
        res.raise_for_status()
        result = res.json()
        st.success(f"Predicted species: **{result['predicted_species']}**")
    except Exception as e:
        st.error("Failed to contact FastAPI")
        st.exception(e)