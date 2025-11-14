# Factory Agent Pydantic Models Analysis

## Executive Summary

This document provides a comprehensive analysis of the Pydantic models used in the Factory Agent codebase. The models follow consistent patterns and conventions that should be replicated when adding new supply chain models.

---

## Project Structure

```
factory-agent/
├── shared/                          # Shared modules used by CLI and API
│   ├── models.py                   # PRIMARY: All Pydantic data models
│   ├── data.py                     # Data generation and persistence
│   └── config.py                   # Configuration management
├── backend/
│   └── src/api/routes/
│       ├── chat.py                 # Chat API models (ChatMessage, ChatRequest, ChatResponse)
│       ├── data.py                 # Data management models (SetupRequest, StatsResponse, etc.)
│       └── metrics.py              # Metrics API (reuses shared models)
└── tests/                          # Test files
```

---

## All Existing Pydantic Models

### Location: `shared/models.py` (Production/Analysis Models)

#### 1. **OEEMetrics** - Overall Equipment Effectiveness
```python
class OEEMetrics(BaseModel):
    """Overall Equipment Effectiveness metrics."""
    
    oee: float                          # Range: 0-1
    availability: float                 # Range: 0-1
    performance: float                  # Range: 0-1
    quality: float                      # Range: 0-1
    total_parts: int                    # >= 0
    good_parts: int                     # >= 0
    scrap_parts: int                    # >= 0
```

**Purpose:** API response model for OEE calculations  
**Usage:** `/api/metrics/oee` endpoint  
**Key Pattern:** Field constraints using `Field(ge=0, le=1)`

---

#### 2. **ScrapMetrics** - Scrap and Waste Analysis
```python
class ScrapMetrics(BaseModel):
    """Scrap and waste metrics."""
    
    total_scrap: int                    # >= 0
    total_parts: int                    # >= 0
    scrap_rate: float                   # Range: 0-100 (percentage)
    scrap_by_machine: Optional[Dict[str, int]]  # Optional breakdown
```

**Purpose:** Scrap rate calculations with optional machine breakdown  
**Usage:** `/api/metrics/scrap` endpoint  
**Key Patterns:**
- `Optional` types for conditional fields
- Default factories for complex types: `default_factory=dict`

---

#### 3. **QualityIssue** - Individual Quality Issue Record
```python
class QualityIssue(BaseModel):
    """Individual quality issue record."""
    
    type: str                           # Defect type
    description: str                    # Issue description
    parts_affected: int                 # >= 0
    severity: str                       # Low, Medium, High
    date: str                           # YYYY-MM-DD format
    machine: str                        # Machine name
```

**Purpose:** Represents a single quality problem  
**Usage:** Part of `QualityIssues` collection model  
**Key Pattern:** No type validation on string enums (kept simple for demo)

---

#### 4. **QualityIssues** - Quality Issues Collection
```python
class QualityIssues(BaseModel):
    """Collection of quality issues with statistics."""
    
    issues: List[QualityIssue]          # default_factory=list
    total_issues: int                   # >= 0
    total_parts_affected: int           # >= 0
    severity_breakdown: Dict[str, int]  # default_factory=dict
```

**Purpose:** Container with aggregated quality metrics  
**Usage:** `/api/metrics/quality` endpoint  
**Key Pattern:** Nested models + aggregated statistics in single response

---

#### 5. **DowntimeEvent** - Individual Downtime Entry
```python
class DowntimeEvent(BaseModel):
    """Individual downtime event record."""
    
    reason: str                         # Downtime category
    description: str                    # Event details
    duration_hours: float               # >= 0
```

**Purpose:** Represents a single downtime occurrence  
**Usage:** Part of downtime analysis  

---

