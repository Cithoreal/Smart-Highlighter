"""Centralized file-based storage utilities.

This module handles:
- Raw events stored as newline-delimited JSON (NDJSON)
- Topic summaries (JSON files)
- Full summaries (Markdown files)
- Rubric evaluations

Each event receives:
    • event_id    – monotonic integer (never reused)
    • timestamp   – UTC ISO-8601 string

Note: Database migration planned for a future phase after security hardening.
"""

import asyncio
import json
from datetime import date, datetime
from itertools import count
from pathlib import Path
from typing import Iterable, Optional

from src.utils.logging import get_logger
from src.utils.paths import (ensure_dir_exists, get_metadata_path,
                             get_raw_log_path, get_summaries_dir,
                             get_user_data_dir)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Concurrency primitives
# ---------------------------------------------------------------------------

log_lock = asyncio.Lock()  # protects raw log (append + read)


# ---------------------------------------------------------------------------
# Event ID management
# ---------------------------------------------------------------------------


def _initial_event_id(user_id: str) -> int:
    """Return the highest existing event_id or 0 if file is empty."""
    try:
        raw_log_file = get_raw_log_path(user_id)

        if not raw_log_file.exists():
            return 0

        # Seek from the end to grab the last line
        with raw_log_file.open("rb") as file:
            file.seek(0, 2)  # Go to end
            file_size = file.tell()

            if file_size == 0:
                return 0

            # Read backwards to find last complete line
            file.seek(-2, 2)
            while file.tell() > 0 and file.read(1) != b"\n":
                file.seek(-2, 1)

            last_line = file.readline().decode().strip()
            if last_line:
                return json.loads(last_line).get("event_id", 0)

        return 0
    except Exception as e:
        logger.error(f"Error reading initial event_id for {user_id}: {e}")
        return 0


# ---------------------------------------------------------------------------
# Raw event operations
# ---------------------------------------------------------------------------


async def append_event(user_id: str, event: dict) -> int:
    """
    Append a single event to web_tracking_log.ndjson.

    Adds event_id + UTC timestamp automatically.
    Guarded by an asyncio.Lock for intra-process safety.

    Args:
        user_id: User identifier
        event: Event data dictionary

    Returns:
        The assigned event_id
    """
    raw_log_file = get_raw_log_path(user_id)

    # Ensure directory exists
    ensure_dir_exists(raw_log_file.parent)

    async with log_lock:
        # Get next event ID
        event_id = _initial_event_id(user_id) + 1

        # Add metadata
        event["event_id"] = event_id
        event["timestamp"] = datetime.utcnow().isoformat()

        # Append to log
        with raw_log_file.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")

        logger.debug(f"Appended event {event_id} for user {user_id}")
        return event_id


def iter_events(
    user_id: str,
    day: Optional[date] = None,
    start_id: Optional[int] = None,
    end_id: Optional[int] = None,
) -> Iterable[dict]:
    """
    Yield events with optional filtering.

    Args:
        user_id: User identifier
        day: Filter by UTC calendar day
        start_id: Minimum event_id (inclusive)
        end_id: Maximum event_id (inclusive)

    Yields:
        Event dictionaries
    """
    raw_log_file = get_raw_log_path(user_id)

    if not raw_log_file.exists():
        return

    with raw_log_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                logger.warning(f"Skipping malformed JSON line: {line[:100]}")
                continue

            # Filter by day
            if day is not None:
                timestamp = event.get("timestamp", "")
                if not timestamp.startswith(str(day)):
                    continue

            # Filter by event_id range
            event_id = event.get("event_id")
            if event_id is not None:
                if start_id is not None and event_id < start_id:
                    continue
                if end_id is not None and event_id > end_id:
                    continue

            yield event


