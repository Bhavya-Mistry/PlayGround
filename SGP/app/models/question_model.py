from pydantic import BaseModel
from typing import List, Dict, Union, Optional

class Question(BaseModel):
    id: str
    text: str
    category: str # e.g., "HR" or "Technical"
    domain: Optional[str] = None # e.g., "Python", "Behavioral"
    ideal_answer: str = ""
    keywords: List[str] = []