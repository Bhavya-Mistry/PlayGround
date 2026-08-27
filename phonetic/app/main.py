"""FastAPI application with a mounted FastMCP server.

Start the combined server with::

    uvicorn app.main:app --reload
"""

import logging

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer

from app.api.routes import router as rest_router
from app.core.config import get_settings
from app.core.exceptions import PhoneticServerError, WordNotFoundError
from app.services.dictionary_api import fetch_ipa
from app.services.phonetics import ipa_to_gujarati

logger = logging.getLogger(__name__)

# ── Settings ──────────────────────────────────────────────────────────────

settings = get_settings()

# ── FastMCP server ────────────────────────────────────────────────────────

mcp = MCPServer(
    name="GujaratiPhoneticsServer",
    instructions=(
        "This server converts English words to Gujarati phonetic script. "
        "Use the get_gujarati_pronunciation tool to get the deterministic "
        "Gujarati rendering of an English word's pronunciation."
    ),
)


@mcp.tool(
    name="get_gujarati_pronunciation",
    description=(
        "Given an English word, fetches its IPA transcription from the Free "
        "Dictionary API and converts it to deterministic Gujarati phonetic "
        "script.  Returns a JSON object with 'word', 'ipa', and 'gujarati' "
        "keys."
    ),
)
async def get_gujarati_pronunciation(word: str) -> dict[str, str]:
    """Chain dictionary lookup and phonetic conversion.

    Args:
        word: The English word to pronounce.

    Returns:
        A dict with ``word``, ``ipa``, and ``gujarati`` fields.
    """
    try:
        ipa = await fetch_ipa(word)
    except WordNotFoundError:
        return {"error": f"'{word}' was not found in the dictionary."}
    except PhoneticServerError as exc:
        return {"error": exc.message}

    gujarati = ipa_to_gujarati(ipa)
    logger.info(
        "MCP tool: '%s' → IPA '%s' → Gujarati '%s'", word, ipa, gujarati
    )
    return {"word": word, "ipa": ipa, "gujarati": gujarati}


# ── FastAPI application ──────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan — configure logging on startup."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    logger.info("Gujarati Phonetics Server starting up 🚀")
    yield
    logger.info("Gujarati Phonetics Server shutting down 🛑")


app = FastAPI(
    title="Gujarati Phonetics API",
    description=(
        "A deterministic English-to-Gujarati phonetic conversion API.  "
        "Uses IPA transcriptions from the Free Dictionary API and maps "
        "them to Gujarati script."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Mount REST routes.
app.include_router(rest_router)

# Mount the MCP server at /mcp (SSE transport).
app.mount("/mcp", mcp.streamable_http_app())

# ── Run directly ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