def get_events_by_id(user_id: str, start: int, end: Optional[int] = None) -> list[dict]:
    """
    Return events whose event_id matches criteria.

    Args:
        user_id: User identifier
        start: Starting event_id (inclusive)
        end: Ending event_id (inclusive). If None, return single event.

    Returns:
        List of matching events
    """
    if end is None:
        # Single event
        events = list(iter_events(user_id, start_id=start, end_id=start))
        return events[:1]

    # Range of events
    return list(iter_events(user_id, start_id=start, end_id=end))


def today_event_count(user_id: str) -> int:
    """Quick count for need-new-summary heuristics."""
    return sum(1 for _ in iter_events(user_id, day=date.today()))


# ---------------------------------------------------------------------------
# Metadata operations
# ---------------------------------------------------------------------------


def get_metadata(user_id: str) -> dict:
    """
    Return the metadata as a dict (empty if none).

    Args:
        user_id: User identifier

    Returns:
        Metadata dictionary
    """
    md_file = get_metadata_path(user_id)

    if not md_file.exists():
        return {}

    try:
        # Read all NDJSON lines and merge
        metadata = {}
        with md_file.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    metadata.update(data)
                except json.JSONDecodeError:
                    logger.warning(f"Skipping malformed metadata line: {line[:100]}")
        return metadata
    except Exception as e:
        logger.error(f"Error reading metadata for {user_id}: {e}")
        return {}


def append_event_to_metadata(user_id: str, event: dict) -> None:
    """
    Append a single event to the metadata NDJSON file.

    Args:
        user_id: User identifier
        event: Event data dictionary
    """
    md_file = get_metadata_path(user_id)
    ensure_dir_exists(md_file.parent)

    with md_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Summary operations
# ---------------------------------------------------------------------------


def _save_json(directory: Path, payload: dict, label: str = "") -> Path:
    """Save a JSON file with timestamp."""
    timestamp = datetime.now().timestamp()
    filename = f"{label}-{timestamp}.json" if label else f"{timestamp}.json"
    file_path = directory / filename

    with file_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)

    return file_path


def _save_text(directory: Path, text: str, suffix: str) -> Path:
    """Save a text file with timestamp."""
    timestamp = datetime.now().timestamp()
    file_path = directory / f"{timestamp}{suffix}"

    with file_path.open("w", encoding="utf-8") as fh:
        fh.write(text or "")

    return file_path


def save_topic_summary(user_id: str, label: str, summary: dict) -> Path:
    """
    Persist a topic summary (JSON).

    Args:
        user_id: User identifier
        label: Topic label
        summary: Summary data

    Returns:
        Path to saved file
    """
    topic_dir = get_summaries_dir(user_id, "topics")
    ensure_dir_exists(topic_dir)

    return _save_json(topic_dir, summary, label=label)


def save_full_summary(user_id: str, markdown: str) -> Path:
    """
    Persist a full summary (Markdown).

    Args:
        user_id: User identifier
        markdown: Summary content

    Returns:
        Path to saved file
    """
    full_dir = get_summaries_dir(user_id, "full")
    ensure_dir_exists(full_dir)

    return _save_text(full_dir, markdown, ".md")


def save_rubric_evaluation(user_id: str, markdown: str) -> Path:
    """
    Persist a rubric evaluation (Markdown).

    Args:
        user_id: User identifier
        markdown: Evaluation content

    Returns:
        Path to saved file
    """
    user_dir = get_user_data_dir(user_id)
    rubric_dir = user_dir / "rubric_evaluations"
    ensure_dir_exists(rubric_dir)

    return _save_text(rubric_dir, markdown, ".md")


# ---------------------------------------------------------------------------
# Summary retrieval
# ---------------------------------------------------------------------------


def _latest_file(dir_path: Path, pattern: str) -> Optional[Path]:
    """Get the most recently modified file matching pattern."""
    if not dir_path.exists():
        return None

    files = list(dir_path.glob(pattern))
    return max(files, default=None, key=lambda p: p.stat().st_mtime)