#### 6. **MajorDowntimeEvent** - Major Outages (>2 hours)
```python
class MajorDowntimeEvent(BaseModel):
    """Major downtime event (>2 hours)."""
    
    date: str                           # YYYY-MM-DD
    machine: str                        # Machine name
    reason: str                         # Downtime reason
    description: str                    # Event description
    duration_hours: float               # > 2 (constraint!)
```

**Purpose:** Filtered downtime events above threshold  
**Usage:** Highlighted in `/api/metrics/downtime` response  
**Key Pattern:** Field constraint using `Field(gt=2)` for business logic

---

#### 7. **DowntimeAnalysis** - Downtime Analysis Summary
```python
class DowntimeAnalysis(BaseModel):
    """Downtime analysis with events and breakdowns."""
    
    total_downtime_hours: float         # >= 0
    downtime_by_reason: Dict[str, float]  # default_factory=dict
    major_events: List[MajorDowntimeEvent]  # default_factory=list
```

**Purpose:** Complete downtime analysis with statistics and major events  
**Usage:** `/api/metrics/downtime` endpoint  
**Key Pattern:** Combines summary stats + detailed events list

---

### Location: `backend/src/api/routes/chat.py` (Chat API Models)

#### 8. **ChatMessage** - Individual Chat Message
```python
class ChatMessage(BaseModel):
    """Individual chat message model with strict role enforcement."""
    
    role: str                           # Validated: 'user' or 'assistant'
    content: str                        # Max 2000 chars, min 1
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Ensure role is either 'user' or 'assistant'."""
        allowed_roles = {"user", "assistant"}
        if v not in allowed_roles:
            raise ValueError(f"Invalid role '{v}'...")
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is non-empty after stripping whitespace."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty...")
        return v
```

**Purpose:** Represents a single chat message in conversation history  
**Usage:** Part of `ChatRequest` and `ChatResponse` models  
**Key Patterns:**
- Custom `@field_validator` decorators for complex validation logic
- Business rule enforcement at model level (not in routes)
- Security validation (empty content, invalid roles)

---

#### 9. **ChatRequest** - Chat Endpoint Request
```python
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str                        # Max 2000 chars, min 1
    history: List[ChatMessage]          # Max 50 messages
    
    @field_validator('history')
    @classmethod
    def validate_total_history_size(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        """Ensure total history size doesn't exceed reasonable limits."""
        total_chars = sum(len(msg.content) for msg in v)
        if total_chars > 50000:  # 50K character limit
            raise ValueError(f"Total conversation history too large...")
        return v
```

**Purpose:** Request payload for `/api/chat` endpoint  
**Usage:** FastAPI request body validation  
**Key Patterns:**
- Nested model validation (list of ChatMessage objects)
- Multi-field validation logic (aggregating across list)
- Security controls (token exhaustion prevention)

---

#### 10. **ChatResponse** - Chat Endpoint Response
```python
class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    response: str                       # AI assistant's response
    history: List[ChatMessage]          # Updated conversation history
```

**Purpose:** Response payload from `/api/chat` endpoint  
**Usage:** FastAPI response model  

---

### Location: `backend/src/api/routes/data.py` (Data Management Models)

#### 11. **SetupRequest** - Data Generation Request
```python
class SetupRequest(BaseModel):
    """Request model for data generation endpoint."""
    
    days: int                           # Range: 1-365, default: 30
```

**Purpose:** Configurable request for synthetic data generation  
**Usage:** `POST /api/setup` request body  
**Key Pattern:** Simple configuration model with range constraints

---

#### 12. **SetupResponse** - Data Generation Response
```python
class SetupResponse(BaseModel):
    """Response model for data generation endpoint."""
    
    message: str                        # Success message
    days: int                           # Days generated
    start_date: str                     # ISO format
    end_date: str                       # ISO format
    machines: int                       # Count
```

**Purpose:** Summary of generated synthetic data  
**Usage:** `POST /api/setup` response  

---

