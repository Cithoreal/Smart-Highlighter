"""High-level summary orchestration.

This module handles two tiers of summarization:

1. Topic summaries – quick JSON snapshots of active topics, generated
   when needed based on time/volume heuristics.
2. Full summaries – end-of-day Markdown reports, built on demand or
   via a nightly scheduler. These embed the latest topic JSON and cite
   exact event_id ranges for traceability.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.core.storage import (get_topic_file_by_name, latest_topic_summary,
                              save_full_summary, save_topic_summary)
from src.llm.request import AI_API, make_llm_request
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Heuristics for determining when to generate new summaries
MAX_EVENT_GAP = 3600  # seconds before considering topic summary stale
MAX_NEW_LINES = 200  # lines of fresh data to trigger new summary


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _need_new_topic_summary(
    new_line_cnt: int, last_generated_at: Optional[str]
) -> bool:
    """
    Determine if a new topic summary is needed.

    Args:
        new_line_cnt: Number of new lines/events
        last_generated_at: ISO timestamp of last summary

    Returns:
        True if new summary should be generated
    """
    if last_generated_at is None:
        return True

    last_dt = datetime.fromisoformat(last_generated_at)
    age = (datetime.utcnow() - last_dt).total_seconds()

    if age > MAX_EVENT_GAP:
        logger.info(f"Topic summary stale ({age:.0f}s old)")
        return True

    if new_line_cnt > MAX_NEW_LINES:
        logger.info(f"Sufficient new data ({new_line_cnt} lines)")
        return True

    return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_summary_json(
    system_prompt: dict,
    latest_events: str,
    user_id: str,
    llm_model: AI_API = AI_API.OPENAI_o4_mini,
    force: bool = False,
) -> Path:
    """
    Generate a topic summary in JSON format.

    Creates a new summary only if necessary based on heuristics,
    unless force=True.

    Args:
        system_prompt: Dict with label and prompt text
        latest_events: Event data to summarize
        user_id: User identifier
        llm_model: Model to use for generation
        force: If True, generate regardless of heuristics

    Returns:
        Path to saved summary file
    """
    label = list(system_prompt.keys())[0]
    logger.info(f"Creating topic summary for user {user_id}, label: {label}")

    prompt_text = system_prompt[label]
    new_line_cnt = len(latest_events.split("\n"))

    # Check if we need a new summary
    last = latest_topic_summary(user_id)
    last_ts: Optional[str] = last.get("generated_at") if last else None

    if not force and not _need_new_topic_summary(new_line_cnt, last_ts):
        logger.info("Topic summary is fresh – skipping generation")
        # Return path to latest summary
        # TODO: Better way to track latest summary path
        return Path("cached")

    # Generate summary
    logger.debug(f"Generating new summary with {llm_model.value}")
    payload = json.dumps(latest_events, ensure_ascii=False, indent=2)

    try:
        summary_txt = make_llm_request(prompt_text, payload, llm_model)
        summary_json = json.loads(summary_txt)
    except json.JSONDecodeError:
        logger.error("LLM returned invalid JSON, wrapping in error structure")
        summary_json = {"error": "LLM returned invalid JSON", "raw": summary_txt}
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}", exc_info=True)
        raise

    # Ensure we can attach metadata even if LLM returns a list
    if isinstance(summary_json, list):
        summary_json = {label: summary_json}

    summary_json["generated_at"] = datetime.utcnow().isoformat()

    # Save and return path
    topic_path = save_topic_summary(user_id, label, summary_json)
    logger.info(f"Saved topic summary to {topic_path}")

    return topic_path


def create_summary_md(
    system_prompt: str,
    summary_file_list: list[dict],
    user_id: str,
    raw_data: Optional[str] = None,
    llm_model: AI_API = AI_API.OPENAI_o4_mini,
    force: bool = False,
) -> Path:
    """
    Generate a full summary in Markdown format.

    Combines multiple topic summaries into a comprehensive report.

    Args:
        system_prompt: Prompt for full summary generation
        summary_file_list: List of dicts with {label: filename}
        user_id: User identifier
        raw_data: Optional raw event data to include
        llm_model: Model to use for generation
        force: If True, generate regardless of existing summary

    Returns:
        Path to saved summary file
    """
    logger.info(f"Creating full summary for user {user_id}")

    # Load all summary files
    summary_dict: dict[str, Any] = {}

    for summary_file in summary_file_list:
        label = list(summary_file.keys())[0]
        file_name = list(summary_file.values())[0]

        logger.debug(f"Loading summary file: {file_name}")
        file_content = get_topic_file_by_name(user_id, str(file_name))

        if not file_content:
            logger.warning(f"Summary file {file_name} not found, skipping")
            continue

        try:
            summary_dict[label] = json.loads(file_content)
            logger.debug(f"Loaded {label}: {len(file_content)} chars")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {file_name}: {e}")
            continue

    if not summary_dict:
        logger.error("No valid summary files loaded")
        raise ValueError("No summary data available to generate full summary")

    # Prepare payload
    payload_data = {"model": llm_model.value, **summary_dict}

    if raw_data:
        payload_data["events"] = raw_data

    wrapped = json.dumps(payload_data, ensure_ascii=False, indent=2)

    # Generate full summary
    logger.debug(f"Generating full summary with {llm_model.value}")
    try:
        md = make_llm_request(system_prompt, wrapped, llm_model)
    except Exception as e:
        logger.error(f"Failed to generate full summary: {e}", exc_info=True)
        raise

    # Save and return path
    full_summary_path = save_full_summary(user_id, md)
    logger.info(f"Saved full summary to {full_summary_path}")

    return full_summary_path


__all__ = [
    "create_summary_json",
    "create_summary_md",
]
