# Option C: Hybrid Approach Implementation Plan

## Overview

Implement a **hybrid normalized/denormalized schema** for supply chain traceability:
- **Normalized master data** (suppliers, materials, orders) - single source of truth
- **Denormalized traceability** in quality issues - fast queries without joins
- **Backward compatible** - existing v1.0 APIs continue working

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│ MASTER DATA (Normalized)                                    │
│                                                              │
│  suppliers[]          material_lots[]         orders[]      │
│  ├─ id               ├─ lot_number           ├─ id          │
│  ├─ name             ├─ material_id          ├─ customer    │
│  ├─ contact          ├─ supplier_id (FK)     ├─ part_number │
│  └─ quality_metrics  ├─ received_date        └─ quantity    │
│                      └─ inspection_results                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Referenced by
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ TRANSACTIONAL DATA (Enhanced with References)               │
│                                                              │
│  production[date][machine]                                  │
│  ├─ batches[] (NEW)                                         │
│  │   ├─ batch_id                                            │
│  │   ├─ order_id (FK → orders)                             │
│  │   ├─ shift, operator                                     │
│  │   ├─ serial_range {start, end}                           │
│  │   └─ materials_consumed[]                                │
│  │       ├─ material_id                                     │
│  │       ├─ lot_number (FK → material_lots)                 │
│  │       └─ quantity                                         │
│  │                                                           │
│  └─ quality_issues[] (ENHANCED)                             │
│      ├─ issue_id                                            │
│      ├─ type, severity, parts_affected                      │
│      │                                                       │
│      ├─ traceability (denormalized for performance)         │
│      │   ├─ batch_id                                        │
│      │   ├─ order_id                                        │
│      │   ├─ customer (cached from order)                    │
│      │   └─ affected_serials[]                              │
│      │                                                       │
│      ├─ materials_used[] (denormalized)                     │
│      │   ├─ lot_number                                      │
│      │   ├─ supplier_id (cached from lot)                   │
│      │   └─ supplier_name (cached from supplier)            │
│      │                                                       │
│      ├─ investigation (NEW)                                 │
│      │   ├─ root_cause_category                             │
│      │   ├─ suspected_lots[]                                │
│      │   └─ status                                           │
│      │                                                       │
│      └─ cost_impact (NEW)                                   │
│          ├─ total_cost                                      │
│          └─ charged_to_supplier                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Foundation (Backend Models & Data Generation)
**Goal**: Add new entities without breaking existing functionality

#### Task 1.1: Create Pydantic Models
**File**: `shared/models.py`

Add new models:

