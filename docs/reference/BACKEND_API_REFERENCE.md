# Factory Agent Backend API Structure

Complete documentation of all Pydantic models and FastAPI endpoints for TypeScript frontend development.

---

## Pydantic Models

### OEEMetrics
**File**: `/shared/models.py`

Overall Equipment Effectiveness metrics with component breakdown.

```python
class OEEMetrics(BaseModel):
    oee: float              # Overall Equipment Effectiveness (0-1)
    availability: float     # Availability component (0-1)
    performance: float      # Performance component (0-1)
    quality: float          # Quality component (0-1)
    total_parts: int        # Total parts produced
    good_parts: int         # Number of good parts
    scrap_parts: int        # Number of scrapped parts
```

**TypeScript Interface**:
```typescript
interface OEEMetrics {
  oee: number;           // 0-1 range
  availability: number;  // 0-1 range
  performance: number;   // 0-1 range
  quality: number;       // 0-1 range
  total_parts: number;
  good_parts: number;
  scrap_parts: number;
}
```

---

### ScrapMetrics
**File**: `/shared/models.py`

Scrap and waste metrics with optional machine breakdown.

```python
class ScrapMetrics(BaseModel):
    total_scrap: int                      # Total scrapped parts
    total_parts: int                      # Total parts produced
    scrap_rate: float                     # Scrap rate as percentage (0-100)
    scrap_by_machine: Optional[Dict[str, int]] = None  # Scrap breakdown by machine
```

**TypeScript Interface**:
```typescript
interface ScrapMetrics {
  total_scrap: number;
  total_parts: number;
  scrap_rate: number;  // 0-100 percentage
  scrap_by_machine?: Record<string, number> | null;
}
```

---

### QualityIssue
**File**: `/shared/models.py`

Individual quality issue record.

```python
class QualityIssue(BaseModel):
    type: str                    # Type of defect
    description: str             # Issue description
    parts_affected: int          # Number of affected parts
    severity: str                # Severity level: "Low", "Medium", "High"
    date: str                    # Date in YYYY-MM-DD format
    machine: str                 # Machine name
```

**TypeScript Interface**:
```typescript
interface QualityIssue {
  type: string;
  description: string;
  parts_affected: number;
  severity: "Low" | "Medium" | "High";
  date: string;    // YYYY-MM-DD
  machine: string;
}
```

---

### QualityIssues
**File**: `/shared/models.py`

Collection of quality issues with statistics.

```python
class QualityIssues(BaseModel):
    issues: List[QualityIssue]         # List of quality issues
    total_issues: int                  # Total number of issues
    total_parts_affected: int          # Total parts affected across all issues
    severity_breakdown: Dict[str, int] # Count of issues by severity ("Low", "Medium", "High")
```

**TypeScript Interface**:
```typescript
interface QualityIssues {
  issues: QualityIssue[];
  total_issues: number;
  total_parts_affected: number;
  severity_breakdown: Record<"Low" | "Medium" | "High", number>;
}
```

---

### DowntimeEvent (Internal)
**File**: `/shared/models.py`

Individual downtime event record (used internally in analysis).

```python
class DowntimeEvent(BaseModel):
    reason: str               # Downtime reason category
    description: str          # Event description
    duration_hours: float     # Duration in hours
```

---

### MajorDowntimeEvent
**File**: `/shared/models.py`

Major downtime event (greater than 2 hours).

```python
class MajorDowntimeEvent(BaseModel):
    date: str               # Date in YYYY-MM-DD format
    machine: str            # Machine name
    reason: str             # Downtime reason
    description: str        # Event description
    duration_hours: float   # Duration in hours (> 2)
```

**TypeScript Interface**:
```typescript
interface MajorDowntimeEvent {
  date: string;      // YYYY-MM-DD
  machine: string;
  reason: string;
  description: string;
  duration_hours: number;  // > 2 hours
}
```

---

### DowntimeAnalysis
**File**: `/shared/models.py`

Downtime analysis with events and breakdowns.

```python
class DowntimeAnalysis(BaseModel):
    total_downtime_hours: float                  # Total downtime hours
    downtime_by_reason: Dict[str, float]         # Downtime hours by reason
    major_events: List[MajorDowntimeEvent]       # Major events (>2 hours)
```

**TypeScript Interface**:
```typescript
interface DowntimeAnalysis {
  total_downtime_hours: number;
  downtime_by_reason: Record<string, number>;
  major_events: MajorDowntimeEvent[];
}
```

