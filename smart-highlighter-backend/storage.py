from __future__ import annotations
import sys

"""Centralised file‑based storage utilities.

▪ Raw events are stored as **newline‑delimited JSON** (ND‑JSON) in
  ``data/raw/tracking_log.ndjson``.
▪ Summaries live under ``data/summaries`` in two sub‑folders:
    ├─ topics/  →  *.json (hourly-ish)
    └─ full/    →  *.md   (daily or on‑demand)

Each event receives:
    • ``event_id``    – monotonic integer (never reused)
    • ``timestamp``   – UTC ISO‑8601 string

The helpers here are purposely minimal so they can be re‑used unchanged
when we swap the backend to SQLite or DuckDB later.
"""

from pathlib import Path
from datetime import datetime, date
from itertools import count
from typing import Iterable, Optional
import asyncio
import json
import yaml
import os
import logging

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
# Directory layout -----------------------------------------------------------
# ---------------------------------------------------------------------------


BASE_DIR   = Path(__file__).parent / "data/" 
RAW_DIR    ="raw/"
SUMMARY_DIR = "summaries/"
TOPIC_DIR  = SUMMARY_DIR + "topics/"
FULL_DIR   = SUMMARY_DIR + "full/"
RUBRIC_DIR = "rubric_evaluations/"


# Ensure the folder tree exists on import so that first writes succeed.
for _p in (RAW_DIR, TOPIC_DIR, FULL_DIR, RUBRIC_DIR):
    Path(_p).mkdir(parents=True, exist_ok=True)

RAW_LOG_FILE = "web_tracking_log"
METADATA_FILE = "web_tracking_metadata.ndjson"

# ---------------------------------------------------------------------------
# Concurrency primitives -----------------------------------------------------
# ---------------------------------------------------------------------------

log_lock = asyncio.Lock()               # protects RAW_LOG (append + read)

# Initialise a monotonic counter that continues after restarts -------------

def _initial_event_id(user_id) -> int:
    """Return the highest existing ``event_id`` or 0 if file is empty."""
    raw_log = BASE_DIR / user_id / "raw" 
    Path(raw_log).mkdir(parents=True, exist_ok=True)
    raw_log_file = Path(raw_log / "web_tracking_log.ndjson")
    if not raw_log_file.exists():
        return 0

    try:
        # Seek from the end to grab the last line cheaply.
        with raw_log_file.open("rb") as file:
            file.seek(-2, os.SEEK_END)       # jump before final newline
            while file.read(1) != b"\n":
                file.seek(-2, os.SEEK_CUR)
            last_line = file.readline().decode()
            return json.loads(last_line).get("event_id", 0)
    except (OSError, json.JSONDecodeError):
        return 0

#_id_counter = count(_initial_event_id() + 1)

# ---------------------------------------------------------------------------
# Raw‑event helpers ----------------------------------------------------------
# ---------------------------------------------------------------------------

async def append_event(event: dict, user_id) -> None:
    """Append a single event to ``web_tracking_log.ndjson, web_tracking_log.json, and web_tracking_log.yaml``.

    Adds ``event_id`` + UTC ``timestamp`` automatically.
    Guarded by an ``asyncio.Lock`` for intra‑process safety.
    """
    
    # Add event to json and yaml log files
    raw_log = BASE_DIR / user_id / "raw" 
    Path(raw_log).mkdir(parents=True, exist_ok=True)
    raw_log = raw_log / "web_tracking_log.ndjson"
    async with log_lock:
        event["event_id"] = next(count(_initial_event_id(user_id) + 1))
        event["timestamp"] = datetime.utcnow().isoformat()

        # Write append‑only.
        with raw_log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        
        #await append_event_to_yaml(event)    
        #await append_event_to_json(event)
        
      
# async def append_event_to_yaml(event:dict)-> None:
#     """Append a single event to the YAML log file."""
    
    
#     yaml_file = RAW_LOG.with_suffix(".yaml")
#     if yaml_file.exists():
#         with yaml_file.open("r", encoding="utf-8") as fh:
#             file_data = fh.read()
#             yaml_data = yaml.safe_load(file_data) if file_data else []
#     else:
#         yaml_data = []

#     if isinstance(yaml_data, list):
#         yaml_data.append(event)
#     else:
#         yaml_data = event

#     with yaml_file.open("w", encoding="utf-8") as fh:
#         yaml.dump(yaml_data, fh, allow_unicode=True, default_flow_style=False)
        

# async def append_event_to_json(event:dict)-> None:
#     """Append a single event to the JSON log file."""
    
