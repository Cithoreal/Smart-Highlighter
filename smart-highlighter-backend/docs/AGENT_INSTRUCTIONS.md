# Agent Instructions for Smart Highlighter Backend

## Project Overview
This is a **web tracking and AI-powered summarization backend** built with FastAPI. It collects browsing events from a browser extension, processes them using multiple LLM providers (OpenAI, Anthropic, Google AI), and generates structured summaries with automated quality evaluation.

## Core Purpose
- Ingest browsing events from Firefox extension via REST API
- Process events through configurable LLM pipelines
- Generate topic summaries and full markdown reports
- Evaluate output quality using LLM-as-judge framework
- Support ablation studies comparing models, prompts, and data formats

---

## Project Architecture

### Key Components

#### 1. **FastAPI Server** (`fastapi_server.py`)
- Main entry point with REST API endpoints
- Handles CORS, authentication headers, background tasks
- Scheduled summarization via APScheduler
- Routes: `/api/log`, `/api/events`, `/api/topic_summary`, `/api/full_summary`, `/api/run_pipeline`

#### 2. **Storage Layer** (`storage.py`)
- NDJSON-based event logging (append-only)
- Per-user data isolation: `data/{user_id}/`
- File structure:
  - `raw/web_tracking_log.ndjson` - Raw events
  - `summaries/topics/*.json` - Topic summaries
  - `summaries/full/*.md` - Full reports
  - `rubric_evaluations/*.md` - Quality evaluations
  - `web_tracking_metadata.ndjson` - Processing metadata

#### 3. **Pipeline** (`web_tracking_pipeline.py`)
- Orchestrates data processing workflow
- Runs multiple models in parallel for comparison
- Configurable prompts and data formats
- Calls summarizer → judge → storage

#### 4. **LLM Integration** (`llm_apis/`)
- Abstraction layer for multiple providers
- `llm_request.py` - Unified interface via `AI_API` enum
- Provider-specific modules: `openai_api.py`, `anthropic_api.py`, `google_api.py`

#### 5. **Evaluation System** (`llm_judge/`)
- Multi-dimensional rubric (Clarity, Detail, Comprehensiveness, Conciseness, Accuracy, Usefulness)
- Score: 1-4 scale per category
- Example-driven evaluation with structured markdown output

#### 6. **Chunking** (`chunking.py`)
- Token-aware sliding window processing
- Handles large event logs efficiently
- Cross-run state management (tracks `last_processed_event_id`)
- Backward file reading for memory efficiency

---

## Critical Design Patterns

### 1. **User Isolation**
- All operations require `user_id` (passed via `X-User-ID` header)
- File paths: `data/{user_id}/{category}/`
- **⚠️ NO AUTHENTICATION CURRENTLY** - user_id is trusted

### 2. **Async Architecture**
- FastAPI async/await throughout
- Background tasks for expensive LLM calls
- APScheduler for automated summarization
- `asyncio.Lock` for file write safety

### 3. **Event ID System**
- Monotonic counter per user: `event_id` field
- Restart-safe (reads last ID from file)
- Used for event range citations in summaries

### 4. **Extensibility Points**
- **Prompts**: `web_tracking_prompts.py` - modify prompt templates
- **Models**: Add to `AI_API` enum and implement `_call_llm()` wrapper
- **Rubrics**: `llm_judge/` - extend evaluation criteria
- **Data formats**: Currently NDJSON, designed for JSON/YAML variants

---

## Common Development Tasks

### Adding a New LLM Provider
1. Create `llm_apis/{provider}_api.py`
2. Implement `_call_llm(system_prompt, user_message) -> str`
3. Add enum to `AI_API` in `llm_request.py`
4. Update `make_llm_request()` switch statement

### Modifying Summary Structure
1. Edit prompt templates in `web_tracking_prompts.py`
2. Update `build_full_summary_prompt()` options
3. Test with `run_pipeline(user_id="Test")`
4. Check output in `data/Test/summaries/full/`

