# Project Improvement Roadmap

**Smart Highlighter Backend - Systematic Cleanup, Stabilization, and Enhancement**

**Created**: November 11, 2025  
**Status**: Planning Phase

---

## 🎯 Overview

This roadmap outlines a four-phase approach to improve the Smart Highlighter Backend project:

1. **Phase 1: Project Cleanup & Organization** (1-2 weeks)
2. **Phase 2: Code Stability & Quality** (2-3 weeks)
3. **Phase 3: Security Hardening** (1-2 weeks)
4. **Phase 4: Feature Enhancement** (Ongoing)

Each phase builds on the previous one, ensuring a stable foundation before adding new capabilities.

---

## 📊 Phase Summary

| Phase | Focus | Duration | Critical Tasks | Status |
|-------|-------|----------|---------------|--------|
| 1 | Cleanup & Organization | 1-2 weeks | Remove dead code, organize structure | ⏸️ Not Started |
| 2 | Stability & Quality | 2-3 weeks | Add tests, fix bugs, improve error handling | ⏸️ Not Started |
| 3 | Security | 1-2 weeks | Auth, validation, CORS, rate limiting | ⏸️ Not Started |
| 4 | Features | Ongoing | Database, caching, real-time, UI | ⏸️ Not Started |

---

## 🧹 Phase 1: Project Cleanup & Organization

**Goal**: Clean codebase, remove technical debt, establish consistent patterns

**Duration**: 1-2 weeks  
**Status**: ⏸️ Not Started

### 1.1 Code Cleanup

#### Remove Dead/Commented Code
**Files to review**:
- [ ] `web_tracking_pipeline.py` (lines 150-180: commented test code)
- [ ] `storage.py` (any unused functions)
- [ ] `fastapi_server.py` (unused imports, commented routes)
- [ ] `scheduler.py` (old scheduling logic)

**Action items**:
```bash
# Find commented code blocks
grep -rn "# *def " --include="*.py" .
grep -rn "# *class " --include="*.py" .

# Find TODO/FIXME comments
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.py" .
```

#### Organize Imports
**Current issue**: Inconsistent import ordering

**Fix**: Apply `isort` + `black`
```bash
pip install isort black
isort . --profile black
black . --line-length 88
```

**Add to pre-commit**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
```

#### Improve Naming Consistency
**Current inconsistencies**:
- Mix of `snake_case` and `camelCase` in JSON fields
- Unclear variable names (e.g., `data`, `result`, `output`)
- Function names don't always indicate purpose

**Examples**:
```python
# Before
def process(data):
    result = something(data)
    return result

# After
def generate_topic_summaries(raw_events: list[dict]) -> list[TopicSummary]:
    topic_summaries = extract_topics_from_events(raw_events)
    return topic_summaries
```

#### Consolidate Duplicate Code
**Known duplicates**:
- File path construction (appears in multiple modules)
- Event timestamp parsing
- User ID extraction from headers

**Create utilities**:
```python
# utils/paths.py
def get_user_data_dir(user_id: str) -> Path:
    return Path("data") / user_id

def get_raw_log_path(user_id: str) -> Path:
    return get_user_data_dir(user_id) / "raw" / "web_tracking_log.ndjson"

# utils/validation.py
def parse_timestamp(ts: str | float) -> datetime:
    # Consolidated timestamp parsing logic
    ...
