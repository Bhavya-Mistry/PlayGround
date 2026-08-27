"""Custom exception classes for the Gujarati Phonetics server."""


class PhoneticServerError(Exception):
    """Base exception for all server-specific errors."""

    def __init__(self, message: str = "An internal server error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class PhoneticDataMissingError(PhoneticServerError):
    """Raised when g2p_en fails to return valid phonemes for a word."""

    def __init__(self, word: str) -> None:
        self.word = word
        super().__init__(
            f"No phonetic data could be generated for: '{word}'"
        )
