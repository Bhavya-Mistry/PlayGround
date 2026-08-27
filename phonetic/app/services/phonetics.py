"""Deterministic IPA → Gujarati phonetic conversion engine.

The engine processes an IPA string left-to-right, greedily matching the
longest multi-character token first (e.g. ``tʃ`` before ``t``).  Context
tracking ensures vowels are rendered as **independent characters** when
word-initial or after another vowel, and as **matras** (combining signs)
when they follow a consonant.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

# Consonant IPA → Gujarati (including digraphs like tʃ, dʒ)
CONSONANTS: dict[str, str] = {
    "tʃ": "ચ",
    "dʒ": "જ",
    "ʃ":  "શ",
    "ʒ":  "ઝ",
    "θ":  "થ",
    "ð":  "દ",
    "ŋ":  "ંગ",
    "b":  "બ",
    "d":  "ડ",
    "f":  "ફ",
    "g":  "ગ",
    "h":  "હ",
    "j":  "ય",
    "k":  "ક",
    "l":  "લ",
    "m":  "મ",
    "n":  "ન",
    "p":  "પ",
    "r":  "ર",
    "s":  "સ",
    "t":  "ટ",
    "v":  "વ",
    "w":  "વ",
    "z":  "ઝ",
    "ɹ":  "ર",
}

# Diphthongs — checked *before* simple vowels because they are longer.
DIPHTHONGS: dict[str, str] = {
    "eɪ": "ેઇ",
    "aɪ": "આઇ",
    "ɔɪ": "ઑઇ",
    "aʊ": "આઉ",
    "əʊ": "ઓ",
    "oʊ": "ઓ",
    "ɪə": "િઅ",
    "eə": "ૅઅ",
    "ʊə": "ુઅ",
}

# Independent vowels — used when a vowel is word-initial or follows another vowel.
INDEPENDENT_VOWELS: dict[str, str] = {
    "iː": "ઈ",
    "ɪ":  "ઇ",
    "e":  "એ",
    "ɛ":  "એ",
    "æ":  "ઍ",
    "ɑː": "આ",
    "ɒ":  "ઑ",
    "ɔː": "ઑ",
    "ɔ":  "ઑ",
    "ʊ":  "ઉ",
    "uː": "ઊ",
    "ʌ":  "અ",
    "ə":  "અ",
    "ɜː": "અર્",
    "oː": "ઓ",
    "o":  "ઓ",
    "a":  "આ",
}

# Matras — combining vowel signs applied after a consonant.
MATRAS: dict[str, str] = {
    "iː": "ી",
    "ɪ":  "િ",
    "e":  "ે",
    "ɛ":  "ે",
    "æ":  "ૅ",
    "ɑː": "ા",
    "ɒ":  "ૉ",
    "ɔː": "ૉ",
    "ɔ":  "ૉ",
    "ʊ":  "ુ",
    "uː": "ૂ",
    "ʌ":  "અ",
    "ə":  "અ",
    "ɜː": "અર્",
    "oː": "ો",
    "o":  "ો",
    "a":  "ા",
}

# Independent diphthong forms for word-initial / post-vowel positions.
INDEPENDENT_DIPHTHONGS: dict[str, str] = {
    "eɪ": "એઇ",
    "aɪ": "આઇ",
    "ɔɪ": "ઑઇ",
    "aʊ": "આઉ",
    "əʊ": "ઓ",
    "oʊ": "ઓ",
    "ɪə": "ઇઅ",
    "eə": "ઍઅ",
    "ʊə": "ઉઅ",
}

# Sorted token lists (longest first) for greedy matching.
_CONSONANT_TOKENS: list[str] = sorted(CONSONANTS, key=len, reverse=True)
_DIPHTHONG_TOKENS: list[str] = sorted(DIPHTHONGS, key=len, reverse=True)
_VOWEL_TOKENS: list[str] = sorted(INDEPENDENT_VOWELS, key=len, reverse=True)

# Characters we silently skip (stress marks, length marks already embedded, etc.)
_SKIP_CHARS: set[str] = {"ˈ", "ˌ", "'", "ˑ", ".", " ", "͡", "(", ")", "̈", "ː"}


# ---------------------------------------------------------------------------
# Token classification helpers
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class _Token:
    """A parsed IPA token with its Gujarati mapping."""

    ipa: str
    kind: str  # "consonant" | "vowel" | "diphthong" | "skip" | "unknown"


def _match_at(ipa: str, pos: int, candidates: list[str]) -> str | None:
    """Return the first (longest) candidate that matches *ipa* at *pos*."""
    for tok in candidates:
        if ipa[pos: pos + len(tok)] == tok:
            return tok
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def ipa_to_gujarati(ipa: str) -> str:
    """Convert an IPA transcription string to Gujarati script.

    Args:
        ipa: A cleaned IPA string (no surrounding slashes).

    Returns:
        The Gujarati phonetic rendering of the input.

    Examples:
        >>> ipa_to_gujarati("stɑːtɪd")
        'સ્ટાટિડ'
    """
    ipa = ipa.strip()
    # Remove tie-bar (combining double inverted breve) so digraphs like
    # t͡ʃ and d͡ʒ match our "tʃ" / "dʒ" tokens directly.
    ipa = ipa.replace("\u0361", "")
    if not ipa:
        return ""

    result: list[str] = []
    pos = 0
    last_was_consonant = False  # tracks whether previous token was a consonant

    logger.debug("Converting IPA: %s", ipa)

    while pos < len(ipa):
        char = ipa[pos]

        # --- skip stress marks and whitespace ---
        if char in _SKIP_CHARS:
            pos += 1
            continue

        # --- try diphthongs first (longest multi-char vowel) ---
        diph = _match_at(ipa, pos, _DIPHTHONG_TOKENS)
        if diph is not None:
            if last_was_consonant:
                result.append(DIPHTHONGS[diph])
            else:
                result.append(INDEPENDENT_DIPHTHONGS[diph])
            pos += len(diph)
            last_was_consonant = False
            continue

        # --- try consonants (includes digraphs like tʃ, dʒ) ---
        cons = _match_at(ipa, pos, _CONSONANT_TOKENS)
        if cons is not None:
            # If the previous token was also a consonant, insert a halant (્)
            # to form a conjunct before appending the new consonant.
            if last_was_consonant:
                result.append("્")
            result.append(CONSONANTS[cons])
            pos += len(cons)
            last_was_consonant = True
            continue

        # --- try vowels ---
        vowel = _match_at(ipa, pos, _VOWEL_TOKENS)
        if vowel is not None:
            if last_was_consonant:
                result.append(MATRAS[vowel])
            else:
                result.append(INDEPENDENT_VOWELS[vowel])
            pos += len(vowel)
            last_was_consonant = False
            continue

        # --- unknown character — emit as-is ---
        logger.warning("Unknown IPA character at pos %d: %r", pos, char)
        result.append(char)
        pos += 1
        last_was_consonant = False

    gujarati = "".join(result)
    logger.info("IPA '%s' → Gujarati '%s'", ipa, gujarati)
    return gujarati
