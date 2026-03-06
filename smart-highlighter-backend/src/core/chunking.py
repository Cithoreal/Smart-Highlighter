"""Text chunking utilities for processing large event logs.

This module provides sliding window chunking with token counting,
designed for feeding event data to LLMs while maintaining context
through overlapping windows.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tiktoken

from src.core.storage import append_event_to_metadata, get_metadata
from src.utils.logging import get_logger
from src.utils.paths import get_raw_log_path

logger = get_logger(__name__)


def tail_ndjson_sliding(
    path: Path,
    *,
    chunk_tokens: int = 4096,
    overlap_tokens: int = 512,
    num_chunks: int = 3,
    model: str = "gpt-4o",
    block_size: int = 64 * 1024,
    last_processed_event_id: Optional[Any] = None,
    cross_run_overlap_tokens: int = 256,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Walk the NDJSON file backwards, return chronological sliding windows.

    Creates `num_chunks` windows, each with <= `chunk_tokens` tokens,
    with `overlap_tokens` overlap between consecutive windows.

    Args:
        path: Path to NDJSON log file
        chunk_tokens: Maximum tokens per chunk
        overlap_tokens: Tokens to overlap between consecutive chunks
        num_chunks: Number of chunks to generate
        model: Model name for tiktoken encoding
        block_size: Size of blocks to read when tailing file
        last_processed_event_id: Skip events after this ID (for incremental processing)
        cross_run_overlap_tokens: Forward context to keep from previous run

    Returns:
        Tuple of (chunks, metadata) where:
            chunks: List of text chunks in chronological order
            metadata: List of dicts with event_id ranges and token counts
    """
    enc = tiktoken.encoding_for_model(model)

    # Calculate minimum tokens needed
    fresh_needed = chunk_tokens + (num_chunks - 1) * (chunk_tokens - overlap_tokens)

    lines: List[str] = []
    toks_per_line: List[int] = []
    event_ids: List[Optional[int]] = []
    tok_before_sentinel = 0
    sentinel_seen = last_processed_event_id is None

    try:
        with path.open("rb") as f:
            f.seek(0, 2)  # Go to end
            pos = f.tell()
            buf = b""

            while pos > 0:
                read = min(block_size, pos)
                pos -= read
                f.seek(pos)
                buf = f.read(read) + buf
                *rest, buf = buf.split(b"\n")

                for raw in reversed(rest):
                    line = raw.decode("utf-8", "ignore")

                    # Extract event_id
                    try:
                        eid = json.loads(line).get("event_id")
                    except Exception:
                        eid = None

                    # Count tokens
                    n_tok = len(enc.encode(line))

                    lines.append(line)
                    toks_per_line.append(n_tok)
                    event_ids.append(eid)

                    if sentinel_seen:
                        tok_before_sentinel += n_tok

                    if not sentinel_seen and eid == last_processed_event_id:
                        sentinel_seen = True

                    # Stop when we have enough tokens
                    if (
                        sentinel_seen
                        and tok_before_sentinel
                        >= fresh_needed + cross_run_overlap_tokens
                    ):
                        break
                else:
                    continue  # Inner loop didn't break, read next block
                break  # Inner loop broke, exit

    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return [], []

    if not lines or not sentinel_seen:
        logger.info("No new events to process")
        return [], []

    # Reverse to chronological order
    lines.reverse()
    toks_per_line.reverse()
    event_ids.reverse()

    # Trim events after the sentinel, keep forward overlap
    if last_processed_event_id in event_ids:
        s_idx = event_ids.index(last_processed_event_id)
        keep_end = s_idx + 1
        tok_fwd = 0
        i = s_idx + 1

        while i < len(lines) and tok_fwd < cross_run_overlap_tokens:
            tok_fwd += toks_per_line[i]
            keep_end = i + 1
            i += 1

        lines = lines[:keep_end]
        toks_per_line = toks_per_line[:keep_end]
        event_ids = event_ids[:keep_end]

    # Build sliding windows
    chunks: List[str] = []
    ranges: List[Dict[str, Any]] = []
    end_idx = len(lines)

    while len(chunks) < num_chunks and end_idx > 0:
        start_idx = end_idx
        tok_sum = 0

        # Walk backwards to fill chunk
        while start_idx > 0:
            nxt = toks_per_line[start_idx - 1]
            if tok_sum and tok_sum + nxt > chunk_tokens:
                break
            start_idx -= 1
            tok_sum += nxt

        # Safeguard: handle single huge line
        if start_idx == end_idx:
            start_idx -= 1
            tok_sum += toks_per_line[start_idx]

        chunk_text = "\n".join(lines[start_idx:end_idx]).strip()

        if not chunk_text:
            break

        chunks.append(chunk_text)

        # Record metadata
        ev_slice = [e for e in event_ids[start_idx:end_idx] if e is not None]
        if ev_slice:
            ranges.append(
                {
                    "created_at": datetime.now().astimezone().isoformat(),
                    "start_event_id": ev_slice[0],
                    "end_event_id": ev_slice[-1],
                    "num_lines": end_idx - start_idx,
                    "tokens": tok_sum,
                }
            )

        # Slide window back by (chunk_tokens - overlap_tokens)
        step = chunk_tokens - overlap_tokens
        moved = 0
        while end_idx > 0 and moved < step:
            end_idx -= 1
            moved += toks_per_line[end_idx]

    # Return in chronological order
    return list(reversed(chunks)), list(reversed(ranges))


def chunk_and_record(
    user_id: str, start_event: Optional[int] = None, **kwargs
) -> List[str]:
    """
    Chunk a user's event log and record metadata.

    Args:
        user_id: User identifier
        start_event: Starting event_id (for incremental processing)
        **kwargs: Additional arguments passed to tail_ndjson_sliding

    Returns:
        List of text chunks
    """
    ndjson_path = get_raw_log_path(user_id)

    if not ndjson_path.exists():
        logger.warning(f"No log file found for user {user_id}")
        return []

    # Get metadata
    meta = get_metadata(user_id)

    # Perform chunking
    chunks, chunk_meta = tail_ndjson_sliding(
        ndjson_path,
        last_processed_event_id=start_event,
        **kwargs,
    )

    # Update metadata
    meta.update(
        {
            "model": kwargs.get("model", "gpt-4o"),
            "chunk_tokens": kwargs.get("chunk_tokens", 4096),
            "overlap_tokens": kwargs.get("overlap_tokens", 512),
        }
    )

    if chunk_meta:
        meta.setdefault("chunks", []).extend(chunk_meta)
        meta["last_processed_event_id"] = chunk_meta[0]["start_event_id"]

    append_event_to_metadata(user_id, meta)

    logger.info(f"Generated {len(chunks)} chunks for user {user_id}")
    return chunks


def get_whole_log(user_id: str) -> str:
    """
    Get entire log file as a single string.

    Warning: This can be very large. Use chunking for production.

    Args:
        user_id: User identifier

    Returns:
        Log file contents
    """
    ndjson_path = get_raw_log_path(user_id)

    if not ndjson_path.exists():
        logger.warning(f"No log file found for user {user_id}")
        return ""

    return ndjson_path.read_text(encoding="utf-8")


__all__ = [
    "tail_ndjson_sliding",
    "chunk_and_record",
    "get_whole_log",
]
