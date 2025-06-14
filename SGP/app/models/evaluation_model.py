from pydantic import BaseModel
from typing import List, Dict, Any

class Feedback(BaseModel):
    overall_score: float
    semantic_similarity_score: float
    grammar_score: float
    sentiment_score: float
    semantic_feedback: str
    grammar_feedback: str
    sentiment_feedback: str
    suggestions: List[str] = []
    raw_grammar_errors: List[Dict[str, Any]] = []