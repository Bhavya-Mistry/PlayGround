"""Oxford-grade verification using Gemini Structured Outputs.

This module validates our deterministic Gujarati phonetics against 
Oxford/RP standards, resolving homographs and identifying edge cases.
"""

import logging
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from app.core.config import get_settings

logger = logging.getLogger(__name__)


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


async def evaluate_phonetics(
    word: str, arpabet: list[str], deterministic_gujarati: str
) -> OxfordEvaluation | None:
    """Evaluate the deterministic phonetics using Gemini.

    Returns `None` if the API key is missing or the call fails, allowing
    the caller to handle fallbacks.
    """
    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not found. Skipping Oxford verification.")
        return None

    logger.info("Starting Oxford evaluation for '%s'...", word)
    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = f"""
    Word: {word}
    ARPAbet tokens: {arpabet}
    Deterministic Gujarati: {deterministic_gujarati}

    You are a strict Oxford English Phonetician. Evaluate the deterministic Gujarati transcription and provide 100% accurate British English (Modern RP) equivalents.
    RULES:
    1. BRITISH RP ONLY: Strictly exclude American rhotic /r/ sounds or /æ/ shifting.
    2. FORCE MULTIPLE VARIANTS: You MUST provide at least 2 (up to 3) ranked pronunciations for EVERY Part of Speech. 
       - Rank 1: The primary Oxford UK RP dictionary standard.
       - Rank 2/3: If no distinct secondary dictionary pronunciation exists, you MUST provide a common British connected-speech form (e.g., using a glottal stop /ʔ/, intrusive 'r', or weak forms). Explain this in the `notes`.
    3. EXHAUSTIVE POS: Identify all major grammatical forms of the word (e.g., Noun, Verb, Adjective). Provide a separate `POSVariant` block for EACH one, even if the pronunciation is identical. Set `is_homograph` to true ONLY if the pronunciation differs across these blocks.
    4. TYPOGRAPHY: Do not form conjuncts (halant '્') across syllable boundaries or suffixes (e.g., 'statement' is સ્ટેટમન્ટ, NEVER સ્ટેટ્મન્ટ). Use Candra matras (ૅ for /æ/ and ૉ for /ɒ/ or /ɔː/).
    """

    try:
        response = await client.aio.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OxfordEvaluation,
                temperature=0.0,  # Keep it deterministic
            ),
        )

        if response.parsed:
            logger.info("Oxford evaluation completed for '%s'.", word)
            return response.parsed
        else:
            logger.error("Failed to parse structured output from Gemini.")
            return None

    except Exception as e:
        logger.exception("Gemini API error during Oxford verification: %s", e)
        return None
