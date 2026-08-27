"""REST API routes — standard HTTP fallback endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.exceptions import PhoneticServerError, WordNotFoundError
from app.services.dictionary_api import fetch_ipa
from app.services.phonetics import ipa_to_gujarati

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pronunciation"])


# ── Response schema ───────────────────────────────────────────────────────


class PronunciationResponse(BaseModel):
    """JSON shape returned by the /pronounce endpoint."""

    word: str
    ipa: str
    gujarati: str


# ── Endpoint ──────────────────────────────────────────────────────────────


@router.get(
    "/pronounce/{word}",
    response_model=PronunciationResponse,
    summary="Get Gujarati pronunciation for an English word",
    responses={
        404: {"description": "Word not found in the dictionary."},
        502: {"description": "Dictionary API error."},
    },
)
async def pronounce(word: str) -> PronunciationResponse:
    """Look up *word* in the Free Dictionary API and return its Gujarati
    phonetic transcription.

    Args:
        word: The English word to pronounce.

    Returns:
        A ``PronunciationResponse`` containing the word, IPA, and Gujarati.
    """
    try:
        ipa = await fetch_ipa(word)
    except WordNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"'{word}' was not found in the dictionary.",
        )
    except PhoneticServerError as exc:
        logger.exception("Dictionary API error for '%s'", word)
        raise HTTPException(status_code=502, detail=exc.message)

    gujarati = ipa_to_gujarati(ipa)
    logger.info("Pronounced '%s' → IPA '%s' → Gujarati '%s'", word, ipa, gujarati)
    return PronunciationResponse(word=word, ipa=ipa, gujarati=gujarati)
