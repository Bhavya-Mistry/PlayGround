from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI()

# Load model (use correct path based on your current directory)
model = joblib.load("iris_logistic_model.pkl")

class IrisFeatures(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float  # Fixed casing

@app.get("/")
def root():
    return {
        "message": "Iris logistic regression API is running"
    }

@app.post("/predict")
def predict_species(features: IrisFeatures):
    data = np.array([[features.SepalLengthCm, features.SepalWidthCm,
                      features.PetalLengthCm, features.PetalWidthCm]])
    prediction = model.predict(data)

    return {
        "predicted_species": prediction[0]
    }