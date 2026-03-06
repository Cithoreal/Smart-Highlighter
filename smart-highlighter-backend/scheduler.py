from __future__ import annotations

"""AsyncIO APScheduler bootstrapper.

This file isolates all background scheduling so it can be imported by
*main.py* without side‑effects during unit‑tests.  It exposes two public
helpers:

    • ``init_scheduler()``     – start scheduler + jobs (idempotent)
    • ``shutdown_scheduler()`` – stop scheduler gracefully

Jobs
----
1. **Topic summary**   – Hourly, at minute 00 (UTC).
2. **Full summary**    – Daily, 23:55 UTC.

Each job calls a wrapper function that logs runtime and errors so the
main application remains stable even if a single run fails.
"""

"""Compatibility shim for scheduler.

This file preserves the old import path (top-level `scheduler`) and
forwards to the refactored implementation in `src.scheduler.scheduler`.
"""

from src.scheduler.scheduler import init_scheduler, shutdown_scheduler  # noqa: F401

__all__ = ["init_scheduler", "shutdown_scheduler"]