#### 13. **StatsResponse** - Data Statistics Response
```python
class StatsResponse(BaseModel):
    """Response model for data statistics endpoint."""
    
    exists: bool                        # Data file exists?
    start_date: Optional[str]           # ISO format (null if no data)
    end_date: Optional[str]             # ISO format (null if no data)
    total_days: Optional[int]           # Null if no data
    total_machines: Optional[int]       # Null if no data
    total_records: Optional[int]        # Null if no data
```

**Purpose:** Metadata about current data state  
**Usage:** `GET /api/stats` response  
**Key Pattern:** Optional fields for conditional data presence

---

#### 14. **MachineInfo** - Machine Details
```python
class MachineInfo(BaseModel):
    """Machine information model."""
    
    id: int                             # Unique identifier
    name: str                           # Machine name
    type: str                           # Machine type
    ideal_cycle_time: int               # Seconds
```

**Purpose:** Machine metadata  
**Usage:** `GET /api/machines` response (list)  

---

#### 15. **DateRangeResponse** - Date Range Information
```python
class DateRangeResponse(BaseModel):
    """Response model for date range endpoint."""
    
    start_date: str                     # ISO format
    end_date: str                       # ISO format
    total_days: int                     # Calculated
```

**Purpose:** Date range metadata  
**Usage:** `GET /api/date-range` response  

---

## Naming Conventions & Patterns

### 1. **Model Naming Conventions**

| Convention | Pattern | Examples |
|-----------|---------|----------|
| **API Response Models** | `{Domain}{Type}` or just `{Domain}` | `OEEMetrics`, `QualityIssues`, `StatsResponse` |
| **API Request Models** | `{Action}Request` | `ChatRequest`, `SetupRequest` |
| **API Response Models** | `{Domain}Response` | `ChatResponse`, `SetupResponse`, `StatsResponse` |
| **Entity Models** | Singular nouns | `QualityIssue`, `MajorDowntimeEvent`, `MachineInfo` |
| **Collection Models** | Plural nouns | `QualityIssues`, `DowntimeAnalysis` (contains collection) |
| **Info Models** | `{Domain}Info` | `MachineInfo` |

### 2. **Field Documentation Style**

All models use docstrings explaining purpose. Fields have `description=` parameter:

```python
class Example(BaseModel):
    """One-line class docstring."""
    
    field_name: Type = Field(
        ge=0,                           # Constraint
        le=100,
        description="What this field means"  # Always include
    )
```

### 3. **Field Constraints & Validation**

#### Built-in Field Constraints
```python
# Numeric ranges
field: int = Field(ge=0)                    # >= 0
field: int = Field(ge=0, le=100)            # 0-100
field: float = Field(gt=2)                  # > 2

# String constraints
field: str = Field(max_length=2000, min_length=1)
```

#### Custom Field Validators
```python
from pydantic import field_validator

class Model(BaseModel):
    role: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Custom validation logic."""
        if v not in {"user", "assistant"}:
            raise ValueError("Invalid role")
        return v
```

### 4. **Optional and Default Values**

```python
# Optional field (can be None)
optional_field: Optional[str] = None
optional_field: Optional[Dict[str, int]] = Field(default=None, ...)

# Required field with default
field: int = Field(default=30, ge=1, le=365)

# Collection defaults (important pattern!)
items: List[Model] = Field(default_factory=list)
breakdown: Dict[str, int] = Field(default_factory=dict)
```

### 5. **Nested Models**

```python
# Single nested model
class Parent(BaseModel):
    child: ChildModel

# List of nested models
class Parent(BaseModel):
    children: List[ChildModel] = Field(default_factory=list)
```

---

## Key Validation Patterns

### 1. **Numeric Range Validation**
```python
# Single bound
value: int = Field(ge=0)           # >= 0
value: float = Field(gt=2)         # > 2

# Dual bounds
rate: float = Field(ge=0, le=100)  # 0-100 (percentage)
oee: float = Field(ge=0, le=1)     # 0-1 (ratio)
```

