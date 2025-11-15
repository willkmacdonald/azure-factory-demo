# Factory Agent - Chat Feature Architecture Overview

## Executive Summary

The Factory Agent chat feature is a **full-stack AI-powered assistant** that integrates Azure OpenAI with a React frontend and FastAPI backend. The chat system enables users to ask natural language questions about factory operations and receive intelligent responses backed by real production data.

**Key Characteristics:**
- **Frontend**: React + TypeScript with Material-UI components
- **Backend**: FastAPI with async/await patterns
- **AI Integration**: Azure OpenAI with tool calling capabilities
- **Data Access**: 4 factory metrics tools (OEE, scrap, quality, downtime)
- **Security**: Input validation, sanitization, rate limiting, CORS protection
- **Architecture**: Clean separation between UI, API routes, and shared business logic

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERACTION LAYER                     │
│                    (React + Material-UI)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ChatPage (frontend/src/pages/ChatPage.tsx)              │   │
│  │  - Message display (user/assistant bubbles)              │   │
│  │  - Text input with submit handler                        │   │
│  │  - Suggested prompts                                     │   │
│  │  - Auto-scroll to latest messages                        │   │
│  │  - Error/loading state display                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  useChat Hook (frontend/src/hooks/useChat.ts)            │   │
│  │  - Message history state management                      │   │
│  │  - Loading/error state management                        │   │
│  │  - sendMessage() async function                          │   │
│  │  - clearMessages() and clearError() utilities            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
                    HTTP POST /api/chat
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                    API CLIENT LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  apiService (frontend/src/api/client.ts)                 │   │
│  │  - Axios instance with interceptors                      │   │
│  │  - Request logging                                       │   │
│  │  - Error formatting & handling                           │   │
│  │  - sendChatMessage(request: ChatRequest)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
           HTTP Request/Response (JSON)
                               │
┌──────────────────────────────┼────────────────────────────────────┐
│                       FASTAPI BACKEND                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI App (backend/src/api/main.py)                   │   │
│  │  - CORS middleware (allow React dev ports)               │   │
│  │  - Rate limiting middleware (slowapi)                    │   │
│  │  - Route registration                                    │   │
│  │  - Health check endpoint                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Chat Router (backend/src/api/routes/chat.py)            │   │
│  │  - POST /api/chat endpoint                               │   │
│  │  - Request validation (Pydantic)                         │   │
│  │  - Azure OpenAI client dependency injection              │   │
│  │  - Rate limiting: 10 req/min                             │   │
│  │  - Error handling (400, 500 responses)                   │   │
│  │  - Request logging with IDs                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Chat Service (shared/chat_service.py)                   │   │
│  │  - build_system_prompt(): Factory context injection      │   │
│  │  - get_chat_response(): Main AI logic                    │   │
│  │  - Tool calling loop (agentic pattern)                   │   │
│  │  - execute_tool(): Tool dispatch system                  │   │
│  │  - sanitize_user_input(): Prompt injection prevention    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                         ┌────┴────┐                              │
│                         │ Tools   │                              │
│                         └────┬────┘                              │
│                              │                                    │
│  ┌──────────────────┬───────────────────┬──────────────────┐    │
│  │                  │                   │                  │     │
│  ▼                  ▼                   ▼                  ▼     │
│ ┌────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐ │
│ │calculate│      │get_scrap│      │get_quality│      │get_downtime│
│ │  _oee  │      │_metrics │      │ _issues  │      │_analysis │
│ └────────┘      └─────────┘      └──────────┘      └──────────┘ │
│      │              │                  │                  │      │
│      └──────────────┴──────────────────┴──────────────────┘      │
│                         │                                        │
│      ┌──────────────────▼──────────────────┐                    │
│      │  Metrics Module (shared/metrics.py) │                    │
│      │  - Analytics calculations (async)   │                    │
│      │  - Date range filtering             │                    │
│      │  - Machine filtering                │                    │
│      └──────────────────┬──────────────────┘                    │
│                         │                                        │
│      ┌──────────────────▼──────────────────┐                    │
│      │   Data Layer (shared/data.py)       │                    │
│      │   - Load production data (async)    │                    │
│      │   - Parse JSON or Azure Blob        │                    │
│      │   - Cache in memory                 │                    │
│      └──────────────────┬──────────────────┘                    │
└───────────────────────┼──────────────────────────────────────────┘
                        │
     ┌──────────────────┴──────────────────┐
     │         DATA SOURCES                 │
     ├──────────────────────────────────────┤
     │  • Local: data/production.json       │
     │  • Cloud: Azure Blob Storage         │
     │  • Generated: Synthetic factory data │
     │  • 30 days × 4 machines              │
     └──────────────────────────────────────┘
