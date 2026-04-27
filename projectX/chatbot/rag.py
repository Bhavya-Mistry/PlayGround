import os
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
import json
from sentence_transformers import SentenceTransformer
import re
from typing import Dict, Any, Tuple

load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL and SUPABASE_KEY not set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize embeddings and LLM
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGroq(temperature=0.7, model="openai/gpt-oss-120b")


def add_document(text, metadata):
    """
    Add a document to Supabase with embedding.

    Args:
        text: Document content
        metadata: Dict with source, subject, from, date, etc.
    """
    try:
        embedding = embeddings.embed_query(text)

        # Insert into Supabase
        data = (
            supabase.table("documents")
            .insert(
                {
                    "source": metadata.get("source", "unknown"),
                    "subject": metadata.get("subject", "No Subject"),
                    "from_addr": metadata.get("from", "Unknown"),
                    "date": metadata.get("date", "Unknown"),
                    "content": text,
                    "embedding": embedding,
                }
            )
            .execute()
        )

        return True
    except Exception as e:
        print(f"❌ Error adding document: {e}")
        return False


def search_documents(question, limit=5, filters=None):
    """
    Search for documents similar to the question with optional metadata filtering.

    Args:
        question: User's question
        limit: Number of results to return
        filters: Dict with metadata filters (e.g., {"source": "gmail"})

    Returns:
        List of similar documents
    """
    try:
        query_embedding = embeddings.embed_query(question)

        # Prepare RPC parameters with filters
        rpc_params = {"query_embedding": query_embedding, "match_count": limit}

        if filters:
            rpc_params.update(
                {
                    "source_filter": filters.get("source"),
                    "subject_filter": filters.get("subject"),
                    "from_filter": filters.get("from"),
                }
            )

        # Call Supabase RPC function for vector similarity with filters
        result = supabase.rpc("match_documents", rpc_params).execute()

        return result.data if result.data else []
    except Exception as e:
        print(f"❌ Error searching documents: {e}")
        return []


def extract_search_intent(question: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extract search string and metadata filters from user question using LLM.

    Args:
        question: User's natural language question

    Returns:
        Tuple of (search_query, filters_dict)
    """
    try:
        # Create a prompt for the LLM to extract intent
        intent_prompt = f"""You are a search intent extractor. Analyze the user's question and determine:
1. The core search terms (what to search for)
2. Any metadata filters (what type of data to search in)

Available data sources:
- gmail: emails and messages
- drive: documents and files  
- calendar: meetings and events

Examples:
"What are my upcoming meetings?" -> search: "upcoming meetings", filter: {{"source": "calendar"}}
"Show me emails from John" -> search: "emails from John", filter: {{"source": "gmail", "from": "John"}}
"Find documents about project X" -> search: "documents about project X", filter: {{"source": "drive"}}
"What did Sarah say about the budget?" -> search: "Sarah budget", filter: {{"source": "gmail", "from": "Sarah"}}

User question: {question}

Respond in JSON format:
{{"search": "core search terms", "filters": {{"source": "source_name", "from": "person_name", "subject": "subject_keywords"}}}}

If no specific filters are needed, use empty filters: {{"filters": {{}}}}"""

        # Get LLM response
        response = llm.invoke(intent_prompt).content.strip()

        # Extract JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            intent_data = json.loads(json_match.group())
            search_query = intent_data.get("search", question)
            filters = intent_data.get("filters", {})

            # Clean up filters - remove None values
            filters = {k: v for k, v in filters.items() if v is not None and v != ""}

            return search_query, filters
        else:
            return question, {}

    except Exception as e:
        print(f"❌ Error extracting search intent: {e}")
        # Fallback to original question with no filters
        return question, {}


def ask_jarvis(question):
    """
    Ask Jarvis a question with full context from your data using self-querying retrieval.

    Args:
        question: User's question

    Returns:
        (answer, sources) tuple
    """
    try:
        # Extract search intent and filters
        search_query, filters = extract_search_intent(question)

        # Debug: Show what the AI extracted
        print(f"🔍 Search Query: {search_query}")
        print(f"🎯 Filters Applied: {filters}")

        # Search for relevant documents with intelligent filtering
        docs = search_documents(search_query, limit=5, filters=filters)

        if not docs:
            return (
                "Sorry, I don't have any context about that yet. Add more data to your Jarvis!",
                [],
            )

        # Build context from documents
        context = "\n\n".join(
            [
                f"[{d['source'].upper()} - {d['date']}]\nSubject: {d['subject']}\nFrom: {d['from_addr']}\n\nContent:\n{d['content'][:500]}"
                for d in docs
            ]
        )

        # Ask LLM with context
        prompt = f"""You are Jarvis, a personal AI assistant with full context of the user's data.

CONTEXT FROM USER'S DATA:
{context}

USER QUESTION: {question}

Answer the question using the context provided. Be helpful, specific, and reference the context when relevant. Avoid providing answers in tables. Just use bullet points."""

        response = llm.invoke(prompt).content

        return response, docs
    except Exception as e:
        print(f"❌ Error in ask_jarvis: {e}")
        return f"Error: {str(e)}", []


def get_db_stats():
    """Get statistics about the database."""
    try:
        result = supabase.table("documents").select("count", count="exact").execute()
        count = result.count if hasattr(result, "count") else 0
        return {"total_documents": count, "status": "✅ Connected to Supabase"}
    except Exception as e:
        return {"total_documents": 0, "status": f"❌ Error: {str(e)}"}
