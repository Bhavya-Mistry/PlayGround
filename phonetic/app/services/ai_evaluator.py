import logging
from typing import TypedDict
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.db import get_similar_feedback

from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

# --- Structured Output Schemas ---
class PronunciationRank(BaseModel):
    rank: int = Field(description="1 for primary UK RP, 2 for secondary, etc.")
    gujarati: str = Field(description="The Gujarati phonetic transcription")
    ipa: str = Field(description="Strict Oxford British RP IPA")
    notes: str = Field(description="Brief note on why this variant exists (e.g., 'Primary non-rhotic', 'Weak form')")

class POSVariant(BaseModel):
    pos: str = Field(description="Part of speech (e.g., 'noun', 'verb')")
    ranked_pronunciations: list[PronunciationRank]

class OxfordEvaluation(BaseModel):
    is_homograph: bool = Field(description="True if the word has different pronunciations for different parts of speech")
    pos_variants: list[POSVariant] = Field(description="List of POS forms and their 1-3 ranked British pronunciations")
    phonetic_breakdown: str = Field(description="Explanation of the British RP transcription choices")

class CriticOutput(BaseModel):
    is_passing: bool = Field(description="True if the draft is perfect. False if there are errors, American sounds, or missing variants.")
    feedback: str = Field(description="If is_passing is False, provide detailed corrections here to fix the draft. If True, say 'PASS'.")

# --- Agent State ---
class AgentState(TypedDict):
    word: str
    arpabet: list[str]
    deterministic_gujarati: str
    feedback_context: str
    research_data: str
    draft_evaluation: OxfordEvaluation | None
    criticism: str
    iterations: int

# --- Nodes ---
def research_word(state: AgentState) -> dict:
    """Use DuckDuckGo to find the official British phonetic transcription."""
    logger.info("Agent researching grounded phonetics for '%s'...", state["word"])
    query = f"site:oxfordlearnersdictionaries.com {state['word']} pronunciation phonetics"
    try:
        results = DDGS().text(query, max_results=3)
        formatted_results = "\n".join([f"{r['title']}: {r['body']}" for r in results])
    except Exception as e:
        logger.warning(f"Search failed: {e}")
        formatted_results = "Search failed, rely on internal knowledge."
    
    return {"research_data": formatted_results}

def generate_draft(state: AgentState) -> dict:
    """Generate the initial evaluation draft using structured output."""
    logger.info("Agent generating initial draft for '%s'...", state["word"])
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=settings.GEMINI_API_KEY)
    structured_llm = llm.with_structured_output(OxfordEvaluation)
    
    prompt = f"""
    Word: {state["word"]}
    ARPAbet tokens: {state["arpabet"]}
    Deterministic Gujarati: {state["deterministic_gujarati"]}
    Online Research: {state["research_data"]}
    
    {state["feedback_context"]}

    You are a strict Oxford English Phonetician. Create a highly accurate evaluation.
    RULES:
    1. BRITISH RP ONLY: Strictly exclude American rhotic /r/ sounds or /æ/ shifting. Use the research data to verify!
    2. FORCE MULTIPLE VARIANTS: You MUST provide at least 2 (up to 3) ranked pronunciations for EVERY Part of Speech.
       - Rank 1: The primary Oxford UK RP standard.
       - Rank 2/3: Common connected speech variations (glottal stops, schwa elision).
    3. SUFFIX CONJUNCTS: Do NOT use a halant (્) across suffix boundaries (e.g., use 'મન્ટ' for '-ment', NOT 'મ્ન્ટ').
    """
    
    result = structured_llm.invoke(prompt)
    return {"draft_evaluation": result, "iterations": state.get("iterations", 0) + 1}