```

---

## End-to-End Request/Response Flow

### 1. User Interaction (Frontend)

```typescript
// User types message and clicks Send button
User Input: "What is the current OEE performance?"

// ChatPage.tsx handles submission
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  await sendMessage(messageContent);  // Call useChat hook
};
```

### 2. Hook State Management

```typescript
// useChat hook in frontend/src/hooks/useChat.ts
const sendMessage = useCallback(async (content: string) => {
  // 1. Create user message with unique ID and timestamp
  const userMessage: Message = {
    id: `user-${Date.now()}`,
    role: 'user',
    content: content.trim(),
    timestamp: new Date(),
  };

  // 2. Add to local state immediately (optimistic update)
  setMessages((prev) => [...prev, userMessage]);
  setIsLoading(true);

  try {
    // 3. Build request with recent history (last 10 messages)
    const request: ChatRequest = {
      message: content.trim(),
      history: messages.slice(-10).map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
    };

    // 4. Call API
    const response = await apiService.sendChatMessage(request);

    // 5. Add assistant response to state
    const assistantMessage: Message = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: response.response,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMessage]);
  } catch (err) {
    setError(getErrorMessage(err));
  } finally {
    setIsLoading(false);
  }
});
```

### 3. API Client Call

```typescript
// frontend/src/api/client.ts
sendChatMessage: async (request: ChatRequest): Promise<ChatResponse> => {
  // Axios configured with:
  // - Base URL: http://localhost:8000 (dev) or production URL
  // - Timeout: 30 seconds
  // - Request interceptor logs in dev mode
  // - Response interceptor formats errors
  const response = await apiClient.post<ChatResponse>('/api/chat', request);
  return response.data;
};

// Request structure:
{
  "message": "What is the current OEE performance?",
  "history": [
    {"role": "user", "content": "What are the top issues?"},
    {"role": "assistant", "content": "Based on the data..."}
  ]
}
```

### 4. FastAPI Endpoint

```python
# backend/src/api/routes/chat.py
@router.post("/chat", response_model=ChatResponse)
@limiter.limit(RATE_LIMIT_CHAT)  # 10/minute
async def chat(
    request: Request,  # For rate limiting
    chat_request: ChatRequest,  # Auto-parsed from JSON
    client: AsyncAzureOpenAI = Depends(get_openai_client)
) -> ChatResponse:
    """
    Flow:
    1. Pydantic validates request:
       - message: 1-2000 chars, non-empty
       - history: max 50 messages, max 50K chars total
       - role values: must be 'user' or 'assistant'
    
    2. Build system prompt with factory context (async)
    
    3. Call chat service with:
       - Azure OpenAI client
       - System prompt
       - Conversation history
       - New user message
    
    4. Return response with updated history
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Chat request [request_id={request_id}]: {chat_request.message[:50]}...")

    try:
        # Build context-aware system prompt
        system_prompt = await build_system_prompt()

        # Call chat service (tool-calling loop happens here)
        response_text, updated_history_dicts = await get_chat_response(
            client=client,
            system_prompt=system_prompt,
            conversation_history=[msg.model_dump() for msg in chat_request.history],
            user_message=chat_request.message,
        )

        # Return response with updated history
        updated_history = [ChatMessage(**msg) for msg in updated_history_dicts]
        return ChatResponse(response=response_text, history=updated_history)

    except RuntimeError as e:
        # Data not available error (400)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Server error (500)
        # DEBUG=true shows full error, DEBUG=false hides details
        raise HTTPException(status_code=500, detail=error_detail)
```

### 5. Chat Service - Tool Calling Loop

```python
# shared/chat_service.py
async def get_chat_response(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    conversation_history: List[Dict[str, Any]],
    user_message: str,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Tool-calling agentic loop:
    
    Iteration 1:
    1. Sanitize user input (prevent prompt injection)
    2. Build messages list:
       [{"role": "system", "content": system_prompt},
        ...conversation_history...,
        {"role": "user", "content": "What is current OEE?"}]
    3. Call Azure OpenAI with tools:
       - TOOLS = [calculate_oee, get_scrap_metrics, ...]
       - tool_choice="auto" (AI decides when to use tools)
    4. AI response: requests calculate_oee tool
    5. Execute tool: calculate_oee(start_date, end_date)
    6. Add tool result to messages
    
    Iteration 2:
    7. Call Azure OpenAI again with tool result
    8. AI response: "Based on the data, OEE is 85%..."
    9. No tool calls = final answer
    
    Return: (response_text, new_history)
    """
    
    # Sanitization
    sanitized_message = sanitize_user_input(user_message)
    
    # Build messages
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": sanitized_message})
    
    # Tool calling loop
    iteration = 0
    while True:
        iteration += 1
        
        # Call Azure OpenAI
        response = await client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,  # "gpt-4"
            messages=messages,
            tools=TOOLS,  # 4 available tools
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        
        # If no tool calls, return final answer
        if not message.tool_calls:
            return message.content, messages[history_start_index:]
        
        # Execute tools
        messages.append(message.model_dump())
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            result = await execute_tool(tool_name, tool_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result),
            })
