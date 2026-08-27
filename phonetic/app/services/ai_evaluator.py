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
    You are an expert Oxford/RP English to Gujarati phonetic evaluator.
    I have generated a deterministic phonetic transcription for an English word.

    Word: {word}
    ARPAbet tokens: {arpabet}
    Deterministic Gujarati: {deterministic_gujarati}

    Your task:
    1. For every applicable Part of Speech (POS) for this word, provide 1 to 3 ranked British RP pronunciations (e.g., rank 1 = primary, rank 2 = secondary/weak form).
    2. Drop American English pronunciations entirely. Focus strictly on Oxford British RP (non-rhotic).
    3. Return the exact Gujarati phonetic spellings and the strict IPA for each rank.
    4. Provide a brief `phonetic_breakdown` explaining your logic.

    TYPOGRAPHY RULES:
    1. Do not form conjuncts (using halant '્') across syllable boundaries or common English suffixes.
    2. For suffixes like -ment, -ness, -ful, and -less, the preceding consonant MUST be a full letter. 
    3. Example: 'arrangement' must be 'અરેઇન્જમન્ટ', NEVER 'અરેઇન્જ્મન્ટ'. 
    4. Example: 'statement' must be 'સ્ટેટમન્ટ', NEVER 'સ્ટેટ્મન્ટ'.
    """

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
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
