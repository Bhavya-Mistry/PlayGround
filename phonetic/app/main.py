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
from app.services.pipeline import run_phonetic_pipeline

logger = logging.getLogger(__name__)

# ── Settings ──────────────────────────────────────────────────────────────

settings = get_settings()

# ── FastMCP server ────────────────────────────────────────────────────────

mcp = MCPServer(
    name="GujaratiPhoneticsServer",
    instructions=(
        "This server converts English words to Gujarati phonetic script "
        "using a 3-step pipeline (G2P extraction -> Deterministic mapping -> "
        "Oxford Verification). Use get_verified_gujarati_pronunciation."
    ),
)


@mcp.tool(
    name="get_verified_gujarati_pronunciation",
    description=(
        "Given an English word, runs the phonetic pipeline to generate "
        "ARPAbet transcriptions, deterministic Gujarati, and Oxford-verified "
        "Gujarati. Returns a structured JSON result including POS variants if applicable."
    ),
)
async def get_verified_gujarati_pronunciation(word: str) -> dict:
    """Run the 3-step pipeline.

    Args:
        word: The English word to pronounce.

    Returns:
        A dict representation of the PipelineResult.
    """
    try:
        result = await run_phonetic_pipeline(word)
        return result.model_dump()
    except Exception as exc:
        logger.exception("Error in pipeline for '%s'", word)
        return {"error": str(exc)}


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
