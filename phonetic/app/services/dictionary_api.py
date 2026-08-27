"""Async client for the Free Dictionary API.

Fetches IPA (International Phonetic Alphabet) transcriptions for English words.
"""

import logging
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.exceptions import (
    DictionaryAPIError,
    PhoneticDataMissingError,
    WordNotFoundError,
)

logger = logging.getLogger(__name__)


async def fetch_ipa(word: str) -> str:
    """Fetch the IPA transcription for *word* from the Free Dictionary API.

    Args:
        word: An English word to look up.

    Returns:
        The cleaned IPA string (slashes stripped), e.g. ``stɑːtɪd``.

    Raises:
        WordNotFoundError: If the API returns 404.
        PhoneticDataMissingError: If no phonetic field is present.
        DictionaryAPIError: For any other non-200 response.
    """
    settings = get_settings()
    url = f"{settings.DICTIONARY_API_BASE}/{word.strip().lower()}"
    logger.info("Fetching IPA for '%s' from %s", word, url)

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

    if response.status_code == 404:
        raise WordNotFoundError(word)
    if response.status_code != 200:
        raise DictionaryAPIError(
            response.status_code,
            detail=response.text[:200],
        )

    entries: list[dict[str, Any]] = response.json()

    # Walk through entries → phonetics looking for a non-empty "text" field.
    for entry in entries:
        # Top-level "phonetic" field (sometimes present)
        top_phonetic: str | None = entry.get("phonetic")
        if top_phonetic:
            return _strip_slashes(top_phonetic)

        # Fall back to the "phonetics" array
        for phon in entry.get("phonetics", []):
            text: str | None = phon.get("text")
            if text:
                return _strip_slashes(text)

    raise PhoneticDataMissingError(word)


def _strip_slashes(ipa: str) -> str:
    """Remove surrounding /…/ or [… ] from an IPA string."""
    return ipa.strip().strip("/").strip("[]").strip()