```

### 1.2 File Structure Reorganization

#### Current Structure Issues
- Flat root directory with too many files
- Test files missing
- Config files scattered

#### Proposed New Structure
```
smart-highlighter-backend/
├── src/                           # NEW: Source code
│   ├── __init__.py
│   ├── main.py                    # Renamed from fastapi_server.py
│   ├── config.py                  # NEW: Centralized config
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── routes.py              # All route handlers
│   │   ├── dependencies.py        # Shared dependencies
│   │   └── models.py              # Request/response models
│   │
│   ├── core/                      # Business logic
│   │   ├── __init__.py
│   │   ├── storage.py
│   │   ├── pipeline.py
│   │   ├── summarizer.py
│   │   └── chunking.py
│   │
│   ├── llm/                       # LLM integrations
│   │   ├── __init__.py
│   │   ├── providers/
│   │   │   ├── openai.py
│   │   │   ├── anthropic.py
│   │   │   └── google.py
│   │   ├── judge/
│   │   │   ├── rubric.py
│   │   │   └── evaluator.py
│   │   └── prompts.py
│   │
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   ├── paths.py
│   │   ├── validation.py
│   │   └── logging.py
│   │
│   └── scheduler/                 # Background tasks
│       ├── __init__.py
│       └── jobs.py
│
├── tests/                         # NEW: Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_storage.py
│   │   ├── test_chunking.py
│   │   └── test_summarizer.py
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   └── test_api.py
│   └── fixtures/
│       └── sample_events.json
│
├── config/                        # NEW: Configuration
│   ├── .env.example
│   └── settings.yaml
│
├── scripts/                       # NEW: Utility scripts
│   ├── migrate_data.py
│   ├── generate_certs.py
│   └── cleanup_logs.py
│
├── docker/                        # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/                          # Documentation (already done)
│   └── ...
│
├── data/                          # Runtime data (gitignored)
├── logs/                          # NEW: Centralized logs
├── README.md
├── requirements.txt
├── requirements-dev.txt           # NEW: Dev dependencies
├── pyproject.toml                 # NEW: Project config
├── setup.py                       # NEW: Package setup
└── .gitignore
```

#### Migration Steps
1. Create new directory structure
2. Move files to appropriate locations
3. Update imports throughout codebase
4. Update documentation references
5. Test everything still works

### 1.3 Configuration Management

#### Current Issues
- Environment variables scattered
- No defaults for optional config
- Hard-coded values in multiple places

#### Implement Centralized Config
```python
# src/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    https: bool = False
    
    # Security
    cors_origins: list[str] = ["*"]  # To be fixed in Phase 3
    api_key_header: str = "X-API-Key"
    
    # LLM APIs
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_ai_api_key: str | None = None
    huggingface_api_key: str | None = None
    
    # Processing
    default_model: str = "gpt-4o-mini"
    chunk_size: int = 3000
    chunk_overlap: int = 200
    
    # Storage
    data_dir: Path = Path("data")
    log_dir: Path = Path("logs")
    
    # Scheduler
    enable_scheduler: bool = True
    hourly_summary_time: str = "0"  # minute of hour
    daily_summary_time: str = "23:55"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage throughout codebase
from src.config import get_settings
settings = get_settings()
```

### 1.4 Logging Improvements

#### Current Issues
- Mix of `print()` and `logging`
- No structured logging
- Logs not organized by module

#### Implement Structured Logging
```python
# src/utils/logging.py
import logging
import sys
from pathlib import Path

def setup_logging(log_dir: Path = Path("logs")):
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (detailed)
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler (concise)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Module-specific loggers
logger = logging.getLogger(__name__)
```

**Replace all print statements**:
```python
# Before
print(f"Processing user: {user_id}")
print(f"Error: {e}")

# After
logger.info("Processing user: %s", user_id)
logger.error("Failed to process: %s", exc_info=True)
```

### 1.5 Documentation Sync

#### Update Documentation for Changes
- [ ] Update `docs/AGENT_INSTRUCTIONS.md` with new structure
- [ ] Update `docs/PROJECT_DOCS.md` with config changes
- [ ] Update `docs/QUICK_REFERENCE.md` with new commands
- [ ] Create migration guide in `docs/MIGRATION_GUIDE.md`

### 1.6 Git Cleanup

#### Clean Up Repository
```bash
# Remove accidentally committed files
git rm --cached debug.log
git rm --cached -r __pycache__/
git rm --cached -r .certs/

# Update .gitignore
echo "
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/

# Logs
*.log
logs/

# Data
data/
.certs/

# IDE
.vscode/
.idea/
*.swp

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
" > .gitignore
```

---

## 🔧 Phase 2: Code Stability & Quality

**Goal**: Ensure code is reliable, maintainable, and well-tested

**Duration**: 2-3 weeks  
**Status**: ⏸️ Not Started  
**Depends on**: Phase 1 completion

### 2.1 Add Comprehensive Tests

#### Test Infrastructure Setup
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config import get_settings

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_event():
    return {
        "url": "https://example.com",
        "action": "pageview",
        "timestamp": "2025-01-15T10:30:00",
        "time_on_page": 45.5
    }

@pytest.fixture
def temp_user_dir(tmp_path):
    user_dir = tmp_path / "test_user"
    user_dir.mkdir(parents=True)
    return user_dir
```