def latest_topic_summary(user_id: str) -> Optional[dict]:
    """Get the latest topic summary."""
    topic_dir = get_summaries_dir(user_id, "topics")
    file_path = _latest_file(topic_dir, "*.json")

    if not file_path:
        return None

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Failed to parse topic summary: {file_path}")
        return None


def latest_full_summary(user_id: str) -> Optional[str]:
    """Get the latest full summary."""
    full_dir = get_summaries_dir(user_id, "full")
    file_path = _latest_file(full_dir, "*.md")

    if not file_path:
        return None

    return file_path.read_text(encoding="utf-8")


def get_topic_file_by_name(user_id: str, topic: str) -> Optional[str]:
    """
    Return topic file content by name.

    Args:
        user_id: User identifier
        topic: Topic filename

    Returns:
        File content or None
    """
    topic_dir = get_summaries_dir(user_id, "topics")
    file_path = topic_dir / topic

    if file_path.exists():
        return file_path.read_text(encoding="utf-8")

    return None


def get_all_full_summaries(user_id: str) -> list[Path]:
    """Return all full summary files."""
    full_dir = get_summaries_dir(user_id, "full")

    if not full_dir.exists():
        return []

    return list(full_dir.glob("*.md"))


def get_all_evaluations(user_id: str) -> list[Path]:
    """Return all rubric evaluation files."""
    user_dir = get_user_data_dir(user_id)
    rubric_dir = user_dir / "rubric_evaluations"

    if not rubric_dir.exists():
        return []

    return list(rubric_dir.glob("*.md"))


# ---------------------------------------------------------------------------
# Topic/Behavior sheet operations (user-level JSON files)
# ---------------------------------------------------------------------------


def get_main_topics_summary_sheet(user_id: str, topic: str) -> list:
    """Get main topics summary sheet content."""
    user_dir = get_user_data_dir(user_id)
    topic_file = user_dir / f"{topic}.json"

    if not topic_file.exists():
        ensure_dir_exists(topic_file.parent)
        topic_file.write_text("[]", encoding="utf-8")
        return []

    try:
        return json.loads(topic_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Failed to parse topic sheet: {topic_file}")
        return []


def add_to_main_topics_summary_sheet(user_id: str, topic: str, content: str) -> None:
    """Add content to main topics summary sheet."""
    user_dir = get_user_data_dir(user_id)
    topic_file = user_dir / f"{topic}.json"

    ensure_dir_exists(topic_file.parent)
    topic_file.write_text(content, encoding="utf-8")


def get_evaluation_summary_sheet(user_id: str) -> list:
    """Get evaluation summary sheet content."""
    user_dir = get_user_data_dir(user_id)
    eval_file = user_dir / "evaluation.json"

    if not eval_file.exists():
        ensure_dir_exists(eval_file.parent)
        eval_file.write_text("[]", encoding="utf-8")
        return []

    try:
        return json.loads(eval_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.error(f"Failed to parse evaluation sheet: {eval_file}")
        return []


def add_to_evaluation_sheet(user_id: str, content: str) -> None:
    """Add content to evaluation sheet."""
    user_dir = get_user_data_dir(user_id)
    eval_file = user_dir / "evaluation.json"

    ensure_dir_exists(eval_file.parent)
    eval_file.write_text(content, encoding="utf-8")


__all__ = [
    "append_event",
    "iter_events",
    "get_events_by_id",
    "today_event_count",
    "get_metadata",
    "append_event_to_metadata",
    "save_topic_summary",
    "save_full_summary",
    "save_rubric_evaluation",
    "latest_topic_summary",
    "latest_full_summary",
    "get_topic_file_by_name",
    "get_all_full_summaries",
    "get_all_evaluations",
    "get_main_topics_summary_sheet",
    "add_to_main_topics_summary_sheet",
    "get_evaluation_summary_sheet",
    "add_to_evaluation_sheet",
]
