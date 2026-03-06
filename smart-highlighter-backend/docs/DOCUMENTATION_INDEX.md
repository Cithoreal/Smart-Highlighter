# Documentation Index

Welcome to the Smart Highlighter Backend documentation! This project uses AI to analyze web browsing behavior and generate insightful summaries.

## 📚 Documentation Structure

This documentation is designed for **GitHub Copilot agents** and **human developers** to quickly understand and work with the codebase.

### Start Here 👋

**New to the project?**
1. Read `README.md` (project setup)
2. Read `AGENT_INSTRUCTIONS.md` (architecture & patterns)
3. Read `QUICK_REFERENCE.md` (common commands)

**Ready to contribute?**
1. Read `CONTRIBUTING.md` (development workflow)
2. Check `TASKS.md` (what needs work)
3. Reference `PROJECT_DOCS.md` (technical details)

---

## 📖 Documentation Files

### Core Documentation

#### **AGENT_INSTRUCTIONS.md** ⭐ Start here for AI agents
- **Purpose**: Complete guide for GitHub Copilot and AI assistants
- **Contents**:
  - Project overview and architecture
  - Component descriptions and interactions
  - Design patterns and conventions
  - Common development tasks
  - Code style guidelines
  - Known issues and workarounds
- **Best for**: Understanding how the system works

#### **PROJECT_DOCS.md** 📋 Technical reference
- **Purpose**: Detailed technical documentation
- **Contents**:
  - System architecture diagrams
  - Complete API reference
  - Data models and schemas
  - File structure
  - Configuration guide
  - Deployment instructions
  - Troubleshooting guide
- **Best for**: Looking up specific technical details

#### **TASKS.md** ✅ Work tracking
- **Purpose**: Project roadmap and task tracking
- **Contents**:
  - Prioritized task list
  - Status tracking (Not Started, In Progress, Completed)
  - Effort estimates
  - Dependencies
  - Completed work history
- **Best for**: Finding what needs to be done

#### **QUICK_REFERENCE.md** ⚡ Cheat sheet
- **Purpose**: Quick lookup for common operations
- **Contents**:
  - Common commands
  - API endpoint examples
  - Configuration snippets
  - Debugging tips
  - Useful code snippets
- **Best for**: Quick answers without reading full docs

#### **CONTRIBUTING.md** 🤝 Contributor guide
- **Purpose**: How to contribute to the project
- **Contents**:
  - Development workflow
  - Code standards
  - Testing procedures
  - Documentation requirements
  - Pull request process
- **Best for**: Making changes to the codebase

---

## 🎯 Documentation Use Cases

### "I want to understand how this project works"
→ Read: `AGENT_INSTRUCTIONS.md` → `PROJECT_DOCS.md`

### "I need to set up the project locally"
→ Read: `README.md` → `.env.example` → `QUICK_REFERENCE.md`

### "I want to add a new feature"
→ Read: `CONTRIBUTING.md` → `AGENT_INSTRUCTIONS.md` (Common Tasks) → `TASKS.md`

### "I'm getting an error"
→ Read: `QUICK_REFERENCE.md` (Common Errors) → `PROJECT_DOCS.md` (Troubleshooting)

### "What should I work on next?"
→ Read: `TASKS.md` (Priority sections)

### "How do I make an API call?"
→ Read: `QUICK_REFERENCE.md` (API Endpoints) → `PROJECT_DOCS.md` (API Reference)

### "I need to understand the data model"
→ Read: `PROJECT_DOCS.md` (Data Models) → Look at example files in `data/`

### "I want to add a new LLM provider"
→ Read: `AGENT_INSTRUCTIONS.md` (Common Tasks → Adding LLM Provider)

---

## 📁 Additional Files

### **README.md** 🏠 Project homepage
- Quick overview
- Setup instructions
- Basic usage
- Links to detailed docs

### **Dev Notes.md** 📝 Research journal
- Original development notes
- Research goals and findings
- Experiment results
- Historical context

### **.env.example** 🔐 Configuration template
- Environment variable reference
- API key placeholders
- Configuration options
- Setup instructions

---

## 🔄 Documentation Workflow

### When to Update Documentation