```python
class Supplier(BaseModel):
    """Supplier/vendor information"""
    id: str = Field(description="Supplier ID (SUP-XXX)")
    name: str = Field(description="Supplier name")
    type: str = Field(description="Supplier type (Raw Material, Component, etc)")
    materials_supplied: List[str] = Field(description="Types of materials")
    contact: Dict[str, str] = Field(description="Contact information")
    quality_metrics: Dict[str, Any] = Field(description="Quality performance")
    status: str = Field(description="Status (approved, probation, rejected)")

class MaterialSpec(BaseModel):
    """Material catalog entry"""
    id: str = Field(description="Material ID (MAT-XXX)")
    name: str = Field(description="Material name")
    category: str = Field(description="Category (Raw Material, Fastener, etc)")
    specification: str = Field(description="Standard specification")
    unit: str = Field(description="Unit of measure")
    preferred_suppliers: List[str] = Field(description="Preferred supplier IDs")
    quality_requirements: Dict[str, Any] = Field(description="Quality specs")

class MaterialLot(BaseModel):
    """Material lot/batch received from supplier"""
    lot_number: str = Field(description="Lot/batch number")
    material_id: str = Field(description="Material ID (FK)")
    supplier_id: str = Field(description="Supplier ID (FK)")
    received_date: str = Field(description="Date received (YYYY-MM-DD)")
    quantity_received: float = Field(description="Quantity received")
    quantity_remaining: float = Field(description="Quantity remaining")
    unit: str = Field(description="Unit of measure")
    certificate_of_conformance: Optional[str] = Field(description="COC filename")
    inspection_results: Dict[str, Any] = Field(description="Incoming inspection")
    status: str = Field(description="Status (approved, rejected, quarantine)")
    quarantine: bool = Field(description="Quarantine flag")
    disposition: Optional[str] = Field(description="Disposition if rejected")

class Order(BaseModel):
    """Customer order"""
    id: str = Field(description="Order ID (ORD-XXXX)")
    order_number: str = Field(description="Customer PO number")
    customer: Dict[str, str] = Field(description="Customer info")
    items: List[Dict[str, Any]] = Field(description="Order line items")
    due_date: str = Field(description="Due date (YYYY-MM-DD)")
    status: str = Field(description="Status (pending, in_progress, completed)")
    priority: str = Field(description="Priority (high, normal, low)")
    shipping_date: Optional[str] = Field(description="Shipping date")
    total_value: float = Field(description="Total order value")

class ProductionBatch(BaseModel):
    """Production batch linking order to materials"""
    batch_id: str = Field(description="Batch ID (BATCH-YYYY-MMDD-XXX)")
    order_id: str = Field(description="Order ID (FK)")
    part_number: str = Field(description="Part number being produced")
    shift: str = Field(description="Shift (Day, Night)")
    operator: str = Field(description="Operator name")
    parts_produced: int = Field(description="Parts produced in batch")
    good_parts: int = Field(description="Good parts")
    scrap_parts: int = Field(description="Scrap parts")
    serial_range: Dict[str, int] = Field(description="{start: int, end: int}")
    materials_consumed: List[Dict[str, Any]] = Field(description="Materials used")
    process_parameters: Optional[Dict[str, Any]] = Field(description="Process params")

class Traceability(BaseModel):
    """Traceability info (denormalized for performance)"""
    batch_id: str = Field(description="Production batch ID")
    order_id: str = Field(description="Order ID")
    part_number: str = Field(description="Part number")
    customer: str = Field(description="Customer name (cached)")
    affected_serials: List[int] = Field(description="Affected serial numbers")
    shift: str = Field(description="Shift")
    operator: str = Field(description="Operator")

class MaterialUsed(BaseModel):
    """Material used in production (denormalized)"""
    material_id: str = Field(description="Material ID")
    material_name: str = Field(description="Material name (cached)")
    lot_number: str = Field(description="Lot number")
    supplier_id: str = Field(description="Supplier ID")
    supplier_name: str = Field(description="Supplier name (cached)")

class Investigation(BaseModel):
    """Quality issue investigation"""
    status: str = Field(description="Status (open, in_progress, closed)")
    root_cause_category: str = Field(description="Category (material, machine, process, operator)")
    root_cause_details: str = Field(description="Detailed explanation")
    suspected_lots: List[str] = Field(description="Suspected lot numbers")
    verification_tests: List[Dict[str, Any]] = Field(description="Tests performed")
    root_cause_confirmed: bool = Field(description="Root cause confirmed flag")
    investigator: str = Field(description="Person investigating")

class CostImpact(BaseModel):
    """Cost impact of quality issue"""
    scrap_cost: float = Field(description="Scrap cost")
    rework_cost: float = Field(description="Rework cost")
    downtime_cost: float = Field(description="Downtime cost")
    investigation_cost: float = Field(description="Investigation cost")
    total_cost: float = Field(description="Total cost")
    charged_to_supplier: bool = Field(description="Charged to supplier flag")
```

**Enhance existing QualityIssue model**:

```python
class QualityIssueEnhanced(BaseModel):
    """Enhanced quality issue with traceability"""
    # Existing fields
    issue_id: str = Field(description="Issue ID (QI-YYYY-MMDD-XXX)")
    type: str = Field(description="Type of defect")
    description: str = Field(description="Issue description")
    parts_affected: int = Field(ge=0, description="Number of affected parts")
    severity: str = Field(description="Severity level (Low, Medium, High)")
    detected_at: str = Field(description="Where detected")
    detected_by: str = Field(description="Who detected")

    # NEW fields
    traceability: Traceability = Field(description="Traceability information")
    materials_used: List[MaterialUsed] = Field(description="Materials in batch")
    investigation: Investigation = Field(description="Investigation details")
    corrective_actions: List[Dict[str, Any]] = Field(description="Corrective actions")
    preventive_actions: List[Dict[str, Any]] = Field(description="Preventive actions")
    supplier_notification: Dict[str, Any] = Field(description="Supplier notification")
    cost_impact: CostImpact = Field(description="Cost impact")
```

