# Factory Agent Model Architecture

## Model Ecosystem Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PYDANTIC MODELS STRUCTURE                        │
└─────────────────────────────────────────────────────────────────────┘

SHARED MODELS (shared/models.py)
├── Production Metrics Domain
│   ├── OEEMetrics (ratio-based metrics)
│   │   ├── oee: float [0-1]
│   │   ├── availability: float [0-1]
│   │   ├── performance: float [0-1]
│   │   ├── quality: float [0-1]
│   │   ├── total_parts: int >=0
│   │   ├── good_parts: int >=0
│   │   └── scrap_parts: int >=0
│   │
│   └── ScrapMetrics (waste analysis)
│       ├── total_scrap: int >=0
│       ├── total_parts: int >=0
│       ├── scrap_rate: float [0-100]
│       └── scrap_by_machine: Optional[Dict]
│
├── Quality Issues Domain
│   ├── QualityIssue (singular event)
│   │   ├── type: str
│   │   ├── description: str
│   │   ├── parts_affected: int >=0
│   │   ├── severity: str (Low|Medium|High)
│   │   ├── date: str (YYYY-MM-DD)
│   │   └── machine: str
│   │
│   └── QualityIssues (collection with stats)
│       ├── issues: List[QualityIssue]
│       ├── total_issues: int >=0
│       ├── total_parts_affected: int >=0
│       └── severity_breakdown: Dict[str, int]
│
└── Downtime Domain
    ├── DowntimeEvent (simple event)
    │   ├── reason: str
    │   ├── description: str
    │   └── duration_hours: float >=0
    │
    ├── MajorDowntimeEvent (filtered: >2h)
    │   ├── date: str (YYYY-MM-DD)
    │   ├── machine: str
    │   ├── reason: str
    │   ├── description: str
    │   └── duration_hours: float >2  ← CONSTRAINT
    │
    └── DowntimeAnalysis (summary + events)
        ├── total_downtime_hours: float >=0
        ├── downtime_by_reason: Dict[str, float]
        └── major_events: List[MajorDowntimeEvent]


ROUTE-SPECIFIC MODELS (backend/src/api/routes/)

Chat API (routes/chat.py)
├── ChatMessage
│   ├── role: str (validated: user|assistant) [validator]
│   └── content: str [1-2000 chars] [validator]
│
├── ChatRequest
│   ├── message: str [1-2000 chars]
│   └── history: List[ChatMessage] [validator: max 50K chars total]
│
└── ChatResponse
    ├── response: str
    └── history: List[ChatMessage]


Data Management API (routes/data.py)
├── SetupRequest
│   └── days: int [1-365]
│
├── SetupResponse
│   ├── message: str
│   ├── days: int
│   ├── start_date: str
│   ├── end_date: str
│   └── machines: int
│
├── StatsResponse
│   ├── exists: bool
│   ├── start_date: Optional[str]
│   ├── end_date: Optional[str]
│   ├── total_days: Optional[int]
│   ├── total_machines: Optional[int]
│   └── total_records: Optional[int]
│
├── MachineInfo
│   ├── id: int
│   ├── name: str
│   ├── type: str
│   └── ideal_cycle_time: int
│
└── DateRangeResponse
    ├── start_date: str
    ├── end_date: str
    └── total_days: int
```

## Field Constraint Reference

```
NUMERIC CONSTRAINTS:
  ge=0        → Greater than or equal to 0 (non-negative)
  le=1        → Less than or equal to 1 (max value)
  gt=2        → Greater than 2 (exclusive)
  ge=0, le=1  → Range: 0 to 1 (ratios, percentages)

STRING CONSTRAINTS:
  max_length=2000     → Maximum 2000 characters
  min_length=1        → Minimum 1 character
  
COLLECTION DEFAULTS:
  default_factory=list  → Empty list if not provided
  default_factory=dict  → Empty dict if not provided
  
OPTIONAL FIELDS:
  Optional[str] = None          → Field can be None
  Optional[Dict[str, int]] = None → Optional breakdown
```

## Validation Architecture

```
FIELD-LEVEL VALIDATION (Pydantic Field)
├── ge, le, gt (numeric bounds)
├── max_length, min_length (string length)
├── description (documentation)
└── default, default_factory (default values)

CUSTOM VALIDATION (@field_validator)
├── Role validation (ChatMessage)
│   └── @field_validator('role')
│       └── Whitelist: {"user", "assistant"}
│
├── Content validation (ChatMessage)
│   └── @field_validator('content')
│       └── Ensure: not empty after strip
│
└── Aggregated validation (ChatRequest)
    └── @field_validator('history')
        └── Total chars across all messages ≤ 50K
