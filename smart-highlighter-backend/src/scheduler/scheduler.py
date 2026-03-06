"""Async scheduler integration for the app.

Wraps APScheduler usage and exposes init/shutdown helpers so the
FastAPI app can import this module without side-effects during tests.

Jobs iterate user data directories and call the pipeline runner for
each user. This keeps behaviour similar to the previous top-level
``scheduler.py`` but adapted to the new `src.` package layout.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import get_settings
from src.core.pipeline import run_pipeline
from src.utils.logging import get_logger
from src.utils.paths import sanitize_user_id

logger = get_logger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


def _safe(func):
    """Decorator wrapping job functions with logging and error handling."""

    async def _wrapper(*args, **kwargs):
        start = datetime.utcnow()
        try:
            logger.info("Job %s started", getattr(func, "__name__", str(func)))
            result = func(*args, **kwargs)
            # allow sync or async inner functions
            if hasattr(result, "__await__"):
                await result
            elapsed = (datetime.utcnow() - start).total_seconds()
            logger.info(
                "Job %s finished in %.2fs",
                getattr(func, "__name__", str(func)),
                elapsed,
            )
        except Exception:  # broad catch to prevent scheduler crash
            logger.exception("Job %s failed", getattr(func, "__name__", str(func)))

    return _wrapper


async def _maybe_await(result):
    if hasattr(result, "__await__"):
        await result
    return result


def _list_users(data_dir: Path = Path("data")) -> list[str]:
    """Return a list of candidate user IDs by scanning the data directory.

    Only directory names that pass `sanitize_user_id` are returned.
    """
    users: list[str] = []
    if not data_dir.exists():
        logger.debug("Data directory %s does not exist", data_dir)
        return users

    for p in data_dir.iterdir():
        if not p.is_dir():
            continue
        try:
            uid = sanitize_user_id(p.name)
        except Exception:
            logger.debug("Skipping invalid user directory: %s", p)
            continue
        users.append(uid)

    return users


def init_scheduler(timezone: str = "UTC") -> AsyncIOScheduler:
    """Create and start the AsyncIOScheduler (idempotent).

    The scheduler registers two jobs:
    - hourly topic run (minute 0)
    - daily full summary (23:55)
    """
    global _scheduler
    if _scheduler and getattr(_scheduler, "running", False):
        logger.debug("Scheduler already running")
        return _scheduler

    settings = get_settings()

    _scheduler = AsyncIOScheduler(timezone=timezone)

    # Hourly topic summary job ------------------------------------------------
    @_safe
    def _hourly_job():
        logger.info("Running hourly pipeline for all users")
        for user in _list_users():
            try:
                run_pipeline(user)
            except Exception:
                logger.exception("Hourly run failed for user %s", user)

    _scheduler.add_job(
        _hourly_job,
        trigger=CronTrigger(minute=0),
        id="topic_summary_hourly",
        max_instances=1,
        misfire_grace_time=180,
        replace_existing=True,
    )

    # Daily full summary job --------------------------------------------------
    @_safe
    def _daily_job():
        logger.info("Running daily pipeline for all users")
        for user in _list_users():
            try:
                run_pipeline(user)
            except Exception:
                logger.exception("Daily run failed for user %s", user)

    # Allow settings to override schedule times in future (placeholder)
    _scheduler.add_job(
        _daily_job,
        trigger=CronTrigger(hour=23, minute=55),
        id="full_summary_daily",
        max_instances=1,
        misfire_grace_time=600,
        replace_existing=True,
    )

    _scheduler.add_listener(_job_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

    _scheduler.start()
    logger.info("Scheduler initialised with %d jobs", len(_scheduler.get_jobs()))
    return _scheduler


def shutdown_scheduler(wait: bool = False) -> None:
    """Shut down the running scheduler if any."""
    global _scheduler
    if _scheduler and getattr(_scheduler, "running", False):
        _scheduler.shutdown(wait=wait)
        logger.info("Scheduler stopped")
        _scheduler = None


def _job_listener(event):
    if getattr(event, "exception", False):
        logger.error(
            "Job %s raised an exception", getattr(event, "job_id", "<unknown>")
        )
    else:
        logger.warning(
            "Job %s missed its run window", getattr(event, "job_id", "<unknown>")
        )


__all__ = ["init_scheduler", "shutdown_scheduler"]