#### Task 1.2: Create TypeScript Interfaces
**File**: `frontend/src/types/api.ts`

Add corresponding TypeScript interfaces for all new Pydantic models (matching structure exactly).

#### Task 1.3: Generate Synthetic Data Functions
**File**: `shared/data_generator.py` (new file)

Create functions to generate realistic synthetic data:

```python
def generate_suppliers(count: int = 10) -> List[Dict[str, Any]]:
    """Generate synthetic supplier data"""
    # Steel suppliers, fastener suppliers, component suppliers
    # Include quality ratings, certifications
    pass

def generate_materials_catalog(machines: List[Dict]) -> List[Dict[str, Any]]:
    """Generate material catalog based on machine types"""
    # Steel bars for CNC, fasteners for assembly, etc.
    pass

def generate_material_lots(
    materials: List[Dict],
    suppliers: List[Dict],
    date_range: Tuple[str, str],
    lots_per_material: int = 5
) -> List[Dict[str, Any]]:
    """Generate material lot receipts"""
    # Create lots with inspection results
    # Randomly mark some as quarantine/rejected
    pass

def generate_orders(
    production_data: Dict[str, Any],
    customer_count: int = 5
) -> List[Dict[str, Any]]:
    """Generate customer orders spanning production dates"""
    # Create orders that production batches will fulfill
    # Mix of completed and in-progress
    pass

def create_production_batches(
    daily_production: Dict[str, Any],
    date: str,
    machine: str,
    orders: List[Dict],
    material_lots: List[Dict]
) -> List[Dict[str, Any]]:
    """Convert daily production totals into batches"""
    # Split by shift (Day/Night)
    # Assign serial number ranges
    # Link to orders and materials
    pass

def enrich_quality_issue(
    issue: Dict[str, Any],
    batch: Dict[str, Any],
    orders: List[Dict],
    material_lots: List[Dict],
    suppliers: List[Dict]
) -> Dict[str, Any]:
    """Enrich quality issue with traceability data"""
    # Add traceability object
    # Add materials_used with supplier info
    # Add investigation structure
    # Add cost_impact
    pass
```

#### Task 1.4: Update Data Initialization
**File**: `shared/data.py`

Modify `generate_production_data()`:

```python
def generate_production_data(days: int = 30, machines=None, shifts=None) -> Dict[str, Any]:
    """Generate production data with v2.0 schema"""

    # Generate master data
    suppliers = generate_suppliers(count=10)
    materials_catalog = generate_materials_catalog(machines or MACHINES)
    material_lots = generate_material_lots(
        materials=materials_catalog,
        suppliers=suppliers,
        date_range=(start_date, end_date)
    )

    # Generate existing production data (v1.0 logic)
    production = {...}  # existing logic

    # Generate orders based on production
    orders = generate_orders(production, customer_count=5)

    # Enhance production with batches
    for date, machines_data in production.items():
        for machine_name, metrics in machines_data.items():
            # Create batches
            batches = create_production_batches(
                daily_production=metrics,
                date=date,
                machine=machine_name,
                orders=orders,
                material_lots=material_lots
            )
            metrics['batches'] = batches

            # Enrich quality issues
            for issue in metrics.get('quality_issues', []):
                batch = find_batch_for_issue(issue, batches)
                enrich_quality_issue(
                    issue=issue,
                    batch=batch,
                    orders=orders,
                    material_lots=material_lots,
                    suppliers=suppliers
                )

    # Return v2.0 schema
    return {
        '_meta': {
            'schema_version': '2.0',
            'generated_at': datetime.utcnow().isoformat(),
            'start_date': start_date,
            'end_date': end_date
        },
        'suppliers': suppliers,
        'materials_catalog': materials_catalog,
        'material_lots': material_lots,
        'orders': orders,
        'machines': machines or MACHINES,
        'shifts': shifts or SHIFTS,
        'production': production,
        'generated_at': datetime.utcnow().isoformat(),
        'start_date': start_date,
        'end_date': end_date
    }
```

#### Task 1.5: Test Data Generation
**File**: `tests/test_data_generation.py` (new)