### 2. **String Validation**
```python
# Length constraints
message: str = Field(max_length=2000, min_length=1)

# Content validation (via validator)
content: str = Field(description="...")

@field_validator('content')
@classmethod
def validate_content(cls, v: str) -> str:
    if not v.strip():
        raise ValueError("Cannot be empty")
    return v
```

### 3. **Role/Status Validation**
```python
# Current pattern: String without validation (simple for demo)
severity: str = Field(description="Severity level (Low, Medium, High)")
role: str = Field(description="Message role: user or assistant only")

# Could be enhanced with:
# from enum import Enum
# 
# class Severity(str, Enum):
#     LOW = "Low"
#     MEDIUM = "Medium"
#     HIGH = "High"
```

### 4. **Aggregated Data Validation**
```python
@field_validator('history')
@classmethod
def validate_total_history_size(cls, v: List[ChatMessage]) -> List[ChatMessage]:
    """Validate entire list, not just individual items."""
    total_chars = sum(len(msg.content) for msg in v)
    if total_chars > 50000:
        raise ValueError("History too large")
    return v
```

---

## Model Organization

### Current Organization

```
shared/models.py
├── Production Metrics Models
│   ├── OEEMetrics
│   ├── ScrapMetrics
│   └── DowntimeAnalysis (+ related: DowntimeEvent, MajorDowntimeEvent)
├── Quality Models
│   ├── QualityIssue
│   └── QualityIssues
└── [Future: Supply Chain Models would go here]

backend/src/api/routes/chat.py
├── ChatMessage
├── ChatRequest
└── ChatResponse

backend/src/api/routes/data.py
├── SetupRequest
├── SetupResponse
├── StatsResponse
├── MachineInfo
└── DateRangeResponse
```

### Principles for Organization

1. **Shared Models** in `shared/models.py`:
   - Used across multiple routes
   - Represent core business domain concepts
   - Production metrics, quality issues, etc.

2. **Route-Specific Models** in route files:
   - Only used in that specific route
   - API protocol models (request/response)
   - Data management endpoints
   - Chat protocol models

---

## Imports Pattern

### In `shared/models.py`:
```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
```

### In route files (e.g., `routes/chat.py`):
```python
from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from shared.models import (
    OEEMetrics,
    ScrapMetrics,
    QualityIssues,
    DowntimeAnalysis,
)
```

---

## Patterns to Replicate for Supply Chain Models

### 1. **Document Every Model with Docstring**
```python
class InventoryLevel(BaseModel):
    """Current inventory level for a SKU."""
    # ... fields
```

### 2. **Document Every Field with description Parameter**
```python
sku_id: str = Field(description="Stock Keeping Unit identifier")
quantity: int = Field(ge=0, description="Current quantity on hand")
```

### 3. **Use Type Hints Consistently**
- Required fields with no default
- Optional fields explicitly: `Optional[Type]`
- Collections with type parameters: `List[Model]`, `Dict[str, Type]`

### 4. **Constrain Fields at the Model Level**
```python
# Not in the route logic, but in the model
lead_time_days: int = Field(ge=0, le=365, description="...")
percentage: float = Field(ge=0, le=100, description="...")
```

### 5. **Use Custom Validators for Complex Logic**
```python
@field_validator('status')
@classmethod
def validate_status(cls, v: str) -> str:
    valid_statuses = {"pending", "in-transit", "received", "rejected"}
    if v not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
    return v
```

### 6. **Group Related Data with Nested Models**
Not flat models, but logical hierarchies:
```python
class OrderLine(BaseModel):
    sku: str
    quantity: int

class Order(BaseModel):
    order_id: str
    lines: List[OrderLine]
    total_value: float
```

### 7. **Use Default Factories for Collections**
```python
# NOT: items: List[Item] = None  # Wrong!
# YES:
items: List[Item] = Field(default_factory=list)
breakdown: Dict[str, int] = Field(default_factory=dict)
```

