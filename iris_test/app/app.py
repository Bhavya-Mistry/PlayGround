import streamlit as st
import joblib
import numpy as np

# Load the saved model
model = joblib.load("savedmodel/saved_model.pkl")


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
