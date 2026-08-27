"""Unified 3-Step Phonetic Pipeline.

Coordinates ARPAbet extraction -> Deterministic mapping -> AI Verification.
"""

import logging
import time
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.g2p_service import get_phonemes
from app.services.phonetics import arpabet_to_gujarati
from app.services.ai_evaluator import evaluate_phonetics, VerificationResult

logger = logging.getLogger(__name__)


class PipelineResult(BaseModel):
    """The unified result from the 3-step pipeline."""
    word: str
    arpabet: list[str]
    deterministic_gujarati: str
    oxford_verified_gujarati: str
    pos_variants: list[dict] | None = None
    phonetic_breakdown: str | None = None
    execution_times: dict[str, float]


async def run_phonetic_pipeline(word: str) -> PipelineResult:
    """Run the 3-step phonetic pipeline for a given word.

    Args:
        word: The English word to process.

    Returns:
        A structured `PipelineResult` containing deterministic outputs and 
        Oxford verification (if available).
    """
    word = word.strip().lower()
    logger.info("--- Starting Pipeline for '%s' ---", word)
    times = {}
    settings = get_settings()

    # ---------------------------------------------------------
    # Step 1: Phoneme Extraction (g2p_en)
    # ---------------------------------------------------------
    t0 = time.perf_counter()
    arpabet = await get_phonemes(word)
    t1 = time.perf_counter()
    times["step_1_extraction_ms"] = round((t1 - t0) * 1000, 2)

    # ---------------------------------------------------------
    # Step 2: Deterministic Mapping (phonetics.py)
    # ---------------------------------------------------------
    t0 = time.perf_counter()
    deterministic_gujarati = arpabet_to_gujarati(arpabet)
    t1 = time.perf_counter()
    times["step_2_deterministic_mapping_ms"] = round((t1 - t0) * 1000, 2)

    # ---------------------------------------------------------
    # Step 3: Oxford Evaluation (Gemini)
    # ---------------------------------------------------------
    # Fast fallback: skip Gemini call if key is invalid or placeholder
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
        logger.warning("Fast fallback: API key invalid/missing. Skipping Oxford eval.")
        return PipelineResult(
            word=word,
            arpabet=arpabet,
            deterministic_gujarati=deterministic_gujarati,
            oxford_verified_gujarati=deterministic_gujarati,
            phonetic_breakdown="Offline fallback mode active. API key not configured.",
            execution_times=times,
        )

    t0 = time.perf_counter()
    eval_result: VerificationResult | None = await evaluate_phonetics(
        word=word,
        arpabet=arpabet,
        deterministic_gujarati=deterministic_gujarati,
    )
    t1 = time.perf_counter()
    times["step_3_oxford_eval_ms"] = round((t1 - t0) * 1000, 2)

    # Compile the final result
    if eval_result:
        # We got a successful Gemini verification
        return PipelineResult(
            word=word,
            arpabet=arpabet,
            deterministic_gujarati=deterministic_gujarati,
            oxford_verified_gujarati=eval_result.oxford_verified_gujarati,
            pos_variants=[v.model_dump() for v in eval_result.pos_variants] if eval_result.pos_variants else None,
            phonetic_breakdown=eval_result.phonetic_breakdown,
            execution_times=times,
        )
    else:
        # Fallback if Gemini errored out
        logger.warning("Falling back to deterministic output for '%s'", word)
        return PipelineResult(
            word=word,
            arpabet=arpabet,
            deterministic_gujarati=deterministic_gujarati,
            oxford_verified_gujarati=deterministic_gujarati,  # Fallback
            phonetic_breakdown="Offline fallback mode active. No Oxford verification performed.",
            execution_times=times,
        )
