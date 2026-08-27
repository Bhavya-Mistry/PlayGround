"""Offline grapheme-to-phoneme service using g2p_en.

Converts English words to ARPAbet phonemes entirely offline using CMUDict.
"""

import asyncio
import logging
from g2p_en import G2p

from app.core.exceptions import PhoneticDataMissingError

logger = logging.getLogger(__name__)

# Initialize G2p as a singleton. The first time this is instantiated, 
# it loads the CMUDict data into memory.
_g2p = G2p()


async def get_phonemes(word: str) -> list[str]:
    """Fetch the ARPAbet phonemes for *word* using g2p_en.

    Args:
        word: An English word to look up.

    Returns:
        A list of ARPAbet phonemes, e.g. ``['P', 'R', 'AA1', 'JH', 'EH0', 'K', 'T']``.

    Raises:
        PhoneticDataMissingError: If g2p fails to return valid phonemes.
    """
    word = word.strip().lower()
    logger.info("Generating ARPAbet phonemes for '%s'", word)

    # g2p() is technically synchronous and CPU bound, but it's very fast
    # for a single word. We wrap it in to_thread to keep the event loop unblocked.
    phonemes = await asyncio.to_thread(_g2p, word)
    
    # g2p_en preserves punctuation if passed in, we should filter out empty or
    # purely punctuation outputs if it completely failed to find word chars.
    cleaned_phonemes = [p for p in phonemes if p.strip() and p.isalnum()]

    if not cleaned_phonemes:
        raise PhoneticDataMissingError(word)

    return cleaned_phonemes