```

### 6. Tool Execution

```python
# Available tools in shared/chat_service.py
TOOLS = [
    {
        "name": "calculate_oee",
        "description": "Calculate Overall Equipment Effectiveness...",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string"},  # YYYY-MM-DD
                "end_date": {"type": "string"},
                "machine_name": {"type": "string", "optional": true}
            },
            "required": ["start_date", "end_date"]
        }
    },
    # ... 3 more tools: get_scrap_metrics, get_quality_issues, get_downtime_analysis
]

async def execute_tool(tool_name: str, tool_args: Dict[str, Any]):
    """Dispatch to appropriate tool implementation"""
    if tool_name == "calculate_oee":
        result = await calculate_oee(**tool_args)
    elif tool_name == "get_scrap_metrics":
        result = await get_scrap_metrics(**tool_args)
    # ... etc
    return result.model_dump() if hasattr(result, "model_dump") else result
```

### 7. Data Access

```python
# shared/metrics.py (async functions)
async def calculate_oee(
    start_date: str,
    end_date: str,
    machine_name: Optional[str] = None
) -> OEEMetrics:
    """
    1. Load production data (cached in memory)
    2. Filter by date range and machine (if specified)
    3. Calculate OEE = Availability × Performance × Quality
    4. Return OEEMetrics Pydantic model
    """
    data = await load_data_async()
    # ... calculations ...
    return OEEMetrics(
        oee=oee_percentage,
        availability=availability,
        performance=performance,
        quality=quality,
        total_parts=total_parts,
        good_parts=good_parts,
        scrap_parts=scrap_parts,
    )
```

### 8. Response Back to Frontend

```
Backend returns:
{
  "response": "Based on the data from 2024-10-15 to 2024-11-14, the overall OEE is 85.3%. This breaks down as: Availability: 92%, Performance: 88%, Quality: 94%. The best performing machine is CNC-001 with 89% OEE...",
  "history": [
    {"role": "user", "content": "What is the current OEE performance?"},
    {"role": "assistant", "content": "Based on the data..."}
  ]
}

Frontend:
1. useChat hook receives response
2. Updates state with assistant message
3. Clears loading state
4. ChatPage re-renders with new message
5. Auto-scroll to latest message
6. User sees response in chat bubble
```

---

## Key Files & Responsibilities

### Frontend Files

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/pages/ChatPage.tsx` | 410 | Main chat UI component, message display, input handling |
| `frontend/src/hooks/useChat.ts` | 150 | Custom hook for chat state and API communication |
| `frontend/src/api/client.ts` | 525 | Axios API client with interceptors and type safety |
| `frontend/src/types/api.ts` | 458 | TypeScript interfaces for all API responses |

### Backend Files

| File | Lines | Purpose |
|------|-------|---------|
| `backend/src/api/main.py` | 198 | FastAPI app, CORS, rate limiting, health check |
| `backend/src/api/routes/chat.py` | 265 | Chat endpoint, validation, logging, error handling |
| `shared/chat_service.py` | 368 | Tool-calling loop, system prompt, sanitization |
| `shared/config.py` | 42 | Environment variables, security settings |
| `shared/metrics.py` | 284 | Analytics calculations (async) |
| `shared/data.py` | 410 | Data loading from JSON or Azure Blob |

### Supporting Infrastructure

| Component | Purpose |
|-----------|---------|
| **Pydantic Models** | Type validation for requests/responses |
| **Rate Limiting** | 10 req/min per IP (slowapi) |
| **CORS Middleware** | Allow React dev ports (3000, 5173) |
| **Error Handling** | Consistent error format, DEBUG mode security |
| **Logging** | Structured logging with request IDs |
| **Input Validation** | Prompt injection prevention, history size limits |

---

## Security Features

### Frontend Security
- Type-safe API calls (TypeScript)
- Input validation before sending
- Error message sanitization
- No credentials stored in code

