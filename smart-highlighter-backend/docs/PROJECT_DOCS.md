# Project Documentation Reference

## Table of Contents
1. [System Architecture](#system-architecture)
2. [API Reference](#api-reference)
3. [Data Models](#data-models)
4. [File Structure](#file-structure)
5. [Configuration](#configuration)
6. [Development Workflow](#development-workflow)
7. [Deployment Guide](#deployment-guide)
8. [Troubleshooting](#troubleshooting)

---

## System Architecture

### Technology Stack
- **Web Framework**: FastAPI 0.x (async/await)
- **Scheduling**: APScheduler (AsyncIO scheduler)
- **LLM Providers**: OpenAI, Anthropic, Google AI, HuggingFace
- **Data Format**: NDJSON (newline-delimited JSON)
- **Templating**: Jinja2
- **Markdown**: Python-Markdown with extensions
- **Token Counting**: tiktoken (OpenAI's tokenizer)
- **TLS**: cryptography (self-signed cert generation)
- **Containerization**: Docker & Docker Compose

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Extension                        │
│                    (Firefox Add-on)                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS POST /api/log
                     │ Header: X-User-ID
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Endpoints  │  │  Middleware  │  │  Scheduler   │     │
│  │  (REST API)  │  │   (CORS)     │  │ (APScheduler)│     │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘     │
│         │                                     │             │
│         └─────────────┬───────────────────────┘             │
│                       ↓                                     │
│         ┌─────────────────────────────┐                    │
│         │      Storage Layer          │                    │
│         │  (NDJSON append-only)       │                    │
│         └─────────────┬───────────────┘                    │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  Processing Pipeline                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Chunking   │→ │  Summarizer  │→ │  LLM Judge   │     │
│  │ (Tokenizer)  │  │  (Multi-LLM) │  │  (Rubric)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                        │
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    File Storage                             │
│  data/{user_id}/                                           │
│    ├── raw/web_tracking_log.ndjson                        │
│    ├── summaries/topics/*.json                            │
│    ├── summaries/full/*.md                                │
│    └── rubric_evaluations/*.md                            │
└─────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Authentication
**Current**: Trust-based via header  
**Header**: `X-User-ID: {user_id_string}`  
**⚠️ Warning**: No validation - implement proper auth before production

### Endpoints

#### 1. **POST /api/log**
Ingest a single tracking event.

**Request**:
```json
{
  "url": "https://example.com/page",
  "action": "pageview",
  "selected_text": "...",
  "time_on_page": 45.2,
  "scroll_depth": 0.75,
  "custom_field": "any_value"
}
```

**Response**:
```json
{
  "status": "success"
}
```

**Notes**:
- `event_id` and `timestamp` added automatically
- Accepts arbitrary JSON fields (Pydantic `extra="allow"`)
- Appends to `data/{user_id}/raw/web_tracking_log.ndjson`

---

#### 2. **GET /api/events**
Query events by ID range or date.

**Query Parameters**:
- `start` (int, optional): Start event_id
- `end` (int, optional): End event_id (inclusive)
- `day` (date, optional): UTC date YYYY-MM-DD

**Examples**:
```bash
# Get events 100-150
GET /api/events?start=100&end=150

# Get events for specific day
GET /api/events?day=2025-01-15
```

**Response**:
```json
[
  {
    "event_id": 100,
    "timestamp": "2025-01-15T10:30:00",
    "url": "...",
    ...
  }
]
```

---

#### 3. **GET /api/topic_summary/latest**
Retrieve the most recent topic summary.

**Headers**: `X-User-ID`

**Response**:
```json
{
  "topics": [
    {
      "topic": "FastAPI Development",
      "description": "Learning FastAPI for web backend",
      "event_range": [100, 150]
    }
  ],
  "generated_at": "2025-01-15T10:00:00"
}
```

---

#### 4. **POST /api/topic_summary**
Force generation of a new topic summary.

**Headers**: `X-User-ID`

**Response**: Same as GET latest

---

#### 5. **GET /api/full_summary/latest**
Get the latest full markdown report (rendered as HTML).

**Headers**: `X-User-ID`

**Response**: HTML page with GitHub-style markdown CSS

---

#### 6. **POST /api/full_summary**
Force generation of a new full summary.

**Query Parameters**:
- `user_id` (string, optional): User ID for tracking

**Response**: HTML rendered markdown report

---

#### 7. **POST /api/run_pipeline**
Execute the complete analysis pipeline (async background task).

**Headers**: `X-User-ID`

**Response** (202 Accepted):
```json
{
  "status": "Running web tracking analysis"
}
```

**Process**:
1. Chunks raw events
2. Runs configured LLM models in parallel
3. Generates topic + full summaries
4. Applies rubric evaluation
5. Saves results to file system

---

#### 8. **GET /**
Homepage listing all summaries.

**Headers**: `X-User-ID`

**Response**: HTML page with links to topic and full summaries

---

#### 9. **GET /healthz**
Health check endpoint.

**Response**:
```json
{
  "ok": true
}
```

---

## Data Models

### Event Structure (NDJSON)
```json
{
  "event_id": 1234,
  "timestamp": "2025-01-15T10:30:45.123456",
  "user_id": "Chris",
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "title": "FastAPI Tutorial",
  "action": "scroll",
  "scroll_depth": 0.45,
  "time_on_page": 23.5,
  "selected_text": null,
  "viewport_width": 1920,
  "viewport_height": 1080
}
```

**Key Fields**:
- `event_id`: Monotonic integer, unique per user
- `timestamp`: UTC ISO-8601 format
- User-defined fields: Extension can send any additional data

---

### Topic Summary (JSON)
```json
{
  "topics": [
    {
      "topic": "string",
      "description": "string",
      "event_range": [start_id, end_id]
    }
  ],
  "generated_at": "ISO-8601 timestamp"
}
```

---

### Full Summary (Markdown)
```markdown
# Web Tracking Summary
Generated by: {model_name}

## Topic: FastAPI Development
### Description
User explored FastAPI documentation...

### Selected Text
- "FastAPI is a modern, fast web framework..."

### Behavior Analysis
- Rapid navigation suggests familiarity with web frameworks
- Long dwell time (120s) on async/await section

### Data Insights
- 15 page views across 3 domains (events 100-150)
- Average time on page: 45.2s

### Ad Traces
None detected

### Actionable Steps
- Consider deep-dive tutorial on Pydantic models
- Explore FastAPI security documentation

---
```

---

### Rubric Evaluation (Markdown)
```markdown
{model_name}
Topic: {topic_name}

**Breakdown**
"{bullet_point_from_summary}"
    - Analysis comment on how it contributes to score

**Scores**
| Category | Score | Justification |
|----------|-------|---------------|
| Clarity | 4 | Crystal clear prose with logical flow |
| Detail | 3 | Covers major points, minor details missing |
| Comprehensiveness | 4 | Addresses 100% of requirements |
| Conciseness | 3 | Minor extraneous wording |
| Accuracy | 4 | Flawless alignment with raw data |
| Usefulness | 4 | Directly actionable recommendations |

**Overall Average**: 3.7

**Overall Rationale**
Strong clarity and accuracy with actionable insights. Could be slightly more concise.
```

---

### Metadata (NDJSON)
```json
{
  "model": "gpt-4o",
  "chunk_tokens": 7000,
  "overlap_tokens": 250,
  "last_processed_event_id": 1500,
  "chunks": [
    {
      "created_at": "2025-01-15T10:00:00",
      "start_event_id": 1200,
      "end_event_id": 1500,
      "num_lines": 300,
      "tokens": 6800
    }
  ]
}
```

---

## File Structure

```
smart-highlighter-backend/
├── .env                          # API keys (gitignored)
├── .gitignore
├── requirements.txt              # Python dependencies
├── pyvenv.cfg                    # Virtual environment config
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Multi-container orchestration
├── README.md                     # Setup instructions
├── Dev Notes.md                  # Research notes & goals
├── AGENT_INSTRUCTIONS.md         # **This guide for AI agents**
├── PROJECT_DOCS.md              # **Technical documentation**
├── TASKS.md                      # **TODO list & priorities**
├── LICENSE
│
├── fastapi_server.py             # ⭐ Main application entry point
├── storage.py                    # File I/O operations
├── web_tracking_pipeline.py      # Processing orchestration
├── web_tracking_prompts.py       # LLM prompt templates
├── summarizer.py                 # Summary generation logic
├── chunking.py                   # Token-based text splitting
├── scheduler.py                  # APScheduler configuration
├── certs.py                      # Self-signed TLS cert generator
├── pipeline.py                   # (legacy/unused)
├── file_convert.py               # (legacy/unused)
│
├── llm_apis/                     # LLM provider integrations
│   ├── llm_request.py            # Unified API interface
│   ├── openai_api.py
│   ├── anthropic_api.py
│   ├── google_api.py
│   └── huggingface_api.py
│
├── llm_judge/                    # Evaluation framework
│   ├── llm_judge.py              # Main judge logic
│   ├── full_summary_rubric_comparison.py
│   ├── full_summary_rubric_examples.py
│   ├── topic_summary_rubric.py
│   ├── judge_output_rubric.py
│   └── example_report.md         # Reference evaluation
│
├── templates/
│   └── index.html                # Homepage template
│
├── data/                         # ⚠️ User data (gitignored)
│   ├── {user_id}/
│   │   ├── raw/
│   │   │   └── web_tracking_log.ndjson
│   │   ├── web_tracking_metadata.ndjson
│   │   ├── topics.json           # Compiled topics
│   │   ├── behavior.json         # Compiled behavior insights
│   │   ├── evaluation.json       # Compiled scores
│   │   ├── summaries/
│   │   │   ├── topics/
│   │   │   │   └── {label}-{timestamp}.json
│   │   │   └── full/
│   │   │       └── {timestamp}.md
│   │   └── rubric_evaluations/
│   │       └── {timestamp}.md
│   └── showcase/                 # Demo data for presentations
│
├── .certs/                       # Self-signed certificates (gitignored)
│   ├── localhost.pem
│   └── localhost-key.pem
│
└── debug.log                     # Application logs (gitignored)
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: LLM API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
HUGGINGFACE_API_KEY=hf_...

# Optional: Server Configuration
HTTPS=1                           # Enable HTTPS (default: 0)
RELOAD=1                          # Hot reload in dev (default: 1)
ALLOWED_ORIGINS=http://localhost:3000,https://example.com

# Optional: Processing Configuration
MAX_CHUNK_TOKENS=7000
OVERLAP_TOKENS=250
```

### Pipeline Configuration

Edit `web_tracking_pipeline.py` (lines 37-42):

```python
# Models to test
models = [AI_API.OPENAI_4o, AI_API.ANTHROPIC, AI_API.GOOGLE]

# Intermediate processing steps
json_summary_prompts = [
    {"topics": topic_summary_prompt_json},
    {"selections": selections_prompt_json},
    {"behavior": behavior_insights_prompt_json},
    {"actionable_steps": actionable_steps_prompt_json}
]

# Final report structure
full_summary_prompt_options = {
    "description": True,
    "selected_text": True,
    "behavior_analysis": True,
    "data_insights": True,
    "ad_traces": True,
    "actionable_steps": True
}
```

### Scheduler Configuration

Edit `scheduler.py`:

```python
# Topic summaries: every hour at :00
trigger=CronTrigger(minute=0)

# Full summaries: daily at 23:55 UTC
trigger=CronTrigger(hour=23, minute=55)
```

---

## Development Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone https://github.com/Cithoreal/smart-highlighter-backend.git
cd smart-highlighter-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Running Locally
```bash
# Development mode (hot reload)
python fastapi_server.py

# Or with uvicorn directly
uvicorn fastapi_server:app --host 127.0.0.1 --port 8000 --reload

# Access:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs (auto-generated)
# - Homepage: http://localhost:8000/
```

### 3. Testing Changes
```bash
# Send test event
curl -X POST http://localhost:8000/api/log \
  -H "Content-Type: application/json" \
  -H "X-User-ID: TestUser" \
  -d '{"url": "https://example.com", "action": "test"}'

# Trigger pipeline manually
curl -X POST http://localhost:8000/api/run_pipeline \
  -H "X-User-ID: TestUser"

# Check output
ls -la data/TestUser/summaries/full/
cat data/TestUser/summaries/full/*.md | tail -50
```

### 4. Debugging
```bash
# Monitor logs
tail -f debug.log

# Check APScheduler status (in Python REPL)
python
>>> from scheduler import _scheduler
>>> _scheduler.print_jobs()

# Validate NDJSON integrity
python -c "import ndjson; ndjson.load(open('data/TestUser/raw/web_tracking_log.ndjson'))"
```

---

## Deployment Guide

### Docker Deployment

#### Build and Run
```bash
# Build image
docker-compose build

# Start service
docker-compose up -d

# View logs
docker-compose logs -f fastapi

# Stop service
docker-compose down
```

#### Docker Configuration
`docker-compose.yml`:
```yaml
services:
  fastapi:
    build:
      dockerfile: Dockerfile
    container_name: fastapi
    restart: unless-stopped
    volumes:
      - ./data:/app/data        # Persist user data
    ports:
      - "8443:8443"             # HTTPS port
    environment:
      - HTTPS=1
```

### Production Considerations

#### 1. **Reverse Proxy** (Recommended)
Use Nginx/Caddy for:
- TLS termination with real certificates (Let's Encrypt)
- Rate limiting
- Static file caching
- Load balancing (if scaling horizontally)

Example Nginx config:
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

#### 2. **Database Migration**
Current file-based storage won't scale. Migration path:
1. Keep NDJSON as write-ahead log
2. Add SQLite for queries
3. Use DuckDB for analytics
4. Eventually: PostgreSQL for production

#### 3. **Monitoring**
Add observability:
```python
# Add Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Track:
- Request latency
- LLM API costs
- Queue length
- Error rates

#### 4. **Security Hardening**
See `TASKS.md` - High Priority items

---

## Troubleshooting

### Issue: "No API key found"
**Symptom**: LLM requests fail with authentication errors  
**Solution**:
1. Check `.env` file exists in project root
2. Verify key format: `OPENAI_API_KEY=sk-...`
3. Restart server to reload environment variables
4. Test with: `python -c "import os; print(os.getenv('OPENAI_API_KEY'))"`

---

### Issue: "File not found" errors
**Symptom**: Storage operations fail  
**Solution**:
1. Ensure `data/` directory exists
2. Check `user_id` is valid (no special chars)
3. Verify permissions: `chmod -R 755 data/`
4. Check logs: `tail -f debug.log`

---

### Issue: Events not being logged
**Symptom**: `/api/log` returns 200 but no file created  
**Solution**:
1. Check `X-User-ID` header is present
2. Verify NDJSON file path: `data/{user_id}/raw/web_tracking_log.ndjson`
3. Test manually: `echo '{"test": true}' >> data/TestUser/raw/web_tracking_log.ndjson`
4. Check disk space: `df -h`

---

### Issue: Scheduler not running
**Symptom**: No automatic summaries generated  
**Solution**:
1. Check scheduler initialized: Look for "Scheduler started" in logs
2. Verify timezone: `_scheduler.timezone` should match your expectation
3. List jobs: In Python REPL, `from scheduler import _scheduler; _scheduler.print_jobs()`
4. Check for job errors: `docker-compose logs -f | grep "Job"`

---

### Issue: LLM returning invalid JSON
**Symptom**: `JSONDecodeError` in logs  
**Solution**:
1. Check prompt clarity in `web_tracking_prompts.py`
2. Add example output format in system prompt
3. Use structured output APIs (OpenAI `response_format={"type": "json_object"}`)
4. Fallback: Wrap response in `{"error": "...", "raw": "..."}`

---

### Issue: High memory usage
**Symptom**: Server crashes or slows down  
**Solution**:
1. Reduce `chunk_tokens` in `web_tracking_pipeline.py`
2. Limit `num_chunks` in chunking calls
3. Process users sequentially instead of parallel
4. Add pagination to `/api/events` endpoint
5. Consider database migration for large datasets

---

### Issue: HTTPS certificate errors
**Symptom**: Browser shows "Your connection is not private"  
**Solution**:
- **Local dev**: Accept self-signed cert warning (expected)
- **Production**: Use real certificates (Let's Encrypt via Nginx/Caddy)
- **Testing**: Import `.certs/localhost.pem` to browser's trusted certificates

---

### Issue: Docker container won't start
**Symptom**: `docker-compose up` fails  
**Solution**:
1. Check logs: `docker-compose logs fastapi`
2. Verify port 8443 not in use: `netstat -an | grep 8443`
3. Rebuild: `docker-compose down && docker-compose up --build`
4. Check Dockerfile syntax
5. Ensure `.env` mounted correctly

---

## Performance Optimization Tips

### 1. **Chunking Strategy**
```python
# For large logs (>100k events)
chunk_and_record(
    chunk_tokens=5000,    # Smaller chunks
    overlap_tokens=200,   # Less overlap
    num_chunks=1,         # Process incrementally
    user_id=user_id
)

# For comprehensive analysis (smaller logs)
chunk_and_record(
    chunk_tokens=10000,   # Larger chunks
    overlap_tokens=500,   # More context
    num_chunks=3,         # Multiple windows
    user_id=user_id
)
```

### 2. **Model Selection**
- **Fast**: `gpt-4o-mini`, `gemini-2.5-flash`
- **Quality**: `gpt-4o`, `claude-opus-4`
- **Budget**: `gemini-2.5-pro` (generous free tier)

### 3. **Caching**
Add Redis for:
- Recent summaries
- User session data
- Rate limit counters

### 4. **Async LLM Calls**
```python
import asyncio
from llm_apis.llm_request import make_llm_request

async def process_parallel():
    tasks = [
        asyncio.create_task(make_llm_request(..., model=AI_API.OPENAI_4o)),
        asyncio.create_task(make_llm_request(..., model=AI_API.GOOGLE)),
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Additional Resources

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **APScheduler Docs**: https://apscheduler.readthedocs.io/
- **NDJSON Specification**: http://ndjson.org/
- **Tiktoken (tokenizer)**: https://github.com/openai/tiktoken
- **Pydantic Models**: https://docs.pydantic.dev/

---

## Contact & Support

For project-specific questions:
- Check `AGENT_INSTRUCTIONS.md` for coding guidelines
- Review `TASKS.md` for known issues and roadmap
- See `Dev Notes.md` for research context

**Repository**: https://github.com/Cithoreal/smart-highlighter-backend  
**Owner**: Cithoreal