```python
def test_v2_schema_generation():
    """Test that v2.0 data generates correctly"""
    data = generate_production_data(days=7)

    # Verify top-level structure
    assert '_meta' in data
    assert data['_meta']['schema_version'] == '2.0'
    assert 'suppliers' in data
    assert 'material_lots' in data
    assert 'orders' in data

    # Verify suppliers have required fields
    assert len(data['suppliers']) > 0
    supplier = data['suppliers'][0]
    assert 'id' in supplier
    assert 'quality_metrics' in supplier

    # Verify batches exist
    first_date = list(data['production'].keys())[0]
    first_machine = list(data['production'][first_date].keys())[0]
    assert 'batches' in data['production'][first_date][first_machine]

    # Verify quality issues have traceability
    for date, machines in data['production'].items():
        for machine, metrics in machines.items():
            for issue in metrics.get('quality_issues', []):
                assert 'traceability' in issue
                assert 'materials_used' in issue
                assert 'investigation' in issue
                assert 'cost_impact' in issue
```

---

### Phase 2: API Layer (New Endpoints)
**Goal**: Expose new data through REST APIs

#### Task 2.1: Supplier APIs
**File**: `backend/src/api/routes/suppliers.py` (new)

```python
@router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    """Get all suppliers"""
    data = await load_data_async()
    return data.get('suppliers', [])

@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(supplier_id: str):
    """Get supplier by ID"""
    data = await load_data_async()
    supplier = next(
        (s for s in data.get('suppliers', []) if s['id'] == supplier_id),
        None
    )
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.get("/suppliers/{supplier_id}/quality")
async def get_supplier_quality(
    supplier_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get quality issues linked to supplier"""
    # Use trace_forward_from_supplier() logic
    pass

@router.get("/suppliers/{supplier_id}/lots")
async def get_supplier_lots(supplier_id: str):
    """Get material lots from supplier"""
    data = await load_data_async()
    lots = [
        lot for lot in data.get('material_lots', [])
        if lot['supplier_id'] == supplier_id
    ]
    return lots
```

#### Task 2.2: Traceability APIs
**File**: `backend/src/api/routes/traceability.py` (new)

```python
@router.get("/traceability/backward/{issue_id}")
async def trace_backward(issue_id: str):
    """Trace backward from quality issue to root cause"""
    # Implement trace_backward_from_issue() logic
    pass

@router.get("/traceability/forward/{supplier_id}")
async def trace_forward(
    supplier_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Trace forward from supplier to quality impact"""
    # Implement trace_forward_from_supplier() logic
    pass

@router.get("/traceability/lot/{lot_number}")
async def trace_lot(lot_number: str):
    """Trace material lot usage"""
    # Implement trace_material_lot() logic
    pass

@router.get("/traceability/serial/{serial}")
async def trace_serial(serial: int):
    """Trace individual part by serial number"""
    # Implement trace_serial_number() logic
    pass
```

#### Task 2.3: Enhance Existing Quality API
**File**: `backend/src/api/routes/metrics.py`

Add query parameters to existing `/api/metrics/quality` endpoint:

```python
@router.get("/metrics/quality")
async def get_quality_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    machine: Optional[str] = None,
    severity: Optional[str] = None,
    # NEW parameters
    supplier_id: Optional[str] = None,
    order_id: Optional[str] = None,
    lot_number: Optional[str] = None,
    root_cause: Optional[str] = None,
):
    """Get quality metrics with enhanced filtering"""
    # Filter by new parameters if provided
    pass
```

#### Task 2.4: Register New Routes
**File**: `backend/src/api/main.py`

```python
from api.routes import suppliers, traceability

app.include_router(suppliers.router, prefix="/api", tags=["suppliers"])
app.include_router(traceability.router, prefix="/api", tags=["traceability"])
```

---

### Phase 3: Frontend Integration
**Goal**: Display traceability data in UI

#### Task 3.1: Create API Client Functions
**File**: `frontend/src/services/api.ts`

