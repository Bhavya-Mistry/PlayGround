from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.resume_parser import parse_resume
from app.prompts import build_ats_prompt
from app.gemini_handler import get_gemini_response
import joblib
import pandas as pd
import tempfile
import os

app = FastAPI(title="Career Navigator API")

# Load models and encoders for career prediction (on startup)
career_model = None
mlb_dict = None
label_encoder = None

@app.on_event("startup")
def load_models():
    global career_model, mlb_dict, label_encoder
    career_model = joblib.load(r"saved-models/career_model.pkl")
    mlb_dict = joblib.load(r"saved-models/mlb_dict.pkl")
    label_encoder = joblib.load(r"saved-models/label_encoder.pkl")

@app.get("/")
def root():
    return {"message": "Career Navigator FastAPI is running!"}

@app.post("/parse-resume/")
def parse_resume_endpoint(file: UploadFile = File(...)):
    """Extract text from uploaded resume (PDF/DOCX)."""
    try:
        text = parse_resume(file)
        return {"resume_text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ats-score/")
def ats_score_endpoint(
    file: UploadFile = File(...),
    job_role: str = Form("Software Engineer")
):
    """Evaluate resume for ATS score and summary."""
    try:
        resume_text = parse_resume(file)
        prompt = build_ats_prompt(resume_text, job_role)
        result = get_gemini_response(prompt)
        return {"ats_result": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/predict-career/")
def predict_career(
    features: dict
):
    """Predict career recommendations based on user features (expects JSON)."""
    try:
        # This expects the client to send all necessary features as a dict
        df = pd.DataFrame([features])
        pred = career_model.predict(df)[0]
        label = label_encoder.inverse_transform([pred])[0]
        return {"recommended_career": label}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