#     json_file = RAW_LOG.with_suffix(".json")
#     with json_file.open("r", encoding="utf-8") as fh:
#         file_data = fh.read()
#         if file_data:
#             json_data = json.loads(file_data)
#             if isinstance(json_data, list):
#                 json_data.append(event)
#             else:
#                 json_data = [json_data, event]
#     with json_file.open("w", encoding="utf-8") as fh:
#         json.dump(json_data, fh, indent=2, ensure_ascii=False)

def get_main_topics_summary_sheet(topic: str, user_id:str):
    user_dir = BASE_DIR / user_id 
    topic_file = f"{user_dir}/{topic}.json"
    
    topic_path = Path(topic_file)
    if not topic_path.exists():
        topic_path.parent.mkdir(parents=True, exist_ok=True)
        topic_path.write_text("[]", encoding="utf-8")
    with topic_path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
def add_to_main_topics_summary_sheet(topic, content, user_id):
    user_dir = BASE_DIR / user_id 
    topic_file = f"{user_dir}/{topic}.json"
    
    topic_path = Path(topic_file)
    print(content)
    topic_path.write_text(content, encoding="utf-8")
   
    
def get_metadata(user_id: str) -> dict:
    """Return the metadata JSON file as a dict (empty if none)."""
    md_dir  = BASE_DIR / user_id
    md_file = md_dir / METADATA_FILE
    md_dir.mkdir(parents=True, exist_ok=True)
    print(md_file)
    if not md_file.exists():
        return {}
    try:
        with md_file.open("r", encoding="utf-8") as fh:
            print(json.load(fh))
            return json.load(fh)
    except json.JSONDecodeError:        # corrupted → start clean but keep a backup
        return {}
        
def append_event_to_metadata(event:dict, user_id)-> None:
    """Append a single event to the metadata JSON file."""
    #print(event)
    #logging.debug(f"Appending event to metadata: {event}")
    metadata_dir = BASE_DIR / user_id 
    #Path(metadata_dir).mkdir(parents=True, exist_ok=True)
    metadata_file = Path(metadata_dir) / METADATA_FILE
    with metadata_file.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def iter_events(day: Optional[date] = None, user_id: Optional[str] = None) -> Iterable[dict]:
    """Yield events; optionally filter by UTC calendar day."""
    raw_log_dir = BASE_DIR / user_id / RAW_DIR
    Path(raw_log_dir).mkdir(parents=True, exist_ok=True)
    raw_log_file = raw_log_dir / RAW_LOG_FILE

    if not raw_log_file.exists():
        return iter(())
    with raw_log_file.open("r", encoding="utf-8") as fh:
        for line in fh:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if day is None or ev["timestamp"].startswith(str(day)):
                yield ev


def get_events_by_id(start: int, end: Optional[int] = None, user_id: Optional[str] = None) -> list[dict]:
    """Return a list of events whose ``event_id`` matches criteria.

    • If *end* is None, return the single matching row.
    • Otherwise return all rows with ``start <= event_id <= end``.
    """
    result: list[dict] = []
    for ev in iter_events():
        ev_id = ev.get("event_id")
        if ev_id is None:
            continue
        if end is None:
            if ev_id == start:
                return [ev]
        else:
            if start <= ev_id <= end:
                result.append(ev)
    return result

# ---------------------------------------------------------------------------
# Summary helpers ------------------------------------------------------------
# ---------------------------------------------------------------------------

def _save_json( directory: Path, payload: dict, label: str = "") -> Path:
    ts = datetime.timestamp(datetime.now())
    fp = directory / f"{label}-{ts}.json"
    with fp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return fp

def _save_yaml(directory: Path, payload: dict) -> Path:
    ts = datetime.timestamp(datetime.now())
    fp = directory / f"{ts}.yaml"
    with fp.open("w", encoding="utf-8") as fh:
        yaml.dump(payload, fh, allow_unicode=True)
    return fp

def _save_text(directory: Path, text: str, suffix: str) -> Path:
    timestamp = datetime.timestamp(datetime.now())
    file_path = directory / f"{timestamp}{suffix}"
    with file_path.open("w", encoding="utf-8") as fh:
        if text is None:
            text = "empty, probably testing without llms"
        fh.write(text)
    return file_path

# --- public wrappers --------------------------------------------------------

def save_topic_summary(label: str, summary: dict, user_id: str) -> Path:
    """Persist a topic summary (JSON). Returns path written."""
    topic_log_dir = BASE_DIR / user_id / TOPIC_DIR
    Path(topic_log_dir).mkdir(parents=True, exist_ok=True)

    return _save_json(topic_log_dir, summary, label=label)


def save_full_summary(markdown: str, user_id: str) -> Path:
    """Persist a full summary (Markdown). Returns path written."""
    
    full_dir = BASE_DIR / user_id / FULL_DIR
    Path(full_dir).mkdir(parents=True, exist_ok=True)
    return _save_text(full_dir, markdown, ".md")

