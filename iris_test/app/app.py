import streamlit as st
import joblib
import numpy as np
import os

# Load the saved model using an absolute path
model_path = os.path.join(os.path.dirname(__file__), '..', 'savedmodel', 'saved_model.pkl')
model_path = os.path.abspath(model_path)
model = joblib.load(model_path)

st.title("Iris Flower Species Prediction")

st.write("Enter the features below:")

sepal_length = st.slider("Sepal Length (cm)", 4.0, 8.0, 5.0)
sepal_width = st.slider("Sepal Width (cm)", 2.0, 4.5, 3.0)
petal_length = st.slider("Petal Length (cm)", 1.0, 7.0, 1.5)
petal_width = st.slider("Petal Width (cm)", 0.1, 2.5, 0.5)

features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
prediction = model.predict(features)

species = ["Setosa", "Versicolor", "Virginica"]
st.write(f"Predicted species: **{species[prediction[0]]}**")