#### Unit Tests
```python
# tests/unit/test_storage.py
import pytest
from src.core.storage import append_event, iter_events

@pytest.mark.asyncio
async def test_append_event(temp_user_dir):
    event = {"type": "test", "data": "value"}
    event_id = await append_event("test_user", event)
    assert event_id is not None
    assert event_id > 0

@pytest.mark.asyncio
async def test_iter_events(temp_user_dir):
    # Add test events
    for i in range(5):
        await append_event("test_user", {"index": i})
    
    # Retrieve events
    events = list(iter_events("test_user"))
    assert len(events) == 5
    assert events[0]["index"] == 0

# tests/unit/test_chunking.py
from src.core.chunking import split_into_chunks

def test_split_into_chunks():
    text = "word " * 1000
    chunks = split_into_chunks(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 120 for chunk in chunks)
```

#### Integration Tests
```python
# tests/integration/test_api.py
def test_log_event(client, sample_event):
    response = client.post(
        "/api/log",
        json=sample_event,
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == 200
    assert "event_id" in response.json()

def test_get_events(client):
    # Create some events
    for i in range(3):
        client.post(
            "/api/log",
            json={"index": i},
            headers={"X-User-ID": "test_user"}
        )
    
    # Query events
    response = client.get(
        "/api/events",
        headers={"X-User-ID": "test_user"}
    )
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 3
```

#### Test Coverage Goals
- **Target**: 80%+ coverage
- **Critical paths**: 100% coverage
  - Storage operations
  - API endpoints
  - Authentication (Phase 3)

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term
```

### 2.2 Fix Async/Await Issues

#### Current Problems
- Sync file I/O blocking event loop
- Inconsistent async patterns
- Missing `await` in some places

#### Fix Blocking I/O
```python
# Before (blocking)
def append_event(user_id: str, event: dict):
    with open(log_path, 'a') as f:
        f.write(json.dumps(event) + '\n')

# After (non-blocking)
import aiofiles

async def append_event(user_id: str, event: dict):
    async with aiofiles.open(log_path, mode='a') as f:
        await f.write(json.dumps(event) + '\n')
```

#### Use Thread Pool for CPU-Bound Tasks
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=4)

async def process_with_llm(text: str) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        expensive_llm_call,
        text
    )
    return result
```

### 2.3 Improve Error Handling

#### Add Custom Exceptions
```python
# src/core/exceptions.py
class SmartHighlighterError(Exception):
    """Base exception for Smart Highlighter"""
    pass

class StorageError(SmartHighlighterError):
    """Raised when storage operations fail"""
    pass

class LLMError(SmartHighlighterError):
    """Raised when LLM API calls fail"""
    pass

class ValidationError(SmartHighlighterError):
    """Raised when input validation fails"""
    pass
```

#### Implement Error Handlers
```python
# src/api/routes.py
from fastapi import HTTPException
from src.core.exceptions import StorageError, LLMError

@app.exception_handler(StorageError)
async def storage_error_handler(request, exc):
    logger.error("Storage error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Storage operation failed", "detail": str(exc)}
    )

@app.exception_handler(LLMError)
async def llm_error_handler(request, exc):
    logger.error("LLM error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"error": "LLM service unavailable", "detail": str(exc)}
    )
```

#### Add Retry Logic
```python
# src/utils/retry.py
import asyncio
from functools import wraps

def async_retry(max_attempts=3, delay=1.0, backoff=2.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator

# Usage
@async_retry(max_attempts=3, delay=2.0)
async def call_llm_api(prompt: str) -> str:
    return await openai_client.create_completion(prompt)
```

### 2.4 Add Type Hints Everywhere

#### Use mypy for Type Checking
```bash
pip install mypy
mypy src/ --strict
```

#### Add Missing Type Hints
```python
# Before
def process_events(events):
    results = []
    for event in events:
        result = transform(event)
        results.append(result)
    return results

# After
from typing import TypedDict

class Event(TypedDict):
    url: str
    action: str
    timestamp: str

def process_events(events: list[Event]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for event in events:
        result = transform(event)
        results.append(result)
    return results
```

### 2.5 Performance Optimization

#### Profile Current Performance
```python
# Add timing decorators
import time
from functools import wraps

def time_it(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.info(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

@time_it
async def run_pipeline(user_id: str):
    ...
```

