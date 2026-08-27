"""Deterministic ARPAbet → Gujarati phonetic conversion engine.

Converts lists of ARPAbet phonemes (from g2p_en) to Gujarati script.
Strict rules applied:
- AA/AO -> ૉ
- AE -> ૅ
- EH -> ે
- IY -> ી
- IH -> િ
- AH -> અ
- ER -> ર (Rhoticity preserved)
"""

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

CONSONANTS: dict[str, str] = {
    "B":  "બ",
    "CH": "ચ",
    "D":  "ડ",
    "DH": "દ",
    "F":  "ફ",
    "G":  "ગ",
    "HH": "હ",
    "JH": "જ",
    "K":  "ક",
    "L":  "લ",
    "M":  "મ",
    "N":  "ન",
    "NG": "ંગ",
    "P":  "પ",
    "R":  "ર",
    "S":  "સ",
    "SH": "શ",
    "T":  "ટ",
    "TH": "થ",
    "V":  "વ",
    "W":  "વ",
    "Y":  "ય",
    "Z":  "ઝ",
    "ZH": "ઝ",
}

# Independent vowels — used when a vowel is word-initial or follows another vowel.
INDEPENDENT_VOWELS: dict[str, str] = {
    "AA": "ઑ",  # Candra O
    "AE": "ઍ",  # Candra E
    "AH": "અ",  # Schwa
    "AO": "ઑ",  # Candra O
    "AW": "આઉ",
    "AY": "આઇ",
    "EH": "એ",  # Normal E
    "ER": "અર",  # Rhoticity preserved
    "EY": "એઇ",
    "IH": "ઇ",  # Short i
    "IY": "ઈ",  # Long ee
    "OW": "ઓ",
    "OY": "ઑઇ",
    "UH": "ઉ",
    "UW": "ઊ",
}

# Matras — combining vowel signs applied after a consonant.
MATRAS: dict[str, str] = {
    "AA": "ૉ",  # Candra O
    "AE": "ૅ",  # Candra E
    "AH": "",   # Inherited vowel in Gujarati script, no matra needed
    "AO": "ૉ",  # Candra O
    "AW": "ાઉ",
    "AY": "ાઇ",
    "EH": "ે",  # Normal E
    "ER": "ર",  # Rhoticity preserved (usually appended to previous consonant)
    "EY": "ેઇ",
    "IH": "િ",  # Short i
    "IY": "ી",  # Long ee
    "OW": "ો",
    "OY": "ૉઇ",
    "UH": "ુ",
    "UW": "ૂ",
}


def _strip_stress(phoneme: str) -> str:
    """Remove trailing digits from vowels (e.g. 'AA1' -> 'AA')."""
    return re.sub(r'\d+', '', phoneme)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def arpabet_to_gujarati(phonemes: list[str]) -> str:
    """Convert an ARPAbet phoneme list to Gujarati script.

    Args:
        phonemes: List of ARPAbet phonemes (e.g. ``['P', 'R', 'AA1', 'JH', 'EH0', 'K', 'T']``).

    Returns:
        The Gujarati phonetic rendering of the input.
    """
    if not phonemes:
        return ""

    result: list[str] = []
    last_was_consonant = False

    # Consonants that often start common English suffixes (-ment, -ness, -ful, -less, -ly)
    SUFFIX_STARTS = {"M", "N", "F", "L"}

    logger.debug("Converting ARPAbet: %s", phonemes)

    for raw_phoneme in phonemes:
        phoneme = _strip_stress(raw_phoneme)

        # Consonant mapping
        if phoneme in CONSONANTS:
            # If the previous token was also a consonant, insert a halant (્)
            # to form a conjunct before appending the new consonant.
            # EXCEPTION: Prevent conjuncts across suffix boundaries.
            if last_was_consonant and phoneme not in SUFFIX_STARTS:
                result.append("્")
            result.append(CONSONANTS[phoneme])
            last_was_consonant = True

        # Vowel mapping
        elif phoneme in INDEPENDENT_VOWELS:
            if last_was_consonant:
                result.append(MATRAS[phoneme])
            else:
                result.append(INDEPENDENT_VOWELS[phoneme])
            last_was_consonant = False
            
            # Special case for ER: it acts as a consonant 'r' sound in rhotic dialects
            if phoneme == "ER":
                last_was_consonant = True

        else:
            logger.warning("Unknown ARPAbet phoneme: %r", raw_phoneme)
            result.append(raw_phoneme)
            last_was_consonant = False

    gujarati = "".join(result)
    logger.info("ARPAbet %s → Gujarati '%s'", phonemes, gujarati)
    return gujarati