### 8. **Separate Collection Models from Items**
```python
# Item model
class SupplierRating(BaseModel):
    supplier_id: str
    rating: float

# Collection model with stats
class SupplierRatings(BaseModel):
    ratings: List[SupplierRating]
    average_rating: float
    total_suppliers: int
```

---

## Common Mistakes to Avoid

### 1. Don't Put Request/Response Models in shared/models.py
```python
# WRONG - in shared/models.py:
class SetupRequest(BaseModel):
    days: int

# RIGHT - in routes/data.py:
class SetupRequest(BaseModel):
    days: int
```

### 2. Don't Use Mutable Defaults
```python
# WRONG:
items: List[Item] = []

# RIGHT:
items: List[Item] = Field(default_factory=list)
```

### 3. Don't Skip Field Descriptions
```python
# WRONG:
total_cost: float

# RIGHT:
total_cost: float = Field(description="Total cost in USD")
```

### 4. Don't Mix Enum Strings with Plain Strings
```python
# INCONSISTENT:
severity: str = Field(description="Low, Medium, or High")

# BETTER (for future):
from enum import Enum
class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

severity: Severity
```

### 5. Don't Validate in Routes When You Should Validate in Models
```python
# WRONG - in route:
if message.role not in {"user", "assistant"}:
    raise HTTPException(...)

# RIGHT - in model:
@field_validator('role')
@classmethod
def validate_role(cls, v: str) -> str:
    ...
```

---

## Summary Table: All Models

| Model | Location | Purpose | Key Features |
|-------|----------|---------|--------------|
| **OEEMetrics** | `shared/models.py` | OEE calculation response | Ratio constraints (0-1) |
| **ScrapMetrics** | `shared/models.py` | Scrap analysis response | Optional breakdown dict |
| **QualityIssue** | `shared/models.py` | Individual quality issue | Simple event record |
| **QualityIssues** | `shared/models.py` | Quality collection | List + aggregated stats |
| **DowntimeEvent** | `shared/models.py` | Individual downtime event | Simple event record |
| **MajorDowntimeEvent** | `shared/models.py` | Major outages (>2h) | Threshold constraint (gt=2) |
| **DowntimeAnalysis** | `shared/models.py` | Downtime analysis | Summary + detailed events |
| **ChatMessage** | `routes/chat.py` | Chat message | Custom validators (role, content) |
| **ChatRequest** | `routes/chat.py` | Chat request payload | Nested validation (history size) |
| **ChatResponse** | `routes/chat.py` | Chat response payload | Nested ChatMessage list |
| **SetupRequest** | `routes/data.py` | Data generation request | Range constraint (1-365) |
| **SetupResponse** | `routes/data.py` | Data generation response | Summary metadata |
| **StatsResponse** | `routes/data.py` | Data statistics response | Optional fields (no data) |
| **MachineInfo** | `routes/data.py` | Machine metadata | Static list item |
| **DateRangeResponse** | `routes/data.py` | Date range metadata | Calculated fields |

---

## For Supply Chain Models

When adding supply chain models, follow these principles:

1. **Location Decision:**
   - If used by multiple routes → `shared/models.py`
   - If only one route → Define in that route file

2. **Structure:**
   - Individual item models (e.g., `InventoryItem`)
   - Collection models with stats (e.g., `Inventory`)
   - Request/Response models in routes

3. **Validation:**
   - Use `Field()` constraints for simple rules
   - Use `@field_validator` for complex logic
   - Always include `description=` parameter

4. **Documentation:**
   - Class docstrings: Purpose
   - Field descriptions: What the field means
   - Inline comments: Why constraints exist

5. **Nesting:**
   - Group related fields logically
   - Use typed collections: `List[Model]`, `Dict[str, Type]`
   - Use `default_factory` for mutable defaults

