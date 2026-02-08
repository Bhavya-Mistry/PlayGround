from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String, index=True)
    pr_number = Column(Integer)
    ai_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewResponse(BaseModel):
    id: int
    repo_name: str
    pr_number: int
    ai_feedback: str
    created_at: datetime

    class Config:
        from_attributes = True  # Tells Pydantic to read standard Python objects


def init_db():
    Base.metadata.create_all(bind=engine)
