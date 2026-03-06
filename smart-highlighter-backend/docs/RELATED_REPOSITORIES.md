# Related Repositories

This document explains how the **smart-highlighter-backend** project relates to two other repositories in the Smart Highlighter ecosystem.

---

## Repository Overview

The Smart Highlighter project consists of three interconnected repositories:

1. **smart-highlighter-backend** (This Repository) - Backend API server
2. **smart-highlighter-firefox-extension** - Browser extension for data collection
3. **Smart-Highlighter-Directed-Study** - Research, documentation, and evaluation framework

---

## 1. smart-highlighter-firefox-extension

**Repository:** `Cithoreal/smart-highlighter-firefox-extension`

### Purpose
Firefox browser extension that collects user browsing activity data and sends it to the backend server for processing and analysis.

### Relationship to Backend
- **Primary Data Source**: The extension is the main data collection client for this backend
- **API Communication**: Sends browsing events to this backend's `/api/log` endpoint via HTTPS
- **Authentication**: Uses `X-User-ID` header injection for user identification (matches backend's trusted header auth)

### Key Features
- **Event Collection**:
  - Click events (coordinates, element context, selections)
  - Mouseup events (text selections, caret positions)
  - Scroll metrics (max scroll %, reversals, intervals)
  - Time on page tracking
  - Idle detection (5-minute threshold)
  - User intent/rating manual input

- **Data Transmission**:
  - Real-time streaming to backend via `fetch()` POST requests
  - Three hosting modes: `local_http`, `local_https`, `remote`
  - Configurable endpoints:
    - Remote: `https://aiapi.cybernautics.net/api/log`
    - Local HTTPS: `https://127.0.0.1:8443/api/log`
    - Local HTTP: `http://127.0.0.1:8123/api/log`

- **User Interface**:
  - Popup for user_id, host selection, intent, page rating
  - Watermark badge: "⦿ AI Copilot Tracker Active" (red, fixed position)
  - Export functionality (JSON download)

### Architecture

```
┌─────────────────────────────────────┐
│   Firefox Browser                   │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  content.js (Content Script)  │ │
│  │  - Scroll tracking            │ │
│  │  - Click/mouseup listeners    │ │
│  │  - Watermark injection        │ │
│  └───────────┬───────────────────┘ │
│              │                      │
│  ┌───────────▼───────────────────┐ │
│  │  background.js (Service Wkr)  │ │
│  │  - Tab/window focus tracking  │ │
│  │  - Time on page calculation   │ │
│  │  - Idle state detection       │ │
│  │  - sendToServer() API calls   │ │
│  │  - X-User-ID header injection │ │
│  └───────────┬───────────────────┘ │
│              │                      │
│  ┌───────────▼───────────────────┐ │
│  │  popup.js (Extension UI)      │ │
│  │  - User ID input              │ │
│  │  - Host option selection      │ │
│  │  - Intent/rating input        │ │
│  │  - Export logs button         │ │
│  └───────────────────────────────┘ │
└─────────────┬───────────────────────┘
              │ POST /api/log
              │ Content-Type: application/json
              │ Body: { type, url, user_id, timestamp, ... }
              │
              ▼
┌─────────────────────────────────────┐
│  smart-highlighter-backend          │
│  (This Repository)                  │
│                                     │
│  fastapi_server.py                  │
│  └─ POST /api/log endpoint          │
│     └─ append_event() → NDJSON      │
└─────────────────────────────────────┘
```

### Event Types Sent to Backend

| Event Type | Description | Key Fields |
|------------|-------------|------------|
| `timeOnPage` | Duration spent on a page/tab | `url`, `title`, `timeSpentMs` |
| `scrollData` | Scroll behavior metrics | `maxScrollPercent`, `reversals`, `avgScrollIntervalMs` |
| `mouseDownEvent` | Click events with context | `coords`, `button`, `element`, `selection`, `caret` |
| `mouseupEvent` | Selection and caret tracking | `coords`, `element`, `selection`, `caret` |
| `userEntry` | Manual user input | `intent`, `rating` |

### Code Correspondence

**Extension Code** → **Backend Endpoint**
```javascript
// smart-highlighter-firefox-extension/background.js
async function sendToServer(data) {
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}
```

```python
# smart-highlighter-backend/fastapi_server.py
@app.post("/api/log")
async def log_event(request: Request):
    data = await request.json()
    user_id = request.headers.get("X-User-ID", "unknown")
    event_id = await append_event(user_id, data)
    return {"status": "ok", "event_id": event_id}
```

### Installation & Configuration

**Extension Setup:**
1. Install in Firefox (temporary or developer mode)
2. Set user_id in popup (e.g., "Chris", "Cat", "Eval")
3. Select hosting option (local_https, local_http, remote)
4. Browse normally - data streams automatically to backend

**Backend Compatibility:**
- Expects NDJSON storage format in `data/{user_id}/raw/web_tracking_log.ndjson`
- Uses `X-User-ID` header for user isolation
- No authentication beyond trusted header (security issue #1 in TASKS.md)

---

## 2. Smart-Highlighter-Directed-Study

**Repository:** `Cithoreal/Smart-Highlighter-Directed-Study`

### Purpose
Academic research repository containing:
- Project documentation and presentations
- LLM evaluation framework (LLM-as-Judge)
- Example browsing sessions with manual/automated analysis
- Development notes and assignment tracking
- Gradio data visualizer prototypes

### Relationship to Backend
- **Research Context**: Documents the academic/research origins of this project
- **Evaluation Data**: Contains sample browsing sessions used to develop/test backend processing
- **Prompt Development**: Houses prompt engineering experiments that led to `web_tracking_prompts.py`
- **Quality Benchmarking**: Provides evaluation rubrics used in `llm_judge/` module

### Key Components

#### Documentation
- **`Documentation/Documentation.md`**: User-facing product documentation
  - Quick start guide
  - Web extension installation
  - Backend self-hosting instructions
  - Code philosophy (3-step pipeline explanation)
  - LLM model cost/quality comparisons
  - Evaluation rubric (6 dimensions: Clarity, Detail, Comprehensiveness, Conciseness, Accuracy, Usefulness)

- **`Documentation/Evaluation/`**: Example reports and rubric comparisons
  - `manual_report.md`: Hand-written gold standard report
  - `LLM_Report_Output/`: Generated reports from GPT-4o, o4-mini, Claude Opus 4, Gemini 2.5 Pro
  - `LLM_Judge_Output/`: Quality scores for each report
  - `general_improvement_notes.md`: Issues observed during evaluation (e.g., dense info, missing ToC, linear time ordering)

#### Evaluation Examples
- **`evaluations/7/17/`**: Full browsing session examples with reports
  - Example: Audio processing pipeline research session
  - Example: AI-API reports endpoint investigation
  - Demonstrates ideal report structure: behavior analysis, activity traces, data insights

#### Development History
- **`docs/index.md`**: Assignment log with timestamps
  - 6/10/25: Read "Nobody Does Anything Until we have an Eval"
  - 6/17/25: Set up Flask (later switched to FastAPI), implement SSL
  - 6/30/25: Topic extraction, hourly/daily processing decisions
  - 7/3/25: Raw trace storage, small topic summaries, pipeline algorithms

#### Prototypes
- **`docs/gradio_data_visualizer/app.py`**: Early UI experiments
  - Exploration graph visualization
  - Feedback collection system
  - Interactive browsing session review

#### Prompt Evolution
- **`data/Prompts.md`**: Original prompt experiments
  - "do everything prompt": First attempt at topic extraction
  - Structured table format instructions (main topics, subtopics, behavior, data insights, ad traces, actionable steps)
  - Evolution visible → became `web_tracking_prompts.py` in backend

### Architectural Influence on Backend

**Research Findings → Backend Design Decisions**

1. **Chunking Strategy**
   - Study finding: "LLM processes data in chunks based on target number of words"
   - Backend implementation: `chunking.py` with token-aware sliding window
   - Cross-run state management for consistent chunking across sessions

2. **Multi-Stage Processing**
   - Study finding: "Event listings aren't useful in user report, probably add secondary processing layer"
   - Backend implementation: 3-stage pipeline (chunking → intermediate JSON → full summary)
   - Parallel LLM requests for topics, behavior, selections, etc.

3. **Model Comparison**
   - Study finding: Cost vs usefulness analysis (GPT-4o: $1.25-$3.75/day, GPT-4o-mini: $0.15-$0.45/day)
   - Backend implementation: `AI_API` enum supporting OpenAI, Anthropic, Google, HuggingFace
   - Configuration in `web_tracking_pipeline.py` (lines 37-42)

4. **Evaluation-First Approach**
   - Study principle: "Nobody Does Anything Until we have an Eval"
   - Backend implementation: `llm_judge/` module with 6-dimensional rubric
   - Comparison across 4+ LLM providers
   - Examples in `llm_judge/full_summary_rubric_examples.py`

5. **Report Structure**
   - Study finding: "Add a table of contents to the report and to each main topic"
   - Study finding: "Group topics by similarity and importance, not linear time"
   - Backend implementation: Structured JSON → Markdown with topic hierarchy
   - Jinja2 templates for consistent formatting

### Data Flow: Study → Backend → Extension

```
┌──────────────────────────────────────────────────────┐
│  Smart-Highlighter-Directed-Study (Research Phase)   │
│                                                       │
│  1. Manual data collection & analysis                │
│  2. Prompt engineering experiments                   │
│  3. Report quality evaluation                        │
│  4. Cost/performance benchmarking                    │
│                                                       │
│  Outputs:                                            │
│  - web_tracking_log.ndjson examples                  │
│  - Evaluation rubric (6 dimensions, 1-4 scale)       │
│  - Prompt templates (topics, behavior, selections)   │
│  - LLM model recommendations (Gemini 2.5 Pro best)   │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ Informs Design
                  ▼
┌──────────────────────────────────────────────────────┐
│  smart-highlighter-backend (This Repository)         │
│                                                       │
│  Implements:                                         │
│  - web_tracking_prompts.py (from study prompts)     │
│  - llm_judge/ (from study rubrics)                  │
│  - chunking.py (from study findings)                │
│  - web_tracking_pipeline.py (3-stage processing)    │
│                                                       │
│  Receives data from:                                 │
└─────────────────┬────────────────────────────────────┘
                  │
                  │ POST /api/log
                  ▼
┌──────────────────────────────────────────────────────┐
│  smart-highlighter-firefox-extension (Data Source)   │
│                                                       │
│  Collects:                                           │
│  - Browsing events (clicks, scrolls, selections)    │
│  - Time on page, idle detection                     │
│  - User intent/ratings                              │
│                                                       │
│  Sends to backend → Stored in NDJSON →              │
│  Processed by pipeline → Evaluated by judge          │
└──────────────────────────────────────────────────────┘
```

### Shared Data Formats

**NDJSON Event Structure** (standardized across all three repos):
```json
{
  "user_id": "Chris",
  "type": "mouseupEvent",
  "url": "https://example.com/page",
  "timestamp": "2025-01-17T23:55:37.432438",
  "coords": { "x": 450, "y": 320 },
  "element": { "tag": "P", "id": "content", "snippet": "Selected text..." },
  "selection": "This is the selected text",
  "caret": { "node": "TEXT_NODE", "offset": 42 }
}
```

**Report Structure** (from study evaluation examples → backend output):
```markdown
# User Interaction Report

## Summary
Overall session description, main topics identified, time range.

## Topic 1: [Topic Name]
### Description
What the user was researching/exploring.

### Selected Text
- "Quoted selections from the user" (event IDs)

### Behavior Analysis
Scroll patterns, time on page, click frequency, engagement level.

### Data Insights
Key findings, component selections, design decisions.

### Ad Traces
Sponsored content encountered (with utm_source tracking params).

### Actionable Steps
Next steps, recommendations, things to research/build/validate.

---

## Open Questions / Next Steps
Cross-topic recommendations, unresolved questions.
```

---

## Development Workflow

### Typical Development Flow Across Repositories

1. **Extension Development** (`smart-highlighter-firefox-extension`)
   - Add new event tracking (e.g., tab grouping, chat integration)
   - Test locally against `http://127.0.0.1:8123/api/log`
   - Update event type documentation

2. **Backend Reception** (`smart-highlighter-backend`)
   - Modify `/api/log` endpoint for new event types
   - Update `storage.py` if event schema changes
   - Add processing logic in `web_tracking_pipeline.py`

3. **Research Validation** (`Smart-Highlighter-Directed-Study`)
   - Export sample NDJSON from extension
   - Run backend processing with different prompts/models
   - Manually evaluate output quality
   - Update rubrics, add to evaluation examples
   - Document findings in `docs/index.md`

4. **Prompt Refinement** (Iterative across all repos)
   - Study: Identify report quality issues
   - Backend: Update `web_tracking_prompts.py`
   - Backend: Run LLM-as-Judge evaluation
   - Study: Document improvements in `Documentation/Evaluation/`

### Example: Adding "Tab Grouping" Feature

**1. Extension Implementation:**
```javascript
// smart-highlighter-firefox-extension/background.js
browser.tabs.onCreated.addListener(async (tab) => {
  const groupData = {
    type: "tabCreated",
    tabId: tab.id,
    openerTabId: tab.openerTabId,  // Track tab genealogy
    url: tab.url,
    timestamp: new Date().toISOString()
  };
  await sendToServer(groupData);
});
```

**2. Backend Storage:**
```python
# smart-highlighter-backend/storage.py
# No changes needed - append_event() handles any event type
```

**3. Backend Processing:**
```python
# smart-highlighter-backend/web_tracking_pipeline.py
# Add prompt for tab relationship analysis
TAB_GROUPING_PROMPT = """
Analyze tab creation events to identify browsing sessions.
Group tabs by:
- Common topic/goal
- Temporal proximity
- Opener tab relationships (openerTabId)
"""
```

**4. Research Validation:**
```markdown
<!-- Smart-Highlighter-Directed-Study/evaluations/tab-grouping-test.md -->
# Tab Grouping Evaluation

## Test Session
- Opened 3 tabs about Python async/await
- Opened 2 tabs about FastAPI
- LLM correctly identified 2 separate topics

## Quality Scores
- Clarity: 4/4
- Accuracy: 4/4
- Usefulness: 3/4 (suggested improvements: add tab count, time span)
```

---

## Repository Interdependencies

### File/Code Mapping

| Concept | Extension | Backend | Study |
|---------|-----------|---------|-------|
| **Event Format** | `background.js` (JSON structure) | `storage.py` (NDJSON append) | `docs/code/2025-06-04-Flask-side-by-side.md` (design notes) |
| **User Isolation** | `X-User-ID` header injection | `data/{user_id}/` directories | `Documentation/Documentation.md` (user management) |
| **Scroll Metrics** | `content.js` (scroll listeners) | Not processed yet | `evaluations/` (behavior analysis examples) |
| **Text Selections** | `mouseupEvent` in `content.js` | `web_tracking_prompts.py` (selection analysis) | `Evaluation/manual_report.md` (selection analysis examples) |
| **Topic Extraction** | N/A (data collection only) | `summarizer.py` + LLM API calls | `data/Prompts.md` (prompt evolution) |
| **Quality Evaluation** | N/A | `llm_judge/` module | `Evaluation/LLM_Judge_Output/` (examples) |
| **Report Generation** | N/A | `web_tracking_pipeline.py` | `Evaluation/LLM_Report_Output/` (gold standards) |
| **Model Selection** | N/A | `llm_apis/llm_request.py` | `Documentation.md` (cost/quality comparisons) |

### Shared Concepts

**1. User Identity**
- Extension: `user_id` input field in popup, stored in local storage
- Backend: `X-User-ID` header parsing, directory isolation
- Study: Example users "Chris", "Cat", "Eval", "Myth", "showcase"

**2. Event Taxonomy**
- Extension: Defines event types (timeOnPage, scrollData, mouseupEvent, etc.)
- Backend: Processes all types uniformly, stores in NDJSON
- Study: Documents expected event structures and usage patterns

**3. Processing Pipeline**
- Extension: Real-time streaming (no local processing)
- Backend: 3-stage (chunking → intermediate → full summary)
- Study: Describes ideal pipeline stages, evaluation criteria

**4. Report Quality**
- Extension: N/A (data collection only)
- Backend: Implements LLM-as-Judge rubric scoring
- Study: Defines 6-dimensional rubric, provides comparison examples

---

## Future Integration Plans

Based on documentation in all three repositories:

### From Study Repository (`docs/index.md`, `presentation.md`)

**Planned Features:**
1. **Automated Tab Grouping**
   - Extension: Suggest tab groups based on content
   - Backend: LLM analysis of tab relationships
   - Study: Evaluation criteria for grouping accuracy

2. **Side-by-Side Chat Interface**
   - Extension: Embed webpage + chat in split view
   - Backend: RAG access to browsing history
   - Study: Prototype in `docs/gradio_data_visualizer/app.py`

3. **Dynamic Prompt Selection**
   - Extension: User preferences (checkboxes in popup)
   - Backend: Prompt variation based on user config
   - Study: A/B testing framework for prompt quality

4. **Feedback Loop**
   - Extension: Rating buttons for each report
   - Backend: Store feedback, retrain prompts
   - Study: Aggregate feedback analysis, model tuning

5. **Knowledge Graph Visualization**
   - Extension: N/A (viewing only)
   - Backend: Topic relationship extraction
   - Study: Obsidian/InfraNodus-style graph rendering

### Migration to Firefox Add-ons Store
- Extension: Production-ready release (remove dev warnings)
- Backend: Public API hosting with authentication
- Study: User onboarding documentation, privacy policy

---

## Getting Started with All Three Repositories

### 1. Clone All Repositories
```bash
# Backend (this repository)
git clone https://github.com/Cithoreal/smart-highlighter-backend.git
cd smart-highlighter-backend

# Firefox Extension
cd ..
git clone https://github.com/Cithoreal/smart-highlighter-firefox-extension.git

# Research/Documentation
cd ..
git clone https://github.com/Cithoreal/Smart-Highlighter-Directed-Study.git
```

### 2. Start Backend Server
```bash
cd smart-highlighter-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python fastapi_server.py
# Server starts at https://127.0.0.1:8443 or http://127.0.0.1:8123
```

### 3. Install Firefox Extension
```bash
cd smart-highlighter-firefox-extension
# In Firefox:
# 1. Type about:debugging in address bar
# 2. Click "This Firefox"
# 3. Click "Load Temporary Add-on"
# 4. Select manifest.json from the extension directory
```

### 4. Configure Extension
1. Click extension icon in Firefox toolbar
2. Enter user_id (e.g., "YourName")
3. Select "Local HTTPS" or "Local HTTP" hosting
4. (Optional) Enter intent/rating for current page
5. Click "Save"

### 5. Verify Data Flow
```bash
# Backend should show logs like:
# INFO: Event logged: user_id=YourName, type=timeOnPage, event_id=1738123456.789

# Check NDJSON file
cat data/YourName/raw/web_tracking_log.ndjson
```

### 6. Run Processing Pipeline
```bash
# Manual trigger via API
curl -X POST http://127.0.0.1:8123/api/run_pipeline \
  -H "X-User-ID: YourName"

# Or use scheduler (runs hourly/daily automatically)
# Check data/YourName/summaries/full/ for output
```

### 7. Review Research Examples
```bash
cd Smart-Highlighter-Directed-Study/Documentation/Evaluation

# Compare LLM outputs
cat LLM_Report_Output/gemini-2.5-pro.md
cat LLM_Report_Output/GPT-4o.md
cat LLM_Report_Output/o4_mini.md

# Review evaluation scores
cat LLM_Judge_Output/Gemini.md
```

---

## Contributing

When contributing to the Smart Highlighter ecosystem:

1. **Extension Changes**: Test against local backend first
2. **Backend Changes**: Update corresponding study documentation
3. **Study Changes**: Validate with real backend/extension data
4. **Cross-Repo Impact**: Document in all affected READMEs

See `CONTRIBUTING.md` in this repository for detailed guidelines.

---

## Additional Resources

- **Backend API Reference**: `PROJECT_DOCS.md` (this repository)
- **Extension Usage**: `README.md` in `smart-highlighter-firefox-extension`
- **Research Background**: `Documentation/Documentation.md` in `Smart-Highlighter-Directed-Study`
- **Evaluation Methodology**: `Documentation/Evaluation/general_improvement_notes.md` in study repo
- **Development History**: `docs/index.md` in study repo

---

## Contact

For questions about:
- **Backend architecture**: See `AGENT_INSTRUCTIONS.md` (this repository)
- **Extension development**: File issue in extension repository
- **Research methodology**: See study repository documentation
- **General inquiries**: cithoreal@gmail.com
