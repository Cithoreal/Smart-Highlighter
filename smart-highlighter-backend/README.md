# Smart Highlighter Backend

**AI-Powered Web Tracking Analysis & Summarization System**

A FastAPI backend that collects browsing events from a Firefox extension, processes them through multiple LLM providers (OpenAI, Anthropic, Google AI), and generates insightful summaries with automated quality evaluation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API key for at least one LLM provider (OpenAI, Anthropic, or Google AI)
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/Cithoreal/smart-highlighter-backend.git
cd smart-highlighter-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env with your API keys
```

### Running the Server

#### Development Mode
```bash
python fastapi_server.py
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

#### Docker Mode
```bash
docker-compose up -d --build
# Access at: http://localhost:8443 (HTTPS)
```

---

## 🎯 Key Features

- **Multi-LLM Support**: OpenAI, Anthropic, Google AI, HuggingFace
- **Intelligent Chunking**: Token-aware sliding window processing
- **Quality Evaluation**: LLM-as-judge with 6-dimensional rubric
- **Scheduled Summarization**: Automated hourly/daily summaries via APScheduler
- **Per-User Isolation**: Separate data directories for each user
- **REST API**: Full-featured API for event ingestion and query
- **Background Processing**: Async pipeline for expensive operations
- **Comprehensive Logging**: Structured logging with file rotation

---

## 📚 Documentation

**All documentation is now organized in the [`docs/`](docs/) directory.**

### 🎯 Start Here
- **[docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)** - Navigation hub for all documentation
- **[docs/README.md](docs/README.md)** - Documentation directory guide

### 📖 Core Documentation
- **[docs/AGENT_INSTRUCTIONS.md](docs/AGENT_INSTRUCTIONS.md)** - Complete guide for AI agents (GitHub Copilot)
- **[docs/PROJECT_DOCS.md](docs/PROJECT_DOCS.md)** - Technical reference and API documentation
- **[docs/TASKS.md](docs/TASKS.md)** - Current priorities, roadmap, and work tracking

### 🛠️ Quick Reference
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Cheat sheet for common commands
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - How to contribute to this project
- **[docs/RELATED_REPOSITORIES.md](docs/RELATED_REPOSITORIES.md)** - Ecosystem architecture

### Quick Links

| I want to... | Read this |
|--------------|-----------|
| Get started | [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) |
| Understand the architecture | [docs/AGENT_INSTRUCTIONS.md](docs/AGENT_INSTRUCTIONS.md) |
| Use the API | [docs/PROJECT_DOCS.md](docs/PROJECT_DOCS.md) → API Reference |
| Set up locally | This README + [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) |
| Find common commands | [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) |
| Contribute code | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| See what needs work | [docs/TASKS.md](docs/TASKS.md) |
| Understand the ecosystem | [docs/RELATED_REPOSITORIES.md](docs/RELATED_REPOSITORIES.md) |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example` for template):

```bash
# Required: At least one LLM API key
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=AIza...

# Optional: Server configuration
HTTPS=0                          # Enable HTTPS with self-signed cert
RELOAD=1                         # Hot reload in development
ALLOWED_ORIGINS=http://localhost:3000
```

For complete configuration options, see [`.env.example`](.env.example)

---

## 📖 Basic Usage

### 1. Log an Event
```bash
curl -X POST http://localhost:8000/api/log \
  -H "Content-Type: application/json" \
  -H "X-User-ID: YourUserID" \
  -d '{"url": "https://example.com", "action": "pageview", "time_on_page": 30}'
```

### 2. Query Events
```bash
# By date
curl http://localhost:8000/api/events?day=2025-01-15 \
  -H "X-User-ID: YourUserID"

# By ID range
curl http://localhost:8000/api/events?start=100&end=200 \
  -H "X-User-ID: YourUserID"
```

### 3. Get Latest Summary
```bash
# Topic summary (JSON)
curl http://localhost:8000/api/topic_summary/latest \
  -H "X-User-ID: YourUserID"

