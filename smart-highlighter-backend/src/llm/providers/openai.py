"""OpenAI API integration."""

import logging
import os

import openai
from dotenv import load_dotenv

from src.utils.logging import get_logger

logger = get_logger(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize client if API key is available
client = None
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    client = openai.OpenAI()
else:
    logger.warning("OPENAI_API_KEY is not set in environment variables")


def _call_llm(
    system_prompt: str,
    user_payload: str,
    model: str = "gpt-4o",
    respond_json: bool = False,
) -> str:
    """
    Single point of contact with OpenAI API.

    Args:
        system_prompt: System instructions
        user_payload: User message/content
        model: OpenAI model name
        respond_json: Whether to request JSON response

    Returns:
        Model response text

    Raises:
        RuntimeError: If API key not configured
    """
    if not client:
        raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY.")

    logger.info(f"OpenAI request: ~{len(user_payload) // 4} tokens to {model}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_payload},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        raise


def reason(
    system_prompt: str,
    user_prompt: str,
    model: str = "o4-mini",
    response_format: str = "text",
) -> str:
    """
    Call OpenAI reasoning model (o-series).

    Args:
        system_prompt: System instructions
        user_prompt: User message
        model: Reasoning model name
        response_format: Response format ("text" or "json")

    Returns:
        Model response text

    Raises:
        RuntimeError: If API key not configured
    """
    if not client:
        raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY.")

    logger.info(f"OpenAI reasoning request to {model}")

    try:
        response = client.responses.create(
            model=model,
            reasoning={"effort": "high"},
            text={"format": {"type": response_format}},
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
    except Exception as e:
        logger.error(f"OpenAI reasoning call failed: {e}", exc_info=True)
        raise


__all__ = ["_call_llm", "reason"]
