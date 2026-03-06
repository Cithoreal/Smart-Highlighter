# Quick Reference Guide

**Smart Highlighter Backend - Developer Cheat Sheet**

---

## 🚀 Quick Start

```bash
# Setup
git clone <repo>
cd smart-highlighter-backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # Add API keys

# Run
python fastapi_server.py
# Access: http://localhost:8000
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `fastapi_server.py` | Main app, API endpoints |
| `storage.py` | File I/O, data persistence |
| `web_tracking_pipeline.py` | Processing orchestration |
| `web_tracking_prompts.py` | LLM prompt templates |
| `summarizer.py` | Summary generation |
| `chunking.py` | Text splitting by tokens |
| `llm_apis/llm_request.py` | LLM provider abstraction |
| `llm_judge/llm_judge.py` | Quality evaluation |

---

## 🔌 API Endpoints

### Core Operations
```bash
# Log event
POST /api/log
Headers: X-User-ID: {user}
Body: {"url": "...", "action": "pageview"}

# Query events
GET /api/events?start=100&end=200
GET /api/events?day=2025-01-15
Headers: X-User-ID: {user}

# Latest topic summary (JSON)
GET /api/topic_summary/latest
Headers: X-User-ID: {user}

# Latest full summary (HTML)
GET /api/full_summary/latest
Headers: X-User-ID: {user}

# Trigger pipeline (async)
POST /api/run_pipeline
Headers: X-User-ID: {user}

# Health check
GET /healthz
```

---

## 🗂️ Data Structure

```
data/{user_id}/
├── raw/
│   └── web_tracking_log.ndjson      # Raw events
├── web_tracking_metadata.ndjson     # Processing state
├── topics.json                       # Compiled topics
├── behavior.json                     # Compiled insights
├── evaluation.json                   # Compiled scores
├── summaries/
│   ├── topics/
│   │   └── {label}-{timestamp}.json
│   └── full/
│       └── {timestamp}.md
└── rubric_evaluations/
    └── {timestamp}.md
```

---

## 🧪 Testing Commands

```bash
# Test event logging
curl -X POST http://localhost:8000/api/log \
  -H "Content-Type: application/json" \
  -H "X-User-ID: TestUser" \
  -d '{"url": "https://example.com", "action": "test"}'

# Trigger pipeline
curl -X POST http://localhost:8000/api/run_pipeline \
  -H "X-User-ID: TestUser"

