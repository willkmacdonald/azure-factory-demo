# Factory Agent Chat Feature - Quick Visual Summary

## Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)                     │
│                                                                      │
│  ChatPage.tsx (410 lines)                                            │
│  ├── Message Display (bubbles, timestamps)                          │
│  ├── Input Field (textarea with Enter to submit)                    │
│  ├── Suggested Prompts (clickable chips)                            │
│  ├── Loading Indicator (spinner + "Thinking...")                    │
│  └── Error Alert (red banner)                                       │
│         ↓                                                             │
│  useChat.ts (150 lines) - Custom Hook                               │
│  ├── messages: Message[] (React state)                              │
│  ├── isLoading: boolean                                             │
│  ├── error: string | null                                           │
│  └── sendMessage(content) → API Call → State Update                 │
│         ↓                                                             │
│  apiService (client.ts) - Axios Client                              │
│  └── sendChatMessage(request: ChatRequest) → Promise<ChatResponse>  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ HTTP POST
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Python)                        │
│                                                                      │
│  FastAPI App (main.py)                                              │
│  ├── CORS Middleware (allow localhost:3000, 5173)                  │
│  ├── Rate Limiting (10 req/min per IP)                             │
│  └── Route: POST /api/chat                                          │
│                                                                      │
│  Chat Route Handler (chat.py - 265 lines)                           │
│  ├── Request Validation (Pydantic)                                  │
│  │   ├── message: str (1-2000 chars)                               │
│  │   └── history: ChatMessage[] (max 50, 50K chars)                │
│  ├── Generate Request ID (for tracking)                             │
│  ├── Build System Prompt (factory context)                          │
│  └── Call Chat Service → Return Response                            │
│                                                                      │
│  Chat Service (shared/chat_service.py - 368 lines)                 │
│  ├── sanitize_user_input() - Prevent prompt injection               │
│  ├── build_system_prompt() - Factory context                        │
│  └── get_chat_response() - Tool Calling Loop                        │
│      │                                                              │
│      ├─ Call Azure OpenAI API                                      │
│      ├─ If tool requested:                                         │
│      │   ├─ execute_tool(tool_name, args)                         │
│      │   └─ Add result to messages, continue loop                 │
│      └─ If no tools: Return response + updated history             │
│                                                                      │
│  Available Tools:                                                    │
│  ├─ calculate_oee(start_date, end_date, machine_name?)            │
│  ├─ get_scrap_metrics(start_date, end_date, machine_name?)        │
│  ├─ get_quality_issues(start_date, end_date, severity?, machine?) │
│  └─ get_downtime_analysis(start_date, end_date, machine_name?)    │
│       ↓                                                              │
│  Metrics Module (shared/metrics.py)                                 │
│  └─ Async calculations + Data filtering                             │
│       ↓                                                              │
│  Data Layer (shared/data.py)                                        │
│  └─ Load from JSON or Azure Blob Storage                            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Message Flow Timeline

```
TIME        FRONTEND                    BACKEND                         AI
───────────────────────────────────────────────────────────────────────
T0          User types query
            "What is OEE?"
                    │
T1                  ├─────► sendMessage()
                    │
T2                  ├─────► POST /api/chat
                    │       {"message": "What is OEE?", "history": [...]}
                    │
                                        ├─ Validate request
T3                                      ├─ Build system prompt
                                        ├─ Call get_chat_response()
                                        │
T4                                      ├─────────────────► generate(
                                        │                   messages=[...],
                                        │                   tools=[...],
                                        │                   tool_choice="auto"
                                        │                )
                    
T5                                      │◄─ Response: tool_call
                                        │   name: "calculate_oee"
                                        │   args: {start_date, end_date}
                                        │
T6                                      ├─ execute_tool()
                                        ├─ Add tool result
                                        │
T7                                      ├─────────────────► generate()
                                        │                   with tool result
                    
T8                                      │◄─ Response: final text
                                        │   "Based on the data, OEE is 85%..."
                                        │   (no tool_calls)
                                        │
T9                                      ├─ Return ChatResponse
                                        ├─ HTTP 200 OK
                    
T10         ◄─────────────────────────────
            Receive response
            
T11         Update state
            Add assistant message
            Re-render
            Auto-scroll
            
T12         User sees response
            in chat bubble
```

