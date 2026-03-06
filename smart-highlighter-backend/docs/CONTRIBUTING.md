# Contributing to Smart Highlighter Backend

Thank you for your interest in improving this project! This guide will help you understand how to work effectively with this codebase.

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Code Standards](#code-standards)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

---

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- Docker (optional, for containerized development)
- API keys for at least one LLM provider (OpenAI, Anthropic, or Google AI)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/Cithoreal/smart-highlighter-backend.git
cd smart-highlighter-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env with your API keys
# At minimum, add one of:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_AI_API_KEY=AIza...
```

### Verify Installation
```bash
# Run the server
python fastapi_server.py

# In another terminal, test the health endpoint
curl http://localhost:8000/healthz

# Expected response: {"ok": true}
```

---

## Development Workflow

### 1. **Check Existing Work**
Before starting any work, check:
- [ ] `TASKS.md` - Is this already planned or in progress?
- [ ] GitHub Issues - Is there an open issue?
- [ ] `Dev Notes.md` - Any historical context?

### 2. **Create a Branch**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New functionality
- `fix/` - Bug fixes
- `refactor/` - Code improvements
- `docs/` - Documentation only
- `test/` - Test additions

### 3. **Make Changes**
Follow the guidelines in [Code Standards](#code-standards)

### 4. **Test Locally**
```bash
# Run manual tests
python -c "from storage import append_event; import asyncio; asyncio.run(append_event({'test': True}, 'TestUser'))"

# Check output
cat data/TestUser/raw/web_tracking_log.ndjson

# Test API endpoints
curl -X POST http://localhost:8000/api/log \
  -H "Content-Type: application/json" \
  -H "X-User-ID: TestUser" \
  -d '{"url": "https://example.com", "action": "test"}'
```

### 5. **Update Documentation**
If your change affects:
- **API** → Update `PROJECT_DOCS.md` (API Reference section)
- **Configuration** → Update `AGENT_INSTRUCTIONS.md` (Configuration section)
- **Tasks** → Update `TASKS.md` (mark completed or add new)

### 6. **Commit Changes**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add rate limiting to /api/log endpoint

- Implemented slowapi rate limiter
- Set limit to 100 requests/minute
- Added rate limit exceeded handler
- Updated PROJECT_DOCS.md with new behavior

Closes #42"
```

Commit message format:
```
<type>: <short summary>

<detailed description>

<footer>
```

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 7. **Push and Create PR**
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
# Include:
# - Description of changes
# - Link to related issue
# - Testing performed
# - Screenshots (if UI changes)
```

---

## Code Standards

### Python Style Guide

#### 1. **Follow PEP 8**
- 4 spaces for indentation (no tabs)
- Max line length: 100 characters (flexible for readability)
- 2 blank lines between top-level functions/classes
- 1 blank line between methods

#### 2. **Type Hints**
Always include type hints for function signatures:

```python
# ✅ Good
async def append_event(event: dict, user_id: str) -> None:
    ...

def get_events_by_id(start: int, end: Optional[int] = None) -> list[dict]:
    ...

# ❌ Avoid
def process_data(data):
    ...
```

#### 3. **Docstrings**
Use Google-style docstrings for public functions:

```python
def chunk_and_record(
    user_id: str,
    chunk_tokens: int = 4096,
    overlap_tokens: int = 512
) -> list[str]:
    """Process raw events into token-based chunks.
    
    Args:
        user_id: User identifier for data isolation
        chunk_tokens: Maximum tokens per chunk
        overlap_tokens: Tokens to overlap between chunks
        
    Returns:
        List of chunk strings (chronological order)
        
    Raises:
        FileNotFoundError: If raw log doesn't exist
        ValueError: If chunk_tokens < overlap_tokens
    """
    ...
```

#### 4. **Error Handling**
Be specific with exceptions:

```python
# ✅ Good
try:
    result = make_llm_request(prompt, data, model)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON from {model.value}: {e}")
    raise HTTPException(500, "LLM returned invalid format")
except ConnectionError as e:
    logger.error(f"LLM API unreachable: {e}")
    raise HTTPException(503, "LLM service unavailable")

# ❌ Avoid
try:
    result = make_llm_request(prompt, data, model)
except Exception as e:
    return str(e)  # Exposes internal errors
```

#### 5. **Path Handling**
Use `pathlib.Path` consistently:

```python
# ✅ Good
from pathlib import Path

file_path = BASE_DIR / user_id / "summaries/full"
file_path.mkdir(parents=True, exist_ok=True)

# ❌ Avoid
import os
file_path = f"data/{user_id}/summaries/full"
os.makedirs(file_path)
```

#### 6. **Async/Await**
Use async for I/O operations:

```python
# ✅ Good
async def save_summary(text: str, user_id: str) -> Path:
    async with aiofiles.open(path, "w") as f:
        await f.write(text)

# ⚠️ Current (to be improved)
def save_summary(text: str, user_id: str) -> Path:
    with open(path, "w") as f:  # Blocks event loop
        f.write(text)
```

### FastAPI Patterns

#### 1. **Dependency Injection**
```python
# Define reusable dependencies
def get_user_id(user_id: str = Header(None, alias="X-User-ID")) -> str:
    if not user_id:
        raise HTTPException(400, "X-User-ID header required")
    return validate_user_id(user_id)

# Use in endpoints
@app.post("/api/log")
async def receive_event(
    event: TrackingEvent,
    user_id: str = Depends(get_user_id)
):
    await append_event(event.dict(), user_id)
    return {"status": "success"}
```

#### 2. **Pydantic Models**
```python
class TrackingEvent(BaseModel):
    url: HttpUrl
    action: str
    timestamp: Optional[datetime] = None
    
    class Config:
        extra = "allow"  # Allow dynamic fields
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "action": "pageview"
            }
        }
