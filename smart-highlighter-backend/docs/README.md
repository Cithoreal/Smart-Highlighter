# Documentation Directory

This directory contains all project documentation organized for easy navigation.

---

## 📑 Quick Navigation

### Start Here
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Central hub with links to all docs
- **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** - Overview of all documentation

### For Developers
- **[AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md)** - Primary guide for GitHub Copilot agents
- **[PROJECT_DOCS.md](PROJECT_DOCS.md)** - Technical reference and API documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Command cheat sheet and debugging tips

### For Contributors
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development workflow and code standards
- **[TASKS.md](TASKS.md)** - Prioritized task list and roadmap

### Architecture
- **[RELATED_REPOSITORIES.md](RELATED_REPOSITORIES.md)** - How this backend relates to the extension and research repos

### Development Notes
- **[Dev Notes.md](Dev Notes.md)** - Ongoing development notes and decisions

---

## 📚 Documentation Types

### Agent Instructions (AI Development Guide)
**File:** `AGENT_INSTRUCTIONS.md` (~800 lines)

**Purpose:** Primary guide for GitHub Copilot agents working on this project

**Contents:**
- System architecture overview
- Code organization and patterns
- Common development tasks with examples
- Module-by-module breakdown
- Testing and debugging workflows
- Code style guidelines

**When to use:**
- Starting work on the project
- Understanding the codebase structure
- Implementing new features
- Following established patterns

---

### Project Documentation (Technical Reference)
**File:** `PROJECT_DOCS.md` (~1,000 lines)

**Purpose:** Comprehensive technical reference for all project components

**Contents:**
- Complete API endpoint reference
- Data models and schemas
- Configuration options
- Module documentation
- Troubleshooting guides
- Deployment instructions

**When to use:**
- Looking up API endpoint details
- Understanding data formats
- Configuring the application
- Deploying to production
- Debugging issues

---

### Tasks (Project Roadmap)
**File:** `TASKS.md` (~600 lines)

**Purpose:** Prioritized task list with implementation details

**Contents:**
- 🔴 Critical priority tasks (security)
- 🟡 High priority tasks (performance)
- 🟢 Medium priority tasks (features)
- 🔵 Low priority tasks (enhancements)
- Effort estimates and dependencies
- Acceptance criteria

**When to use:**
- Planning what to work on next
- Understanding project priorities
- Estimating work effort
- Checking task dependencies

---

### Quick Reference (Cheat Sheet)
**File:** `QUICK_REFERENCE.md` (~400 lines)

**Purpose:** Fast lookup for common commands and patterns

**Contents:**
- Server startup commands
- API testing examples (curl/httpie)
- Database queries
- Debugging commands
- Common code patterns
- Quick troubleshooting tips

**When to use:**
- Need a quick command
- Testing API endpoints
- Debugging common issues
- Looking for code examples

---

### Contributing Guide
**File:** `CONTRIBUTING.md` (~500 lines)

**Purpose:** Development workflow and contribution guidelines

**Contents:**
- Setting up development environment
- Code style and standards
- Git workflow and branching
- Pull request process
- Testing requirements
- Documentation standards

**When to use:**
- Making your first contribution
- Setting up development environment
- Following code standards
- Creating pull requests

---

### Documentation Index (Navigation Hub)
**File:** `DOCUMENTATION_INDEX.md` (~300 lines)

**Purpose:** Central navigation hub for all documentation

**Contents:**
- Quick links to all docs
- Use case → document mapping
- File organization structure
- Getting started paths
- Maintenance guidelines

**When to use:**
- Finding the right document
- Understanding doc structure
- Onboarding new developers
- Planning documentation updates

---

### Documentation Summary
**File:** `DOCUMENTATION_SUMMARY.md`

**Purpose:** High-level overview of all documentation

**Contents:**
- Summary of each document
- Key takeaways
- Usage recommendations
- Maintenance notes

**When to use:**
- Getting an overview of available docs
- Understanding what each doc covers
- Deciding which doc to read

---

### Related Repositories
**File:** `RELATED_REPOSITORIES.md` (~700 lines)

**Purpose:** Explains relationship to extension and research repos