### Adding New Endpoints
1. Define route in `fastapi_server.py`
2. Add Pydantic models for request/response
3. Use `user_id: str | None = Header(default=None, alias="X-User-ID")`
4. Call appropriate storage/pipeline functions
5. Handle errors with `HTTPException`

### Running Experiments
1. Configure models/prompts in `web_tracking_pipeline.py`:
   ```python
   models = [AI_API.OPENAI_4o, AI_API.GOOGLE]
   json_summary_prompts = [{"topics": topic_summary_prompt_json}]
   ```
2. Uncomment `run_pipeline("user_id")` at bottom of file for manual runs
3. Results saved to `data/{user_id}/rubric_evaluations/`
4. Use `compile_scores(user_id)` to aggregate evaluations

---

## Code Style Guidelines

### General Principles
- Use type hints for all function signatures
- Prefer `Path` objects over string paths
- Log important operations with `logging.info/debug`
- Use f-strings for formatting
- Follow FastAPI best practices (dependency injection, Pydantic models)

### File Operations
```python
# ✅ Good
file_path = BASE_DIR / user_id / "summaries/full"
file_path.mkdir(parents=True, exist_ok=True)

# ❌ Avoid
file_path = f"data/{user_id}/summaries/full"
os.makedirs(file_path)
```

### Error Handling
```python
# ✅ Good - Specific exceptions with context
try:
    result = make_llm_request(prompt, data, model)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON from {model.value}: {e}")
    raise HTTPException(500, "LLM returned invalid format")

# ❌ Avoid - Bare except or exposing internals
except Exception as e:
    return str(e)  # Don't expose internal errors to clients
```

### Async Patterns
```python
# ✅ Good - Use async for I/O
async def append_event(event: dict, user_id: str) -> None:
    async with log_lock:
        # Safe concurrent writes

# ⚠️ Note - Current code uses sync file I/O (blocks event loop)
# Future improvement: Use aiofiles
```

---

## Environment Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_AI_API_KEY=...
HUGGINGFACE_API_KEY=...

# Optional
HTTPS=1                    # Enable HTTPS with self-signed cert
RELOAD=1                   # Hot reload in development
ALLOWED_ORIGINS=http://localhost:3000,https://example.com
```

### Running the Server
```bash
# Development (hot reload)
uvicorn fastapi_server:app --host 127.0.0.1 --port 8000 --reload

# Production (Docker)
docker-compose up -d --build
```

---

## Testing Strategy

### Manual Testing
```python
# In web_tracking_pipeline.py (bottom of file)
if __name__ == "__main__":
    run_pipeline("Test")  # Uncomment to test full pipeline
```

### API Testing
```bash
# Log an event
curl -X POST http://localhost:8000/api/log \
  -H "Content-Type: application/json" \
  -H "X-User-ID: TestUser" \
  -d '{"url": "https://example.com", "action": "pageview"}'

# Trigger pipeline
curl -X POST http://localhost:8000/api/run_pipeline \
  -H "X-User-ID: TestUser"
```

### Output Validation
1. Check `data/{user_id}/summaries/full/` for markdown reports
2. Verify `rubric_evaluations/` contains structured scores
3. Confirm `web_tracking_metadata.ndjson` tracks processing state

---

## Known Issues & Workarounds

### 1. **No Authentication**
- **Issue**: `X-User-ID` header is trusted without verification
- **Impact**: Security vulnerability, data isolation not enforced
- **Workaround**: Deploy behind auth proxy or implement JWT middleware
- **TODO**: See `TASKS.md` - High Priority Security item

### 2. **Sync File I/O**
- **Issue**: File operations block async event loop
- **Impact**: Reduced concurrency, slower request handling
- **Workaround**: Use background tasks for large writes
- **TODO**: Migrate to `aiofiles` for async file operations

### 3. **No Rate Limiting**
- **Issue**: Unlimited LLM API calls can exhaust quotas/budget
- **Impact**: Cost overruns, API throttling
- **Workaround**: Manually monitor `data/` directory growth
- **TODO**: Implement `slowapi` rate limiting per user

### 4. **Commented Production Code**
- **Issue**: Test calls left in source files
- **Impact**: Confusing, accidental execution risk
- **Workaround**: Keep commented, search before running
- **Example**: `web_tracking_pipeline.py` bottom section

### 5. **CORS Wildcard**
- **Issue**: `allow_origins=["*"]` too permissive
- **Impact**: Security risk for credential-based requests
- **Workaround**: Acceptable for local development only
- **TODO**: Use environment variable for allowed origins

---

## Data Flow Diagram

```
Browser Extension (Firefox)
    ↓ POST /api/log (HTTPS)