```

#### 3. **Background Tasks**
```python
@app.post("/api/run_pipeline")
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_user_id)
):
    background_tasks.add_task(run_pipeline, user_id=user_id)
    return {"status": "Pipeline started"}
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Good - Structured with context
logger.info(
    "Processing events",
    extra={"user_id": user_id, "event_count": count}
)

# ✅ Good - Include relevant details
logger.error(
    f"LLM request failed for {model.value}",
    exc_info=True  # Include stack trace
)

# ❌ Avoid - Generic messages
print("Processing...")
logger.info("Something happened")
```

---

## Making Changes

### Adding a New Endpoint

1. **Define Pydantic models** (if needed)
```python
class NewFeatureRequest(BaseModel):
    param1: str
    param2: Optional[int] = None
```

2. **Create endpoint** in `fastapi_server.py`
```python
@app.post("/api/new-feature")
async def new_feature(
    request: NewFeatureRequest,
    user_id: str = Depends(get_user_id)
):
    """Brief description of what this does."""
    # Implementation
    return {"status": "success"}
```

3. **Update documentation**
- Add to `PROJECT_DOCS.md` → API Reference
- Add example to docstring

4. **Test manually**
```bash
curl -X POST http://localhost:8000/api/new-feature \
  -H "Content-Type: application/json" \
  -H "X-User-ID: TestUser" \
  -d '{"param1": "value"}'
```

### Adding a New LLM Provider

1. **Create provider module** `llm_apis/new_provider_api.py`
```python
import os
import logging

logger = logging.getLogger(__name__)

def _call_llm(system_prompt: str, user_message: str) -> str:
    """Call New Provider's LLM API.
    
    Args:
        system_prompt: System instructions
        user_message: User input/data
        
    Returns:
        LLM response text
        
    Raises:
        ConnectionError: If API unreachable
        ValueError: If API key missing
    """
    api_key = os.getenv("NEW_PROVIDER_API_KEY")
    if not api_key:
        raise ValueError("NEW_PROVIDER_API_KEY not set")
    
    # API call implementation
    ...
    
    return response_text
```

2. **Add to enum** in `llm_apis/llm_request.py`
```python
class AI_API(Enum):
    # Existing...
    NEW_PROVIDER = "new-model-name"
```

3. **Update switch statement**
```python
def make_llm_request(system_prompt, wrapped, llm_model, response_format="text"):
    if llm_model == AI_API.NEW_PROVIDER:
        response = new_provider._call_llm(system_prompt, wrapped)
    # ... existing cases
```

4. **Document**
- Add to `PROJECT_DOCS.md` → Configuration → Environment Variables
- Update `AGENT_INSTRUCTIONS.md` → Common Development Tasks

5. **Test**
```python
# In Python REPL or test script
from llm_apis.llm_request import make_llm_request, AI_API

result = make_llm_request(
    "You are a helpful assistant",
    "Test message",
    AI_API.NEW_PROVIDER
)
print(result)
```

### Modifying Prompt Templates

1. **Edit** `web_tracking_prompts.py`
```python
new_prompt = (
    "You are an expert analyst. "
    "Your task is to... "
    "Return JSON in this format: ..."
)
```

2. **Update pipeline** if adding new prompt type
```python
# In web_tracking_pipeline.py
json_summary_prompts = [
    {"topics": topic_summary_prompt_json},
    {"new_feature": new_prompt},  # Add here
]
```

3. **Test with real data**
```python
# Uncomment in web_tracking_pipeline.py
if __name__ == "__main__":
    run_pipeline("TestUser")