#### Optimize Hot Paths
- Cache LLM responses
- Batch file operations
- Use connection pooling for LLM APIs
- Implement lazy loading for large files

### 2.6 Data Integrity

#### Add Data Validation on Read
```python
def validate_event_structure(event: dict) -> bool:
    required_fields = ["url", "timestamp"]
    return all(field in event for field in required_fields)

def iter_events(user_id: str):
    for line in read_ndjson(user_id):
        try:
            event = json.loads(line)
            if validate_event_structure(event):
                yield event
            else:
                logger.warning(f"Malformed event: {line[:100]}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line[:100]}")
            continue
```

#### Add Data Backup System
```python
# scripts/backup_data.py
import shutil
from datetime import datetime

def backup_user_data(user_id: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    src = Path("data") / user_id
    dst = Path("backups") / f"{user_id}_{timestamp}"
    shutil.copytree(src, dst)
    logger.info(f"Backed up {user_id} to {dst}")
```

---

## 🔒 Phase 3: Security Hardening

**Goal**: Address all critical security vulnerabilities

**Duration**: 1-2 weeks  
**Status**: ⏸️ Not Started  
**Depends on**: Phase 2 completion

### 3.1 Implement Authentication

#### Choose Auth Strategy: JWT + API Keys

**JWT for browser extension**:
- User logs in via web interface
- Receives JWT token
- Extension stores token securely
- Includes token in all requests

**API Keys for programmatic access**:
- Generate API keys via dashboard
- Store hashed keys in database
- Validate on each request

#### Implementation Steps

**1. Add Auth Dependencies**
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

**2. Create Auth Module**
```python
# src/auth/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid authentication")
        return user_id
    except JWTError:
        raise HTTPException(401, "Invalid authentication")
```

**3. Add Auth Endpoints**
```python
# src/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/register")
async def register(username: str, password: str):
    # Check if user exists
    if user_exists(username):
        raise HTTPException(400, "User already exists")
    
    # Hash password
    hashed_password = pwd_context.hash(password)
    
    # Store user
    create_user(username, hashed_password)
    
    return {"message": "User created successfully"}

@router.post("/login")
async def login(username: str, password: str):
    # Verify credentials
    user = get_user(username)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    # Create token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    return verify_token(credentials.credentials)
```

**4. Protect All Endpoints**
```python
# src/api/routes.py
@app.post("/api/log")
async def log_event(
    event: dict,
    user_id: str = Depends(get_current_user)
):
    event_id = await append_event(user_id, event)
    return {"status": "ok", "event_id": event_id}

@app.get("/api/events")
async def get_events(
    user_id: str = Depends(get_current_user),
    start: int | None = None,
    end: int | None = None
):
    events = list(iter_events(user_id, start_id=start, end_id=end))
    return events
```

### 3.2 Input Validation with Pydantic

#### Create Request Models
```python
# src/api/models.py
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Literal

class TrackingEvent(BaseModel):
    url: HttpUrl
    type: Literal["timeOnPage", "scrollData", "mouseDownEvent", "mouseupEvent", "userEntry"]
    timestamp: datetime
    
    # Optional fields
    time_spent_ms: int | None = Field(None, ge=0, le=3600000)
    coords: dict[str, float] | None = None
    selection: str | None = Field(None, max_length=10000)
    max_scroll_percent: float | None = Field(None, ge=0, le=100)
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = [
            "timeOnPage", "scrollData", "mouseDownEvent",
            "mouseupEvent", "userEntry"
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid event type: {v}")
        return v
    
    class Config:
        extra = "allow"  # Allow additional fields from extension

class PipelineRequest(BaseModel):
    force: bool = False
    model: str | None = None
    
class EventsQuery(BaseModel):
    start: int | None = Field(None, ge=0)
    end: int | None = Field(None, ge=0)
    day: str | None = None
    
    @validator('day')
    def validate_day(cls, v):
        if v:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Day must be in YYYY-MM-DD format")
        return v
```

#### Use Models in Endpoints
```python
@app.post("/api/log")
async def log_event(
    event: TrackingEvent,  # Automatic validation!
    user_id: str = Depends(get_current_user)
):
    event_dict = event.dict()
    event_id = await append_event(user_id, event_dict)
    return {"status": "ok", "event_id": event_id}

@app.get("/api/events")
async def get_events(
    query: EventsQuery = Depends(),  # Query parameters validated
    user_id: str = Depends(get_current_user)
):
    ...
```