# Full summary (HTML)
curl http://localhost:8000/api/full_summary/latest \
  -H "X-User-ID: YourUserID"
```

### 4. Trigger Pipeline
```bash
curl -X POST http://localhost:8000/api/run_pipeline \
  -H "X-User-ID: YourUserID"
```

For more examples, see [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

## 🏗️ Project Structure

```
smart-highlighter-backend/
├── fastapi_server.py              # Main application
├── storage.py                     # Data persistence
├── web_tracking_pipeline.py       # Processing orchestration
├── web_tracking_prompts.py        # LLM prompts
├── summarizer.py                  # Summary generation
├── chunking.py                    # Text splitting
├── scheduler.py                   # Automated tasks
├── llm_apis/                      # LLM provider integrations
├── llm_judge/                     # Quality evaluation
├── templates/                     # Jinja2 templates
└── data/                          # User data (gitignored)
    └── {user_id}/
        ├── raw/                   # Event logs
        ├── summaries/             # Generated summaries
        └── rubric_evaluations/    # Quality scores
```

For detailed architecture, see [docs/AGENT_INSTRUCTIONS.md](docs/AGENT_INSTRUCTIONS.md)

---

## 🧪 Testing

```bash
# Check health
curl http://localhost:8000/healthz

# Test event logging
python -c "from storage import append_event; import asyncio; asyncio.run(append_event({'test': True}, 'TestUser'))"

# Monitor logs
tail -f debug.log
```

For comprehensive testing guide, see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 🐳 Docker Deployment

### docker-compose.yml
```yaml
services:
  fastapi:
    build:
      dockerfile: Dockerfile
    container_name: fastapi
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    ports:
      - "8443:8443"
    environment:
      - HTTPS=1
```

### Commands
```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f fastapi

# Stop
docker-compose down
```

---

## ⚠️ Security Notice

**This project is currently in development and has known security issues:**

- ⚠️ No authentication (user IDs are trusted)
- ⚠️ No input validation
- ⚠️ CORS wildcard enabled
- ⚠️ No rate limiting
- ⚠️ Path traversal vulnerability

**DO NOT deploy to production without addressing these issues!**

See [docs/TASKS.md](docs/TASKS.md) → Critical Priority for security hardening tasks.

---

## 🗺️ Roadmap

### Current Focus (v0.2)
- [ ] Implement authentication (JWT/OAuth)
- [ ] Add input validation (Pydantic models)
- [ ] Fix CORS configuration
- [ ] Add rate limiting
- [ ] Path sanitization

### Future Enhancements (v0.3+)
- [ ] Database migration (SQLite/PostgreSQL)
- [ ] Redis caching layer
- [ ] Real-time dashboard (WebSockets)
- [ ] User management UI
- [ ] Export functionality (PDF, DOCX)

For detailed roadmap, see [docs/TASKS.md](docs/TASKS.md)

---

## 🤝 Contributing

We welcome contributions! Please see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Development workflow
- Code standards
- Testing procedures
- Pull request process

---

## 📊 Research Context

This project is part of a directed study on:
- Comparing LLM models for summarization quality
- Prompt engineering effectiveness
- Data format impact on LLM performance
- Automated quality evaluation (LLM-as-judge)

See [docs/RELATED_REPOSITORIES.md](docs/RELATED_REPOSITORIES.md) for the full ecosystem architecture and [docs/Dev Notes.md](docs/Dev%20Notes.md) for experiment logs and findings.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **OpenAI, Anthropic, Google AI** - LLM providers
- **APScheduler** - Task scheduling
- **Tiktoken** - Token counting

---

## 📧 Contact

- **Repository**: https://github.com/Cithoreal/smart-highlighter-backend
- **Owner**: Cithoreal
- **Issues**: https://github.com/Cithoreal/smart-highlighter-backend/issues
- **Email**: cithoreal@gmail.com

---

**📚 For comprehensive documentation, start with [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)**