**Contents:**
- smart-highlighter-firefox-extension integration
- Smart-Highlighter-Directed-Study research background
- Data flow diagrams
- Shared concepts and formats
- Development workflow across repos
- Getting started with all three repos

**When to use:**
- Understanding the full project ecosystem
- Working across multiple repositories
- Tracing data flow from extension to backend
- Understanding research methodology

---

### Dev Notes
**File:** `Dev Notes.md`

**Purpose:** Ongoing development notes and decisions

**Contents:**
- Current development status
- Design decisions
- Implementation notes
- Temporary reminders

**When to use:**
- Tracking in-progress work
- Recording design decisions
- Quick notes during development

---

## 🎯 Common Use Cases

### "I'm new to the project"
1. Start with [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
2. Read [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) (Architecture section)
3. Follow setup in [PROJECT_DOCS.md](PROJECT_DOCS.md) (Installation section)
4. Try commands from [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### "I want to add a feature"
1. Check [TASKS.md](TASKS.md) for priorities
2. Review [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) (Common Tasks section)
3. Follow [CONTRIBUTING.md](CONTRIBUTING.md) (Development Workflow)
4. Reference [PROJECT_DOCS.md](PROJECT_DOCS.md) (API Reference)

### "I need to fix a bug"
1. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) (Debugging section)
2. Review [PROJECT_DOCS.md](PROJECT_DOCS.md) (Troubleshooting section)
3. Reference [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) (Module details)

### "I'm working with the extension"
1. Read [RELATED_REPOSITORIES.md](RELATED_REPOSITORIES.md) (Extension section)
2. Review [PROJECT_DOCS.md](PROJECT_DOCS.md) (API Endpoints)
3. Check [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) (Data Flow)

### "I need to understand the research background"
1. Read [RELATED_REPOSITORIES.md](RELATED_REPOSITORIES.md) (Study section)
2. Review design decisions in [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md)
3. Check evaluation criteria in [TASKS.md](TASKS.md)

---

## 📁 File Organization

```
docs/
├── README.md                      ← You are here
├── DOCUMENTATION_INDEX.md         ← Start here (navigation hub)
├── DOCUMENTATION_SUMMARY.md       ← Quick overview
│
├── AGENT_INSTRUCTIONS.md          ← For AI agents/developers
├── PROJECT_DOCS.md                ← Technical reference
├── QUICK_REFERENCE.md             ← Command cheat sheet
│
├── CONTRIBUTING.md                ← For contributors
├── TASKS.md                       ← Roadmap and priorities
│
├── RELATED_REPOSITORIES.md        ← Ecosystem architecture
└── Dev Notes.md                   ← Development notes
```

---

## 🔄 Documentation Maintenance

### Keeping Docs Updated

**After adding a feature:**
- Update relevant sections in `PROJECT_DOCS.md`
- Add examples to `QUICK_REFERENCE.md`
- Update task status in `TASKS.md`
- Note in `Dev Notes.md`

**After fixing a bug:**
- Add troubleshooting entry to `PROJECT_DOCS.md`
- Update debugging tips in `QUICK_REFERENCE.md`
- Document the fix in `AGENT_INSTRUCTIONS.md` if it affects architecture

**After changing architecture:**
- Update diagrams in `AGENT_INSTRUCTIONS.md`
- Revise technical details in `PROJECT_DOCS.md`
- Update related repository docs in `RELATED_REPOSITORIES.md`
- Adjust priorities in `TASKS.md`

### Documentation Standards

- **Code examples:** Use triple backticks with language identifier
- **File paths:** Use backticks for inline code
- **Commands:** Show both the command and expected output
- **Warnings:** Use `⚠️` or `> **Warning:**` format
- **Cross-references:** Link to other docs using relative paths
- **Sections:** Use clear hierarchy with H1/H2/H3 headings

---

## 🤝 Contributing to Documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Documentation style guide
- How to add new docs
- Review process
- Documentation testing

---

## 📞 Getting Help

If you can't find what you're looking for:
1. Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for a complete list
2. Search across all docs (Ctrl+Shift+F in VS Code)
3. File an issue requesting documentation
4. Contact: cithoreal@gmail.com
