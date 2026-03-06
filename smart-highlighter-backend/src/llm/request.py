"""Unified LLM request interface.

This module provides a single interface for making requests to different
LLM providers (OpenAI, Anthropic, Google AI, etc.).
"""

import logging
from enum import Enum

from src.llm.providers import anthropic, google, openai
from src.utils.logging import get_logger

logger = get_logger(__name__)


class AI_API(Enum):
    """Supported LLM models."""

    # OpenAI models
    OPENAI_5 = "gpt-5-2025-08-07"
    OPENAI_5_mini = "gpt-5-mini-2025-08-07"
    OPENAI_4o = "gpt-4o"
    OPENAI_o4_mini = "o4-mini"

    # Anthropic models
    ANTHROPIC = "claude-opus-4-20250514"

    # Google models
    GOOGLE = "gemini-2.5-pro"


def make_llm_request(
    system_prompt: str,
    user_prompt: str,
    llm_model: AI_API,
    response_format: str = "text",
) -> str:
    """
    Make a generic LLM request to any supported provider.

    Args:
        system_prompt: System instructions
        user_prompt: User message/content
        llm_model: Model to use (from AI_API enum)
        response_format: Response format ("text" or "json")

    Returns:
        Model response text

    Raises:
        Exception: If LLM request fails
    """
    try:
        logger.info(f"Making LLM request to {llm_model.value}")

        # Route to appropriate provider
        if llm_model == AI_API.OPENAI_o4_mini:
            response = openai.reason(
                system_prompt, user_prompt, response_format=response_format
            )
        elif llm_model in [AI_API.OPENAI_4o, AI_API.OPENAI_5, AI_API.OPENAI_5_mini]:
            response = openai._call_llm(
                system_prompt, user_prompt, model=llm_model.value
            )
        elif llm_model == AI_API.ANTHROPIC:
            response = anthropic._call_llm(
                system_prompt, user_prompt, model=llm_model.value
            )
        elif llm_model == AI_API.GOOGLE:
            response = google._call_llm(
                system_prompt, user_prompt, model=llm_model.value
            )
        else:
            raise ValueError(f"Unsupported model: {llm_model}")

        logger.debug(f"LLM response received: {len(response)} chars")
        return response

    except Exception as e:
        logger.error(f"LLM request failed for {llm_model.value}: {e}", exc_info=True)
        raise


__all__ = ["AI_API", "make_llm_request"]
