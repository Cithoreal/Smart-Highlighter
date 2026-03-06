"""Google AI (Gemini) API integration."""

import logging
import os

from dotenv import load_dotenv
from google import genai

from src.utils.logging import get_logger

logger = get_logger(__name__)

load_dotenv()

GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# Initialize client if API key is available
client = None
if GOOGLE_AI_API_KEY:
    client = genai.Client(api_key=GOOGLE_AI_API_KEY)
else:
    logger.warning("GOOGLE_AI_API_KEY is not set in environment variables")


def _call_llm(
    system_prompt: str, user_payload: str, model: str = "gemini-2.5-pro"
) -> str:
    """
    Single point of contact with Google AI API.

    Args:
        system_prompt: System instructions
        user_payload: User message/content
        model: Gemini model name

    Returns:
        Model response text

    Raises:
        RuntimeError: If API key not configured
    """
    if not client:
        raise RuntimeError("Google AI client not initialized. Set GOOGLE_AI_API_KEY.")

    logger.info(f"Google AI request: ~{len(user_payload) // 4} tokens to {model}")

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                system_prompt.strip(),
                user_payload,
            ],
        )
        return response.text
    except Exception as e:
        logger.error(f"Google AI API call failed: {e}", exc_info=True)
        raise


__all__ = ["_call_llm"]
