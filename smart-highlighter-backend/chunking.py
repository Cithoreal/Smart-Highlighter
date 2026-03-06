from datetime import datetime
import json
import logging
import os, tiktoken, io
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from storage import get_raw_log_path, get_metadata, append_event_to_metadata

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()  # This sends logs to the console
    ]
)

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
import json, tiktoken

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
import json, tiktoken

def tail_ndjson_sliding(
    path: str,
    *,
    chunk_tokens: int = 4096,
    overlap_tokens: int = 512,            # within-run overlap
    num_chunks: int = 3,
    model: str = "gpt-4o",
    block_size: int = 64 * 1024,
    # cross-run control
    last_processed_event_id: Optional[Any] = None,
    cross_run_overlap_tokens: int = 256,  # duplicated context from prev run
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Walk the .ndjson file backwards, return `num_chunks` chronological
    windows (<= `chunk_tokens` tokens each, with `overlap_tokens` overlap).

    * Lines that come **AFTER** `last_processed_event_id`
      (i.e. newer events already processed last run) are dropped,
      except for up to `cross_run_overlap_tokens` tokens kept as
      forward context.
    * If `last_processed_event_id` is `None`, we start from EOF as usual.
    * If there aren't enough new tokens to build a full set of windows
      the function returns ([], []) so the caller can skip the run.
    """
    enc = tiktoken.encoding_for_model(model)

    fresh_needed = chunk_tokens + (num_chunks - 1) * (chunk_tokens - overlap_tokens)

    lines, toks_per_line, event_ids = [], [], []
    tok_before_sentinel = 0
    sentinel_seen = last_processed_event_id is None  # first run shortcut

    with open(path, "rb") as f:
        f.seek(0, 2)
        pos, buf = f.tell(), b""

        while pos > 0:
            read = min(block_size, pos)
            pos -= read
            f.seek(pos)
            buf = f.read(read) + buf
            *rest, buf = buf.split(b"\n")

            for raw in reversed(rest):          # newest → older
                line = raw.decode("utf-8", "ignore")
                try:
                    eid = json.loads(line).get("event_id")
                except Exception:
                    eid = None

                n_tok = len(enc.encode(line))

                lines.append(line)
                toks_per_line.append(n_tok)
                event_ids.append(eid)

                if sentinel_seen:
                    tok_before_sentinel += n_tok

                if not sentinel_seen and eid == last_processed_event_id:
                    sentinel_seen = True

                # Stop when we have enough *older* tokens
                if (sentinel_seen and
                        tok_before_sentinel >= fresh_needed + cross_run_overlap_tokens):
                    break
            else:
                continue     # inner loop didn't break → read next block
            break            # inner loop broke → exit outer loop

    if not lines or not sentinel_seen:          # nothing new to do
        return [], []

    # chronological order
    lines.reverse()
    toks_per_line.reverse()
    event_ids.reverse()

    # Trim everything AFTER the sentinel, keep fwd-overlap
    if last_processed_event_id in event_ids:
        s_idx = event_ids.index(last_processed_event_id)
        keep_end = s_idx + 1
        tok_fwd = 0
        i = s_idx + 1
        while i < len(lines) and tok_fwd < cross_run_overlap_tokens:
            tok_fwd += toks_per_line[i]
            keep_end = i + 1
            i += 1

        lines         = lines[:keep_end]
        toks_per_line = toks_per_line[:keep_end]
        event_ids     = event_ids[:keep_end]

    # ---------- build sliding windows ----------
    chunks, ranges = [], []
    end_idx = len(lines)

    while len(chunks) < num_chunks and end_idx > 0:
        start_idx, tok_sum = end_idx, 0
        while start_idx > 0:
            nxt = toks_per_line[start_idx - 1]
            if tok_sum and tok_sum + nxt > chunk_tokens:
                break
            start_idx -= 1
            tok_sum += nxt

        if start_idx == end_idx:         # safeguard: single huge line
            start_idx -= 1
            tok_sum += toks_per_line[start_idx]

        chunk_text = "\n".join(lines[start_idx:end_idx]).strip()
        if not chunk_text:               # paranoia guard
            break

        chunks.append(chunk_text)

        ev_slice = [e for e in event_ids[start_idx:end_idx] if e is not None]
        if ev_slice:
            ranges.append({
                "created_at": datetime.now().astimezone().isoformat(),
                "start_event_id": ev_slice[0],
                "end_event_id":   ev_slice[-1],
                "num_lines": end_idx - start_idx,
                "tokens": tok_sum,
            })

        step, moved = chunk_tokens - overlap_tokens, 0
        while end_idx > 0 and moved < step:
            end_idx -= 1
            moved += toks_per_line[end_idx]

    return list(reversed(chunks)), list(reversed(ranges))



def chunk_and_record(user_id: Optional[str] = None, start_event: int = None, **kwargs) -> List[str]:
    ndjson_path   = Path(__file__).parent / "data" / user_id / "raw/web_tracking_log.ndjson"
    metadata_path = Path(__file__).parent / "data" / user_id / "web_tracking_metadata.json"

    meta = get_metadata(user_id=user_id)
    #print(meta)
    #last_eid = meta.get("last_processed_event_id")          # ← NEW
    #print(f"Last processed event_id: {last_eid}")

    chunks, chunk_meta = tail_ndjson_sliding(
        ndjson_path,
        last_processed_event_id = start_event,                 # ← pass it through
        **kwargs,
    )

    # --- existing bookkeeping, unchanged except we update last_eid ---
    meta.update({
        "model": kwargs.get("model", "gpt-4o"),
        "chunk_tokens": kwargs.get("chunk_tokens", 4096),
        "overlap_tokens": kwargs.get("overlap_tokens", 512),
    })
    if chunk_meta:
        meta.setdefault("chunks", []).extend(chunk_meta)
        meta["last_processed_event_id"] = chunk_meta[0]["start_event_id"]  # ← NEW
    append_event_to_metadata(meta, user_id=user_id)
    return chunks

def get_whole_log(user_id: Optional[str] = None) -> str:
    ndjson_path   = Path(__file__).parent / "data" / user_id / "raw/web_tracking_log.ndjson"
    with open(ndjson_path, "r", encoding="utf-8") as f:
        return f.read()
#chunk = tail_ndjson("tracking_log.ndjson", token_budget=12_000)
#print(f"Chunk size: {len(chunk.encode())/1024:.1f} KB")
"""for chunk in tail_ndjson_sliding(chunk_tokens=10000, overlap_tokens=500, num_chunks=3, model="gpt-4o"):
    print(f"Chunk size: {len(chunk.encode())/1024:.1f} KB")
    print(chunk)
    print("-" * 40)"""
    #500 tokens is roughly 3 overlap events

#print(tail_ndjson_sliding("web_tracking_log.ndjson", chunk_tokens=100, overlap_tokens=10, num_chunks=3, model="gpt-4o"))



# t=chunk_and_record(
#     #start_event=1693,
#     chunk_tokens=7000,
#     overlap_tokens=250,
#     num_chunks=20,
#     user_id="Chris"
# )
# for i in t:
#     print(f"Chunk size: {len(i.encode())/1024:.1f} KB")
#     print(i)
#     print("-" * 40)
