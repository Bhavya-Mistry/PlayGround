from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel # Import BaseModel here as AnswerRequest uses it
from app.models.question_model import Question
from app.models.evaluation_model import Feedback
from app.services.question_service import question_service_instance
from app.ml.evaluator import nlp_evaluator_instance
import random

router = APIRouter()

@router.get("/questions/random/{category}", response_model=Question, summary="Get a random question by category")
async def get_random_question_endpoint(category: str):
    """
    Retrieves a random HR or Technical question.
    """
    question = question_service_instance.get_random_question(category)
    if not question:
        raise HTTPException(status_code=404, detail=f"No questions found for category: {category}")
    return question

@router.get("/questions/{category}/{question_id}", response_model=Question, summary="Get a specific question by ID and category")
async def get_specific_question_endpoint(category: str, question_id: str):
    """
    Retrieves a specific HR or Technical question by its ID.
    """
    question = question_service_instance.get_question_by_id(question_id, category)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question with ID '{question_id}' not found in category '{category}'.")
    return question

class AnswerRequest(BaseModel):
    user_answer: str
    question_id: str
    category: str

@router.post("/evaluate_answer", response_model=Feedback, summary="Evaluate a user's answer")
async def evaluate_answer_endpoint(request: AnswerRequest):
    """
    Evaluates a user's answer against an ideal answer using NLP models.
    Provides scores for semantic similarity, grammar, and sentiment, along with feedback.
    """
    question = question_service_instance.get_question_by_id(request.question_id, request.category)
    if not question:
        raise HTTPException(status_code=404, detail=f"Question with ID '{request.question_id}' not found in category '{request.category}'. Cannot evaluate.")
    
    feedback = nlp_evaluator_instance.evaluate_answer(question, request.user_answer)
    return feedback

# Root endpoint for basic health check
@router.get("/", summary="Root endpoint for health check")
async def root():
    return {"message": "AI Interview Coach API is running!"}