| Action | Update Files |
|--------|--------------|
| Add new endpoint | `PROJECT_DOCS.md` (API Reference), `QUICK_REFERENCE.md` |
| Add new feature | `README.md`, `AGENT_INSTRUCTIONS.md`, `PROJECT_DOCS.md` |
| Fix a bug | Commit message (detailed) |
| Add new config | `PROJECT_DOCS.md`, `.env.example` |
| Complete a task | `TASKS.md` (mark completed) |
| Add new prompt | `AGENT_INSTRUCTIONS.md` |
| Change architecture | `AGENT_INSTRUCTIONS.md`, `PROJECT_DOCS.md` |
| Breaking change | `README.md` (Breaking Changes section) |

### Documentation Standards

#### ✅ Good Documentation
- Clear, concise language
- Examples for complex concepts
- Updated when code changes
- Organized with headers and tables
- Cross-references between files

#### ❌ Poor Documentation
- Outdated information
- No examples
- Vague descriptions
- Duplicated content
- No structure

---

## 🛠️ Maintaining Documentation

### Regular Review
- [ ] **Monthly**: Review all docs for accuracy
- [ ] **Before each release**: Update version-specific info
- [ ] **After major changes**: Update architecture diagrams
- [ ] **When tasks complete**: Move from TASKS.md to completed section

### Documentation Checklist (for contributors)
- [ ] Updated relevant documentation files
- [ ] Added examples where helpful
- [ ] Cross-referenced related sections
- [ ] Tested all code snippets
- [ ] Fixed any typos or formatting issues
- [ ] Removed outdated information

---

## 🤖 For AI Agents (GitHub Copilot)

### Primary Reference: `AGENT_INSTRUCTIONS.md`
This file contains:
- Complete system architecture
- Coding patterns and conventions
- Common tasks with examples
- Known issues and workarounds
- Quick reference to key functions

### Secondary References:
- `PROJECT_DOCS.md` - Technical specifications
- `TASKS.md` - Current priorities and TODOs
- `QUICK_REFERENCE.md` - Command cheat sheet

### Best Practices for AI Agents:
1. **Always read** `AGENT_INSTRUCTIONS.md` first
2. **Check** `TASKS.md` for related ongoing work
3. **Follow** code style guidelines in `AGENT_INSTRUCTIONS.md`
4. **Reference** existing code examples
5. **Update** documentation when making changes
6. **Test** changes before considering task complete
7. **Cross-reference** between documentation files for consistency

---

## 📊 Documentation Statistics

| File | Lines | Purpose | Update Frequency |
|------|-------|---------|------------------|
| AGENT_INSTRUCTIONS.md | ~800 | AI agent guide | Weekly |
| PROJECT_DOCS.md | ~1000 | Technical reference | Monthly |
| TASKS.md | ~600 | Task tracking | Daily/Weekly |
| QUICK_REFERENCE.md | ~400 | Cheat sheet | Monthly |
| CONTRIBUTING.md | ~500 | Contributor guide | Quarterly |
| README.md | ~100 | Project overview | Quarterly |

---

## 🔗 External Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **GitHub Repository**: https://github.com/Cithoreal/smart-highlighter-backend
- **LLM Provider Docs**:
  - OpenAI: https://platform.openai.com/docs
  - Anthropic: https://docs.anthropic.com/
  - Google AI: https://ai.google.dev/docs

---

## 📞 Support

**Questions about documentation?**
1. Check if answer is in existing docs
2. Open a GitHub Issue with "docs:" prefix
3. Tag as "documentation" label

**Found an error in docs?**
1. Fork the repository
2. Fix the documentation
3. Submit a pull request

**Want to improve docs?**
- See `CONTRIBUTING.md` for guidelines
- Focus on clarity and examples
- Test all code snippets before submitting

---

## 🎉 Quick Links

- [Main README](README.md)
- [Agent Instructions](AGENT_INSTRUCTIONS.md)
- [Project Documentation](PROJECT_DOCS.md)
- [Task List](TASKS.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Environment Template](.env.example)

---

**Last Updated**: 2025-01-15  
**Maintained By**: Project Contributors  
**License**: See LICENSE file