```typescript
export async function getSuppliers(): Promise<Supplier[]> {
  const response = await fetch(`${API_BASE_URL}/api/suppliers`);
  return response.json();
}

export async function getSupplierQuality(
  supplierId: string,
  startDate?: string,
  endDate?: string
): Promise<SupplierQualityMetrics> {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);

  const response = await fetch(
    `${API_BASE_URL}/api/suppliers/${supplierId}/quality?${params}`
  );
  return response.json();
}

export async function traceBackward(issueId: string): Promise<TraceResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/traceability/backward/${issueId}`
  );
  return response.json();
}
```

#### Task 3.2: Create Traceability Components
**File**: `frontend/src/components/traceability/` (new directory)

Components to create:
- `TraceabilityViewer.tsx` - Main traceability display
- `SupplierCard.tsx` - Supplier information card
- `MaterialLotCard.tsx` - Material lot details
- `BatchCard.tsx` - Production batch info
- `TraceabilityFlow.tsx` - Visual flowchart

#### Task 3.3: Enhance Quality Dashboard
**File**: `frontend/src/pages/Quality.tsx`

Add traceability panel to quality issues:

```tsx
{qualityData.issues.map(issue => (
  <div key={issue.issue_id} className="quality-issue-card">
    {/* Existing issue display */}

    {/* NEW: Traceability section */}
    {issue.traceability && (
      <TraceabilityPanel issue={issue} />
    )}

    {/* NEW: Materials section */}
    {issue.materials_used && (
      <MaterialsUsedList materials={issue.materials_used} />
    )}

    {/* NEW: Investigation section */}
    {issue.investigation && (
      <InvestigationStatus investigation={issue.investigation} />
    )}
  </div>
))}
```

#### Task 3.4: Create Supplier Management Page
**File**: `frontend/src/pages/Suppliers.tsx` (new)

```tsx
export default function Suppliers() {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);

  useEffect(() => {
    getSuppliers().then(setSuppliers);
  }, []);

  return (
    <div>
      <h1>Supplier Management</h1>

      <div className="supplier-grid">
        {suppliers.map(supplier => (
          <SupplierCard
            key={supplier.id}
            supplier={supplier}
            onClick={() => navigate(`/suppliers/${supplier.id}`)}
          />
        ))}
      </div>
    </div>
  );
}
```

Add route:
```tsx
// App.tsx
<Route path="/suppliers" element={<Suppliers />} />
<Route path="/suppliers/:id" element={<SupplierDetail />} />
```

---

### Phase 4: Testing & Validation
**Goal**: Ensure everything works correctly

#### Task 4.1: Backend Tests
**File**: `tests/test_traceability.py` (new)

```python
def test_backward_trace():
    """Test backward trace from quality issue"""
    # Create test data with known issue
    # Trace backward
    # Verify supplier is identified
    pass

def test_forward_trace():
    """Test forward trace from supplier"""
    # Create test data
    # Trace forward from supplier
    # Verify all issues found
    pass

def test_lot_quarantine():
    """Test material lot quarantine identification"""
    # Create test data with defective lot
    # Trace lot
    # Verify quarantine recommendation
    pass
```

#### Task 4.2: Frontend Tests
**File**: `frontend/src/components/traceability/__tests__/`

Test components render correctly with mock data.

#### Task 4.3: Integration Tests
**File**: `tests/test_integration.py` (new)

Test complete end-to-end flows:
- Generate data → API call → Frontend display
- Backward trace → Display results
- Supplier quality scorecard → Display metrics

#### Task 4.4: Backward Compatibility Tests
Verify existing APIs still work:
- `/api/metrics/oee` returns same structure
- `/api/metrics/quality` returns issues (with optional new fields)
- Existing frontend pages work without changes

---

### Phase 5: Migration & Deployment
**Goal**: Deploy to production

#### Task 5.1: Create Migration Script
**File**: `scripts/migrate_to_v2.py` (new)

```python
async def migrate_production_data():
    """Migrate existing production.json to v2.0 schema"""

    # Load existing data
    old_data = await load_data_async()

    if old_data.get('_meta', {}).get('schema_version') == '2.0':
        print("Already on v2.0 schema")
        return

    # Generate synthetic masters
    suppliers = generate_suppliers()
    materials = generate_materials_catalog(old_data['machines'])
    material_lots = generate_material_lots(...)
    orders = generate_orders(old_data['production'])

    # Enhance production with batches
    for date, machines in old_data['production'].items():
        for machine, metrics in machines.items():
            batches = create_production_batches(...)
            metrics['batches'] = batches

            for issue in metrics.get('quality_issues', []):
                enrich_quality_issue(issue, ...)

    # Save v2.0 data
    new_data = {
        '_meta': {'schema_version': '2.0', ...},
        'suppliers': suppliers,
        'material_lots': material_lots,
        'orders': orders,
        **old_data
    }

    await save_data_async(new_data)
    print("Migration complete!")
