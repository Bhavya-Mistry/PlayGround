import spacy
from textblob import TextBlob
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import List, Dict, Any, Tuple
import re
import os # Import os for environment variable check

from app.models.question_model import Question
from app.models.evaluation_model import Feedback

class NLPEvaluator:
    _instance = None # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLPEvaluator, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Check if models are already loaded to prevent re-loading on multiple instantiations
        if hasattr(self, '_initialized') and self._initialized:
            return

        print("Initializing NLPEvaluator: Loading models...")
        # Load SentenceTransformer model
        # 'all-MiniLM-L6-v2' is a good balance of speed and performance.
        # For better accuracy, consider 'all-mpnet-base-v2' but it's larger.
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Load spaCy model for grammar/syntax analysis
        # In a non-Docker setup, this will download if not present.
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("spaCy 'en_core_web_sm' loaded.")
        except OSError:
            print("spaCy model 'en_core_web_sm' not found. Attempting download...")
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
                print("spaCy 'en_core_web_sm' downloaded and loaded successfully.")
            except Exception as e:
                print(f"Error downloading spaCy model: {e}. Grammar analysis might be impaired.")
                self.nlp = None # Set to None if download fails

        # TextBlob relies on NLTK data. It generally handles downloads on first use,
        # but if issues arise, uncomment and run `nltk.download('punkt')` and `nltk.download('wordnet')`
        # import nltk
        # nltk.download('punkt', quiet=True)
        # nltk.download('wordnet', quiet=True)
        
        self._initialized = True
        print("NLPEvaluator initialized.")

    def _calculate_semantic_similarity(self, ideal_answer: str, user_answer: str) -> float:
        """Calculates cosine similarity between embeddings of ideal and user answers."""
        if not ideal_answer or not user_answer:
            return 0.0

        embeddings1 = self.sentence_model.encode(ideal_answer, convert_to_tensor=True)
        embeddings2 = self.sentence_model.encode(user_answer, convert_to_tensor=True)

        cosine_similarity = util.cos_sim(embeddings1, embeddings2).item()
        return round(cosine_similarity * 100, 2)

    def _analyze_grammar(self, text: str) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Analyzes grammar using TextBlob for spelling and basic spaCy-based heuristics.
        This is a rudimentary grammar checker.
        """
        if self.nlp is None:
            return 0.0, [{"type": "Error", "message": "SpaCy model not loaded, grammar analysis skipped."}]

        errors = []
        doc = self.nlp(text)
        
        # 1. Spelling errors with TextBlob
        text_blob = TextBlob(text)
        spelling_corrections = text_blob.correct()
        spelling_errors_count = sum(1 for original, corrected in zip(text_blob.words, spelling_corrections.words) if original != corrected)
        
        if spelling_errors_count > 0:
            errors.append({
                "type": "Spelling",
                "message": f"Found {spelling_errors_count} potential spelling error(s).",
                "details": [] # Could add details of specific errors if needed
            })
        
        # 2. Punctuation checks (simple)
        sentences = [sent.text.strip() for sent in doc.sents]
        for i, sent in enumerate(sentences):
            if i < len(sentences) - 1: # Don't check the very last sentence's end if it's the last thing
                if not re.search(r'[.!?]$', sent):
                    errors.append({
                        "type": "Punctuation",
                        "message": f"Sentence {i+1} might be missing end punctuation ('.', '!', '?').",
                        "details": sent
                    })
            # Check for starting capitalization (simple, can be fooled by names/acronyms)
            if sent and not sent[0].isupper() and len(sent) > 2: # Ignore very short "sentences" like 'oh.'
                 errors.append({
                    "type": "Capitalization",
                    "message": f"Sentence {i+1} might not start with a capital letter.",
                    "details": sent
                })

        # 3. Conciseness/Completeness heuristic (penalize extremely short answers relative to expected)
        word_count = len([token for token in doc if not token.is_punct and not token.is_space])
        
        grammar_score = 100.0 # Start perfect, then deduct
        
        # Arbitrary penalties
        grammar_score -= min(spelling_errors_count * 10, 50) # Max 50 points off for spelling
        grammar_score -= min(len([e for e in errors if e["type"] == "Punctuation"]) * 5, 20) # Max 20 for punctuation
        grammar_score -= min(len([e for e in errors if e["type"] == "Capitalization"]) * 5, 20) # Max 20 for capitalization
        
        # If the answer is too short for a typical interview response, penalize.
        # This threshold might need tuning.
        if word_count < 20 and grammar_score > 50: # If it's short but otherwise seems fine
            errors.append({"type": "Conciseness/Completeness", "message": "Answer might be too short for a comprehensive response.", "details": f"Word count: {word_count}"})
            grammar_score = max(0, grammar_score - 20) # Apply a penalty

        return round(max(0, grammar_score), 2), errors # Ensure score is not negative

    def _analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """Analyzes sentiment of the text using TextBlob."""
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity # -1.0 (negative) to +1.0 (positive)

        # Scale polarity to 0-100 score
        sentiment_score = round((polarity + 1) * 50, 2) # Convert to 0-100 range

        if polarity > 0.3:
            sentiment_feedback = "Your answer conveys a positive and confident tone."
        elif polarity < -0.3:
            sentiment_feedback = "Consider a more neutral or positive tone in your response."
        else:
            sentiment_feedback = "Your answer has a neutral tone."

        return sentiment_score, sentiment_feedback

    def evaluate_answer(self, question: Question, user_answer: str) -> Feedback:
        """
        Evaluates a user's answer based on semantic similarity, grammar, and sentiment.
        """
        # Minimum length check for meaningful analysis
        if not user_answer or len(user_answer.strip()) < 10: # Increased minimum length
            return Feedback(
                overall_score=0.0,
                semantic_similarity_score=0.0,
                grammar_score=0.0,
                sentiment_score=0.0,
                semantic_feedback="Please provide a more substantial answer for evaluation (minimum 10 characters).",
                grammar_feedback="Answer too short for meaningful grammar analysis.",
                sentiment_feedback="Answer too short for meaningful sentiment analysis.",
                suggestions=["Provide a more detailed and complete answer."]
            )

        # 1. Semantic Similarity
        semantic_score = 0.0
        semantic_feedback = "No ideal answer provided for semantic comparison."
        if question.ideal_answer:
            semantic_score = self._calculate_semantic_similarity(question.ideal_answer, user_answer)
            if semantic_score >= 80:
                semantic_feedback = "Excellent! Your answer is highly relevant and semantically close to the ideal response."
            elif semantic_score >= 60:
                semantic_feedback = "Good. Your answer is relevant, but could be more aligned with the key points of the ideal response."
            elif semantic_score >= 40:
                semantic_feedback = "Your answer has some relevance, but try to incorporate more key concepts from the ideal response."
            else:
                semantic_feedback = "Your answer seems to lack significant semantic similarity to the ideal response. Consider revising the core content."
        
        # 2. Grammar Analysis
        grammar_score, raw_grammar_errors = self._analyze_grammar(user_answer)
        grammar_feedback = ""
        suggestions = []

        if grammar_score >= 90:
            grammar_feedback = "Your grammar and spelling are excellent."
        elif grammar_score >= 70:
            grammar_feedback = "Your answer has good grammar, with minor issues."
            if raw_grammar_errors:
                grammar_feedback += " Please review specific points."
        else:
            grammar_feedback = "Your answer has several grammatical or spelling concerns. Focus on clarity and correctness."
            
        # Add suggestions based on grammar errors (simplified)
        if any("Spelling" in err.get("type", "") for err in raw_grammar_errors):
            suggestions.append("Check for spelling mistakes.")
        if any("Punctuation" in err.get("type", "") for err in raw_grammar_errors):
            suggestions.append("Ensure proper punctuation, especially at sentence endings.")
        if any("Capitalization" in err.get("type", "") for err in raw_grammar_errors):
            suggestions.append("Ensure sentences start with a capital letter.")
        if any("Conciseness" in err.get("type", "") for err in raw_grammar_errors):
            suggestions.append("Elaborate further to provide a more complete answer.")


        # 3. Sentiment Analysis
        sentiment_score, sentiment_feedback = self._analyze_sentiment(user_answer)
        if "neutral tone" in sentiment_feedback or "negative tone" in sentiment_feedback:
            suggestions.append("Aim for a more positive and confident tone in your responses.")


        # 4. Overall Score (Weighted Average)
        # You can adjust these weights based on what you prioritize.
        semantic_weight = 0.5
        grammar_weight = 0.3
        sentiment_weight = 0.2

        overall_score = (semantic_score * semantic_weight +
                         grammar_score * grammar_weight +
                         sentiment_score * sentiment_weight)

        # Ensure suggestions are unique
        suggestions = list(set(suggestions))

        return Feedback(
            overall_score=round(overall_score, 2),
            semantic_similarity_score=semantic_score,
            grammar_score=semantic_score if self.nlp is None else grammar_score, # If no spacy, use semantic score as a fallback
            sentiment_score=sentiment_score,
            semantic_feedback=semantic_feedback,
            grammar_feedback=grammar_feedback if self.nlp else "Grammar analysis skipped (model not loaded).",
            sentiment_feedback=sentiment_feedback,
            suggestions=suggestions,
            raw_grammar_errors=raw_grammar_errors
        )

# Singleton instance of NLPEvaluator
nlp_evaluator_instance = NLPEvaluator()