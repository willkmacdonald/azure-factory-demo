# Pydantic Models Documentation Index

This directory contains comprehensive documentation about the Pydantic models used in Factory Agent, including existing patterns and guidance for creating new supply chain models.

## Documentation Files

### 1. PYDANTIC_MODELS_ANALYSIS.md (710 lines)
**Comprehensive reference for all existing models**

Complete analysis of the existing Pydantic model structure including:
- All 15 existing models catalogued with full details
- Purpose and usage of each model
- Naming conventions (Request/Response, Item/Collection patterns)
- Field constraints and validation patterns
- Custom validator examples
- Model organization principles (shared vs route-specific)
- Common mistakes to avoid
- Summary table of all models

**Use this when:** You need to understand the complete model ecosystem or see detailed examples of existing patterns.

**Key sections:**
- All Existing Pydantic Models (7 shared + 3 chat + 5 data models)
- Naming Conventions & Patterns
- Key Validation Patterns
- Patterns to Replicate for Supply Chain Models
- Common Mistakes to Avoid

---

### 2. MODEL_QUICK_REFERENCE.md (315 lines)
**Quick templates and cheat sheets for creating new models**

Fast reference guide with copy-paste templates:
- Copy-paste model templates for shared models
- Copy-paste templates for route-specific models
- Field constraint cheat sheet (numeric, string, collections)
- Custom validation examples
- Naming conventions quick reference
- Common patterns with code snippets
- Anti-patterns to avoid
- File locations
- Import statements

**Use this when:** You're writing new models and want quick templates to copy.

**Key sections:**
- TL;DR - Copy Paste Templates
- Field Constraint Cheat Sheet
- Custom Validation Examples
- Naming Conventions
- Common Patterns
- Don't Do This (anti-patterns)

---

### 3. MODEL_ARCHITECTURE.md (305 lines)
**Visual model architecture and decision trees**

ASCII diagrams and visual representations:
- Complete model ecosystem overview (tree structure)
- Field constraint reference chart
- Validation architecture diagram
- Model patterns (Item+Collection, Summary+Details, Request/Response)
- Naming convention quick lookup
- Location strategy (where to put models)
- Development workflow for new models
- Decision trees (shared vs route-specific, constraints, defaults)

**Use this when:** You need to understand model relationships or make architectural decisions.

**Key sections:**
- Model Ecosystem Overview (ASCII tree)
- Field Constraint Reference
- Validation Architecture
- Model Patterns (diagrams)
- Location Strategy
- Development Workflow
- Quick Decision Tree

---

## How to Use These Documents

### Scenario 1: Creating a New Supply Chain Model
1. Read **MODEL_QUICK_REFERENCE.md** - Copy the template
2. Refer to **MODEL_ARCHITECTURE.md** - Use decision tree to determine:
   - Shared vs route-specific
   - Item vs collection pattern
   - Field constraints
3. Review **PYDANTIC_MODELS_ANALYSIS.md** - See examples of similar patterns

### Scenario 2: Understanding Existing Models
1. Read **MODEL_ARCHITECTURE.md** - Overview of ecosystem
2. Browse **PYDANTIC_MODELS_ANALYSIS.md** - Detailed catalog
3. Reference **MODEL_QUICK_REFERENCE.md** - Naming conventions

### Scenario 3: Implementing New Feature with Models
1. **MODEL_ARCHITECTURE.md** - Decision tree (shared or route-specific?)
2. **MODEL_QUICK_REFERENCE.md** - Copy template and constraints
3. **PYDANTIC_MODELS_ANALYSIS.md** - Find similar existing models for reference

## Quick Reference: Key Patterns

### Model Naming
```
Shared:        OEEMetrics, QualityIssues, DowntimeAnalysis
Request:       ChatRequest, SetupRequest
Response:      ChatResponse, StatsResponse, MachineInfo
Item:          QualityIssue, DowntimeEvent
Collection:    QualityIssues (plural)
```

### Field Constraints
```
Numeric:       Field(ge=0, le=1)
String length: Field(max_length=2000, min_length=1)
Collections:   Field(default_factory=list)
Optional:      Optional[Type] = None
Validation:    @field_validator('field_name')
```

### File Locations
```
Shared models:     shared/models.py
Chat models:       backend/src/api/routes/chat.py
Data models:       backend/src/api/routes/data.py
Your route models: backend/src/api/routes/{your_route}.py
```

## All Existing Models

| Model | File | Purpose |
|-------|------|---------|
| **OEEMetrics** | shared/models.py | Overall Equipment Effectiveness |
| **ScrapMetrics** | shared/models.py | Scrap and waste analysis |
| **QualityIssue** | shared/models.py | Individual quality issue |
| **QualityIssues** | shared/models.py | Quality issues collection |
| **DowntimeEvent** | shared/models.py | Individual downtime event |
| **MajorDowntimeEvent** | shared/models.py | Major outages (>2h) |
| **DowntimeAnalysis** | shared/models.py | Downtime analysis summary |
| **ChatMessage** | routes/chat.py | Chat message (with validators) |
| **ChatRequest** | routes/chat.py | Chat API request |
| **ChatResponse** | routes/chat.py | Chat API response |
| **SetupRequest** | routes/data.py | Data generation request |
| **SetupResponse** | routes/data.py | Data generation response |
| **StatsResponse** | routes/data.py | Data statistics response |
| **MachineInfo** | routes/data.py | Machine metadata |
| **DateRangeResponse** | routes/data.py | Date range metadata |

## Key Principles for Supply Chain Models

### 1. Structure
- Create singular item models (InventoryItem, SupplierRating)
- Create plural collection models (Inventory, SupplierRatings)
- Include aggregated statistics in collection models

### 2. Validation
- Use Field() constraints for simple rules (ge, le, max_length, min_length)
- Use @field_validator for complex logic (enum validation, aggregation)
- Always include description= parameter

### 3. Documentation
- Model docstring: "What this represents"
- Field descriptions: "Why this field exists"
- Validator docstrings: "What constraint is being enforced"

### 4. Organization
- Shared models: Used by multiple routes
- Route-specific models: Used by one endpoint
- Location: shared/models.py vs routes/{route}.py

### 5. Defaults
- Required fields: No default
- Optional fields: Optional[Type] = None
- Collections: Field(default_factory=list or dict)

## Development Workflow

```
1. DESIGN: Determine shared or route-specific
2. TEMPLATE: Copy from MODEL_QUICK_REFERENCE.md
3. CONSTRAINTS: Add Field validation from cheat sheet
4. VALIDATORS: Add @field_validator for complex rules
5. TEST: Write pytest tests for validation
6. DOCUMENT: Add to implementation-plan.md
```

## Getting Help

**For templates:** → MODEL_QUICK_REFERENCE.md
**For architecture:** → MODEL_ARCHITECTURE.md
**For examples:** → PYDANTIC_MODELS_ANALYSIS.md
**For decisions:** → MODEL_ARCHITECTURE.md (Decision Tree)

---

Last Updated: November 12, 2024
Total Models: 15 (7 shared + 8 route-specific)
Documentation Files: 3 comprehensive guides