### Backend Security
- Pydantic model validation
- Prompt injection detection (chat_service.py)
- Rate limiting (10 req/min)
- CORS protection (specific origins)
- HTTP methods restricted (GET/POST only)
- Error messages differ by DEBUG mode
- Request ID tracking
- History size limits (50 messages, 50K chars)

### Azure OpenAI Integration
- API key in environment variables
- Endpoint validation
- Async client for concurrency
- Tool-calling safety (known tools only)

---

## Conversation History Management

### How History Works
1. **Frontend State**: Messages stored in React state with timestamps and IDs
2. **Frontend to Backend**: Last 10 messages sent with each request (context window)
3. **Backend Processing**: Full history + new message sent to Azure OpenAI
4. **Backend to Frontend**: Updated history with new user/assistant messages returned
5. **Frontend Update**: New messages added to state

### History Optimization
- **Limited Context**: Frontend sends last 10 messages (to save tokens)
- **Full History**: Backend receives full conversation
- **Stateless**: Backend doesn't store history (stateless design)
- **Size Limits**: 
  - Max 50 messages per conversation
  - Max 50K characters total
  - Individual messages: 1-2000 chars

### Example History Flow
```
User Message 1 → Assistant Response 1
User Message 2 → Assistant Response 2 (backend receives all 4 + this new message)
User Message 3 → Assistant Response 3 (backend receives all 6 + this new message)
```

---

## Data Flow Diagram - Request to Response

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Input (ChatPage)                                    │
│    "What is the current OEE performance?"                   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 2. useChat Hook                                             │
│    - Validates input (non-empty, trimmed)                   │
│    - Creates user message with ID/timestamp                 │
│    - Updates state immediately (optimistic)                 │
│    - Sets loading = true                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 3. API Client (Axios)                                       │
│    - POST /api/chat with ChatRequest                        │
│    - Message + last 10 history messages                     │
│    - Request interceptor logs                               │
│    - 30s timeout                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
    HTTP POST http://localhost:8000/api/chat
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 4. FastAPI Route Handler                                    │
│    - Pydantic validates ChatRequest                         │
│    - Rate limit check (10/min)                              │
│    - Create Azure OpenAI client                             │
│    - Generate request ID for tracking                       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 5. System Prompt Builder                                    │
│    - Load production data                                   │
│    - Extract date range                                     │
│    - Build context:                                         │
│      "You are a factory assistant for Demo Factory...       │
│       30 days of data (2024-10-15 to 2024-11-14)            │
│       4 machines: CNC-001, Laser-001, etc..."               │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 6. Chat Service - Tool Calling Loop                         │
│                                                             │
│    Build Messages:                                          │
│    [{"role": "system", "content": "You are..."},            │
│     ...history...,                                          │
│     {"role": "user", "content": "What is current OEE?"}]    │
│                                                             │
│    Call Azure OpenAI with TOOLS                             │
│    ↓ AI requests: calculate_oee tool                        │
│                                                             │
│    Execute: calculate_oee(                                  │
│      start_date="2024-10-15",                               │
│      end_date="2024-11-14",                                 │
│      machine_name=None)                                     │
│    ↓ Returns: OEEMetrics {...}                              │
│                                                             │
│    Add tool result to messages                              │
│    Call Azure OpenAI again                                  │
│    ↓ AI generates final response                            │
│    ↓ No more tool calls                                     │
│                                                             │
│    Return: (response_text, updated_history)                │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 7. Response to Frontend                                     │
│    HTTP 200 OK                                              │
│    {                                                        │
│      "response": "Based on the data, OEE is 85.3%...",      │
│      "history": [                                           │
│        {"role": "user", "content": "What is..."},           │
│        {"role": "assistant", "content": "Based on..."}      │
│      ]                                                      │
│    }                                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│ 8. Frontend Update                                          │
│    - useChat receives response                              │
│    - Add assistant message to state                         │
│    - Set loading = false                                    │
│    - Clear any errors                                       │
│    - ChatPage re-renders                                    │
│    - useEffect triggers auto-scroll                         │
│    - User sees response                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### Frontend to Backend
- **Endpoint**: `POST /api/chat`
- **Protocol**: JSON over HTTP
- **Async**: Frontend uses `async/await`, backend processes asynchronously
- **Error Handling**: Axios interceptor formats errors

### Backend Internal
- **FastAPI Routes**: All routes are async functions
- **Chat Service**: Async Azure OpenAI client
- **Tool Execution**: Async metric calculations
- **Data Access**: Async file/blob operations
- **No Blocking I/O**: Enables concurrent request handling