```

#### Task 5.2: Update Setup Command
**File**: `backend/src/api/routes/data.py`

Modify `/api/setup` to generate v2.0 data by default:

```python
@router.post("/setup")
async def setup_data(request: SetupRequest):
    """Generate production data (v2.0 schema)"""
    data = await initialize_data_async(days=request.days)
    # Now generates v2.0 data automatically
    return {"message": "Data generated", "schema_version": "2.0"}
```

#### Task 5.3: Documentation Updates
Update:
- README.md - mention new traceability features
- API documentation - document new endpoints
- User guide - explain how to use traceability

#### Task 5.4: Deploy
1. Run migration script on production data
2. Deploy backend with new routes
3. Deploy frontend with new pages
4. Verify everything works

---

## Data Flow Diagrams

### Backward Trace Flow

```
User clicks "Trace" on Quality Issue QI-2025-1003-001
                    ↓
Frontend: GET /api/traceability/backward/QI-2025-1003-001
                    ↓
Backend: Find issue in production data
                    ↓
Backend: Extract traceability.batch_id → "BATCH-2025-1003-001"
                    ↓
Backend: Find batch in production[date][machine].batches
                    ↓
Backend: Extract batch.order_id → "ORD-1001"
Backend: Extract batch.materials_consumed → [{lot_number: "LOT-2025-001"}]
                    ↓
Backend: Lookup order in orders[] → get customer
Backend: Lookup lot in material_lots[] → get supplier_id
Backend: Lookup supplier in suppliers[] → get supplier name
                    ↓
Backend: Return complete trace result
                    ↓
Frontend: Display traceability flow visualization
```

### Forward Trace Flow

```
User selects Supplier "Acme Steel Co. (SUP-001)"
                    ↓
Frontend: GET /api/suppliers/SUP-001/quality?start=2025-10-01&end=2025-10-31
                    ↓
Backend: Find all material_lots where supplier_id = "SUP-001"
        → Extract lot_numbers: ["LOT-2025-001", "LOT-2025-015", ...]
                    ↓
Backend: Iterate through production[date][machine].batches
        → Find batches using these lot_numbers
        → Collect batch_ids
                    ↓
Backend: Iterate through production[date][machine].quality_issues
        → Filter issues where traceability.batch_id in batch_ids
        → Aggregate: count, total_cost, severity_breakdown
                    ↓
Backend: Return supplier quality metrics
                    ↓
Frontend: Display supplier scorecard with metrics
```

---

## Key Implementation Notes

### 1. Denormalization Strategy

When enriching quality issues, cache frequently accessed data:

```python
def enrich_quality_issue(issue, batch, orders, material_lots, suppliers):
    # Find order
    order = find_order(batch['order_id'], orders)

    # Find materials and suppliers
    materials_used = []
    for material in batch['materials_consumed']:
        lot = find_lot(material['lot_number'], material_lots)
        supplier = find_supplier(lot['supplier_id'], suppliers)

        materials_used.append({
            'material_id': material['material_id'],
            'lot_number': material['lot_number'],
            'supplier_id': supplier['id'],
            'supplier_name': supplier['name']  # ← Cached!
        })

    # Add traceability object
    issue['traceability'] = {
        'batch_id': batch['batch_id'],
        'order_id': order['id'],
        'customer': order['customer']['name'],  # ← Cached!
        'affected_serials': [...],
        'shift': batch['shift'],
        'operator': batch['operator']
    }

    issue['materials_used'] = materials_used