---

### ChatMessage
**File**: `/backend/src/api/routes/chat.py`

Individual chat message with role validation.

```python
class ChatMessage(BaseModel):
    role: str       # "user" or "assistant" only
    content: str    # 1-2000 characters
```

**Validation Rules**:
- `role`: Must be exactly "user" or "assistant"
- `content`: Non-empty, max 2000 characters

**TypeScript Interface**:
```typescript
interface ChatMessage {
  role: "user" | "assistant";
  content: string;  // 1-2000 chars
}
```

---

### ChatRequest
**File**: `/backend/src/api/routes/chat.py`

Request model for chat endpoint.

```python
class ChatRequest(BaseModel):
    message: str                        # User's message text (1-2000 chars)
    history: List[ChatMessage]          # Previous messages (max 50)
```

**Validation Rules**:
- `message`: 1-2000 characters
- `history`: Max 50 messages, total history size max 50,000 characters

**TypeScript Interface**:
```typescript
interface ChatRequest {
  message: string;        // 1-2000 chars
  history: ChatMessage[]; // max 50 items
}
```

---

### ChatResponse
**File**: `/backend/src/api/routes/chat.py`

Response model for chat endpoint.

```python
class ChatResponse(BaseModel):
    response: str                    # AI assistant's response
    history: List[ChatMessage]       # Updated conversation history
```

**TypeScript Interface**:
```typescript
interface ChatResponse {
  response: string;
  history: ChatMessage[];
}
```

---

### SetupRequest
**File**: `/backend/src/api/routes/data.py`

Request model for data generation endpoint.

```python
class SetupRequest(BaseModel):
    days: int  # 1-365 days, default: 30
```

**TypeScript Interface**:
```typescript
interface SetupRequest {
  days?: number;  // 1-365, default: 30
}
```

---

### SetupResponse
**File**: `/backend/src/api/routes/data.py`

Response model for data generation endpoint.

```python
class SetupResponse(BaseModel):
    message: str      # Success message
    days: int         # Number of days generated
    start_date: str   # ISO format date
    end_date: str     # ISO format date
    machines: int     # Number of machines
```

**Example Response**:
```json
{
  "message": "Data generated successfully",
  "days": 60,
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "machines": 4
}
```

**TypeScript Interface**:
```typescript
interface SetupResponse {
  message: string;
  days: number;
  start_date: string;  // ISO format
  end_date: string;    // ISO format
  machines: number;
}
```

---

### StatsResponse
**File**: `/backend/src/api/routes/data.py`

Response model for data statistics endpoint.

```python
class StatsResponse(BaseModel):
    exists: bool                        # Whether data file exists
    start_date: Optional[str] = None    # ISO format (if exists)
    end_date: Optional[str] = None      # ISO format (if exists)
    total_days: Optional[int] = None    # Total days with data
    total_machines: Optional[int] = None # Total machines
    total_records: Optional[int] = None  # Total production records
```

**Example Response (with data)**:
```json
{
  "exists": true,
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "total_days": 60,
  "total_machines": 4,
  "total_records": 240
}
```

**Example Response (no data)**:
```json
{
  "exists": false,
  "start_date": null,
  "end_date": null,
  "total_days": null,
  "total_machines": null,
  "total_records": null
}
```

**TypeScript Interface**:
```typescript
interface StatsResponse {
  exists: boolean;
  start_date?: string | null;    // ISO format
  end_date?: string | null;      // ISO format
  total_days?: number | null;
  total_machines?: number | null;
  total_records?: number | null;
}
```

---

### MachineInfo
**File**: `/backend/src/api/routes/data.py`

Machine information model.

```python
class MachineInfo(BaseModel):
    id: int            # Machine ID
    name: str          # Machine name (e.g., "CNC-001")
    type: str          # Machine type (e.g., "CNC Machining Center")
    ideal_cycle_time: int  # Cycle time in seconds
```

**Example**:
```json
{
  "id": 1,
  "name": "CNC-001",
  "type": "CNC Machining Center",
  "ideal_cycle_time": 45
}
```

**TypeScript Interface**:
```typescript
interface MachineInfo {
  id: number;
  name: string;
  type: string;
  ideal_cycle_time: number;  // seconds
}
```

---

### DateRangeResponse
**File**: `/backend/src/api/routes/data.py`

Response model for date range endpoint.

