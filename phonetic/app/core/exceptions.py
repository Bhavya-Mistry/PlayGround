"""Custom exception classes for the Gujarati Phonetics server."""


class PhoneticServerError(Exception):
    """Base exception for all server-specific errors."""

    def __init__(self, message: str = "An internal server error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class WordNotFoundError(PhoneticServerError):
    """Raised when the Free Dictionary API returns 404 for a word."""

    def __init__(self, word: str) -> None:
        self.word = word
        super().__init__(f"Word not found in the dictionary: '{word}'")


class PhoneticDataMissingError(PhoneticServerError):
    """Raised when a dictionary entry exists but has no IPA transcription."""

    def __init__(self, word: str) -> None:
        self.word = word
        super().__init__(
            f"No IPA phonetic transcription available for: '{word}'"
        )


class DictionaryAPIError(PhoneticServerError):
    """Raised for unexpected HTTP errors from the Dictionary API."""

    def __init__(self, status_code: int, detail: str = "") -> None:
        self.status_code = status_code
        super().__init__(
            f"Dictionary API returned HTTP {status_code}. {detail}".strip()
        )