# Check output
cat data/TestUser/summaries/full/*.md | tail -50

# Monitor logs
tail -f debug.log

# Check event count
wc -l data/TestUser/raw/web_tracking_log.ndjson
```

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required: At least one
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...
HUGGINGFACE_API_KEY=hf_...

# Optional
HTTPS=1
RELOAD=1
ALLOWED_ORIGINS=http://localhost:3000
```

### Pipeline Config (web_tracking_pipeline.py)
```python
# Line 37-42
models = [AI_API.GOOGLE, AI_API.OPENAI_4o]

json_summary_prompts = [
    {"topics": topic_summary_prompt_json},
    {"behavior": behavior_insights_prompt_json}
]

full_summary_prompt_options = {
    "description": True,
    "selected_text": True,
    "behavior_analysis": True
}
```

---

## 🤖 LLM Models

### Available Providers (AI_API enum)
```python
AI_API.OPENAI_4o          # GPT-4o
AI_API.OPENAI_o4_mini     # GPT-4o-mini with reasoning
AI_API.ANTHROPIC          # Claude Opus 4
AI_API.GOOGLE             # Gemini 2.5 Pro
AI_API.HUGGINGFACE        # (not fully implemented)
```

### Making LLM Requests
```python
from llm_apis.llm_request import make_llm_request, AI_API

response = make_llm_request(
    system_prompt="You are an analyst...",
    wrapped=json.dumps(data),
    llm_model=AI_API.GOOGLE,
    response_format="text"  # or "json"
)
```

---

## 📝 Common Tasks

### Add New Endpoint
```python
# fastapi_server.py
@app.post("/api/new-feature")
async def new_feature(
    user_id: str = Header(None, alias="X-User-ID")
):
    # Implementation
    return {"status": "success"}
```

### Add New LLM Provider
1. Create `llm_apis/provider_api.py`
2. Implement `_call_llm(system_prompt, user_message)`
3. Add to `AI_API` enum
4. Update `make_llm_request()` switch

### Modify Prompts
Edit `web_tracking_prompts.py`:
```python
new_prompt = "You are an expert..."
```

### Run Pipeline Manually
```python
# Uncomment in web_tracking_pipeline.py
if __name__ == "__main__":
    run_pipeline("TestUser")
```

### Check Processing State
```python
from storage import get_metadata
metadata = get_metadata("Chris")
print(metadata)  # Shows last_processed_event_id, chunks, etc.
```

---

## 🐛 Debugging

### Check Logs
```bash
# Real-time
tail -f debug.log

# Search for errors
grep ERROR debug.log

# Filter by user
grep "user_id: TestUser" debug.log
```

### Validate NDJSON
```python
import json

with open("data/TestUser/raw/web_tracking_log.ndjson") as f:
    for i, line in enumerate(f, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f"Line {i}: {e}")
```

### Test Storage Functions
```python
from storage import append_event, latest_topic_summary
import asyncio

# Test event logging
asyncio.run(append_event({"test": True}, "TestUser"))

# Check latest summary
summary = latest_topic_summary("TestUser")
print(summary)
```

### Check Scheduler Status
```python
from scheduler import _scheduler

# List jobs
for job in _scheduler.get_jobs():
    print(f"{job.id}: Next run at {job.next_run_time}")
```

---

## 🔐 Security Checklist

Current vulnerabilities (see `TASKS.md` for fixes):
- [ ] ⚠️ No authentication (X-User-ID trusted)
- [ ] ⚠️ No input validation (Pydantic models missing)
- [ ] ⚠️ CORS wildcard (`allow_origins=["*"]`)
- [ ] ⚠️ No rate limiting
- [ ] ⚠️ Path traversal possible (user_id not sanitized)

**DO NOT deploy to production without addressing these!**

---

## 📊 Performance Tips

### Optimize Chunking
```python
# Small logs (<10k events)
chunk_tokens=10000, overlap_tokens=500, num_chunks=1

# Large logs (>100k events)
chunk_tokens=5000, overlap_tokens=200, num_chunks=1

# Comprehensive analysis
chunk_tokens=7000, overlap_tokens=250, num_chunks=3
```

### Choose Fast Models
- Fast: `AI_API.OPENAI_o4_mini`, `gemini-flash`
- Quality: `AI_API.OPENAI_4o`, `claude-opus-4`
- Budget: `AI_API.GOOGLE` (generous free tier)

### Monitor Costs
```bash
# Count LLM requests in logs
grep "make_llm_request" debug.log | wc -l

# Estimate tokens (rough)
cat data/TestUser/raw/web_tracking_log.ndjson | wc -c
# Divide by 4 for approximate tokens
```

---

## 🐳 Docker Commands

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f fastapi

# Stop
docker-compose down

# Rebuild single service
docker-compose build fastapi

# Shell into container
docker-compose exec fastapi bash
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `AGENT_INSTRUCTIONS.md` | **Start here** - Architecture, patterns, guidelines |
| `PROJECT_DOCS.md` | Technical reference, API docs, troubleshooting |
| `TASKS.md` | TODO list, priorities, roadmap |
| `CONTRIBUTING.md` | How to contribute, PR process |
| `QUICK_REFERENCE.md` | **This file** - Cheat sheet |
| `Dev Notes.md` | Research notes, experiment logs |
| `README.md` | Setup instructions, overview |

---

## 🔄 Git Workflow

```bash
# Start new feature
git checkout -b feature/my-feature

# Make changes, commit
git add .
git commit -m "feat: add rate limiting

- Implemented slowapi
- Set 100 req/min limit
- Updated docs"

# Push and create PR
git push origin feature/my-feature
```

### Commit Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code restructuring
- `test:` Add tests
- `chore:` Maintenance

---

## 💡 Useful Python Snippets

### Get Event Count
```python
from storage import iter_events

count = sum(1 for _ in iter_events(user_id="Chris"))
print(f"Total events: {count}")
```

### Manually Trigger Summary
```python
from web_tracking_pipeline import create_topic_summary

result = create_topic_summary(force=True, user_id="TestUser")
print(f"Saved to: {result}")
```

### Check Token Count
```python
import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")
text = open("data/TestUser/raw/web_tracking_log.ndjson").read()
tokens = len(enc.encode(text))
print(f"Tokens: {tokens:,}")
```

### Compile All Scores
```python
from llm_judge.llm_judge import compile_scores

compile_scores("TestUser")
print("Scores compiled to data/TestUser/evaluation.json")
```

---

## 🆘 Common Errors

### "No API key found"
```bash
# Check .env file exists
ls -la .env

# Verify key format
grep OPENAI_API_KEY .env

# Restart server
python fastapi_server.py
```

### "File not found"
```bash
# Ensure data directory exists
mkdir -p data/TestUser/raw

# Check permissions
chmod -R 755 data/

# Verify user_id is valid
echo $USER_ID  # Should not contain special chars
```

### "Scheduler not running"
```bash
# Check logs for "Scheduler started"
grep "Scheduler" debug.log

# Verify APScheduler initialized
python -c "from scheduler import _scheduler; print(_scheduler.running)"
```

### High memory usage
```python
# Reduce chunk size in web_tracking_pipeline.py
chunk_tokens=5000  # Was 10000
num_chunks=1       # Was 3
```

---

## 📞 Getting Help

1. **Check documentation**:
   - `AGENT_INSTRUCTIONS.md` - How things work
   - `PROJECT_DOCS.md` - API & troubleshooting
   - `TASKS.md` - Known issues

2. **Search logs**:
   ```bash
   grep -i "error\|warning" debug.log | tail -20
   ```

3. **Test in isolation**:
   ```python
   # Test specific function in Python REPL
   from storage import append_event
   import asyncio
   asyncio.run(append_event({"test": True}, "TestUser"))
   ```

4. **Open issue**: GitHub Issues with:
   - Error message
   - Steps to reproduce
   - Relevant logs
   - Environment (OS, Python version)

---

**For detailed information, always refer to the full documentation files!**