```python
class DateRangeResponse(BaseModel):
    start_date: str    # ISO format
    end_date: str      # ISO format
    total_days: int    # Total days with data
```

**Example**:
```json
{
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "total_days": 60
}
```

**TypeScript Interface**:
```typescript
interface DateRangeResponse {
  start_date: string;  // ISO format
  end_date: string;    // ISO format
  total_days: number;
}
```

---

## API Endpoints

### Metrics Endpoints

Base Path: `/api/metrics`

#### 1. GET /api/metrics/oee

Get Overall Equipment Effectiveness (OEE) metrics.

**Query Parameters**:
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `machine` (optional): Machine name filter

**Response Model**: `OEEMetrics | {"error": string}`

**Example Request**:
```
GET /api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31
GET /api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31&machine=CNC-001
```

**Example Response** (200 OK):
```json
{
  "oee": 0.645,
  "availability": 0.85,
  "performance": 0.95,
  "quality": 0.8,
  "total_parts": 5000,
  "good_parts": 4000,
  "scrap_parts": 1000
}
```

**Error Response** (200 OK with error dict):
```json
{
  "error": "No data for specified date range"
}
```

---

#### 2. GET /api/metrics/scrap

Get scrap and waste metrics.

**Query Parameters**:
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `machine` (optional): Machine name filter

**Response Model**: `ScrapMetrics | {"error": string}`

**Example Request**:
```
GET /api/metrics/scrap?start_date=2024-01-01&end_date=2024-01-31
GET /api/metrics/scrap?start_date=2024-01-01&end_date=2024-01-31&machine=Assembly-001
```

**Example Response** (200 OK):
```json
{
  "total_scrap": 150,
  "total_parts": 5000,
  "scrap_rate": 3.0,
  "scrap_by_machine": {
    "CNC-001": 50,
    "Assembly-001": 60,
    "Testing-001": 40
  }
}
```

---

#### 3. GET /api/metrics/quality

Get quality issues and defects.

**Query Parameters**:
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `severity` (optional): "Low", "Medium", or "High"
- `machine` (optional): Machine name filter

**Response Model**: `QualityIssues | {"error": string}`

**Example Requests**:
```
GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31
GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31&severity=High
GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31&machine=Testing-001&severity=Medium
```

**Example Response** (200 OK):
```json
{
  "issues": [
    {
      "type": "Dimensional Error",
      "description": "Parts exceed tolerance",
      "parts_affected": 25,
      "severity": "High",
      "date": "2024-01-15",
      "machine": "CNC-001"
    },
    {
      "type": "Surface Finish",
      "description": "Rough surface detected",
      "parts_affected": 10,
      "severity": "Low",
      "date": "2024-01-16",
      "machine": "Polishing-001"
    }
  ],
  "total_issues": 2,
  "total_parts_affected": 35,
  "severity_breakdown": {
    "High": 1,
    "Medium": 0,
    "Low": 1
  }
}
```

---

#### 4. GET /api/metrics/downtime

Get downtime analysis and major events.

**Query Parameters**:
- `start_date` (required): YYYY-MM-DD format
- `end_date` (required): YYYY-MM-DD format
- `machine` (optional): Machine name filter

**Response Model**: `DowntimeAnalysis | {"error": string}`

**Example Requests**:
```
GET /api/metrics/downtime?start_date=2024-01-01&end_date=2024-01-31
GET /api/metrics/downtime?start_date=2024-01-01&end_date=2024-01-31&machine=Packaging-001
```

**Example Response** (200 OK):
```json
{
  "total_downtime_hours": 24.5,
  "downtime_by_reason": {
    "Maintenance": 10.0,
    "Electrical Failure": 8.5,
    "Tool Change": 6.0
  },
  "major_events": [
    {
      "date": "2024-01-10",
      "machine": "CNC-001",
      "reason": "Electrical Failure",
      "description": "Motor control unit failure",
      "duration_hours": 4.5
    },
    {
      "date": "2024-01-22",
      "machine": "Assembly-001",
      "reason": "Maintenance",
      "description": "Preventive maintenance",
      "duration_hours": 3.0
    }
  ]
}
```

---

### Chat Endpoint

#### POST /api/chat

Chat endpoint with AI assistant using tool calling.

**Rate Limiting**: 10 requests/minute per IP (configurable via `RATE_LIMIT_CHAT`)

**Request Body**: `ChatRequest`

