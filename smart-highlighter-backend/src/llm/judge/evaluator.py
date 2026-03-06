"""LLM-as-Judge evaluation system.

This module provides functionality to evaluate summaries using LLMs
as judges, applying rubrics to assess quality across multiple dimensions.
"""

from typing import Optional

from src.core.storage import (add_to_evaluation_sheet, get_all_evaluations,
                              get_evaluation_summary_sheet,
                              get_topic_file_by_name, save_rubric_evaluation)
# Import rubric modules
from src.llm.judge import (full_summary_rubric_comparison,
                           full_summary_rubric_examples, judge_output_rubric,
                           topic_summary_rubric)
from src.llm.request import AI_API, make_llm_request
from src.utils.logging import get_logger

logger = get_logger(__name__)


def apply_rubric(
    original_prompt: str,
    summary_file: str,
    summaries_model: AI_API,
    user_id: str,
    notes: str = "",
    llm_model: AI_API = AI_API.OPENAI_o4_mini,
) -> Optional[str]:
    """
    Apply rubric evaluation to a summary file.

    Args:
        original_prompt: The original prompt used to generate the summary
        summary_file: Filename of the summary to evaluate
        summaries_model: Model that generated the summary
        user_id: User identifier
        notes: Additional context/notes
        llm_model: Model to use as judge

    Returns:
        Path to saved evaluation file, or None if failed
    """
    logger.info(f"Evaluating summary {summary_file} from {summaries_model.value}")

    try:
        # Get summary content
        from src.core.storage import get_full_summary

        text_to_evaluate = get_full_summary(summary_file, user_id)

        if not text_to_evaluate:
            logger.warning(f"No text to evaluate at {summary_file}")
            return None

        # Prepare evaluation context
        prompt_and_text = (
            f"model: {summaries_model.value}\n"
            f"other_details: {notes}\n"
            f"original_prompt: {original_prompt}\n"
            f"text_to_evaluate: {text_to_evaluate}"
        )

        # Get rubric
        rubric = full_summary_rubric_comparison.get_rubric()

        # Perform evaluation
        logger.debug("Sending evaluation request to LLM judge")
        output = make_llm_request(prompt_and_text, rubric, llm_model)

        # Save evaluation
        saved_file = save_rubric_evaluation(user_id, output)
        logger.info(f"Saved rubric evaluation to {saved_file}")

        return str(saved_file)

    except Exception as e:
        logger.error(f"Failed to apply rubric: {e}", exc_info=True)
        return None


COMBINED_PROMPT = (
    "You are an expert data analyst and AI specialist. "
    "Your task is to merge two sets of notes into a single comprehensive summary. "
    "Focus on comparing the scores as you compare both sets of data"
)


def compile_scores(user_id: str) -> None:
    """
    Retrieve all evaluations and merge them into a single comprehensive sheet.

    Iteratively merges evaluation files, comparing scores and building
    a consolidated view of all evaluations.

    Args:
        user_id: User identifier
    """
    logger.info(f"Compiling evaluation scores for user {user_id}")

    evaluation_files = get_all_evaluations(user_id)
    logger.info(f"Found {len(evaluation_files)} evaluation files")

    for file_path in evaluation_files:
        try:
            # Get current main sheet
            main_topics_sheet = get_evaluation_summary_sheet(user_id)

            # Get content from evaluation file
            content = get_topic_file_by_name(
                user_id, file_path.name, directory="rubric_evaluations"
            )

            if not content:
                logger.warning(f"Empty content in {file_path}")
                continue

            # First file - just copy it
            if len(main_topics_sheet) == 0:
                logger.debug(f"Initializing evaluation sheet with {file_path.name}")
                add_to_evaluation_sheet(user_id, content)
            else:
                # Merge with existing sheet
                logger.debug(f"Merging {file_path.name} into evaluation sheet")
                wrapped_data = (
                    f"Primary file:\n{main_topics_sheet}\n\n"
                    f"New data to merge:\n{content}"
                )

                output = make_llm_request(
                    COMBINED_PROMPT, wrapped_data, AI_API.OPENAI_o4_mini
                )

                add_to_evaluation_sheet(user_id, output)
                logger.info(f"Successfully merged {file_path.name}")

        except Exception as e:
            logger.error(
                f"Failed to process evaluation file {file_path}: {e}", exc_info=True
            )
            continue

    logger.info("Finished compiling evaluation scores")


__all__ = ["apply_rubric", "compile_scores"]
