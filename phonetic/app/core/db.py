import sqlite3
import json
from pathlib import Path

DB_PATH = Path("data/phonetics.db")

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    # Ensure the data directory exists
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

def save_feedback(word: str, pos: str, original_options: list[dict], selected_gujarati: str, selected_ipa: str):
    """Save a user-approved pronunciation to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (word, pos, original_options, selected_gujarati, selected_ipa)
            VALUES (?, ?, ?, ?, ?)
        """, (word, pos, json.dumps(original_options, ensure_ascii=False), selected_gujarati, selected_ipa))
        conn.commit()

def get_recent_feedback(limit: int = 5) -> list[dict]:
    """Retrieve the most recent feedback entries to inject into the LLM prompt."""
    try:
        if not DB_PATH.exists():
            return []
            
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT word, pos, original_options, selected_gujarati, selected_ipa 
                FROM feedback 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error:
        return []