### 3.3 Fix CORS Configuration

#### Replace Wildcard with Specific Origins
```python
# src/config.py
class Settings(BaseSettings):
    # Before
    # cors_origins: list[str] = ["*"]
    
    # After
    cors_origins: list[str] = [
        "https://aiapi.cybernautics.net",
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_allow_headers: list[str] = ["Authorization", "Content-Type"]

# src/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers
)
```

### 3.4 Add Rate Limiting

#### Install slowapi
```bash
pip install slowapi
```

#### Implement Rate Limits
```python
# src/api/middleware.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@app.post("/api/log")
@limiter.limit("100/minute")
async def log_event(
    request: Request,
    event: TrackingEvent,
    user_id: str = Depends(get_current_user)
):
    ...

@app.post("/api/run_pipeline")
@limiter.limit("5/hour")  # Expensive operation
async def run_pipeline(
    request: Request,
    user_id: str = Depends(get_current_user)
):
    ...
```

#### Per-User Rate Limiting
```python
def get_user_id_from_request(request: Request) -> str:
    # Extract from JWT token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user_id = verify_token(token)
    return user_id

limiter_by_user = Limiter(key_func=get_user_id_from_request)

@app.post("/api/log")
@limiter_by_user.limit("1000/hour")
async def log_event(...):
    ...
```

### 3.5 Path Sanitization

#### Validate and Sanitize Paths
```python
# src/utils/paths.py
from pathlib import Path
import re

def sanitize_user_id(user_id: str) -> str:
    """
    Ensure user_id contains only safe characters.
    Prevents path traversal attacks.
    """
    # Allow only alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise ValueError("Invalid user_id format")
    
    # Prevent path traversal
    if ".." in user_id or "/" in user_id or "\\" in user_id:
        raise ValueError("Invalid user_id: path traversal attempt")
    
    return user_id

def get_safe_user_path(user_id: str, subpath: str = "") -> Path:
    """
    Get a safe path within the user's data directory.
    Prevents escaping the user directory.
    """
    safe_user_id = sanitize_user_id(user_id)
    base_dir = Path("data") / safe_user_id
    
    if subpath:
        full_path = (base_dir / subpath).resolve()
        # Ensure result is still within base_dir
        if not str(full_path).startswith(str(base_dir.resolve())):
            raise ValueError("Invalid path: attempted directory traversal")
        return full_path
    
    return base_dir
```

### 3.6 Security Headers

#### Add Security Middleware
```python
# src/api/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### 3.7 Secrets Management

#### Move Secrets Out of .env
```python
# Use environment-specific secrets
# Development: .env.local (gitignored)
# Production: Environment variables or secrets manager

# src/config.py
import os
from typing import Optional

class Settings(BaseSettings):
    secret_key: str = Field(
        default_factory=lambda: os.urandom(32).hex()
    )
    
    # LLM API keys from environment
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
    
    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        env_file_encoding = "utf-8"
```

---

## 🚀 Phase 4: Feature Enhancement

**Goal**: Expand capabilities while maintaining stability and security

**Duration**: Ongoing  
**Status**: ⏸️ Not Started  
**Depends on**: Phase 3 completion

### 4.1 Database Migration

#### Replace NDJSON with SQLite/PostgreSQL

**Why migrate?**
- Better query performance
- ACID compliance
- Concurrent access
- Indexing capabilities
- Easier analytics

#### Implementation with SQLAlchemy
```python
# src/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    events = relationship("Event", back_populates="user")
    summaries = relationship("Summary", back_populates="user")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    event_type = Column(String, index=True)
    url = Column(String)
    timestamp = Column(DateTime, index=True)
    data = Column(JSON)
    
    user = relationship("User", back_populates="events")

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    summary_type = Column(String)  # "topic" or "full"
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)
    
    user = relationship("User", back_populates="summaries")
```

#### Migration Script
```python
# scripts/migrate_ndjson_to_db.py
import asyncio
from sqlalchemy.orm import Session
from src.db.models import User, Event
from src.core.storage import iter_events

