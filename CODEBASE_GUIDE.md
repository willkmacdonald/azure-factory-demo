# Factory Agent Codebase Guide

## Overview

This directory contains **three comprehensive documentation files** created to help you understand and work with the Factory Agent codebase:

1. **ARCHITECTURE.md** - Complete technical architecture
2. **QUICK_REFERENCE.md** - Quick lookup for common tasks
3. **EXPLORATION_SUMMARY.md** - High-level project assessment

---

## Which Document Should I Read?

### If you want to... → Read this document

| Goal | Document | Key Sections |
|------|----------|--------------|
| **Get started quickly** | QUICK_REFERENCE | Setup, Run API, Common Tasks |
| **Understand the full architecture** | ARCHITECTURE | All sections |
| **See big picture overview** | EXPLORATION_SUMMARY | Executive Summary, Current State |
| **Find where to add code** | QUICK_REFERENCE | File Locations section |
| **Understand async/await patterns** | ARCHITECTURE | Async/Sync Patterns section |
| **Learn about data models** | ARCHITECTURE | Data Models section |
| **See all 9 endpoints** | EXPLORATION_SUMMARY | REST API Endpoints section |
| **Know what files to modify** | QUICK_REFERENCE | Key Files table |
| **Understand error handling** | ARCHITECTURE | Error Handling section |
| **Configure the app** | QUICK_REFERENCE | Environment Variables section |

---

## Quick Navigation

### ARCHITECTURE.md (18 KB)
**Best for**: Understanding the complete system architecture and all technical details

**Sections**:
- Project Overview
- Directory Structure
- Key Components (6 major components)
  - Configuration Management
  - Data Models
  - Data Access Layer
  - Metrics Calculations
  - Chat Service
  - FastAPI Application
- Routes Implementation (metrics, data, chat)
- Async/Sync Patterns
- Key Architecture Patterns (5 patterns)
- Dependencies
- Common Issues & Considerations
- File Dependencies
- To Run FastAPI Locally
- Key Files for FastAPI Implementation

### QUICK_REFERENCE.md (8 KB)
**Best for**: Quick lookup and common development tasks

**Sections**:
- Project Structure at a Glance
- Key Files to Know
- Common Tasks
  - Add New API Endpoint
  - Add Calculation Function
  - Add Data Model
- Development Workflow
- Important Patterns
- File Locations
- Rate Limiting
- CORS Configuration
- Logging
- Testing
- Environment Variables
- Troubleshooting

### EXPLORATION_SUMMARY.md (13 KB)
**Best for**: Getting a high-level overview and current state assessment

**Sections**:
- Executive Summary
- Current Backend Architecture
  - REST API Endpoints (9 total)
  - Technology Stack
- Code Organization
- Key Components Deep Dive
- Key Patterns & Best Practices
- Current State Assessment
- Files for FastAPI Implementation
- Quick Start Guide
- Summary

---

## Project Structure (Quick Reference)

```
factory-agent/
├── backend/src/api/              # FastAPI application
│   ├── main.py                   # App initialization (177 lines)
│   └── routes/
│       ├── metrics.py            # Metric endpoints (129 lines)
│       ├── data.py               # Data endpoints (381 lines)
│       └── chat.py               # Chat endpoint (212 lines)
│
├── shared/                        # Shared business logic
│   ├── config.py                 # Configuration (33 lines)
│   ├── models.py                 # Pydantic models (86 lines)
│   ├── data.py                   # Data access (283 lines)
│   ├── metrics.py                # Calculations (285 lines)
│   └── chat_service.py           # LLM integration (368 lines)
│
├── data/
│   └── production.json           # Synthetic test data (generated)
│
├── tests/                         # Test suite
│   ├── test_config.py
│   └── test_chat_service.py
│
└── [DOCUMENTATION FILES]
    ├── ARCHITECTURE.md           # This guide (18 KB)
    ├── QUICK_REFERENCE.md        # Quick lookup (8 KB)
    ├── EXPLORATION_SUMMARY.md    # Overview (13 KB)
    └── CODEBASE_GUIDE.md         # This file
```

---

## 9 REST API Endpoints

### Metrics Endpoints (Read-only, GET)
- `GET /api/metrics/oee` - Overall Equipment Effectiveness
- `GET /api/metrics/scrap` - Scrap metrics
- `GET /api/metrics/quality` - Quality issues
- `GET /api/metrics/downtime` - Downtime analysis

### Data Management (POST + GET)
- `POST /api/setup` - Generate synthetic data (rate-limited)
- `GET /api/stats` - Data statistics
- `GET /api/machines` - List machines
- `GET /api/date-range` - Data date range

### Chat/AI (POST)
- `POST /api/chat` - AI assistant with tool calling (rate-limited)

### Health Check
- `GET /health` - Service health status

---

## Essential Patterns

### 1. All FastAPI Routes Must Be Async
```python
@router.get("/api/endpoint")
async def endpoint() -> Model:          # async def
    data = await load_data_async()      # await all I/O
    return data
```

### 2. Complete Type Hints Required
```python
async def function(param: str) -> ReturnType:  # All params and return typed
    pass
```

### 3. Error Handling Pattern
```python
try:
    result = await operation()
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Failed: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Error")
```

### 4. Pydantic Models for Validation
```python
class Request(BaseModel):
    field: str = Field(max_length=100, description="...")
```

---

## Getting Started

### 1. Read This Guide (You're doing it!)

### 2. Understand the Big Picture
- Read: **EXPLORATION_SUMMARY.md** Executive Summary section
- Time: 5 minutes

### 3. Learn the Architecture
- Read: **ARCHITECTURE.md** Key Components section (focus on 2-3 components)
- Time: 20 minutes

