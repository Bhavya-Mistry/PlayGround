import sqlite3
import json
import logging
from pathlib import Path

from app.core.config import get_settings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)

DB_PATH = Path("data/phonetics.db")
FAISS_DIR = Path("data/faiss_index")

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                pos TEXT NOT NULL,
                original_options TEXT NOT NULL,
                selected_gujarati TEXT NOT NULL,
                selected_ipa TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def _get_embeddings():
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004", 
        google_api_key=settings.GEMINI_API_KEY
    )

def save_feedback(word: str, pos: str, original_options: list[dict], selected_gujarati: str, selected_ipa: str):
    """Save feedback to SQLite and FAISS for semantic vector search."""
    # 1. Save to SQLite
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (word, pos, original_options, selected_gujarati, selected_ipa)
            VALUES (?, ?, ?, ?, ?)
        """, (word, pos, json.dumps(original_options, ensure_ascii=False), selected_gujarati, selected_ipa))
        row_id = cursor.lastrowid
        conn.commit()

    # 2. Save to FAISS
    try:
        embeddings = _get_embeddings()
        metadata = {"id": row_id}
        
        if FAISS_DIR.exists():
            faiss_index = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
            faiss_index.add_texts(texts=[word], metadatas=[metadata])
        else:
            faiss_index = FAISS.from_texts(texts=[word], embedding=embeddings, metadatas=[metadata])
            
        faiss_index.save_local(str(FAISS_DIR))
        logger.info(f"Successfully saved '{word}' to FAISS semantic index.")
    except Exception as e:
        logger.error(f"Failed to save to FAISS: {e}")

def get_similar_feedback(word: str, limit: int = 5) -> list[dict]:
    """Retrieve the most semantically similar feedback entries from FAISS & SQLite."""
    if not FAISS_DIR.exists() or not DB_PATH.exists():
        return []
        
    try:
        # 1. Query FAISS for semantic matches
        embeddings = _get_embeddings()
        faiss_index = FAISS.load_local(str(FAISS_DIR), embeddings, allow_dangerous_deserialization=True)
        results = faiss_index.similarity_search(word, k=limit)
        
        if not results:
            return []
            
        # Extract row IDs
        row_ids = [doc.metadata["id"] for doc in results]
        placeholders = ",".join("?" * len(row_ids))
        
        # 2. Fetch full context from SQLite using IDs
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT word, pos, original_options, selected_gujarati, selected_ipa 
                FROM feedback 
                WHERE id IN ({placeholders})
            """, row_ids)
            
            return [dict(row) for row in cursor.fetchall()]
            
    except Exception as e:
        logger.error(f"Failed to retrieve similar feedback: {e}")
        return []