```

## Model Patterns

```
PATTERN 1: Item + Collection
┌──────────────────────┐    ┌──────────────────────────┐
│  QualityIssue        │    │  QualityIssues           │
│  (singular)          │    │  (plural, container)     │
├──────────────────────┤    ├──────────────────────────┤
│ - type: str          │    │ - issues: List[...]      │
│ - severity: str      │    │ - total_issues: int      │
│ - parts_affected: int│    │ - severity_breakdown: {} │
└──────────────────────┘    └──────────────────────────┘
         ↑                            ↑
      Used By                    Uses Above


PATTERN 2: Summary + Details
┌─────────────────────────────────────────┐
│  DowntimeAnalysis                       │
├─────────────────────────────────────────┤
│ - total_downtime_hours: float (summary) │
│ - downtime_by_reason: Dict (breakdown)  │
│ - major_events: List[Events] (details)  │
└─────────────────────────────────────────┘


PATTERN 3: Request/Response Pair
┌──────────────────┐        ┌──────────────────┐
│  ChatRequest     │        │  ChatResponse    │
├──────────────────┤        ├──────────────────┤
│ - message: str   │───────→│ - response: str  │
│ - history: List[]│        │ - history: List[]│
└──────────────────┘        └──────────────────┘


PATTERN 4: Configuration Model
┌──────────────────┐
│  SetupRequest    │
├──────────────────┤
│ - days: int      │
│   [1-365]        │
│   (default: 30)  │
└──────────────────┘
```

## Naming Conventions

```
SHARED MODELS (used across routes):
  Domain + Type = {OEEMetrics, ScrapMetrics, QualityIssues, DowntimeAnalysis}

ROUTE-SPECIFIC REQUEST:
  {Action}Request = {ChatRequest, SetupRequest}

ROUTE-SPECIFIC RESPONSE:
  {Domain}Response = {ChatResponse, SetupResponse, StatsResponse}
                  or {Domain}Info = {MachineInfo}
                  or {Domain}Range = {DateRangeResponse}

ENTITY MODELS:
  Singular = {QualityIssue, DowntimeEvent, MajorDowntimeEvent}

COLLECTION MODELS:
  Plural = {QualityIssues}
  or -Analysis suffix = {DowntimeAnalysis}
```

## Location Strategy

```
WHERE TO PUT MODELS:

Shared Models (shared/models.py)
├── Used by MULTIPLE routes
├── Represent CORE DOMAIN CONCEPTS
├── Examples: OEEMetrics, QualityIssues, DowntimeAnalysis
└── DOMAIN: Production metrics, Quality, Downtime

Route-Specific Models (backend/src/api/routes/{route}.py)
├── Used by SINGLE route only
├── API PROTOCOL models (Request/Response)
├── Examples: ChatRequest, ChatResponse, SetupRequest
└── DOMAIN: API communication protocol


SUPPLY CHAIN MODELS (when you create them):
├── Shared: InventoryLevel, SupplierRating, Purchase Order
│   └── Used by multiple routes (analytics, reporting)
└── Route-specific: InventoryRequest, SupplierResponse
    └── Used by one endpoint
```

## Development Workflow for New Models

```
STEP 1: Design Model
├── Identify if shared or route-specific
├── List all fields with types
├── Determine constraints (ge, le, max_length, etc.)
└── Plan nested relationships

STEP 2: Create Template
├── Use MODEL_QUICK_REFERENCE.md template
├── Add class docstring
├── Add field descriptions
└── Add @field_validator if needed

STEP 3: Add to File
├── Shared: Add to shared/models.py
├── Route: Add to backend/src/api/routes/{route}.py
└── Import in route: from shared.models import ...

STEP 4: Test
├── Use pytest for validation tests
├── Test valid data
├── Test invalid data (constraints should reject)
├── Test edge cases (empty lists, None values, etc.)

STEP 5: Document
├── Add to README if significant
├── Document constraints in field description
├── Add examples in docstring if complex
└── Add to implementation-plan.md PR notes
```

## Quick Decision Tree

```
Is this model used by multiple routes?
├─ YES → shared/models.py (shared model)
│  ├─ Represents core domain? → OEEMetrics pattern
│  ├─ Is it a single item? → QualityIssue pattern
│  ├─ Is it a collection? → QualityIssues pattern
│  └─ Has summary + details? → DowntimeAnalysis pattern
│
└─ NO → backend/src/api/routes/{route}.py (route-specific)
   ├─ Is it a request? → {Action}Request pattern
   ├─ Is it a response? → {Domain}Response pattern
   ├─ Is it configuration? → {Action}Request pattern
   └─ Is it metadata? → {Domain}Info or {Domain}Response

Does field have constraints?
├─ Numeric range → Use Field(ge=, le=)
├─ String length → Use Field(max_length=, min_length=)
├─ Complex rule → Use @field_validator
└─ No constraint → Just Field(description="...")

Is field always provided?
├─ YES → No default needed
├─ NO → Use Optional[Type] = None
└─ Collection → Use Field(default_factory=list/dict)
```