def save_rubric_evaluation(markdown: str, user_id) -> Path:
    """Persist a full summary (Markdown). Returns path written."""
    
    rubric_dir = BASE_DIR / user_id / RUBRIC_DIR
    Path(rubric_dir).mkdir(parents=True, exist_ok=True)
    return _save_text(rubric_dir, markdown, ".md")

# --- retrieval --------------------------------------------------------------


def _latest_file(dir_path: Path, pattern: str) -> Optional[Path]:
    files = list(dir_path.glob(pattern))
    return max(files, default=None, key=lambda p: p.stat().st_mtime)


def latest_topic_summary(user_id) -> Optional[dict]:
    topic_log_dir = BASE_DIR / user_id / TOPIC_DIR
    Path(topic_log_dir).mkdir(parents=True, exist_ok=True)
    fp = _latest_file(topic_log_dir, "*.json")
    if not fp:
        return None
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

def get_topic_file_by_name(topic: str, user_id: str, directory: Path = TOPIC_DIR) -> Optional[Path]:
    """Return a file by its name in the specified directory."""
    summary_dir = BASE_DIR / user_id / directory
    Path(summary_dir).mkdir(parents=True, exist_ok=True)
    fp = summary_dir / topic
    if fp.exists():
        return fp.read_text(encoding="utf-8")
    return None

def latest_full_summary(user_id: str) -> Optional[str]:
    full_dir = BASE_DIR / user_id / FULL_DIR
    Path(full_dir).mkdir(parents=True, exist_ok=True)
    fp = _latest_file(full_dir, "*.md")
    if not fp:
        return None
    return fp.read_text(encoding="utf-8")

def latest_raw_chunk(user_id: str) -> Optional[str]:
    """Return the latest chunk of raw events as a string."""
    raw_dir = BASE_DIR / user_id / RAW_DIR
    Path(raw_dir).mkdir(parents=True, exist_ok=True)
    fp = _latest_file(raw_dir, "tracking_log.ndjson")
    if not fp:
        return None
    try:
        return fp.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    
def get_raw_log_path(user_id: str) -> Path:
    """Return the path to the raw log file."""
    raw_log_dir = BASE_DIR / user_id / RAW_DIR
    return Path(RAW_LOG_FILE).with_suffix(".ndjson")


def get_full_summary(filename: str, user_id: str) -> Path:
    """Return the path to the latest full summary file."""
    full_dir = BASE_DIR / user_id / FULL_DIR
    Path(full_dir).mkdir(parents=True, exist_ok=True)
    file = get_topic_file_by_name(filename, FULL_DIR)
    if file:
        return file
    raise FileNotFoundError("No full summary file found.")

def get_all_summary_type(summary_type: str, user_id: str) -> list[Path]:
    """Return all files of a specific summary type."""
    summary_dir = BASE_DIR / user_id / TOPIC_DIR
    Path(summary_dir).mkdir(parents=True, exist_ok=True)
    return list(summary_dir.glob(f"{summary_type}*"))

def get_all_full_summaries(user_id: str) -> list[Path]:
    """Return all full summary files."""
    full_dir = BASE_DIR / user_id / FULL_DIR
    Path(full_dir).mkdir(parents=True, exist_ok=True)
    return list(full_dir.glob("*.md"))

def get_all_evaluations(user_id: str) -> list[Path]:
    """Return all files of a specific summary type."""
    summary_dir = BASE_DIR / user_id / RUBRIC_DIR
    Path(summary_dir).mkdir(parents=True, exist_ok=True)
    return list(summary_dir.glob(f"*"))

def add_to_evaluation_sheet(content, user_id):
    user_dir = BASE_DIR / user_id 
    topic_file = f"{user_dir}/evaluation.json"
    
    topic_path = Path(topic_file)
    print(content)
    topic_path.write_text(content, encoding="utf-8")

def get_evaluation_summary_sheet(user_id:str):
    user_dir = BASE_DIR / user_id 
    topic_file = f"{user_dir}/evaluation.json"
    
    topic_path = Path(topic_file)
    if not topic_path.exists():
        topic_path.parent.mkdir(parents=True, exist_ok=True)
        topic_path.write_text("[]", encoding="utf-8")
    with topic_path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
# ---------------------------------------------------------------------------
# Convenience ----------------------------------------------------------------
# ---------------------------------------------------------------------------


def today_event_count(user_id: str) -> int:
    """Quick length for need‑new‑summary heuristics."""
    return sum(1 for _ in iter_events(date.today(), user_id=user_id))


__all__ = [
    "append_event",
    "iter_events",
    "get_events_by_id",
    "save_topic_summary",
    "save_full_summary",
    "latest_topic_summary",
    "latest_full_summary",
    "today_event_count",
]
