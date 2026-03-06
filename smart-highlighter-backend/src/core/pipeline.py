"""Web tracking data processing pipeline.

This module orchestrates the full pipeline for processing web tracking data:
1. Load raw events from NDJSON logs
2. Generate topic summaries using LLMs
3. Create full summaries combining multiple perspectives
4. Apply LLM-as-Judge evaluation rubrics

The pipeline supports multiple models and configurable summary options.
"""

import json
from typing import Any, Optional

from src.core.chunking import chunk_and_record, get_whole_log
from src.core.storage import (add_to_main_topics_summary_sheet,
                              get_all_full_summaries,
                              get_main_topics_summary_sheet,
                              get_topic_file_by_name)
from src.core.summarizer import create_summary_json, create_summary_md
from src.llm.judge.evaluator import apply_rubric, compile_scores
from src.llm.prompts import (actionable_steps_prompt_json,
                             behavior_insights_prompt_json,
                             build_full_summary_prompt, full_summary_prompt,
                             selections_prompt_json, topic_combination_prompt,
                             topic_summary_prompt_json)
from src.llm.request import AI_API, make_llm_request
from src.utils.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Pipeline Configuration
# ---------------------------------------------------------------------------

# Middle layer prompts (topic extraction, behavior analysis, etc.)
JSON_SUMMARY_PROMPTS = [
    {"topics": topic_summary_prompt_json},
    {"selections": selections_prompt_json},
    {"behavior": behavior_insights_prompt_json},
    {"actionable_steps": actionable_steps_prompt_json},
]

# Final report configuration
FULL_SUMMARY_OPTIONS = {
    "description": True,
    "selected_text": True,
    "behavior_analysis": True,
    "data_insights": True,
    "ad_traces": True,
    "actionable_steps": True,
}

# Models to use for generation
DEFAULT_MODELS = [AI_API.GOOGLE]


# ---------------------------------------------------------------------------
# Pipeline Execution
# ---------------------------------------------------------------------------


def run_pipeline(user_id: str, models: Optional[list[AI_API]] = None) -> list[str]:
    """
    Run the complete web tracking pipeline for a user.

    Processes all raw event data and generates summaries.

    Args:
        user_id: User identifier
        models: List of models to use (defaults to DEFAULT_MODELS)

    Returns:
        List of report file paths
    """
    logger.info(f"Running web tracking pipeline for user {user_id}")

    if models is None:
        models = DEFAULT_MODELS

    try:
        # Load raw data
        raw_data = get_whole_log(user_id)

        if not raw_data:
            logger.warning(f"No raw data found for user {user_id}")
            return []

        logger.info(f"Loaded {len(raw_data)} chars of raw data")

        # Run models
        report = run_models(raw_data, user_id, models)
        reports = [{"full_log": report}]

        logger.info(f"Pipeline complete. Generated {len(reports)} reports")
        return reports

    except Exception as e:
        logger.error(f"Pipeline failed for user {user_id}: {e}", exc_info=True)
        raise


def run_models(raw_data: str, user_id: str, models: list[AI_API]) -> list[str]:
    """
    Run multiple models on raw data.

    Args:
        raw_data: Raw event data (NDJSON)
        user_id: User identifier
        models: List of models to use

    Returns:
        List of report file paths
    """
    logger.info(f"Running {len(models)} models on data for user {user_id}")

    reports = []

    for model in models:
        try:
            logger.info(f"Processing with model: {model.value}")

            notes = (
                f"JSON - topics, behavior insights, selections, actionable steps preprocessed "
                f"- raw data is NDJSON"
            )

            report = run_pipeline_json(
                JSON_SUMMARY_PROMPTS, raw_data, user_id, model=model, notes=notes
            )

            reports.append(report)
            logger.info(f"Model {model.value} complete")

        except Exception as e:
            logger.error(f"Model {model.value} failed: {e}", exc_info=True)
            continue

    return reports


