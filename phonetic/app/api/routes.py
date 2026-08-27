"""REST API routes — standard HTTP fallback endpoints."""

import logging

from fastapi import APIRouter, HTTPException

from app.core.exceptions import PhoneticServerError, PhoneticDataMissingError
from app.services.pipeline import run_phonetic_pipeline, PipelineResult

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pronunciation"])

# ── Endpoint ──────────────────────────────────────────────────────────────

@router.get(
    "/pronounce/{word}",
    response_model=PipelineResult,
    summary="Get verified Gujarati pronunciation for an English word",
    responses={
        404: {"description": "Phonetic data not available."},
        502: {"description": "Server error."},
    },
)
async def pronounce(word: str) -> PipelineResult:
    """Run the 3-step phonetic pipeline (Extraction -> Mapping -> AI Eval).

    Args:
        word: The English word to pronounce.

    Returns:
        A ``PipelineResult`` containing the full phonetic breakdown.
    """
    try:
        result = await run_phonetic_pipeline(word)
        return result
    except PhoneticDataMissingError as exc:
        raise HTTPException(
            status_code=404,
            detail=exc.message,
        )
    except PhoneticServerError as exc:
        logger.exception("Phonetic engine error for '%s'", word)
        raise HTTPException(status_code=502, detail=exc.message)
    except Exception as exc:
        logger.exception("Unexpected error in pipeline for '%s'", word)
        raise HTTPException(status_code=500, detail="Internal server error")


from pydantic import BaseModel
from app.core.db import save_feedback

class FeedbackRequest(BaseModel):
    word: str
    pos: str
    original_options: list[dict]
    selected_gujarati: str
    selected_ipa: str

@router.post(
    "/feedback",
    summary="Submit user feedback for pronunciation ranking",
    responses={
        200: {"description": "Feedback successfully recorded."},
    },
)
async def submit_feedback(request: FeedbackRequest):
    """Save user feedback into the SQLite database for RLHF."""
    try:
        save_feedback(
            word=request.word,
            pos=request.pos,
            original_options=request.original_options,
            selected_gujarati=request.selected_gujarati,
            selected_ipa=request.selected_ipa
        )
        return {"status": "success", "message": "Feedback recorded."}
    except Exception as exc:
        logger.exception("Failed to save feedback for '%s'", request.word)
        raise HTTPException(status_code=500, detail="Internal server error saving feedback")
