"""Gemini 2.5 Flash agent with automatic function-calling.

Demonstrates using the ``google-genai`` SDK to let Gemini call the
``get_gujarati_pronunciation`` tool, which chains the dictionary lookup
and IPA→Gujarati conversion.
"""

import asyncio
import logging
import sys

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.services.dictionary_api import fetch_ipa
from app.services.phonetics import ipa_to_gujarati
from app.core.exceptions import PhoneticServerError

logger = logging.getLogger(__name__)

# ── Tool that Gemini will call ────────────────────────────────────────────


async def get_gujarati_pronunciation(word: str) -> dict[str, str]:
    """Look up *word* in the dictionary and return its Gujarati pronunciation.

    Args:
        word: An English word.

    Returns:
        A dict with keys ``word``, ``ipa``, and ``gujarati``.
    """
    ipa = await fetch_ipa(word)
    gujarati = ipa_to_gujarati(ipa)
    return {"word": word, "ipa": ipa, "gujarati": gujarati}


# Synchronous wrapper so it can be registered as a genai tool.
def _get_gujarati_pronunciation_sync(word: str) -> dict[str, str]:
    """Sync shim for ``get_gujarati_pronunciation`` used by the genai SDK."""
    return asyncio.run(get_gujarati_pronunciation(word))


# ── Agent loop ────────────────────────────────────────────────────────────


def _build_tool_declaration() -> types.FunctionDeclaration:
    """Build the Gemini FunctionDeclaration for the pronunciation tool."""
    return types.FunctionDeclaration(
        name="get_gujarati_pronunciation",
        description=(
            "Given an English word, fetches its IPA transcription from the "
            "dictionary and converts it to Gujarati phonetic script."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "word": types.Schema(
                    type=types.Type.STRING,
                    description="The English word to pronounce.",
                ),
            },
            required=["word"],
        ),
    )


async def run_agent_loop() -> None:
    """Interactive terminal loop: ask a question, Gemini triggers the tool."""
    settings = get_settings()
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
        logger.error(
            "GEMINI_API_KEY is not set. Please add it to your .env file."
        )
        sys.exit(1)

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    tool_decl = _build_tool_declaration()
    tool = types.Tool(function_declarations=[tool_decl])

    system_instruction = (
        "You are a helpful pronunciation assistant. When a user asks how to "
        "pronounce an English word in Gujarati, call the "
        "get_gujarati_pronunciation tool to get the deterministic Gujarati "
        "rendering.  Present the result clearly, showing the English word, "
        "IPA, and Gujarati script."
    )

    # Maintain conversational history.
    history: list[types.Content] = []

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║  Gujarati Phonetics Agent  (powered by Gemini 2.5 Flash)   ║")
    print("║  Type a question like: How do you pronounce 'secure'?      ║")
    print("║  Type 'quit' or 'exit' to leave.                           ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    while True:
        try:
            user_input = input("You ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break

        # Append user message to history.
        history.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_input)],
            )
        )

        # First call — model may return a function_call part.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=types.GenerateContentConfig(
                tools=[tool],
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )

        # Handle possible tool-call loop (single round expected).
        while response.candidates:
            candidate = response.candidates[0]
            parts = candidate.content.parts

            # Check if the model wants to call a function.
            function_call_part = None
            for part in parts:
                if part.function_call is not None:
                    function_call_part = part
                    break

            if function_call_part is None:
                # No function call — the model gave a text answer.
                break

            fc = function_call_part.function_call
            logger.info("Gemini requested tool call: %s(%s)", fc.name, fc.args)

            # Execute the tool.
            try:
                result = await get_gujarati_pronunciation(
                    word=fc.args["word"],
                )
            except PhoneticServerError as exc:
                result = {"error": exc.message}

            # Build the function-response content.
            fn_response_content = types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=fc.name,
                        response=result,
                    )
                ],
            )

            # Append assistant + tool-response to history.
            history.append(candidate.content)
            history.append(fn_response_content)

            # Second call — let the model produce a natural-language answer.
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=history,
                config=types.GenerateContentConfig(
                    tools=[tool],
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )

        # Print the final text response.
        if response.text:
            history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.text)],
                )
            )
            print(f"\nGemini ▸ {response.text}\n")
        else:
            print("\nGemini ▸ (no text response)\n")


# ── Entry point ───────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for ``python -m app.services.ai_agent``."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
    asyncio.run(run_agent_loop())


if __name__ == "__main__":
    main()
