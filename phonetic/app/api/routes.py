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