FastAPI Server
    ↓ append_event()
NDJSON Raw Log (data/{user_id}/raw/web_tracking_log.ndjson)
    ↓ (scheduled or manual trigger)
Chunking System (chunk_and_record)
    ↓ sliding window batches
Web Tracking Pipeline
    ↓ parallel execution
LLM APIs (OpenAI/Anthropic/Google)
    ↓ JSON responses
Summarizer (create_summary_json, create_summary_md)
    ↓ structured files
Storage (save_topic_summary, save_full_summary)
    ↓
LLM Judge (apply_rubric)
    ↓ markdown evaluation
Rubric Evaluations (data/{user_id}/rubric_evaluations/*.md)
    ↓
Compilation (compile_scores)
    ↓ aggregated JSON
Final Report (data/{user_id}/evaluation.json)
```

---

## Quick Reference

### Important File Paths
- **Main app**: `fastapi_server.py`
- **Pipeline config**: `web_tracking_pipeline.py` (lines 37-42)
- **Prompt templates**: `web_tracking_prompts.py`
- **Storage functions**: `storage.py`
- **LLM abstraction**: `llm_apis/llm_request.py`
- **Evaluation rubric**: `llm_judge/full_summary_rubric_comparison.py`

### Key Functions
- `append_event(event, user_id)` - Log new event
- `run_pipeline(user_id)` - Full processing workflow
- `create_summary_json(prompt, events, model, user_id)` - Generate topic summary
- `create_summary_md(prompt, summaries, raw_data, model, user_id)` - Generate full report
- `apply_rubric(prompt, summary_file, model, user_id)` - Evaluate quality

### Useful Commands
```bash
# View logs
tail -f debug.log

# Check data structure
tree data/

# Count events for user
wc -l data/Chris/raw/web_tracking_log.ndjson

# Find latest summary
ls -t data/Chris/summaries/full/ | head -1
```

---

## When Making Changes

### Before Modifying Code
1. ✅ Read relevant sections in `PROJECT_DOCS.md`
2. ✅ Check `TASKS.md` for related work
3. ✅ Review existing implementations (don't reinvent)
4. ✅ Consider impact on user data isolation
5. ✅ Plan error handling strategy

### After Making Changes
1. ✅ Update docstrings if function signature changed
2. ✅ Test with at least one user_id
3. ✅ Check `debug.log` for errors
4. ✅ Verify output files are created correctly
5. ✅ Update `TASKS.md` if completing a TODO
6. ✅ Document any new configuration in this file

### Debugging Checklist
- [ ] Is `user_id` passed correctly through call chain?
- [ ] Are file paths using `Path` objects consistently?
- [ ] Did you check for existing similar functionality?
- [ ] Are exceptions caught and logged appropriately?
- [ ] Does the change work with background tasks?
- [ ] Are LLM API keys loaded from environment?

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **APScheduler**: https://apscheduler.readthedocs.io/
- **Tiktoken**: https://github.com/openai/tiktoken
- **NDJSON Spec**: http://ndjson.org/

For project-specific details, see:
- `PROJECT_DOCS.md` - Detailed technical documentation
- `TASKS.md` - Current work items and priorities
- `Dev Notes.md` - Original development notes and research goals