```json
{
  "message": "What is the current OEE for CNC-001?",
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hello! I'm your factory operations assistant. How can I help?"
    }
  ]
}
```

**Response Model**: `ChatResponse`

**Example Response** (200 OK):
```json
{
  "response": "Based on the data, CNC-001 has an OEE of 0.68 with an availability of 0.85, performance of 0.95, and quality of 0.80.",
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hello! I'm your factory operations assistant. How can I help?"
    },
    {
      "role": "user",
      "content": "What is the current OEE for CNC-001?"
    },
    {
      "role": "assistant",
      "content": "Based on the data, CNC-001 has an OEE of 0.68 with an availability of 0.85, performance of 0.95, and quality of 0.80."
    }
  ]
}
```

**Error Response** (429 Too Many Requests):
```json
{
  "detail": "429 Too Many Requests"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Chat processing failed: ..." (if DEBUG=true)
  // OR
  "detail": "An error occurred while processing your request. Please try again later." (if DEBUG=false)
}
```

---

### Data Management Endpoints

#### POST /api/setup

Generate synthetic production data.

**Rate Limiting**: 5 requests/minute per IP (configurable via `RATE_LIMIT_SETUP`)

**Request Body**: `SetupRequest` (optional)

```json
{
  "days": 60
}
```

**Response Model**: `SetupResponse`

**Example Response** (200 OK):
```json
{
  "message": "Data generated successfully",
  "days": 60,
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "machines": 4
}
```

**Error Response** (429 Too Many Requests):
```json
{
  "detail": "429 Too Many Requests"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "Failed to generate data: ..."
}
```

---

#### GET /api/stats

Get data statistics.

**Query Parameters**: None

**Response Model**: `StatsResponse`

**Example Request**:
```
GET /api/stats
```

**Example Response (with data)** (200 OK):
```json
{
  "exists": true,
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "total_days": 60,
  "total_machines": 4,
  "total_records": 240
}
```

**Example Response (no data)** (200 OK):
```json
{
  "exists": false,
  "start_date": null,
  "end_date": null,
  "total_days": null,
  "total_machines": null,
  "total_records": null
}
```

---

#### GET /api/machines

List available machines.

**Query Parameters**: None

**Response Model**: `List[MachineInfo]`

**Example Request**:
```
GET /api/machines
```

**Example Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "CNC-001",
    "type": "CNC Machining Center",
    "ideal_cycle_time": 45
  },
  {
    "id": 2,
    "name": "Assembly-001",
    "type": "Assembly Station",
    "ideal_cycle_time": 120
  },
  {
    "id": 3,
    "name": "Testing-001",
    "type": "Testing Station",
    "ideal_cycle_time": 60
  },
  {
    "id": 4,
    "name": "Packaging-001",
    "type": "Packaging Station",
    "ideal_cycle_time": 30
  }
]
```

---

#### GET /api/date-range

Get available data date range.

**Query Parameters**: None

**Response Model**: `DateRangeResponse`

**Example Request**:
```
GET /api/date-range
```

**Example Response** (200 OK):
```json
{
  "start_date": "2024-12-03T00:00:00",
  "end_date": "2025-01-31T00:00:00",
  "total_days": 60
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "No data available. Generate data using POST /api/setup"
}
```

---

### Health Check Endpoint

#### GET /health

Health check endpoint for service monitoring.

**Query Parameters**: None

**Response**: `{"status": "healthy"}`

**Example Request**:
```
GET /health
```

**Example Response** (200 OK):
```json
{
  "status": "healthy"
}
```

---

## Implementation Notes for Frontend

### TypeScript Complete Types File

Create `src/api/types/index.ts`:

```typescript
// ============================================================================
// METRICS MODELS
// ============================================================================

export interface OEEMetrics {
  oee: number;
  availability: number;
  performance: number;
  quality: number;
  total_parts: number;
  good_parts: number;
  scrap_parts: number;
}

export interface ScrapMetrics {
  total_scrap: number;
  total_parts: number;
  scrap_rate: number;
  scrap_by_machine?: Record<string, number> | null;
}

export interface QualityIssue {
  type: string;
  description: string;
  parts_affected: number;
  severity: "Low" | "Medium" | "High";
  date: string;
  machine: string;
}

export interface QualityIssues {
  issues: QualityIssue[];
  total_issues: number;
  total_parts_affected: number;
  severity_breakdown: Record<"Low" | "Medium" | "High", number>;
}

