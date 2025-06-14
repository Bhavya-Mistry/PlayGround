import csv
import random
from typing import List, Union, Optional
from app.models.question_model import Question

class QuestionService:
    def __init__(self, hr_csv_file: str = "questions/hr.csv", technical_csv_file: str = "questions/technical.csv"):
        self.hr_csv_file = hr_csv_file
        self.technical_csv_file = technical_csv_file
        self.hr_questions: List[Question] = []
        self.technical_questions: List[Question] = []
        self._load_questions()

    def _load_questions(self):
        """Loads HR and Technical questions from their respective CSV files."""
        self.hr_questions = []
        self.technical_questions = []

        # Load HR questions
        try:
            with open(self.hr_csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    question = Question(
                        id=row['id'],
                        text=row['question'],
                        category=row['type'],
                        domain=row.get('domain', None),
                        ideal_answer=row.get('reference_answer', ''),
                        keywords=[] # Keep empty for now
                    )
                    if question.category.lower() == "hr": # Sanity check for HR file
                        self.hr_questions.append(question)
                    else:
                        print(f"Warning: Question ID {question.id} in {self.hr_csv_file} has unexpected category '{question.category}'. Expected 'HR'.")

        except FileNotFoundError:
            print(f"Error: HR questions CSV file not found at {self.hr_csv_file}. Please ensure the path is correct.")
        except KeyError as e:
            print(f"Error: Missing expected column in {self.hr_csv_file}: {e}. Required: id,type,domain,question,reference_answer")
        except Exception as e:
            print(f"An unexpected error occurred while loading HR questions: {e}")

        # Load Technical questions
        try:
            with open(self.technical_csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    question = Question(
                        id=row['id'],
                        text=row['question'],
                        category=row['type'],
                        domain=row.get('domain', None),
                        ideal_answer=row.get('reference_answer', ''),
                        keywords=[] # Keep empty for now
                    )
                    if question.category.lower() == "technical": # Sanity check for Technical file
                        self.technical_questions.append(question)
                    else:
                        print(f"Warning: Question ID {question.id} in {self.technical_csv_file} has unexpected category '{question.category}'. Expected 'Technical'.")

        except FileNotFoundError:
            print(f"Error: Technical questions CSV file not found at {self.technical_csv_file}. Please ensure the path is correct.")
        except KeyError as e:
            print(f"Error: Missing expected column in {self.technical_csv_file}: {e}. Required: id,type,domain,question,reference_answer")
        except Exception as e:
            print(f"An unexpected error occurred while loading Technical questions: {e}")


    def get_hr_questions(self) -> List[Question]:
        """Returns all loaded HR questions."""
        return self.hr_questions

    def get_technical_questions(self) -> List[Question]:
        """Returns all loaded Technical questions."""
        return self.technical_questions

    def get_random_question(self, category: str) -> Union[Question, None]:
        """Returns a random question from the specified category."""
        if category.lower() == "hr":
            if self.hr_questions:
                return random.choice(self.hr_questions)
        elif category.lower() == "technical":
            if self.technical_questions:
                return random.choice(self.technical_questions)
        return None

    def get_question_by_id(self, question_id: str, category: str) -> Union[Question, None]:
        """Returns a specific question by ID from the specified category."""
        if category.lower() == "hr":
            for q in self.hr_questions:
                if q.id == question_id:
                    return q
        elif category.lower() == "technical":
            for q in self.technical_questions:
                if q.id == question_id:
                    return q
        return None

# Singleton pattern for QuestionService to avoid reloading questions multiple times
question_service_instance = QuestionService()