from __future__ import annotations

"""FastAPI entry point (migrated from top-level).

This module wires configuration and logging, initialises the scheduler
at startup and exposes the same HTTP endpoints as the original
``fastapi_server.py`` but updated to use the `src.` package layout and
the refactored storage APIs.
"""

import os
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from jinja2 import Environment, FileSystemLoader
from markdown import markdown as md

from src.config import get_settings
from src.core.pipeline import create_summary_md, run_pipeline  # type: ignore
from src.core.storage import (append_event, get_events_by_id, iter_events,
                              latest_full_summary, latest_topic_summary)
from src.scheduler.scheduler import init_scheduler, shutdown_scheduler
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: configure logging and start scheduler
    settings = get_settings()
    setup_logging(Path(settings.log_dir) if settings.log_dir else Path("logs"))
    init_scheduler()
    logger.info("Scheduler started")
    yield
    # Shutdown: stop scheduler
    shutdown_scheduler()


app = FastAPI(title="AI-API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MARKDOWN_CSS = (
    "https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css"
)

env = Environment(loader=FileSystemLoader("templates"))


# ---------------------------------------------------------------------------
# Routes – ingestion
# ---------------------------------------------------------------------------


@app.post("/api/log")
async def receive_tracking_event(
    event: dict, user_id: Optional[str] = Header(default=None, alias="X-User-ID")
):
    # Prefer explicit header; fall back to payload user_id
    uid = user_id or event.get("user_id") or "default_user"
    logger.debug("Received event for user %s", uid)
    # storage.append_event expects (user_id, event)
    await append_event(uid, event)
    return {"status": "success"}


# ---------------------------------------------------------------------------
# Routes – raw event query
# ---------------------------------------------------------------------------


@app.get("/api/events")
async def fetch_events(
    start: Optional[int] = Query(None, description="start event_id"),
    end: Optional[int] = Query(None, description="end event_id (inclusive)"),
    day: Optional[date] = Query(None, description="UTC date YYYY-MM-DD"),
    user_id: str | None = Header(default=None, alias="X-User-ID"),
):
    if start is not None:
        data = get_events_by_id(user_id or "default_user", start, end)
        if not data:
            raise HTTPException(404, "No events for given ID range")
        return data
    # else by date
    events = list(iter_events(user_id or "default_user", day=day))
    if not events:
        raise HTTPException(404, "No events for given day")
    return events


# ---------------------------------------------------------------------------
# Routes – topic summaries
# ---------------------------------------------------------------------------


@app.get("/api/topic_summary/latest")
async def latest_topic(user_id: str | None = Header(default=None, alias="X-User-ID")):
    summary = latest_topic_summary(user_id or "default_user")
    if summary is None:
        raise HTTPException(404, "No topic summary yet")
    return summary


@app.post("/api/topic_summary")
async def force_topic(user_id: str | None = Header(default=None, alias="X-User-ID")):
    # Trigger pipeline run which will create topic summaries
    run_pipeline(user_id or "default_user")
    return {"status": "started"}


# ---------------------------------------------------------------------------
# Routes – full summaries
# ---------------------------------------------------------------------------


@app.post("/api/run_pipeline")
async def run_pipeline_endpoint(
    background_tasks: BackgroundTasks,
    user_id: str | None = Header(default=None, alias="X-User-ID"),
):
    try:
        background_tasks.add_task(run_pipeline, user_id or "default_user")
        return JSONResponse(
            content={"status": "Running web tracking analysis"}, status_code=202
        )
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/full_summary/latest", response_class=HTMLResponse)
async def latest_full(user_id: str | None = Header(default=None, alias="X-User-ID")):
    md_text = latest_full_summary(user_id or "default_user")
    if md_text is None:
        raise HTTPException(404, "No full summary yet")
    html_body = md(md_text, extensions=["fenced_code", "tables"])
    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><link rel='stylesheet' href='{MARKDOWN_CSS}'></head>
<body class='markdown-body'>{html_body}</body></html>"""


@app.post("/api/full_summary", response_class=HTMLResponse)
async def force_full(
    user_id: Optional[str] = Query(None, description="User ID for tracking")
):
    # Synchronously generate full summary (may be slow)
    md_text = create_summary_md(
        "", [], user_id or "default_user", raw_data=None, force=True
    )  # placeholder usage
    html_body = md(md_text, extensions=["fenced_code", "tables"])
    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><link rel='stylesheet' href='{MARKDOWN_CSS}'></head>
<body class='markdown-body'>{html_body}</body></html>"""


# ---------------------------------------------------------------------------
# Home page
# ---------------------------------------------------------------------------


template_index = env.get_template("index.html")


@app.get("/", response_class=HTMLResponse)
async def homepage(user_id: str | None = Header(default=None, alias="X-User-ID")):
    if user_id is None:
        raise HTTPException(status_code=400, detail="Missing X-User-ID header")
    logger.info("Rendering homepage for user_id: %s", user_id)

    topic_files = sorted(
        Path(f"data/{user_id}/summaries/topics").glob("*.json"), key=lambda p: p.name
    )
    full_files = sorted(
        Path(f"data/{user_id}/summaries/full").glob("*.md"), key=lambda p: p.name
    )
    return template_index.render(topic_files=topic_files, full_files=full_files)


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
    use_https = os.getenv("HTTPS", "").lower() in ("1", "true", "yes")
    reload = os.getenv("RELOAD", "1") == "1"
    host = "127.0.0.1"
    port = 8443 if use_https else 8000

    if use_https:
        # try to use top-level cert helper if available
        try:
            from certs import ensure_dev_cert

            _, cert, key = ensure_dev_cert()
        except Exception:
            cert = key = None

    # run via import string so reload works
    if reload:
        uvicorn.run(
            "src.main:app",
            host=host,
            port=port,
            reload=True,
            ssl_certfile=str(cert) if use_https and cert is not None else None,
            ssl_keyfile=str(key) if use_https and key is not None else None,
        )
    else:
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            ssl_certfile=str(cert) if use_https and cert is not None else None,
            ssl_keyfile=str(key) if use_https and key is not None else None,
        )