def criticize_draft(state: AgentState) -> dict:
    """Act as a harsh critic to review the drafted evaluation."""
    logger.info("Agent criticizing draft (iteration %s)...", state["iterations"])
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=settings.GEMINI_API_KEY)
    structured_llm = llm.with_structured_output(CriticOutput)
    
    prompt = f"""
    You are a meticulous Phonetic Reviewer. Review this drafted Gujarati phonetics evaluation for the word '{state['word']}'.
    
    Draft to Review:
    {state['draft_evaluation'].model_dump_json(indent=2) if state['draft_evaluation'] else 'None'}
    
    Research Truth:
    {state['research_data']}
    
    Feedback Context (Rules to enforce):
    {state['feedback_context']}
    
    CRITIQUE CHECKLIST:
    1. Are there ANY American rhotic /r/ sounds (e.g. 'ર' at the end of words like 'water')? If yes, FAIL.
    2. Does EVERY part of speech have at least 2 ranked variants? If only 1, FAIL.
    3. Does the Gujarati text improperly use a halant (્) across a suffix boundary (like -ment)? If yes, FAIL.
    4. Does it perfectly align with the Research Truth? If it hallucinates, FAIL.
    """
    
    result = structured_llm.invoke(prompt)
    if not result.is_passing:
        logger.warning(f"Critic rejected draft. Feedback: {result.feedback}")
    else:
        logger.info("Critic approved draft.")
        
    return {"criticism": result.feedback if not result.is_passing else "PASS"}

def refine_draft(state: AgentState) -> dict:
    """Rewrite the draft based on the critic's feedback."""
    logger.info("Agent refining draft based on criticism...")
    settings = get_settings()
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=settings.GEMINI_API_KEY)
    structured_llm = llm.with_structured_output(OxfordEvaluation)
    
    prompt = f"""
    You are a strict Oxford English Phonetician. You must FIX your previous draft based on the Critic's feedback.
    
    Word: {state["word"]}
    Previous Draft: {state['draft_evaluation'].model_dump_json(indent=2) if state['draft_evaluation'] else 'None'}
    Critic's Feedback: {state["criticism"]}
    
    Rewrite the entire JSON to fix ALL issues mentioned by the Critic.
    """
    
    result = structured_llm.invoke(prompt)
    return {"draft_evaluation": result, "iterations": state["iterations"] + 1}

# --- Edge Logic ---
def should_continue(state: AgentState) -> str:
    """Determine whether to loop back to refine or end."""
    if state["criticism"] == "PASS" or state["iterations"] >= 3:
        return END
    return "refine_draft"

# --- Graph Compilation ---
def build_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research_word", research_word)
    workflow.add_node("generate_draft", generate_draft)
    workflow.add_node("criticize_draft", criticize_draft)
    workflow.add_node("refine_draft", refine_draft)
    
    # Add edges
    workflow.set_entry_point("research_word")
    workflow.add_edge("research_word", "generate_draft")
    workflow.add_edge("generate_draft", "criticize_draft")
    
    workflow.add_conditional_edges(
        "criticize_draft",
        should_continue,
        {
            "refine_draft": "refine_draft",
            END: END
        }
    )
    
    workflow.add_edge("refine_draft", "criticize_draft")
    
    return workflow.compile()

graph = build_graph()

# --- Main Entry Function ---
async def evaluate_phonetics(
    word: str, arpabet: list[str], deterministic_gujarati: str
) -> OxfordEvaluation | None:
    """Run the self-correcting LangGraph agent pipeline."""
    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not found. Skipping Oxford verification.")
        return None

    logger.info("Starting LangGraph evaluation for '%s'...", word)
    
    # Prepare RAG context
    recent_feedback = get_similar_feedback(word, limit=5)
    feedback_context = ""
    if recent_feedback:
        feedback_context = "USER APPROVED FEEDBACK EXAMPLES:\n"
        for fb in recent_feedback:
            feedback_context += (
                f"- Word: {fb['word']} (POS: {fb['pos']})\n"
                f"  Approved Rank 1: {fb['selected_gujarati']} ({fb['selected_ipa']})\n"
            )
        feedback_context += "\nCRITICAL: You MUST align your stylistic choices with the user-approved feedback above.\n"

    # Initialize state
    initial_state = {
        "word": word,
        "arpabet": arpabet,
        "deterministic_gujarati": deterministic_gujarati,
        "feedback_context": feedback_context,
        "research_data": "",
        "draft_evaluation": None,
        "criticism": "",
        "iterations": 0
    }
    
    # Execute graph synchronously since DuckDuckGo search is sync
    result = graph.invoke(initial_state)
    
    return result.get("draft_evaluation")
