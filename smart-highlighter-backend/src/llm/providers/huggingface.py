"""HuggingFace API integration (placeholder)."""

import logging
import os

from dotenv import load_dotenv

from src.utils.logging import get_logger

logger = get_logger(__name__)

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    logger.warning("HUGGINGFACE_API_KEY is not set in environment variables")


def _call_llm(
    system_prompt: str, user_payload: str, model: str = "meta-llama/Llama-2-70b-chat-hf"
) -> str:
    """
    Single point of contact with HuggingFace API.

    Note: This is a placeholder implementation.

    Args:
        system_prompt: System instructions
        user_payload: User message/content
        model: HuggingFace model name

    Returns:
        Model response text

    Raises:
        NotImplementedError: This provider is not yet implemented
    """
    raise NotImplementedError("HuggingFace API integration not yet implemented")


__all__ = ["_call_llm"]