```

4. **Review output**
```bash
cat data/TestUser/summaries/topics/new_feature-*.json
```

---

## Testing

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Server starts without errors
- [ ] Health check responds: `curl http://localhost:8000/healthz`
- [ ] Can log events: `POST /api/log`
- [ ] Can query events: `GET /api/events?day=2025-01-15`
- [ ] Pipeline runs: `POST /api/run_pipeline`
- [ ] Check logs: `tail -f debug.log`
- [ ] Verify file outputs in `data/` directory

### Testing with Real Data

```bash
# 1. Generate test data
curl -X POST http://localhost:8000/api/log \
  -H "X-User-ID: TestUser" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "action": "pageview", "time_on_page": 30}'

# 2. Run pipeline
curl -X POST http://localhost:8000/api/run_pipeline \
  -H "X-User-ID: TestUser"

# 3. Wait for completion (check logs)
tail -f debug.log

# 4. View results
curl http://localhost:8000/api/full_summary/latest \
  -H "X-User-ID: TestUser"

# 5. Check file system
ls -la data/TestUser/summaries/full/
cat data/TestUser/summaries/full/*.md | head -50
```

### Future: Automated Tests

Once testing infrastructure is added (see `TASKS.md` #11):

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Documentation

### What to Document

| Change Type | Update Required |
|-------------|-----------------|
| New endpoint | `PROJECT_DOCS.md` → API Reference |
| New LLM provider | `AGENT_INSTRUCTIONS.md` → LLM Integration |
| New environment var | `PROJECT_DOCS.md` → Configuration, `.env.example` |
| New prompt | `AGENT_INSTRUCTIONS.md` → Prompt Templates |
| Bug fix | Git commit message (detailed) |
| Breaking change | `README.md` → Breaking Changes section |
| Configuration change | `PROJECT_DOCS.md` → Configuration |
| New feature | All three: README, PROJECT_DOCS, AGENT_INSTRUCTIONS |

### Documentation Style

#### Code Comments
```python
# ✅ Good - Explain WHY, not WHAT
# Use backward file reading to avoid loading entire log into memory
with open(path, "rb") as f:
    f.seek(-2, os.SEEK_END)

# ❌ Avoid - Obvious "what"
# Open file
f = open(path)
```

#### Inline Documentation
```python
# ✅ Good - Complex logic explanation
# Sliding window: move back by (chunk_size - overlap)
# to create next window with configured overlap
step = chunk_tokens - overlap_tokens
```

#### Docstrings
See [Code Standards → Docstrings](#code-standards) above

---

## Pull Request Process

### PR Checklist

Before submitting:
- [ ] Branch is up to date with `main`
- [ ] Code follows style guide
- [ ] All functions have type hints
- [ ] Public functions have docstrings
- [ ] Manual testing completed
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No commented-out code (move to tests/ or remove)
- [ ] No secrets/API keys in code

### PR Template

```markdown
## Description
Brief description of changes and motivation.

## Related Issue
Closes #42

## Changes Made
- Added rate limiting to /api/log
- Updated CORS configuration
- Fixed path traversal vulnerability

## Testing Performed
- Manual testing with curl
- Tested with 1000+ events
- Verified rate limiting triggers at 100 req/min
- Checked logs for errors

## Documentation Updated
- [x] PROJECT_DOCS.md
- [x] AGENT_INSTRUCTIONS.md
- [ ] TASKS.md (not applicable)

## Breaking Changes
None

## Screenshots
(if applicable)
```

### Review Process

1. **Automated Checks** (future)
   - Linting (ruff/pylint)
   - Type checking (mypy)
   - Tests passing

2. **Manual Review**
   - Code quality
   - Documentation completeness
   - Security considerations
   - Performance impact

3. **Approval & Merge**
   - Requires 1 approval (project owner)
   - Squash and merge preferred
   - Delete branch after merge

---

## Questions?

- **General**: Check `AGENT_INSTRUCTIONS.md`
- **Technical**: Check `PROJECT_DOCS.md`
- **Tasks**: Check `TASKS.md`
- **Issues**: Open a GitHub Issue
- **Direct contact**: See repository owner info

---

## License

By contributing, you agree that your contributions will be licensed under the same license as this project (see `LICENSE` file).

Thank you for contributing! 🎉
