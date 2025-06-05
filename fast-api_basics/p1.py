# filename: main.py

from fastapi import FastAPI
from pydantic import BaseModel

# Initialize app
app = FastAPI()

# Sample input schema
class InputData(BaseModel):
    feature1: float
    feature2: float

# Home route
@app.get("/")
def read_root():
    return {"message": "Welcome to your first FastAPI app!"}

# Predict route
@app.post("/predict")
def predict(data: InputData):
    # Dummy logic (in real case, load your ML model and use it here)
    result = data.feature1 + data.feature2
    return {"prediction": result}