async def migrate_user_data(session: Session, user_id: str):
    # Create user if not exists
    user = session.query(User).filter_by(username=user_id).first()
    if not user:
        user = User(username=user_id, hashed_password="migrated")
        session.add(user)
        session.flush()
    
    # Migrate events
    for event_dict in iter_events(user_id):
        event = Event(
            user_id=user.id,
            event_type=event_dict.get("type"),
            url=event_dict.get("url"),
            timestamp=event_dict.get("timestamp"),
            data=event_dict
        )
        session.add(event)
    
    session.commit()
    print(f"Migrated {user_id}")
```

### 4.2 Redis Caching Layer

#### Add Caching for LLM Responses
```python
# src/cache/redis_cache.py
import redis.asyncio as redis
import json
from typing import Optional

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost"):
        self.redis = redis.from_url(redis_url)
    
    async def get_llm_response(self, prompt_hash: str) -> Optional[str]:
        cached = await self.redis.get(f"llm:{prompt_hash}")
        return cached.decode() if cached else None
    
    async def set_llm_response(
        self,
        prompt_hash: str,
        response: str,
        ttl: int = 86400  # 24 hours
    ):
        await self.redis.setex(
            f"llm:{prompt_hash}",
            ttl,
            response
        )
    
    async def get_summary(self, user_id: str, summary_type: str) -> Optional[dict]:
        key = f"summary:{user_id}:{summary_type}:latest"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None
    
    async def set_summary(
        self,
        user_id: str,
        summary_type: str,
        data: dict,
        ttl: int = 3600
    ):
        key = f"summary:{user_id}:{summary_type}:latest"
        await self.redis.setex(key, ttl, json.dumps(data))

# Usage in summarizer
cache = CacheManager()

async def generate_summary(prompt: str) -> str:
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    
    # Check cache
    cached = await cache.get_llm_response(prompt_hash)
    if cached:
        logger.info("Cache hit for prompt hash: %s", prompt_hash[:8])
        return cached
    
    # Generate new
    response = await call_llm(prompt)
    
    # Store in cache
    await cache.set_llm_response(prompt_hash, response)
    
    return response
```

### 4.3 Real-Time Updates with WebSockets

#### Add WebSocket Endpoint
```python
# src/api/websockets.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id].discard(websocket)
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            self.active_connections[user_id] -= dead_connections

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Notify user when summary is ready
async def process_summary_background(user_id: str):
    summary = await generate_summary(user_id)
    await manager.send_to_user(user_id, {
        "type": "summary_ready",
        "data": summary
    })
```

### 4.4 User Management Dashboard

#### Add Admin Endpoints
```python
# src/api/admin.py
from fastapi import APIRouter, Depends
from src.auth.security import get_current_user, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
async def list_users(
    current_user: str = Depends(require_admin)
):
    users = await get_all_users()
    return users

@router.get("/stats")
async def get_stats(
    current_user: str = Depends(require_admin)
):
    return {
        "total_users": await count_users(),
        "total_events": await count_events(),
        "total_summaries": await count_summaries(),
        "disk_usage": calculate_disk_usage()
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: str = Depends(require_admin)
):
    await delete_user_data(user_id)
    return {"message": f"User {user_id} deleted"}
```

### 4.5 Export Functionality

#### Add Export Endpoints
```python
# src/api/export.py
from fastapi import APIRouter
from fastapi.responses import FileResponse
import markdown

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/summary/pdf/{summary_id}")
async def export_summary_pdf(
    summary_id: str,
    user_id: str = Depends(get_current_user)
):
    summary = await get_summary(summary_id, user_id)
    pdf_path = await generate_pdf(summary)
    return FileResponse(pdf_path, media_type="application/pdf")

@router.get("/data/csv")
async def export_events_csv(
    start_date: str,
    end_date: str,
    user_id: str = Depends(get_current_user)
):
    events = await get_events_range(user_id, start_date, end_date)
    csv_path = await generate_csv(events)
    return FileResponse(csv_path, media_type="text/csv")
```

### 4.6 Advanced Analytics

#### Add Analytics Endpoints
```python
# src/api/analytics.py
@router.get("/analytics/activity")
async def get_activity_stats(
    user_id: str = Depends(get_current_user),
    days: int = 30
):
    return {
        "pages_visited": await count_pages(user_id, days),
        "time_spent": await total_time_spent(user_id, days),
        "top_domains": await top_domains(user_id, days),
        "activity_by_hour": await activity_heatmap(user_id, days)
    }

