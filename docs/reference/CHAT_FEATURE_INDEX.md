# Factory Agent Chat Feature - Documentation Index

This directory contains comprehensive documentation about the Factory Agent chat feature architecture, implementation, and integration.

## Documents

### 1. CHAT_ARCHITECTURE.md (35 KB, 782 lines)
**Comprehensive architectural deep-dive** - Start here for complete understanding

Contents:
- Executive summary of the full-stack chat system
- Detailed architecture overview with ASCII diagrams
- End-to-end request/response flow with code examples
- Tool-calling agentic pattern explanation
- Conversation history management
- Key files and responsibilities
- Security features (frontend, backend, Azure integration)
- Integration points and configuration
- Testing & debugging guidance
- Key insights and design patterns
- Limitations and future improvements

**Best for:**
- Understanding the complete system architecture
- Implementing new chat features
- Security reviews
- Debugging complex issues
- Training new developers

### 2. CHAT_QUICK_SUMMARY.md (11 KB, 268 lines)
**Quick visual reference** - Use this for rapid lookups and team discussions

Contents:
- Component map with file structures
- Message flow timeline (T0-T12)
- Request/response JSON examples
- Key statistics table
- File ownership map
- Critical paths (happy path + error path)
- Configuration reference
- Testing checklist

**Best for:**
- Quick reference during development
- Team meetings and discussions
- Onboarding new team members
- Verification before deployment
- Bug triage

## Quick Navigation

### By Role

**Frontend Developer**
1. Start: CHAT_QUICK_SUMMARY.md (Component Map section)
2. Deep dive: CHAT_ARCHITECTURE.md (Frontend Security section)
3. Reference: frontend/src/pages/ChatPage.tsx, hooks/useChat.ts

**Backend Developer**
1. Start: CHAT_QUICK_SUMMARY.md (Message Flow Timeline)
2. Deep dive: CHAT_ARCHITECTURE.md (Tool Calling Loop section)
3. Reference: backend/src/api/routes/chat.py, shared/chat_service.py

**DevOps/Infrastructure**
1. Start: CHAT_QUICK_SUMMARY.md (Configuration section)
2. Deep dive: CHAT_ARCHITECTURE.md (Configuration & Environment Variables)
3. Deployment: Docker, Azure Container Apps, CI/CD

**Project Manager**
1. Start: CHAT_QUICK_SUMMARY.md (Key Statistics)
2. Timeline: Message Flow Timeline section
3. Test: Testing Checklist section

**QA/Tester**
1. Start: CHAT_QUICK_SUMMARY.md (Testing Checklist)
2. Details: CHAT_ARCHITECTURE.md (Testing & Debugging section)
3. Run: pytest tests/test_chat_api.py

### By Task

**I need to understand the chat flow**
→ CHAT_QUICK_SUMMARY.md - Message Flow Timeline section

**I need to add a new tool**
→ CHAT_ARCHITECTURE.md - Tool Execution section + Tool-Calling Pattern

**I need to debug an API error**
→ CHAT_QUICK_SUMMARY.md - Error Path section

**I need to configure the API**
→ CHAT_QUICK_SUMMARY.md - Configuration section

**I need security details**
→ CHAT_ARCHITECTURE.md - Security Features section

**I need to test the chat**
→ CHAT_QUICK_SUMMARY.md - Testing Checklist

**I need to deploy to production**
→ CHAT_ARCHITECTURE.md - Configuration & Environment Variables section

## Key Metrics at a Glance

| Metric | Value |
|--------|-------|
| Frontend | React + TypeScript (4 files, ~1,650 lines) |
| Backend | FastAPI + Python (6 files, 1,000+ lines) |
| Endpoint | POST /api/chat |
| Rate Limit | 10 requests/minute per IP |
| Timeout | 30 seconds |
| Tools | 4 available (OEE, scrap, quality, downtime) |
| History | Max 50 messages, 50K characters |
| Response Time | 2-5 seconds typical |

## File Locations

### Frontend
```
frontend/src/
├── pages/ChatPage.tsx          # Main chat UI component
├── hooks/useChat.ts             # Custom hook for chat state
├── api/client.ts                # Axios HTTP client
└── types/api.ts                 # TypeScript interfaces
```

### Backend
```
backend/src/api/
├── main.py                      # FastAPI app setup
└── routes/chat.py               # Chat endpoint

shared/
├── chat_service.py              # Tool-calling logic
├── metrics.py                   # Analytics calculations
├── data.py                      # Data access layer
└── config.py                    # Configuration
```

## Integration Points

1. **Frontend → Backend**: HTTP POST to `/api/chat` (JSON)
2. **Backend → Azure**: AsyncAzureOpenAI API calls with tools
3. **Tools → Data**: Async metrics calculations from production.json

## Configuration

### Required Environment Variables
```env
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_KEY=your-api-key-here
```

### Optional (defaults provided)
```env
AZURE_DEPLOYMENT_NAME=gpt-4
AZURE_API_VERSION=2024-08-01-preview
DEBUG=false
RATE_LIMIT_CHAT=10/minute
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Quick Start for New Developers

1. **Read**: CHAT_QUICK_SUMMARY.md (entire document) - 20 minutes
2. **Review**: Relevant source files based on your role - 30 minutes
3. **Try**: Run locally and test with sample prompts - 15 minutes
4. **Reference**: CHAT_ARCHITECTURE.md for detailed questions

Total: ~65 minutes to productive chat development

## Testing

### Manual Testing
```bash
# Terminal 1: Backend
cd backend && python -m src.api.main

# Terminal 2: Frontend
cd frontend && npm run dev

# Open http://localhost:5173 and test chat
```

### Automated Testing
```bash
# Backend tests
pytest tests/test_chat_api.py -v

# With coverage
pytest tests/test_chat_api.py --cov=backend --cov-report=html
```

## Troubleshooting

| Issue | Document Section | Solution |
|-------|------------------|----------|
| Chat not responding | CHAT_ARCHITECTURE.md - Debugging section | Check AZURE_ENDPOINT, AZURE_API_KEY |
| Rate limit hit | CHAT_QUICK_SUMMARY.md - Configuration | Wait 1 minute or increase RATE_LIMIT_CHAT |
| Frontend error | CHAT_ARCHITECTURE.md - Frontend Security | Check browser console, API logs |
| Tool not executing | CHAT_ARCHITECTURE.md - Tool Execution | Verify data/production.json exists |
| CORS error | CHAT_QUICK_SUMMARY.md - Configuration | Add origin to ALLOWED_ORIGINS |

## Related Documents

- `/docs/ARCHITECTURE.md` - Overall system architecture
- `/docs/BACKEND_API_REFERENCE.md` - All API endpoints
- `/README.md` - Project overview
- `/.claude/CLAUDE.md` - Project guidelines and patterns

## Contributing

When making changes to the chat feature:

1. Update CHAT_QUICK_SUMMARY.md for quick changes
2. Update CHAT_ARCHITECTURE.md for detailed changes
3. Update relevant source file docstrings
4. Update tests if logic changes
5. Verify configuration still works

## Document Maintenance

These documents are living documentation. Update them when:
- Adding new tools
- Changing API contracts
- Modifying security policies
- Adding/removing features
- Updating configuration

Last Updated: November 14, 2025
Maintainer: Will MacDonald