## Request/Response Example

### Request (Frontend → Backend)
```json
{
  "message": "What is the current OEE performance?",
  "history": [
    {
      "role": "user",
      "content": "How many machines do we have?"
    },
    {
      "role": "assistant",
      "content": "You have 4 machines: CNC-001, Laser-001, Press-001, and Assembly-001."
    }
  ]
}
```

### Response (Backend → Frontend)
```json
{
  "response": "Based on the data from 2024-10-15 to 2024-11-14, your overall OEE is 85.3%. The breakdown is: Availability: 92%, Performance: 88%, Quality: 94%. CNC-001 is your best performer at 89% OEE.",
  "history": [
    {
      "role": "user",
      "content": "How many machines do we have?"
    },
    {
      "role": "assistant",
      "content": "You have 4 machines: CNC-001, Laser-001, Press-001, and Assembly-001."
    },
    {
      "role": "user",
      "content": "What is the current OEE performance?"
    },
    {
      "role": "assistant",
      "content": "Based on the data from 2024-10-15 to 2024-11-14, your overall OEE is 85.3%..."
    }
  ]
}
```

## Key Statistics

| Metric | Value |
|--------|-------|
| **Frontend Components** | 4 main files |
| **Frontend Lines** | ~1,650 (React + TypeScript) |
| **Backend Routes** | 1 endpoint (/api/chat) |
| **Backend Lines** | 265 (chat.py) + 368 (chat_service.py) |
| **Available Tools** | 4 functions |
| **Rate Limit** | 10 requests/minute per IP |
| **Max History** | 50 messages, 50K characters |
| **Message Length** | 1-2000 characters |
| **Request Timeout** | 30 seconds |
| **Typical Response Time** | 2-5 seconds |

## File Ownership Map

| Frontend | Backend | Shared |
|----------|---------|--------|
| ChatPage.tsx | main.py | chat_service.py |
| useChat.ts | chat.py | config.py |
| client.ts | | metrics.py |
| types/api.ts | | data.py |

## Critical Paths

### Happy Path (1 Tool Call)
```
User Input
  ↓
useChat Hook
  ↓
API Call (POST /api/chat)
  ↓
FastAPI Route
  ↓
System Prompt Builder
  ↓
Chat Service
  ↓
Azure OpenAI (1st call) → Requests Tool
  ↓
Tool Execution (calculate_oee)
  ↓
Azure OpenAI (2nd call) → Final Response
  ↓
Return to Frontend
  ↓
Display in Chat
```

### Error Path
```
Any Step → Exception
  ↓
Caught in Chat Route Handler
  ↓
HTTPException(400 or 500)
  ↓
Sent to Frontend
  ↓
Axios Interceptor Formats Error
  ↓
useChat Sets Error State
  ↓
ChatPage Shows Error Alert
```

## Configuration

### Required Environment Variables
- `AZURE_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_API_KEY` - Azure OpenAI API key

### Optional (with Defaults)
- `AZURE_DEPLOYMENT_NAME` - Default: "gpt-4"
- `AZURE_API_VERSION` - Default: "2024-08-01-preview"
- `DEBUG` - Default: false
- `RATE_LIMIT_CHAT` - Default: "10/minute"
- `ALLOWED_ORIGINS` - Default: "http://localhost:3000,http://localhost:5173"

## Testing Checklist

Frontend:
- [ ] Message appears after sending
- [ ] Loading state shows during processing
- [ ] Auto-scroll works
- [ ] Suggested prompts work
- [ ] Clear chat button works
- [ ] Error message displays

Backend:
- [ ] POST /api/chat validates request
- [ ] Rate limit returns 429 after 10 requests
- [ ] Tool calling loop executes correctly
- [ ] CORS allows React dev ports
- [ ] Health check endpoint works

Integration:
- [ ] API timeout after 30 seconds
- [ ] Azure OpenAI API key works
- [ ] Message history persists in conversation
- [ ] Tool results are accurate