@router.get("/analytics/topics")
async def get_topic_trends(
    user_id: str = Depends(get_current_user),
    days: int = 30
):
    return {
        "trending_topics": await get_trending_topics(user_id, days),
        "topic_distribution": await topic_distribution(user_id, days),
        "topic_evolution": await topic_timeline(user_id, days)
    }
```

---

## 📋 Implementation Checklist

### Phase 1: Cleanup & Organization (Weeks 1-2)
- [ ] Remove all commented/dead code
- [ ] Apply isort + black formatting
- [ ] Improve variable naming throughout
- [ ] Consolidate duplicate code into utilities
- [ ] Reorganize file structure (move to src/)
- [ ] Implement centralized configuration
- [ ] Replace print() with logging
- [ ] Update all documentation
- [ ] Clean up git repository

### Phase 2: Stability & Quality (Weeks 3-5)
- [ ] Set up pytest infrastructure
- [ ] Write unit tests (80% coverage goal)
- [ ] Write integration tests for API
- [ ] Fix all async/await issues
- [ ] Implement custom exceptions
- [ ] Add error handlers
- [ ] Add retry logic for LLM calls
- [ ] Add type hints everywhere
- [ ] Profile and optimize hot paths
- [ ] Implement data validation on read
- [ ] Add data backup system

### Phase 3: Security (Weeks 6-7)
- [ ] Implement JWT authentication
- [ ] Add API key support
- [ ] Create auth endpoints
- [ ] Protect all routes
- [ ] Create Pydantic models for validation
- [ ] Fix CORS configuration
- [ ] Add rate limiting
- [ ] Implement path sanitization
- [ ] Add security headers
- [ ] Move secrets to proper management

### Phase 4: Features (Ongoing)
- [ ] Migrate to SQLite/PostgreSQL
- [ ] Add Redis caching layer
- [ ] Implement WebSocket real-time updates
- [ ] Create user management dashboard
- [ ] Add PDF/CSV export functionality
- [ ] Build analytics dashboard
- [ ] Create admin interface

---

## 🎯 Success Metrics

### Phase 1 Success Criteria
- ✅ Zero commented code blocks
- ✅ All code passes black/isort
- ✅ Consistent naming conventions
- ✅ DRY principle applied (no duplicate code)
- ✅ Clear file structure
- ✅ No print() statements
- ✅ All docs updated

### Phase 2 Success Criteria
- ✅ 80%+ test coverage
- ✅ All tests passing
- ✅ Zero blocking I/O in async functions
- ✅ All functions type-hinted
- ✅ Error rate < 1%
- ✅ Graceful degradation on LLM failures

### Phase 3 Success Criteria
- ✅ All endpoints require authentication
- ✅ Input validation on all routes
- ✅ CORS properly configured
- ✅ Rate limiting active
- ✅ No path traversal vulnerabilities
- ✅ Security headers present
- ✅ Pass OWASP security scan

### Phase 4 Success Criteria
- ✅ Database migration complete
- ✅ Query performance < 100ms
- ✅ Cache hit rate > 50%
- ✅ Real-time updates working
- ✅ Export functionality available
- ✅ Analytics dashboard live

---

## 📊 Timeline

```
Week 1-2:   Phase 1 (Cleanup)
Week 3-5:   Phase 2 (Stability)
Week 6-7:   Phase 3 (Security)
Week 8+:    Phase 4 (Features)

Total:      ~8 weeks for Phases 1-3
            Ongoing for Phase 4
```

---

## 🚦 Getting Started

### Immediate Next Steps
1. Review this roadmap
2. Create a new branch: `git checkout -b phase-1-cleanup`
3. Start with Phase 1.1: Code Cleanup
4. Work through tasks systematically
5. Test after each major change
6. Document changes in commit messages

### Daily Workflow
1. Pick a task from current phase
2. Create feature branch
3. Implement with tests
4. Run test suite
5. Update documentation
6. Create PR
7. Review and merge
8. Move to next task

---

## 📞 Support

**Questions or need help?**
- Check relevant docs in `docs/` directory
- Create GitHub issue for discussion
- Contact: cithoreal@gmail.com

---

**Last Updated**: November 11, 2025  
**Version**: 1.0  
**Status**: Ready for implementation
