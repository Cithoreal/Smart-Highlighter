from __future__ import annotations
import sys

"""High‑level summary orchestration.

This module handles two tiers of summarisation:

1. *Topic summaries* – quick JSON snapshots of active topics, generated
   hourly **when needed** (time/volume heuristic).
   2. *Full summaries*  – end‑of‑day Markdown reports, built on demand or
      via a nightly scheduler.  These embed the latest topic JSON and cite
         exact `event_id` ranges for traceability.

         Both rely on the raw‑event helpers in ``storage.py``.
         """

from datetime import datetime, timedelta, date
from typing import Optional, Any
import json
import os
import logging
from pathlib import Path
from llm_apis.llm_request import AI_API, make_llm_request
from storage import (
iter_events,
today_event_count,
latest_topic_summary,
save_topic_summary,
save_full_summary,
get_topic_file_by_name
)
#logger = logging.getLogger(__name__)
#logger.addHandler(logging.StreamHandler(sys.stdout)) 
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()  # This sends logs to the console
    ]
)
# ---------------------------------------------------------------------------
# Config --------------------------------------------------------------------
# ---------------------------------------------------------------------------

MODEL = "o4-mini"
# Heuristics
MAX_EVENT_GAP = 3600           # secs before we consider the topic summary stale
MAX_NEW_LINES  = 200           # lines of fresh data to trigger new summary

# ---------------------------------------------------------------------------
# Internal helpers -----------------------------------------------------------
# ---------------------------------------------------------------------------




def _need_new_topic_summary(new_line_cnt: int, last_generated_at: Optional[str]) -> bool:
    if last_generated_at is None:
        return True
    last_dt = datetime.fromisoformat(last_generated_at)
    age = (datetime.utcnow() - last_dt).total_seconds()
    if age > MAX_EVENT_GAP:
        return True
    if new_line_cnt > MAX_NEW_LINES:
        return True
    return False

# ---------------------------------------------------------------------------
# Public API -----------------------------------------------------------------
# ---------------------------------------------------------------------------
import yaml
def create_summary_json(system_prompt: dict, latest_events: str, llm_model: AI_API = AI_API.OPENAI_o4_mini, force: bool = False, user_id: Optional[str] = None) -> dict[str, Any]:
    
    """Return a topic summary, generating a new one only if necessary."""
    label = list(system_prompt.keys())[0]
    logging.info(f"Creating topic summary... user_id: {user_id}, label: {label}")
    system_prompt = system_prompt[label]
    
    new_line_cnt = len(latest_events)
    last = latest_topic_summary(user_id=user_id)

    last_ts: Optional[str] = last.get("generated_at") if last else None

    if not force and not _need_new_topic_summary(new_line_cnt, last_ts):
        logging.debug("Topic summary fresh – skipping generation")
        return last
    
    # Build prompt -----------------------------------------------------------
    # system_prompt = (
    #     "You are an analyst.  You receive an array of browsing events.  "
    #     "Each event has an `event_id` (integer) and other metadata.  "
    #     "Identify all main topics the user is exploring.  Return valid "
    #     "JSON in the form: [{ 'topic': str, 'description': str, "
    #     "'event_range': [start_id, end_id] }, ...]  "
    #     "Order the array by importance / user activity.  "
    #     "Always cite the smallest contiguous event_id range covering the topic."
    # )

    payload = json.dumps(latest_events, ensure_ascii=False, indent=2)
    summary_txt = make_llm_request(system_prompt, payload, llm_model)
 
    try:
        summary_json = json.loads(summary_txt)
    except json.JSONDecodeError:
        # Fallback: wrap raw LLM string
        summary_json = {"error": "LLM returned invalid JSON", "raw": summary_txt}

    # Ensure we can attach metadata even if LLM returns a list
    if isinstance(summary_json, list):
        summary_json = {label: summary_json}
    summary_json["generated_at"] = datetime.utcnow().isoformat()
    
    #returning path instead of text
    topic_save = save_topic_summary(label, summary_json, user_id=user_id)
    return topic_save
    #return summary_json


def create_summary_md(system_prompt: str, summary_file_list: list[dict], raw_data: str = None, llm_model: AI_API = AI_API.OPENAI_o4_mini, force: bool = False, user_id: Optional[str] = None) -> str:
    """Return a markdown daily report, generating one if *force* is True."""
    # Ensure we have the freshest topic file first.
    #topics = create_summary_json(force=force)
    logging.debug("Creating full summary")


    # system_prompt = (
    #     "You are a technical writer.  Using the *topics* and *events* JSON "
    #     "below, create a structured table in markdown format with the following columns. First create a summary"
    #     "of all of the main topics. There could be any number of main topics in the file. After you have all of the topics listed, go through each one and"
    #     "create the table. If there has been no activity for over a minute, assume the user is inactive during the time on page. Write each cell with multiple"
    #     "entries as bulleted lists. Main topic: - Description: “What is the primary goal, intention, or topic the user is browsing for? Sort by timestamp"
    #     "ascending of when a topic is first explored.” Sub topics: - Description: “What does the main topic break down into from the user’s activity?”"
    #     "Behavior: - Description: “What insights can you interpret from the way the user is browsing this topic?” Data insights: - Description: “What insights"
    #     "can you interpret from the data collected? ” Summaries of research: - Description: “Summarize all of the information collected from this topic.”"
    #     "Selected text: - Description: “Copy important selections the user made exactly.” Ad traces: - Description: “Separate any ads or sponsors collected"
    #     "while browsing this topic and collect them here  "
    #     "When referencing evidence, cite event_id ranges in parentheses, e.g. "
    #     "(events 233–271).  Finish with a bullet‑point recap of open questions "
    #     "or next steps."
    # )
    summary_dict: dict[str, Any] = {}
    for summary_file in summary_file_list:
        print(f"Processing summary file: {summary_file}")
        label = list(summary_file.keys())[0]
        file_name = list(summary_file.values())[0]
        #logging.debug("Processing summary file: %s", file_name.values())
        file_path = get_topic_file_by_name(file_name,user_id=user_id)
        if not file_path:
            logging.warning("Summary file %s not found, skipping", file_name)
            continue

        try:
            content = Path(file_path).read_text(encoding="utf-8")
            logging.debug(f"Loaded summary file {file_name} with {len(content)} characters")
            summary_dict[label] = json.loads(content)
        except (OSError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read/parse {file_name}: {e}")
    if raw_data:
        raw_events = raw_data
        wrapped = json.dumps(
            {"model": llm_model.value,"events": raw_events, **summary_dict},
            ensure_ascii=False,
            indent=2
        )
    else :
        wrapped = json.dumps(
            {"model": llm_model.value, **summary_dict},
            ensure_ascii=False,
            indent=2
        )

    md = make_llm_request(system_prompt, wrapped, llm_model)
    full_summary_file = save_full_summary(md, user_id=user_id)
    return full_summary_file


__all__ = [
    "create_summary_json",
    "create_summary_md",
]