```

**Why cache?**
- Quality issues are queried frequently
- Avoids lookups in suppliers[], orders[] on every query
- Slight data duplication acceptable for massive performance gain

**Keep in sync:**
- When supplier name changes, update all quality issues referencing it
- Run periodic "sync" job to ensure consistency

### 2. Batch Assignment Logic

Split daily production into batches:

```python
def create_production_batches(daily_production, date, machine, orders, materials):
    batches = []

    # Split by shift
    shifts_data = daily_production.get('shifts', {})
    serial_counter = 1000  # Starting serial

    for shift_name, shift_metrics in shifts_data.items():
        parts = shift_metrics['parts_produced']

        # Assign to order (round-robin or based on priority)
        order = assign_to_order(orders, date)

        # Select materials (based on machine type)
        materials_consumed = select_materials(machine, materials, parts)

        batch = {
            'batch_id': f"BATCH-{date}-{machine}-{shift_name}",
            'order_id': order['id'],
            'part_number': order['items'][0]['part_number'],
            'shift': shift_name,
            'operator': generate_operator_name(),
            'parts_produced': parts,
            'good_parts': shift_metrics['good_parts'],
            'scrap_parts': shift_metrics['scrap_parts'],
            'serial_range': {
                'start': serial_counter,
                'end': serial_counter + parts - 1
            },
            'materials_consumed': materials_consumed
        }

        batches.append(batch)
        serial_counter += parts

    return batches
```

### 3. Backward Compatibility

Ensure v1.0 clients don't break:

```python
# Option 1: API versioning
@router.get("/v1/metrics/quality")  # Old endpoint
async def get_quality_v1(...):
    return old_format_response()

@router.get("/v2/metrics/quality")  # New endpoint
async def get_quality_v2(...):
    return new_format_response()

# Option 2: Response transformation
@router.get("/metrics/quality")
async def get_quality(..., version: str = "v2"):
    issues = fetch_issues(...)

    if version == "v1":
        # Strip new fields
        return [{
            'type': i['type'],
            'severity': i['severity'],
            'parts_affected': i['parts_affected'],
            'description': i['description'],
            'date': i.get('traceability', {}).get('date', ''),
            'machine': i.get('machine', '')
        } for i in issues]
    else:
        # Return full v2.0 format
        return issues
```

**Recommendation**: Use Option 2 with default `version="v2"` to encourage adoption.

---

## Success Criteria

### Phase 1 Complete When:
- [x] All Pydantic models created and validated
- [x] TypeScript interfaces match Pydantic models
- [x] Data generation creates v2.0 schema correctly
- [x] `POST /api/setup` generates data with suppliers, orders, batches
- [x] Quality issues have traceability objects
- [x] Existing APIs still return data (backward compatible)

### Phase 2 Complete When:
- [x] `/api/suppliers` returns supplier list
- [x] `/api/suppliers/{id}/quality` returns quality metrics
- [x] `/api/traceability/backward/{issue_id}` traces to supplier
- [x] `/api/traceability/forward/{supplier_id}` shows impact
- [x] All endpoints have proper error handling
- [x] API tests pass

### Phase 3 Complete When:
- [x] Frontend can fetch and display suppliers
- [x] Quality dashboard shows traceability info
- [x] New Supplier Management page works
- [x] Traceability visualization renders
- [x] No console errors in browser

### Phase 4 Complete When:
- [x] All backend tests pass
- [x] All frontend tests pass
- [x] Integration tests pass
- [x] Backward compatibility verified
- [x] Performance acceptable (API responses < 500ms)

### Phase 5 Complete When:
- [x] Migration script tested on copy of production data
- [x] Migration runs successfully in production
- [x] All features working in production
- [x] Documentation updated
- [x] No regressions in existing features

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 1-2 weeks | None |
| Phase 2 | 1 week | Phase 1 complete |
| Phase 3 | 1-2 weeks | Phase 2 complete |
| Phase 4 | 3-5 days | Phase 3 complete |
| Phase 5 | 2-3 days | Phase 4 complete |
| **Total** | **4-6 weeks** | - |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data file size grows too large | Performance | Implement pagination, consider database |
| Denormalized data gets out of sync | Data integrity | Add validation, periodic sync job |
| Breaking changes to existing APIs | Production issues | Thorough testing, API versioning |
| Complex queries slow on large data | UX issues | Add indexes, optimize queries, caching |
| Migration fails in production | Data loss | Backup before migration, test on copy first |

---

## Next Steps

1. **Review & Approve**: Stakeholder sign-off on this plan
2. **Set Up Dev Environment**: Ensure all tools installed
3. **Create Feature Branch**: `git checkout -b feature/traceability-v2`
4. **Start Phase 1**: Begin with Pydantic model creation
5. **Daily Standups**: Track progress against tasks

---

**Ready to start implementation?** Let's begin with Phase 1, Task 1.1! 🚀