### 4. Setup and Run
- Follow: **QUICK_REFERENCE.md** Development Workflow section
- Time: 10 minutes

### 5. Try Common Tasks
- Reference: **QUICK_REFERENCE.md** Common Tasks section
- Time: As needed

---

## Most Important Files

| Priority | File | What | Lines |
|----------|------|------|-------|
| 1 | backend/src/api/main.py | App setup | 177 |
| 2 | shared/config.py | Config | 33 |
| 3 | shared/models.py | Data models | 86 |
| 4 | backend/src/api/routes/metrics.py | Metric endpoints | 129 |
| 5 | shared/data.py | Data access | 283 |

These 5 files (~708 lines) handle 80% of the functionality.

---

## Common Questions Answered

### Where do I add a new endpoint?
See **QUICK_REFERENCE.md** → "Add New API Endpoint"

### How do I add a new metric calculation?
See **QUICK_REFERENCE.md** → "Add Calculation Function"

### What's the data format?
See **ARCHITECTURE.md** → "Data Access Layer" section

### How does tool calling work?
See **ARCHITECTURE.md** → "Chat Service" section

### What are all the async/sync rules?
See **ARCHITECTURE.md** → "Async/Sync Patterns" section

### How do I run the API locally?
See **QUICK_REFERENCE.md** → "Development Workflow" → "Run API"

### What's the error handling pattern?
See **ARCHITECTURE.md** → "Key Architecture Patterns" → "Error Handling"

### How do I add rate limiting?
See **QUICK_REFERENCE.md** → "Rate Limiting" section

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | FastAPI 0.104+ |
| Server | Uvicorn 0.24+ |
| Data Validation | Pydantic 2.0+ |
| LLM Integration | Azure OpenAI SDK |
| Async File I/O | aiofiles 25.0+ |
| Rate Limiting | SlowAPI |
| Configuration | python-dotenv |

---

## Key Metrics to Calculate

The system can calculate 4 factory metrics:

1. **OEE** (Overall Equipment Effectiveness)
   - Formula: Availability × Performance × Quality
   - Components: Uptime, defect rate, speed

2. **Scrap Metrics**
   - Scrap count, scrap rate, breakdown by machine

3. **Quality Issues**
   - Defects, severity levels, affected parts

4. **Downtime Analysis**
   - Downtime hours, reasons, major events (>2 hours)

All calculations support:
- Date range filtering
- Optional machine filtering

---

## Security Features

1. **CORS** - Whitelist origins (configurable)
2. **Rate Limiting** - IP-based request throttling
3. **Input Validation** - Pydantic models
4. **Input Sanitization** - Prevent prompt injection (chat)
5. **Configuration Security** - Environment variables (no hardcoding)
6. **Error Messages** - Generic for unknown errors, detailed for known

---

## Development Hints

### Python Version
- Requires Python 3.10+
- Tested on Python 3.10, 3.11, 3.12

### Dependencies
- Install: `pip install -r requirements.txt` or `pip install -e ".[dev]"`
- Main deps: fastapi, uvicorn, pydantic, openai, aiofiles, python-dotenv

### Code Quality
- Type hints: Required for all functions
- Format: Black (88 char line length)
- Tests: pytest with coverage

### Documentation
- Docstrings: Google style
- Inline comments: Only for "why", not "what"
- Auto-docs: Available at /docs endpoint

---

## Next Steps

### For API Development
1. Read QUICK_REFERENCE.md "Add New API Endpoint"
2. Follow the async/await pattern
3. Use Pydantic models for validation
4. Add proper error handling

### For Frontend Development
1. Read EXPLORATION_SUMMARY.md "REST API Endpoints"
2. Use http://localhost:8000/docs for endpoint details
3. All endpoints return JSON
4. Chat endpoint requires conversation history

### For Extended Functionality
1. Read ARCHITECTURE.md "Key Components"
2. Understand the tool calling pattern
3. Add new tools to shared/chat_service.py
4. Extend metrics in shared/metrics.py

---

## Getting Help

1. **Can't find something?** → Check QUICK_REFERENCE.md "File Locations" table
2. **Error with async?** → Read ARCHITECTURE.md "Async/Sync Patterns"
3. **Adding new feature?** → Read QUICK_REFERENCE.md "Common Tasks"
4. **Understanding module?** → Read ARCHITECTURE.md "Key Components"
5. **Quick lookup?** → Use QUICK_REFERENCE.md as index

---

## Document Statistics

| Document | Size | Focus | Best For |
|----------|------|-------|----------|
| ARCHITECTURE.md | 18 KB | Technical depth | Learning the system |
| QUICK_REFERENCE.md | 8 KB | Practical lookup | Development tasks |
| EXPLORATION_SUMMARY.md | 13 KB | High-level overview | Understanding scope |
| CODEBASE_GUIDE.md | 6 KB | This index | Navigating docs |

**Total: 45 KB of documentation for a 2KB line project**

---

## Final Thoughts

This codebase is:
- **Well-structured**: Clear separation of concerns
- **Production-ready**: Security, error handling, validation
- **Extensible**: Easy to add new endpoints and calculations
- **Type-safe**: Complete type hints throughout
- **Well-documented**: Comprehensive docstrings and comments

You're ready to:
- Build a React/Vue/Angular frontend
- Deploy to Azure Container Apps
- Integrate Azure AD authentication
- Add database persistence
- Extend with new metrics

Start with QUICK_REFERENCE.md for immediate productivity, refer to ARCHITECTURE.md when you need deep understanding.

---

**Last Updated**: November 2, 2025
**Project**: Factory Agent (Demo Application for Industry 4.0)
**Status**: Production-ready FastAPI backend with 9 endpoints
