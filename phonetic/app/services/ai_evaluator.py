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


class POSVariant(BaseModel):
    pos: str = Field(description="Part of speech (e.g. 'noun', 'verb').")
    ipa: str = Field(description="The standard IPA representation for this POS.")
    gujarati: str = Field(description="The Gujarati phonetic spelling for this POS.")


class VerificationResult(BaseModel):
    word: str
    arpabet: list[str]
    deterministic_gujarati: str
    oxford_verified_gujarati: str = Field(
        description="The Oxford-verified Gujarati phonetic transcription."
    )
    pos_variants: list[POSVariant] | None = Field(
        default=None,
        description="Populated if the word is a homograph with different pronunciations based on POS (e.g. project).",
    )
    phonetic_breakdown: str = Field(
        description="A brief explanation of any corrections made to the deterministic output."
    )


async def evaluate_phonetics(
    word: str, arpabet: list[str], deterministic_gujarati: str
) -> VerificationResult | None:
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
    1. Verify if '{deterministic_gujarati}' matches the standard Oxford English Dictionary (RP/AmE) pronunciation.
    2. If it is perfect, return it in `oxford_verified_gujarati`. If it needs a minor tweak (like replacing a schwa or adjusting a matra), return the corrected version.
    3. If this word is a homograph (e.g. 'project' noun vs verb), populate `pos_variants` with the different ways it can be pronounced.
    4. Provide a brief `phonetic_breakdown` explaining your logic.

    TYPOGRAPHY RULES:
    1. Do not form conjuncts (using halant '્') across syllable boundaries or common English suffixes.
    2. For suffixes like -ment, -ness, -ful, and -less, the preceding consonant MUST be a full letter. 
    3. Example: 'arrangement' must be 'અરેઇન્જમન્ટ', NEVER 'અરેઇન્જ્મન્ટ'. 
    4. Example: 'statement' must be 'સ્ટેટમન્ટ', NEVER 'સ્ટેટ્મન્ટ'.
    """

    try:
        # Use asyncio.to_thread because the google-genai client doesn't currently 
        # expose first-class async functions for generate_content natively in all contexts.
        # Actually, genai.Client has .aio if we want async, but let's just use synchronous 
        # generate_content and wrap it to be safe. Wait, `client.aio.models.generate_content` exists in google-genai 0.1+.
        # We will use `client.aio.models.generate_content`.
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VerificationResult,
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