export interface MajorDowntimeEvent {
  date: string;
  machine: string;
  reason: string;
  description: string;
  duration_hours: number;
}

export interface DowntimeAnalysis {
  total_downtime_hours: number;
  downtime_by_reason: Record<string, number>;
  major_events: MajorDowntimeEvent[];
}

// ============================================================================
// CHAT MODELS
// ============================================================================

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  history: ChatMessage[];
}

// ============================================================================
// DATA MANAGEMENT MODELS
// ============================================================================

export interface SetupRequest {
  days?: number;
}

export interface SetupResponse {
  message: string;
  days: number;
  start_date: string;
  end_date: string;
  machines: number;
}

export interface StatsResponse {
  exists: boolean;
  start_date?: string | null;
  end_date?: string | null;
  total_days?: number | null;
  total_machines?: number | null;
  total_records?: number | null;
}

export interface MachineInfo {
  id: number;
  name: string;
  type: string;
  ideal_cycle_time: number;
}

export interface DateRangeResponse {
  start_date: string;
  end_date: string;
  total_days: number;
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

export interface HealthResponse {
  status: string;
}
```

### Date Format Notes

- All dates use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
- Query parameters for date ranges use `YYYY-MM-DD` format (without time)
- Backend automatically handles time portion in responses

### Error Handling

All endpoints that return business data may return an error dictionary:
```json
{
  "error": "No data for specified date range"
}
```

HTTP error responses use standard status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid input (chat history too large, etc.)
- `404 Not Found`: Data not found (date-range endpoint when no data exists)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Rate Limiting

- **Chat Endpoint**: 10 requests/minute per IP (configurable)
- **Setup Endpoint**: 5 requests/minute per IP (configurable)
- Other endpoints: No rate limiting

When rate limited, the API returns:
```
Status: 429 Too Many Requests
{
  "detail": "429 Too Many Requests"
}
```

### CORS Configuration

**Allowed Origins** (default, configurable via `ALLOWED_ORIGINS` env var):
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

**Allowed Methods**: GET, POST

**Allowed Headers**: Content-Type, Authorization, X-Requested-With

---

## Environment Variables

Required for API functionality:
- `AZURE_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_API_KEY`: Azure OpenAI API key
- `AZURE_DEPLOYMENT_NAME`: Model deployment name (default: "gpt-4")
- `AZURE_API_VERSION`: API version (default: "2024-08-01-preview")

Optional:
- `DEBUG`: Set to "true" for detailed error messages (development only)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `RATE_LIMIT_CHAT`: Rate limit for chat endpoint (default: "10/minute")
- `RATE_LIMIT_SETUP`: Rate limit for setup endpoint (default: "5/minute")
- `STORAGE_MODE`: "local" or "azure" (default: "local")

---

## Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Setup data
curl -X POST http://localhost:8000/api/setup \
  -H "Content-Type: application/json" \
  -d '{"days": 30}'

# Get stats
curl http://localhost:8000/api/stats

# Get machines
curl http://localhost:8000/api/machines

# Get date range
curl http://localhost:8000/api/date-range

# Get OEE metrics
curl "http://localhost:8000/api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31"

# Get scrap metrics
curl "http://localhost:8000/api/metrics/scrap?start_date=2024-01-01&end_date=2024-01-31"

# Get quality issues (with severity filter)
curl "http://localhost:8000/api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31&severity=High"

# Get downtime analysis
curl "http://localhost:8000/api/metrics/downtime?start_date=2024-01-01&end_date=2024-01-31"

# Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the OEE?",
    "history": []
  }'
```

---

## Notes for Frontend Integration

1. **Date Handling**: Always format dates as `YYYY-MM-DD` in query parameters, but responses use ISO format with time.

2. **Optional Fields**: Many response models have optional fields that may be `null`. Handle these gracefully in TypeScript.

3. **Severity Levels**: Quality issues use exactly three severity levels: "Low", "Medium", "High".

4. **Error Dictionary vs HTTP Error**: Some endpoints return error dictionaries in the 200 OK response body (check for `error` key) rather than HTTP error status codes.

5. **Rate Limiting**: Implement exponential backoff when receiving 429 responses.

6. **Machine Names**: Machine names are strings (e.g., "CNC-001") and are used as filter parameters in metric queries.

7. **Chat History Limits**: Keep conversation history under 50 messages and 50,000 total characters to avoid validation errors.

