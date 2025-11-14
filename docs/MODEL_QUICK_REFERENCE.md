# Pydantic Models Quick Reference

## TL;DR - Copy Paste Template

### For Shared Models (used by multiple routes)

Location: `shared/models.py`

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class YourModel(BaseModel):
    """One-sentence description of what this model represents."""
    
    # Required fields (no default)
    field_name: str = Field(description="What this field represents")
    count: int = Field(ge=0, description="Must be non-negative")
    
    # Optional fields
    notes: Optional[str] = Field(default=None, description="Optional notes")
    
    # Collections with proper defaults
    items: List[dict] = Field(default_factory=list, description="List of items")
    breakdown: Dict[str, int] = Field(default_factory=dict, description="Count by category")
    
    # Custom validation
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v: str) -> str:
        """Validate field_name constraint."""
        if not v.strip():
            raise ValueError("field_name cannot be empty")
        return v.strip()
```

### For Route-Specific Models

Location: `backend/src/api/routes/your_route.py`

```python
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class YourRequest(BaseModel):
    """Request model for the endpoint."""
    
    param1: str = Field(description="First parameter")
    param2: int = Field(default=10, ge=1, le=100, description="Second parameter (1-100)")


class YourResponse(BaseModel):
    """Response model for the endpoint."""
    
    message: str = Field(description="Status message")
    data: List[dict] = Field(default_factory=list, description="Result data")
```

---

## Field Constraint Cheat Sheet

### Numeric Fields

```python
# Non-negative
count: int = Field(ge=0, description="...")

# Range with bounds
percentage: float = Field(ge=0, le=100, description="0-100%")
ratio: float = Field(ge=0, le=1, description="0-1 ratio")

# Exclusive bounds
duration: float = Field(gt=0, description="Must be positive")
major_event: float = Field(gt=2, description="Greater than 2 hours")
```

### String Fields

```python
# Length constraints
text: str = Field(max_length=2000, min_length=1, description="...")

# Just a description (no constraint)
name: str = Field(description="Friendly name")
```

### Collections

```python
# List with proper default
items: List[Model] = Field(default_factory=list, description="...")

# Dict with proper default
breakdown: Dict[str, int] = Field(default_factory=dict, description="...")

# Optional collections
optional_items: Optional[List[Model]] = Field(default=None, description="...")
```

---

## Custom Validation Examples

### Enum-like String Validation

```python
@field_validator('status')
@classmethod
def validate_status(cls, v: str) -> str:
    """Status must be one of: pending, active, complete."""
    allowed = {"pending", "active", "complete"}
    if v not in allowed:
        raise ValueError(f"Status must be one of {allowed}, got '{v}'")
    return v
```

### Aggregated List Validation

```python
@field_validator('items')
@classmethod
def validate_items(cls, v: List[Item]) -> List[Item]:
    """Ensure items list doesn't exceed size limit."""
    if len(v) > 100:
        raise ValueError(f"Too many items: {len(v)} (max: 100)")
    return v
```

### Whitespace Trimming

```python
@field_validator('name')
@classmethod
def validate_name(cls, v: str) -> str:
    """Trim whitespace and validate non-empty."""
    v = v.strip()
    if not v:
        raise ValueError("Name cannot be empty")
    return v
```

---

## Naming Conventions

### Collection vs Item Models

```python
# Individual item model (singular)
class QualityIssue(BaseModel):
    """Single quality issue."""
    issue_id: str
    severity: str

# Collection model (plural, contains items + stats)
class QualityIssues(BaseModel):
    """Collection of quality issues."""
    issues: List[QualityIssue]
    total_issues: int
    severity_breakdown: Dict[str, int]
```

### Request/Response Naming

```python
# Request
class GetMetricsRequest(BaseModel):
    start_date: str

# Response
class GetMetricsResponse(BaseModel):
    metrics: List[Metric]
    total: int
```

### API Response Naming

```python
# Stats response
class StatsResponse(BaseModel):
    total_items: int
    date_range: str

# Info response
class MachineInfo(BaseModel):
    machine_id: str
    name: str
```

---

## Common Patterns

### Pattern 1: Item + Collection

```python
class SupplierRating(BaseModel):
    """Single supplier rating."""
    supplier_id: str = Field(description="Supplier ID")
    rating: float = Field(ge=0, le=5, description="Rating 0-5")
    review_date: str = Field(description="YYYY-MM-DD")


class SupplierRatings(BaseModel):
    """Collection of supplier ratings with statistics."""
    ratings: List[SupplierRating] = Field(default_factory=list)
    average_rating: float = Field(ge=0, le=5)
    total_suppliers: int = Field(ge=0)
```

### Pattern 2: Summary with Details

```python
class Order(BaseModel):
    """Order with summary and detailed lines."""
    order_id: str
    total_value: float = Field(ge=0)
    line_count: int = Field(ge=0)
    lines: List[OrderLine] = Field(default_factory=list)
```

### Pattern 3: Status Tracking

```python
class ProcessStatus(BaseModel):
    """Process with status and optional details."""
    process_id: str
    status: str  # validated in @field_validator
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
```

### Pattern 4: Optional Breakdown

```python
class Metrics(BaseModel):
    """Metrics with optional breakdown by category."""
    total: int = Field(ge=0)
    by_category: Optional[Dict[str, int]] = Field(default=None)
```

---

## Don't Do This

```python
# WRONG: Mutable default
items: List[Item] = []

# RIGHT: Use default_factory
items: List[Item] = Field(default_factory=list)


# WRONG: No field description
field: str

# RIGHT: Always document
field: str = Field(description="What this field means")


# WRONG: Validation in route
if request.role not in {"admin", "user"}:
    raise HTTPException(...)

# RIGHT: Validation in model
@field_validator('role')
@classmethod
def validate_role(cls, v: str) -> str:
    if v not in {"admin", "user"}:
        raise ValueError("Invalid role")
    return v
```

---

## File Locations

### Shared Models (used by multiple routes)
`shared/models.py`

### Route-Specific Models
- Chat models: `backend/src/api/routes/chat.py`
- Data models: `backend/src/api/routes/data.py`
- Metrics models: use `shared/models.py`
- Your route models: `backend/src/api/routes/your_route.py`

---

## Imports in shared/models.py

```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
```

---

## Imports in routes/your_route.py

```python
from typing import List, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from shared.models import (
    YourSharedModel,
    AnotherSharedModel,
)

router = APIRouter(prefix="/api/your-endpoint", tags=["Your Feature"])
```