### Azure Services
- **Azure OpenAI**: 
  - Endpoint: `AZURE_ENDPOINT` env var
  - API Key: `AZURE_API_KEY` env var
  - Model: `AZURE_DEPLOYMENT_NAME` (default: "gpt-4")
  - API Version: `AZURE_API_VERSION` (2024-08-01-preview)
- **Azure Blob Storage** (optional):
  - Connection string for production data
  - Fallback to local JSON

---

## Configuration & Environment Variables

### Required
```env
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_API_KEY=your-api-key-here
```

### Optional (Defaults Provided)
```env
AZURE_DEPLOYMENT_NAME=gpt-4
AZURE_API_VERSION=2024-08-01-preview
FACTORY_NAME=Demo Factory
DEBUG=false
RATE_LIMIT_CHAT=10/minute
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
STORAGE_MODE=local
```

---

## Summary Table

| Aspect | Frontend | Backend |
|--------|----------|---------|
| **Framework** | React + TypeScript | FastAPI + Python |
| **UI Library** | Material-UI (MUI) | N/A |
| **HTTP Client** | Axios | N/A |
| **State Management** | React Hooks | Async/Await |
| **Chat Logic** | Display + Input | Tool Calling |
| **AI Integration** | N/A | Azure OpenAI |
| **Data Access** | API Calls | Metrics Calculations |
| **Error Handling** | Try/Catch | Try/Except + HTTPException |
| **Type Safety** | TypeScript | Pydantic |
| **Concurrency** | Event Loop | async/await |
| **Persistence** | Browser State | Memory + JSON/Blob |

---

## Testing & Debugging

### Frontend Testing
- Manual testing via browser
- Console logs for API requests
- React DevTools for state inspection

### Backend Testing
- Test files: `tests/test_chat_*.py`
- Run: `pytest tests/test_chat_api.py -v`
- Logging: Use request IDs to trace requests

### Local Development
```bash
# Terminal 1: Backend
cd backend
python -m src.api.main  # or: uvicorn src.api.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev  # Starts on http://localhost:5173

# Open http://localhost:5173 in browser
```

### Production Deployment
- Docker containers for both services
- Azure Container Apps for orchestration
- Environment variables for secrets
- CORS restricted to production domains
- DEBUG=false for security

---

## Key Insights & Patterns

### 1. Separation of Concerns
- **UI Layer**: React components handle display only
- **State Layer**: Hooks manage data flow
- **API Layer**: Axios abstracts HTTP
- **Route Layer**: FastAPI handles HTTP/validation
- **Service Layer**: Chat service handles AI logic
- **Data Layer**: Metrics/Data modules handle calculations

### 2. Async/Await Throughout Stack
- Frontend: `async/await` for API calls
- Backend: `async/await` for all I/O operations
- Enables concurrent request handling

### 3. Tool-Calling Pattern
- AI requests tools by name + parameters
- Backend executes trusted tools only
- Results fed back to AI for synthesis
- Enables AI to "think" step-by-step

### 4. Type Safety
- TypeScript on frontend prevents prop errors
- Pydantic on backend prevents invalid data
- Shared `types/api.ts` mirrors backend models

### 5. Security by Design
- Input validation at every layer
- Prompt injection detection
- Rate limiting to prevent abuse
- CORS to prevent unauthorized domains
- Error hiding in production (DEBUG=false)

---

## Common Use Cases

1. **Simple Query**: "What is OEE?" → 1 tool call → Response
2. **Filtered Query**: "OEE for CNC-001?" → 1 tool call with filter → Response
3. **Multi-Tool**: "Compare OEE and scrap rates" → 2 tool calls → Synthesis → Response
4. **Conversation**: User provides context in previous messages → AI uses context + tools

---

## Limitations & Future Improvements

### Current Limitations
- Stateless backend (history only in frontend)
- Memory-based data (scales to ~30 days × 4 machines)
- No user authentication
- Single Azure OpenAI model
- Limited to 4 tools

### Future Enhancements
- Persistent conversation history (database)
- Multi-user support with authentication
- More tools (cost analysis, predictive maintenance)
- Streaming responses for real-time feedback
- Voice interface integration
- Export chat history

---

## Quick Reference

**Chat Endpoint**: `POST /api/chat`
**Rate Limit**: 10 requests/minute per IP
**Request Timeout**: 30 seconds (frontend)
**Max History**: 50 messages, 50K characters
**Message Length**: 1-2000 characters
**Available Tools**: calculate_oee, get_scrap_metrics, get_quality_issues, get_downtime_analysis
**Response Time**: 2-5 seconds typical (depends on Azure OpenAI)