def run_pipeline_json(
    summary_prompts: list[dict],
    raw_data: str,
    user_id: str,
    model: AI_API = AI_API.OPENAI_o4_mini,
    json_format_raw: bool = False,
    notes: str = "",
) -> Optional[str]:
    """
    Run pipeline with JSON-formatted summaries.

    Args:
        summary_prompts: List of {label: prompt} dicts
        raw_data: Raw event data
        user_id: User identifier
        model: Model to use
        json_format_raw: If True, parse NDJSON to JSON first
        notes: Additional notes for evaluation

    Returns:
        Path to rubric evaluation file
    """
    logger.info(f"Running JSON pipeline for user {user_id} with {model.value}")

    try:
        # Parse NDJSON if requested
        if json_format_raw:
            raw_data_parsed = parse_ndjson(raw_data)
            if raw_data_parsed is None:
                logger.error("Failed to parse NDJSON data")
                return None
            raw_data = json.dumps(raw_data_parsed, indent=2)

        # Generate topic summaries
        summary_files_list = []

        for summary_prompt in summary_prompts:
            label = list(summary_prompt.keys())[0]
            logger.debug(f"Generating {label} summary")

            summary_path = create_summary_json(
                summary_prompt,
                latest_events=raw_data,
                user_id=user_id,
                llm_model=model,
                force=True,
            )

            summary_files_list.append({label: summary_path})

        logger.info(f"Generated {len(summary_files_list)} topic summaries")

        # Generate full summary
        full_summary_prompt = build_full_summary_prompt(FULL_SUMMARY_OPTIONS)

        full_summary = create_summary_md(
            full_summary_prompt,
            summary_files_list,
            user_id=user_id,
            raw_data=raw_data,
            llm_model=model,
            force=True,
        )

        logger.info(f"Generated full summary: {full_summary}")

        # Apply evaluation rubric
        rubric_file = apply_rubric(
            full_summary_prompt,
            str(full_summary.name),
            model,
            user_id=user_id,
            notes=notes,
        )

        if rubric_file:
            logger.info(f"Applied rubric evaluation: {rubric_file}")

        return rubric_file

    except Exception as e:
        logger.error(f"JSON pipeline failed: {e}", exc_info=True)
        raise


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------


def parse_ndjson(blob: str) -> Optional[list[dict]]:
    """
    Parse NDJSON string into list of dictionaries.

    Args:
        blob: NDJSON string

    Returns:
        List of parsed objects, or None if parsing fails
    """
    if not isinstance(blob, str):
        logger.error("Input must be a string containing NDJSON data")
        return None

    decoder = json.JSONDecoder()
    objs = []

    for lineno, line in enumerate(blob.splitlines(), start=1):
        txt = line.strip()
        if not txt:
            continue

        try:
            objs.append(decoder.decode(txt))
        except json.JSONDecodeError as e:
            logger.warning(f"Skipping malformed NDJSON (line {lineno}): {e}")

    logger.debug(f"Parsed {len(objs)} objects from NDJSON")
    return objs


def combine_topics(topic: str, user_id: str) -> None:
    """
    Merge all topic summaries into a primary topics sheet.

    Iteratively combines topic summaries using LLM to maintain
    a consolidated view of all topics.

    Args:
        topic: Topic name/label
        user_id: User identifier
    """
    logger.info(f"Combining topics for {topic}, user {user_id}")

    for file_path in get_all_full_summaries(user_id):
        try:
            main_sheet = get_main_topics_summary_sheet(user_id, topic)
            content = get_topic_file_by_name(user_id, str(file_path.name))

            if not content:
                logger.warning(f"Empty content in {file_path}")
                continue

            # Initialize sheet if empty
            if len(main_sheet) == 0:
                logger.debug(f"Initializing topics sheet with {file_path.name}")
                add_to_main_topics_summary_sheet(user_id, topic, content)
            else:
                # Merge with existing
                logger.debug(f"Merging {file_path.name} into topics sheet")
                wrapped_data = (
                    f"Primary file:\n{main_sheet}\n\n" f"New data to merge:\n{content}"
                )

                output = make_llm_request(
                    topic_combination_prompt, wrapped_data, AI_API.OPENAI_o4_mini
                )

                add_to_main_topics_summary_sheet(user_id, topic, output)
                logger.info(f"Successfully merged {file_path.name}")

        except Exception as e:
            logger.error(
                f"Failed to combine topics for {file_path}: {e}", exc_info=True
            )
            continue


def judge_reports(user_id: str, model: AI_API = AI_API.OPENAI_o4_mini) -> None:
    """
    Apply LLM-as-Judge evaluation to all reports for a user.

    Args:
        user_id: User identifier
        model: Model to use as judge
    """
    logger.info(f"Judging reports for user {user_id} with {model.value}")

    try:
        for file_path in get_all_full_summaries(user_id):
            logger.debug(f"Judging report: {file_path.name}")
            apply_rubric(full_summary_prompt, file_path.name, model, user_id=user_id)

        logger.info("Finished judging all reports")

    except Exception as e:
        logger.error(f"Failed to judge reports: {e}", exc_info=True)
        raise


__all__ = [
    "run_pipeline",
    "run_models",
    "run_pipeline_json",
    "parse_ndjson",
    "combine_topics",
    "judge_reports",
]
