# Pydantic Models Reference

---
**Last Updated**: November 14, 2025
**Status**: Current (reflects models through PR12, supply chain models pending in PR13-14)
**Related Docs**: See `CODEBASE_OVERVIEW.md` for general project structure
---

## Table of Contents
1. [Quick Start - Copy-Paste Templates](#quick-start)
2. [All Existing Models](#all-existing-models)
3. [Model Architecture & Patterns](#model-architecture)
4. [Naming Conventions](#naming-conventions)
5. [Common Mistakes to Avoid](#common-mistakes)

---

## Quick Start - Copy-Paste Templates {#quick-start}

### For Shared Models (used by multiple routes)

**Location**: `shared/models.py`

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class YourModel(BaseModel):
    """One-sentence description of what this model represents."""

    # Required fields (no default) - ALL parameters must have type hints (CLAUDE.md requirement)
    field_name: str = Field(description="What this field represents")
    count: int = Field(ge=0, description="Must be non-negative")

    # Optional fields
    notes: Optional[str] = Field(default=None, description="Optional notes")

    # Collections with proper defaults (CRITICAL: use default_factory)
    items: List[dict] = Field(default_factory=list, description="List of items")
    breakdown: Dict[str, int] = Field(default_factory=dict, description="Count by category")

    # Custom validation - note: type hints required on parameters AND return value
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """Validate field_name constraint."""
        if not v.strip():
            raise ValueError("field_name cannot be empty")
        return v.strip()
```

### For API Request Models

**Location**: `api/routes/yourroute.py` (route-specific) or `shared/models.py` (reusable)

```python
class YourOperationRequest(BaseModel):
    """Request model for POST /api/your-operation endpoint."""

    parameter1: str = Field(description="Required input")
    parameter2: Optional[int] = Field(default=None, ge=0, description="Optional parameter")

    # CRITICAL: Validate inputs to prevent injection attacks
    @field_validator('parameter1')
    @classmethod
    def validate_parameter1(cls, v: str) -> str:
        """Sanitize user input."""
        # Add sanitization logic here
        return v.strip()
```

### For API Response Models

**Location**: `api/routes/yourroute.py` (route-specific) or `shared/models.py` (reusable)

```python
class YourOperationResponse(BaseModel):
    """Response model for POST /api/your-operation endpoint."""

    # Use descriptive field names
    result: str = Field(description="Operation result")
    metadata: Dict[str, any] = Field(default_factory=dict, description="Additional info")

    # IMPORTANT: Response models should NOT have custom validators
    # Validators are for input sanitization, not output formatting
```

---

## All Existing Models {#all-existing-models}

### Summary Table

| Model Name | Location | Purpose | Key Fields | Request/Response/Data |
|------------|----------|---------|------------|----------------------|
| **Production Metrics** | | | | |
| `OEEMetrics` | `shared/models.py` | OEE calculations | oee, availability, performance, quality | Data |
| `ScrapMetrics` | `shared/models.py` | Waste analysis | total_scrap, scrap_rate, breakdown | Data |
| **Quality Management** | | | | |
| `QualityIssue` | `shared/models.py` | Single quality event | type, severity, parts_affected | Data |
| `QualityIssues` | `shared/models.py` | Collection of issues + stats | issues (List), severity_breakdown | Data |
| **Machine Management** | | | | |
| `MachineStatus` | `shared/models.py` | Machine state snapshot | name, status, shift, current_part | Data |
| `MachineCollection` | `shared/models.py` | All machines + stats | machines (List), status_breakdown | Data |
| **Alerts** | | | | |
| `Alert` | `shared/models.py` | Single alert event | machine, type, severity, timestamp | Data |
| **AI Chat** | | | | |
| `ChatRequest` | `api/routes/chat.py` | User message to AI | message (str) | Request |
| `ChatResponse` | `api/routes/chat.py` | AI response | response (str), context (optional) | Response |
| `ConversationHistory` | `api/routes/chat.py` | Message history validation | conversation_id, messages (List) | Request |
| **Data Access** | | | | |
| `ProductionData` | `shared/models.py` | Complete factory snapshot | machines, metrics, alerts, system_info | Data |
| `MachineData` | `shared/models.py` | Single machine state | All machine fields | Data |
| `SystemInfo` | `shared/models.py` | Factory metadata | last_updated, shift, data_mode | Data |
| **Health** | | | | |
| `HealthResponse` | `api/main.py` | API health status | status, timestamp, version | Response |
| **Dashboard** | | | | |
| `DashboardData` | `api/routes/dashboard.py` | Full dashboard payload | production_data, oee, scrap, issues | Response |

**Total**: 15 models (7 shared domain, 3 chat, 5 data models)

### Detailed Model Descriptions

#### Production Metrics

**OEEMetrics** - Overall Equipment Effectiveness calculations
```python
class OEEMetrics(BaseModel):
    oee: float = Field(ge=0, le=1, description="Overall Equipment Effectiveness (0-1)")
    availability: float = Field(ge=0, le=1, description="Machine uptime ratio")
    performance: float = Field(ge=0, le=1, description="Speed efficiency")
    quality: float = Field(ge=0, le=1, description="Good parts ratio")
    total_parts: int = Field(ge=0, description="Total parts produced")
    good_parts: int = Field(ge=0, description="Parts meeting quality standards")
    scrap_parts: int = Field(ge=0, description="Defective parts")
```
- **Purpose**: Track manufacturing efficiency using industry-standard OEE formula
- **Usage**: `src/metrics.py:calculate_oee_metrics()` → API response
- **Validation**: All ratios constrained to [0-1], counts must be non-negative
- **Pattern**: Data model (no Request/Response suffix)

**ScrapMetrics** - Waste and defect analysis
```python
class ScrapMetrics(BaseModel):
    total_scrap: int = Field(ge=0, description="Total scrap parts")
    total_parts: int = Field(ge=0, description="Total parts produced")
    scrap_rate: float = Field(ge=0, le=100, description="Scrap percentage")
    scrap_by_machine: Optional[Dict[str, int]] = Field(default=None, description="Per-machine breakdown")
```
- **Purpose**: Analyze waste patterns and identify problem machines
- **Usage**: `src/metrics.py:calculate_scrap_metrics()` → Dashboard display
- **Validation**: Scrap rate is percentage [0-100], not ratio [0-1]
- **Pattern**: Optional breakdown for detailed analysis

#### Quality Management

**QualityIssue** - Singular quality event
```python
class QualityIssue(BaseModel):
    type: str = Field(description="Issue category")
    description: str = Field(description="Detailed description")
    parts_affected: int = Field(ge=0, description="Number of affected parts")
    severity: str = Field(description="Low, Medium, or High")
    date: str = Field(description="ISO date format YYYY-MM-DD")
    machine: str = Field(description="Machine identifier")
```
- **Purpose**: Represent a single quality problem incident
- **Usage**: Component of `QualityIssues` collection
- **Validation**: Severity should be validated to enum values (Low/Medium/High)
- **Pattern**: Singular item in Item/Collection pattern

**QualityIssues** - Collection with aggregated statistics
```python
class QualityIssues(BaseModel):
    issues: List[QualityIssue] = Field(default_factory=list, description="All quality issues")
    total_issues: int = Field(ge=0, description="Count of issues")
    total_parts_affected: int = Field(ge=0, description="Sum of affected parts")
    severity_breakdown: Dict[str, int] = Field(default_factory=dict, description="Issues per severity")
```
- **Purpose**: Aggregate quality data with analytics
- **Usage**: `src/metrics.py:get_quality_issues()` → Dashboard charts
- **Validation**: Uses `default_factory` for mutable defaults (CRITICAL pattern)
- **Pattern**: Collection with computed statistics (total_*, *_breakdown)

#### Machine Management

**MachineStatus** - Current state of a single machine
```python
class MachineStatus(BaseModel):
    name: str = Field(description="Machine identifier")
    status: str = Field(description="running, idle, maintenance, down")
    shift: str = Field(description="Current shift (morning/evening/night)")
    current_part: Optional[str] = Field(default=None, description="Part being manufactured")
    parts_today: int = Field(ge=0, description="Parts produced today")
    target_output: int = Field(ge=0, description="Daily production target")
    utilization: float = Field(ge=0, le=100, description="Utilization percentage")
```
- **Purpose**: Real-time machine state snapshot
- **Usage**: Component of `MachineCollection`, displayed in machine grid
- **Validation**: Utilization is percentage [0-100]
- **Pattern**: Singular entity with optional fields for unavailable data

**MachineCollection** - All machines with summary statistics
```python
class MachineCollection(BaseModel):
    machines: List[MachineStatus] = Field(default_factory=list, description="All machines")
    status_breakdown: Dict[str, int] = Field(default_factory=dict, description="Machines per status")
```
- **Purpose**: Full factory floor view with aggregated status
- **Usage**: Dashboard overview, machine page
- **Pattern**: Collection pattern (List + Dict breakdown)

#### AI Chat Models

**ChatRequest** - User message input
```python
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000, description="User's question or command")

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """Prevent injection attacks."""
        return v.strip()
```
- **Purpose**: Validate user input to AI chat endpoint
- **Usage**: `POST /api/chat` request body
- **Validation**: Length limits prevent abuse, sanitization prevents injection
- **Pattern**: Request model with security-focused validation

**ChatResponse** - AI-generated response
```python
class ChatResponse(BaseModel):
    response: str = Field(description="AI-generated answer")
    context: Optional[str] = Field(default=None, description="Additional context")
```
- **Purpose**: Structure AI responses consistently
- **Usage**: `POST /api/chat` response body
- **Pattern**: Response model (no validators)

**ConversationHistory** - Chat history validation
```python
class ConversationHistory(BaseModel):
    conversation_id: str = Field(description="Unique conversation identifier")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Chat history")

    @field_validator('messages')
    @classmethod
    def validate_message_structure(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Ensure each message has role and content."""
        for msg in v:
            if 'role' not in msg or 'content' not in msg:
                raise ValueError("Each message must have 'role' and 'content'")
        return v
```
- **Purpose**: Validate conversation history before passing to Azure OpenAI
- **Usage**: `POST /api/chat` with conversation_id parameter
- **Validation**: Ensures messages conform to OpenAI API format
- **Pattern**: Request validation with structural checks

#### Data Access Models

**ProductionData** - Complete factory snapshot
```python
class ProductionData(BaseModel):
    machines: List[MachineData] = Field(default_factory=list, description="All machines")
    metrics: Dict[str, any] = Field(default_factory=dict, description="Calculated metrics")
    alerts: List[Alert] = Field(default_factory=list, description="Active alerts")
    system_info: SystemInfo = Field(description="System metadata")
```
- **Purpose**: Root data structure loaded from `data/production.json`
- **Usage**: `src/data.py:load_production_data()` → All API endpoints
- **Pattern**: Composite model aggregating all factory data

**SystemInfo** - Factory metadata
```python
class SystemInfo(BaseModel):
    last_updated: str = Field(description="ISO timestamp of last data update")
    shift: str = Field(description="Current shift")
    data_mode: str = Field(description="local or blob")
```
- **Purpose**: Track data freshness and system configuration
- **Usage**: Displayed in dashboard footer
- **Pattern**: Metadata model

---

## Model Architecture & Patterns {#model-architecture}

### Model Ecosystem Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PYDANTIC MODELS STRUCTURE                        │
└─────────────────────────────────────────────────────────────────────┘

SHARED MODELS (shared/models.py)
├── Production Metrics Domain
│   ├── OEEMetrics ............ Ratio-based manufacturing metrics
│   └── ScrapMetrics .......... Waste analysis with machine breakdown
│
├── Quality Issues Domain
│   ├── QualityIssue ......... Single quality event (Item pattern)
│   └── QualityIssues ........ Collection + statistics (Collection pattern)
│
├── Machine Management Domain
│   ├── MachineStatus ........ Single machine state (Item pattern)
│   └── MachineCollection .... All machines + status breakdown (Collection pattern)
│
└── Alerts Domain
    └── Alert ................ Single alert event

API MODELS (api/routes/*.py)
├── Chat Models (api/routes/chat.py)
│   ├── ChatRequest .......... User input validation (Request pattern)
│   ├── ChatResponse ......... AI response structure (Response pattern)
│   └── ConversationHistory .. Chat history validation (Request pattern)
│
├── Dashboard Models (api/routes/dashboard.py)
│   └── DashboardData ........ Aggregated dashboard payload (Response pattern)
│
└── Health Models (api/main.py)
    └── HealthResponse ....... API status check (Response pattern)

DATA MODELS (shared/models.py)
├── ProductionData ........... Root factory data structure
├── MachineData .............. Single machine complete state
└── SystemInfo ............... Factory metadata
```

### Key Architectural Patterns

#### 1. Item/Collection Pattern
```
Single Entity (Item)          Collection (with stats)
─────────────────            ────────────────────────
QualityIssue                 QualityIssues
  type: str                    issues: List[QualityIssue]
  description: str             total_issues: int
  parts_affected: int          total_parts_affected: int
  severity: str                severity_breakdown: Dict[str, int]

MachineStatus                MachineCollection
  name: str                    machines: List[MachineStatus]
  status: str                  status_breakdown: Dict[str, int]
  parts_today: int
```

**When to use:**
- **Item model**: When representing a single entity or event
- **Collection model**: When you need the list PLUS aggregated statistics

**Pattern characteristics:**
- Collection includes `List[Item]` field named as plural (`issues`, `machines`)
- Collection adds statistics: `total_*` counts, `*_breakdown` dictionaries
- Both use `default_factory` for mutable defaults

#### 2. Request/Response Pattern
```
Request Model                 Response Model
─────────────                ──────────────
ChatRequest                  ChatResponse
  message: str                 response: str
  [validators present]         context: Optional[str]
                              [NO validators]

ConversationHistory          DashboardData
  conversation_id: str         production_data: ProductionData
  messages: List[Dict]         oee: OEEMetrics
  [validators present]         scrap: ScrapMetrics
                              issues: QualityIssues
                              [NO validators]
```

**When to use:**
- **Request model**: For API endpoint inputs (POST/PUT body, query params)
- **Response model**: For API endpoint outputs

**Pattern characteristics:**
- **Request**: Has `@field_validator` decorators for input sanitization
- **Response**: NO validators (output formatting only)
- **Naming**: Use `*Request` and `*Response` suffixes
- **Security**: Request models MUST validate/sanitize to prevent injection

#### 3. Metrics Pattern
```
OEEMetrics                   ScrapMetrics
  [core metric]: float         [core metric]: float
  [component 1]: float         [total]: int
  [component 2]: float         [breakdown]: Optional[Dict]
  [supporting data]: int
```

**When to use:**
- For calculated analytics (OEE, scrap rate, efficiency)
- When you need to expose both the computed value AND its components

**Pattern characteristics:**
- Primary metric field (e.g., `oee`, `scrap_rate`)
- Component fields that explain the calculation
- Optional breakdown dictionaries for detailed analysis
- All fields have constraints (e.g., `ge=0`, `le=1`)

#### 4. Data Model Pattern
```
ProductionData (root)
  machines: List[MachineData]
  metrics: Dict[str, any]
  alerts: List[Alert]
  system_info: SystemInfo
```

**When to use:**
- For data persistence structures (JSON file, database)
- As the root of your data hierarchy

**Pattern characteristics:**
- Composite structure (contains other models)
- Mirrors your data storage schema
- No Request/Response suffix (it's not API-specific)
- Loaded by `src/data.py` functions

---

## Naming Conventions {#naming-conventions}

### Model Names

| Pattern | Example | When to Use |
|---------|---------|-------------|
| Singular noun | `Alert`, `Machine` | Single entity or event |
| Plural noun | `QualityIssues`, `Metrics` | Collection with statistics |
| `*Request` suffix | `ChatRequest`, `ConversationHistory` | API request body |
| `*Response` suffix | `ChatResponse`, `HealthResponse` | API response body |
| `*Data` suffix | `ProductionData`, `MachineData` | Data persistence model |
| `*Info` suffix | `SystemInfo` | Metadata/configuration model |
| `*Status` suffix | `MachineStatus` | Current state snapshot |
| `*Collection` suffix | `MachineCollection` | Explicit collection with stats |

### Field Names

| Pattern | Example | When to Use |
|---------|---------|-------------|
| Singular noun | `name`, `status`, `machine` | Single value |
| Plural noun | `machines`, `issues`, `alerts` | List of items |
| `total_*` prefix | `total_parts`, `total_issues` | Count/sum aggregation |
| `*_breakdown` suffix | `severity_breakdown`, `status_breakdown` | Dictionary grouping |
| `*_rate` suffix | `scrap_rate`, `defect_rate` | Percentage [0-100] |
| No suffix for ratio | `oee`, `availability`, `quality` | Decimal [0-1] |
| `current_*` prefix | `current_part`, `current_shift` | Current state |
| `*_by_*` | `scrap_by_machine` | Grouped aggregation |

### Validation Method Names

```python
@field_validator('message')
@classmethod
def sanitize_message(cls, v: str) -> str:  # Use verb: sanitize_, validate_, check_
    """Verb + noun pattern."""
    return v.strip()
```

**Naming conventions:**
- `validate_*`: For constraint checking (e.g., `validate_severity`)
- `sanitize_*`: For input cleaning (e.g., `sanitize_message`)
- `check_*`: For cross-field validation (e.g., `check_date_range`)

---

## Common Mistakes to Avoid {#common-mistakes}

### 1. ❌ Mutable Default Values
```python
# WRONG - All instances share the same list!
class BadModel(BaseModel):
    items: List[str] = []  # ❌ Mutable default

# CORRECT - Each instance gets its own list
class GoodModel(BaseModel):
    items: List[str] = Field(default_factory=list)  # ✅ Factory pattern
```

**Why this matters:** Python evaluates default values once at class definition time. Using `[]` or `{}` as defaults means ALL instances share the same object, causing data to leak between instances.

### 2. ❌ Missing Type Hints
```python
# WRONG - No type hints
def process_data(data):  # ❌ What type is data?
    return data['machines']

# CORRECT - Full type annotations
def process_data(data: ProductionData) -> List[MachineData]:  # ✅ Clear types
    return data.machines
```

**Why this matters:** CLAUDE.md requires type hints on ALL parameters and return values. Type hints enable IDE autocomplete, catch errors at development time, and serve as inline documentation.

### 3. ❌ Validators on Response Models
```python
# WRONG - Response models shouldn't validate
class BadResponse(BaseModel):
    result: str

    @field_validator('result')  # ❌ Don't validate output
    @classmethod
    def uppercase_result(cls, v: str) -> str:
        return v.upper()

# CORRECT - Format data before creating response
class GoodResponse(BaseModel):
    result: str  # ✅ No validators

# Format data in the route handler
response_data = result.upper()  # ✅ Format before Pydantic
return GoodResponse(result=response_data)
```

**Why this matters:** Response models structure output, they don't transform it. Validators are for INPUT sanitization (security). Output formatting should happen in your business logic, not in Pydantic validators.

### 4. ❌ Missing Input Sanitization
```python
# WRONG - No validation on user input
class BadRequest(BaseModel):
    user_input: str  # ❌ No sanitization = injection risk

# CORRECT - Always sanitize user input
class GoodRequest(BaseModel):
    user_input: str = Field(min_length=1, max_length=500)

    @field_validator('user_input')
    @classmethod
    def sanitize_input(cls, v: str) -> str:  # ✅ Prevents injection
        return v.strip()
```

**Why this matters:** Unsanitized user input can lead to injection attacks (SQL injection, prompt injection, XSS). ALL request models MUST validate and sanitize inputs.

### 5. ❌ Inconsistent Naming
```python
# WRONG - Mixing patterns
class BadPatterns(BaseModel):
    totalCount: int  # ❌ camelCase (this is Python, not JavaScript)
    items_list: List[Item]  # ❌ Redundant suffix
    num_of_machines: int  # ❌ Verbose

# CORRECT - Consistent Python conventions
class GoodPatterns(BaseModel):
    total_count: int  # ✅ snake_case
    items: List[Item]  # ✅ Plural implies collection
    machine_count: int  # ✅ Concise
```

**Why this matters:** Consistent naming improves code readability and maintainability. Follow Python conventions (snake_case), avoid redundant suffixes, and use clear, concise names.

### 6. ❌ Using Percentages as Ratios (or vice versa)
```python
# WRONG - Mixing percentage and ratio conventions
class BadMetrics(BaseModel):
    oee: float = Field(ge=0, le=100)  # ❌ Should be [0-1]
    scrap_rate: float = Field(ge=0, le=1)  # ❌ Should be [0-100]

# CORRECT - Consistent conventions
class GoodMetrics(BaseModel):
    oee: float = Field(ge=0, le=1, description="Ratio (0-1)")  # ✅ Ratio
    scrap_rate: float = Field(ge=0, le=100, description="Percentage (0-100)")  # ✅ Percentage
```

**Why this matters:** Mixing [0-1] and [0-100] ranges causes calculation errors. Convention in this project:
- **Ratios** (no suffix): Use [0-1] range (e.g., `oee`, `availability`)
- **Rates** (*_rate suffix): Use [0-100] percentage (e.g., `scrap_rate`)

### 7. ❌ Missing Descriptions in Field()
```python
# WRONG - No descriptions
class BadModel(BaseModel):
    value: int = Field(ge=0)  # ❌ What does this represent?

# CORRECT - Descriptive Field() usage
class GoodModel(BaseModel):
    parts_produced: int = Field(ge=0, description="Total parts produced today")  # ✅ Clear purpose
```

**Why this matters:** Descriptions serve as inline documentation and appear in auto-generated API docs. They help future developers understand field purpose without reading code.

---

## Next Steps

- **Adding new models?** Start with the [Quick Start templates](#quick-start)
- **Understanding existing code?** Check [All Existing Models](#all-existing-models) table
- **Designing architecture?** Review [Model Architecture](#model-architecture) patterns
- **Code review?** Verify against [Common Mistakes](#common-mistakes) checklist

For general project structure and architecture, see `CODEBASE_OVERVIEW.md`.
