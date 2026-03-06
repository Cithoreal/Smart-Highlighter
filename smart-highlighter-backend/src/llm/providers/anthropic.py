"""Anthropic API integration."""

import logging
import os

import anthropic
from dotenv import load_dotenv

from src.utils.logging import get_logger

logger = get_logger(__name__)

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize client if API key is available
client = None
if ANTHROPIC_API_KEY:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    logger.warning("ANTHROPIC_API_KEY is not set in environment variables")


def _call_llm(
    system_prompt: str, user_payload: str, model: str = "claude-opus-4-20250514"
) -> str:
    """
    Single point of contact with Anthropic API.

    Args:
        system_prompt: System instructions
        user_payload: User message/content
        model: Claude model name

    Returns:
        Model response text

    Raises:
        RuntimeError: If API key not configured
    """
    if not client:
        raise RuntimeError("Anthropic client not initialized. Set ANTHROPIC_API_KEY.")

    logger.info(f"Anthropic request: ~{len(user_payload) // 4} tokens to {model}")

    try:
        response = client.messages.create(
            model=model,
            max_tokens=8000,
            temperature=0.2,
            messages=[
                {"role": "user", "content": system_prompt.strip()},
                {"role": "user", "content": user_payload},
            ],
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Anthropic API call failed: {e}", exc_info=True)
        raise


__all__ = ["_call_llm"]
