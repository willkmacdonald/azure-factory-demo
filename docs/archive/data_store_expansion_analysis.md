# Data Store Expansion Analysis: Quality-Order-Supplier Linkage

## Executive Summary

**Current State**: Quality issues are isolated events with no supply chain traceability
**Target State**: Full traceability from supplier → materials → orders → production → quality issues
**Approach**: Hybrid normalized/denormalized schema with backward compatibility

---

## 1. Current Architecture (v1.0)

```
┌─────────────────────────────────────────────────────────────┐
│ CURRENT DATA MODEL                                          │
│                                                              │
│  Production Data (Hierarchical)                             │
│  └── Date                                                    │
│      └── Machine                                             │
│          ├── Parts Produced (aggregate)                     │
│          ├── Quality Issues (orphaned)                      │
│          │   ├── type                                       │
│          │   ├── severity                                   │
│          │   └── parts_affected                             │
│          └── Downtime Events                                │
│                                                              │
│  ❌ NO supplier information                                 │
│  ❌ NO order tracking                                       │
│  ❌ NO material traceability                                │
│  ❌ NO batch/lot tracking                                   │
│  ❌ NO root cause linkage                                   │
└─────────────────────────────────────────────────────────────┘
```

**Limitations:**
- Cannot answer: "Which supplier caused this defect?"
- Cannot answer: "Which customer orders are affected?"
- Cannot answer: "Which material lot is defective?"
- Cannot answer: "What's the total cost impact on Order #1001?"
- Cannot perform supplier quality analysis
- Cannot implement lot quarantine/recall

---

## 2. Proposed Architecture (v2.0)

```
┌─────────────────────────────────────────────────────────────────────┐
│ EXPANDED DATA MODEL (Hybrid Approach)                               │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ MASTER DATA (Normalized - Single Source of Truth)           │   │
│  │                                                              │   │
│  │  Suppliers                  Orders                           │   │
│  │  ├── Contact info          ├── Customer                     │   │
│  │  ├── Certifications        ├── Part numbers                 │   │
│  │  └── Quality metrics       └── Quantities/dates             │   │
│  │                                                              │   │
│  │  Materials Catalog         Material Lots                    │   │
│  │  ├── Specifications        ├── Lot numbers                  │   │
│  │  ├── Requirements          ├── Inspection results           │   │
│  │  └── Preferred suppliers   └── Quarantine status            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                       │
│                              │ References                            │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ TRANSACTIONAL DATA (Enhanced with References)               │   │
│  │                                                              │   │
│  │  Production (by Date → Machine)                             │   │
│  │  └── Batches (NEW)                                          │   │
│  │      ├── batch_id                                           │   │
│  │      ├── order_id ──────────┐ (FK)                          │   │
│  │      ├── shift, operator    │                               │   │
│  │      ├── serial ranges      │                               │   │
│  │      └── materials_consumed │                               │   │
│  │          ├── material_id ───┼─────┐ (FK)                    │   │
│  │          └── lot_number ────┼─────┼─────┐ (FK)              │   │
│  │                             │     │     │                    │   │
│  │  └── Quality Issues (ENHANCED)    │     │                   │   │
│  │      ├── batch_id ──────────┘     │     │                   │   │
│  │      ├── order_id (derived)       │     │                   │   │
│  │      ├── affected_serials         │     │                   │   │
│  │      │                             │     │                   │   │
│  │      ├── traceability (denorm)    │     │                   │   │
│  │      │   ├── order_number ────────┘     │                   │   │
│  │      │   ├── materials_used ────────────┘                   │   │
│  │      │   │   ├── lot_number ────────────────────┘           │   │
│  │      │   │   └── supplier_id/name (cached)                  │   │
│  │      │   └── customer (cached)                              │   │
│  │      │                                                       │   │
│  │      ├── investigation (NEW)                                │   │
│  │      │   ├── root_cause_category                            │   │
│  │      │   ├── suspected_lots                                 │   │
│  │      │   └── verification_tests                             │   │
│  │      │                                                       │   │
│  │      ├── corrective_actions (NEW)                           │   │
│  │      ├── preventive_actions (NEW)                           │   │
│  │      │                                                       │   │
│  │      ├── supplier_notification (NEW)                        │   │
│  │      │   ├── supplier_capa_number                           │   │
│  │      │   └── response                                       │   │
│  │      │                                                       │   │
│  │      └── cost_impact (NEW)                                  │   │
│  │          ├── scrap_cost                                     │   │
│  │          ├── rework_cost                                    │   │
│  │          └── charged_to_supplier                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Entity Relationships

```
                        SUPPLY CHAIN FLOW

Supplier ────supplies───> Material Lot ────consumed by───> Production Batch
  │                            │                                  │
  │                            │                                  │
  │                            │                              produces
  │                            │                                  │
  │                            │                                  ▼
  │                            │                              Parts (Serials)
  │                            │                                  │
  │                            │                                  │
  │                            └──────────linked to──────────┐    │
  │                                                           │    │
  └────────────────notified of───────────┐                   │    │
                                         ▼                   ▼    ▼
Customer ──places──> Order ──fulfilled by──> Quality Issue (with full trace)
                       │                           │
                       │                           │
                       └────impacted by────────────┘


                    TRACEABILITY QUERIES

FORWARD TRACE (Supplier → Impact):
  Supplier → Material Lots → Batches → Parts → Quality Issues → Affected Orders

BACKWARD TRACE (Defect → Root Cause):
  Quality Issue → Batch → Materials → Lot → Supplier

IMPACT ANALYSIS:
  Material Lot → All Batches Using Lot → All Quality Issues → Total Cost
```

---

## 4. Key Additions to Data Model

### 4.1 New Root Entities

```typescript
// Reference data (normalized)
interface DataStore {
  // NEW
  suppliers: Supplier[]
  materials_catalog: MaterialSpec[]
  material_lots: MaterialLot[]
  orders: Order[]

  // EXISTING (unchanged)
  machines: Machine[]
  shifts: Shift[]
  production: { [date: string]: { [machine: string]: ProductionData } }
}
```

### 4.2 New Nested Entities

```typescript
// Inside production[date][machine]
interface ProductionData {
  // NEW
  batches: ProductionBatch[]  // Track production in batches

  // EXISTING
  parts_produced: number
  quality_issues: QualityIssue[]  // Enhanced with traceability
  downtime_events: DowntimeEvent[]
  shifts: { [shift: string]: ShiftMetrics }
}
```

### 4.3 Enhanced Quality Issue

```typescript
interface QualityIssue {
  // EXISTING
  type: string
  description: string
  parts_affected: number
  severity: string

  // NEW - Core linkage
  issue_id: string
  batch_id: string                  // Links to batch
  detected_at: string               // Where found
  detected_by: string               // Who found it

  // NEW - Traceability (denormalized for performance)
  traceability: {
    batch_id: string
    order_id: string
    part_number: string
    customer: string
    affected_serials: number[]
    shift: string
    operator: string
  }

  // NEW - Material linkage
  materials_used: Array<{
    material_id: string
    material_name: string
    lot_number: string
    supplier_id: string
    supplier_name: string           // Cached from supplier master
  }>

  // NEW - Investigation
  investigation: {
    status: 'open' | 'in_progress' | 'closed'
    root_cause_category: 'material' | 'machine' | 'process' | 'operator' | 'design'
    root_cause_details: string
    suspected_lots: string[]
    verification_tests: Test[]
    root_cause_confirmed: boolean
    investigator: string
  }

  // NEW - Actions
  corrective_actions: Action[]
  preventive_actions: Action[]

  // NEW - Supplier communication
  supplier_notification: {
    notified: boolean
    notification_date?: string
    supplier_response?: string
    supplier_capa_number?: string
  }

  // NEW - Financial impact
  cost_impact: {
    scrap_cost: number
    rework_cost: number
    downtime_cost: number
    investigation_cost: number
    total_cost: number
    charged_to_supplier: boolean
  }
}
```

---

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Add reference data without breaking existing functionality

- [ ] Create `Supplier` Pydantic model + TypeScript interface
- [ ] Create `MaterialLot` model + interface
- [ ] Create `Order` model + interface
- [ ] Add top-level keys to data store: `suppliers`, `material_lots`, `orders`
- [ ] Generate synthetic data for 5-10 suppliers
- [ ] Generate synthetic material lots
- [ ] Generate synthetic orders spanning date range
- [ ] Update `initialize_data_async()` to include new entities
- [ ] **Verify**: Existing APIs still work, no breaking changes

### Phase 2: Batch Tracking (Week 2-3)
**Goal**: Link production to orders and materials

- [ ] Create `ProductionBatch` model + interface
- [ ] Modify production data structure to include `batches` array
- [ ] Update data generator to create batches
- [ ] Link batches to orders (many batches → one order)
- [ ] Link batches to material lots (batch consumes multiple lots)
- [ ] Add serial number ranges to batches
- [ ] **Verify**: Can trace from batch → order and batch → materials

### Phase 3: Quality Enhancement (Week 3-4)
**Goal**: Link quality issues to supply chain

- [ ] Enhance `QualityIssue` model with new fields
- [ ] Add `batch_id` to quality issues
- [ ] Add `traceability` object (denormalized)
- [ ] Add `materials_used` array
- [ ] Add `investigation` object
- [ ] Add `corrective_actions` / `preventive_actions`
- [ ] Add `supplier_notification`
- [ ] Add `cost_impact`
- [ ] Create data enrichment function to populate denormalized fields
- [ ] **Verify**: Quality issues have full supply chain context

### Phase 4: API Expansion (Week 4-5)
**Goal**: Expose new data through APIs

**New Endpoints**:
```python
# Supplier APIs
GET    /api/suppliers
GET    /api/suppliers/{id}
GET    /api/suppliers/{id}/quality-metrics
GET    /api/suppliers/{id}/lots
GET    /api/suppliers/{id}/issues

# Order APIs
GET    /api/orders
GET    /api/orders/{id}
GET    /api/orders/{id}/batches
GET    /api/orders/{id}/quality

# Material APIs
GET    /api/materials/lots
GET    /api/materials/lots/{lot_number}
GET    /api/materials/lots/{lot_number}/usage
GET    /api/materials/lots/{lot_number}/issues

# Traceability APIs
GET    /api/traceability/forward/{batch_id}
GET    /api/traceability/backward/{serial_number}
GET    /api/traceability/lot/{lot_number}
GET    /api/traceability/supplier/{supplier_id}

# Enhanced Quality APIs (add query params)
GET    /api/metrics/quality?supplier_id=SUP-001
GET    /api/metrics/quality?order_id=ORD-1001
GET    /api/metrics/quality?lot_number=LOT-2025-001
GET    /api/metrics/quality?root_cause=material
```

### Phase 5: Analytics (Week 5-6)
**Goal**: Provide actionable insights

- [ ] Supplier quality scorecard
  - Defect rate (PPM) by supplier
  - On-time delivery %
  - Cost of quality by supplier
  - Trending over time

- [ ] Root cause Pareto analysis
  - Issues by category (material/machine/process/operator)
  - Top 3 suppliers with quality issues
  - Top 3 material lots with issues

- [ ] Cost of quality dashboard
  - Total cost by supplier
  - Cost by order
  - Cost trend over time
  - Scrap vs. rework split

### Phase 6: Frontend Integration (Week 6-8)
**Goal**: Visualize traceability

**New Pages**:
1. **Supplier Management** (`/suppliers`)
   - List all suppliers with quality ratings
   - Drill into supplier details
   - View quality issues by supplier
   - View material lots from supplier

2. **Order Tracking** (`/orders`)
   - List all orders with status
   - Drill into order production details
   - View batches fulfilling order
   - View quality issues affecting order

3. **Quality Investigation** (enhance `/quality`)
   - Add traceability panel to each issue
   - Show affected order/customer
   - Show material lots involved
   - Show supplier info
   - Track investigation status
   - Log corrective/preventive actions

4. **Traceability Viewer** (`/traceability`)
   - Interactive flowchart
   - Input: Lot number, batch ID, serial number, or order ID
   - Output: Full supply chain visualization
   - Highlight quality issues in flow

**Component Examples**:
```tsx
// Traceability Timeline
<TraceabilityFlow
  batchId="BATCH-2025-1003-001"
  highlightIssues={true}
/>

// Supplier Quality Card
<SupplierQualityCard
  supplierId="SUP-001"
  dateRange={{ start: '2025-10-01', end: '2025-11-01' }}
  metrics={['defect_rate', 'on_time_delivery', 'cost_of_quality']}
/>

// Quality Issue Investigation Panel
<QualityInvestigation
  issueId="QI-2025-1003-001"
  showActions={true}
  allowEdit={true}
/>
```

---

## 6. Migration Strategy

### 6.1 Data Migration Function

```python
async def migrate_to_schema_v2(storage_mode: str = 'local') -> Dict[str, Any]:
    """
    Migrate existing v1.0 data to v2.0 schema

    Strategy:
    1. Load existing production data
    2. Generate synthetic suppliers, materials, orders
    3. Create batches from daily production totals
    4. Link quality issues to batches
    5. Enrich quality issues with traceability
    6. Save migrated data
    """

    # Load v1.0 data
    old_data = await load_data_async()
    if not old_data:
        raise ValueError("No existing data to migrate")

    # Generate master data
    suppliers = generate_suppliers(count=10)
    materials = generate_materials_catalog(machines=old_data['machines'])
    material_lots = generate_material_lots(
        materials=materials,
        suppliers=suppliers,
        date_range=(old_data['start_date'], old_data['end_date'])
    )
    orders = generate_orders(
        production_data=old_data['production'],
        customer_count=5
    )

    # Enhance production data
    for date, machines in old_data['production'].items():
        for machine_name, metrics in machines.items():
            # Create batches
            batches = create_batches_from_metrics(
                metrics=metrics,
                date=date,
                machine=machine_name,
                orders=orders,
                materials=material_lots
            )
            metrics['batches'] = batches

            # Enhance quality issues
            for issue in metrics.get('quality_issues', []):
                batch = assign_issue_to_batch(issue, batches)
                enrich_quality_issue(
                    issue=issue,
                    batch=batch,
                    orders=orders,
                    materials=material_lots,
                    suppliers=suppliers
                )

    # Assemble v2.0 data
    new_data = {
        '_meta': {
            'schema_version': '2.0',
            'migrated_at': datetime.utcnow().isoformat(),
            'migrated_from': 'v1.0'
        },
        'suppliers': suppliers,
        'materials_catalog': materials,
        'material_lots': material_lots,
        'orders': orders,
        'machines': old_data['machines'],
        'shifts': old_data['shifts'],
        'production': old_data['production'],
        'generated_at': old_data['generated_at'],
        'start_date': old_data['start_date'],
        'end_date': old_data['end_date']
    }

    # Save migrated data
    await save_data_async(new_data)

    return new_data
```

### 6.2 Backward Compatibility

Ensure v1.0 API responses still work:

```python
# Option 1: Version the API
GET /api/v1/metrics/quality  # Returns old format
GET /api/v2/metrics/quality  # Returns new format

# Option 2: Use response transformers
def transform_to_v1_response(v2_data: Dict) -> Dict:
    """Strip new fields for backward compatibility"""
    return {
        'type': v2_data['type'],
        'description': v2_data['description'],
        'parts_affected': v2_data['parts_affected'],
        'severity': v2_data['severity'],
        'date': v2_data.get('traceability', {}).get('date', v2_data['date']),
        'machine': v2_data.get('traceability', {}).get('machine', '')
    }
```

---

## 7. Query Examples

### 7.1 Find All Issues from a Supplier

```python
def find_issues_by_supplier(supplier_id: str) -> List[QualityIssue]:
    issues = []
    for date, machines in production.items():
        for machine, metrics in machines.items():
            for issue in metrics['quality_issues']:
                if any(m['supplier_id'] == supplier_id
                       for m in issue.get('materials_used', [])):
                    issues.append(issue)
    return issues
```

### 7.2 Trace Backward from Defect to Supplier

```python
def trace_backward(issue_id: str) -> Dict:
    issue = find_issue_by_id(issue_id)
    batch = find_batch_by_id(issue['batch_id'])
    order = find_order_by_id(batch['order_id'])
    materials = [find_material_lot(m['lot_number'])
                 for m in batch['materials_consumed']]
    suppliers = [find_supplier(m['supplier_id']) for m in materials]

    return {
        'issue': issue,
        'batch': batch,
        'order': order,
        'materials': materials,
        'suppliers': suppliers,
        'timeline': build_timeline(issue, batch, materials)
    }
```

### 7.3 Calculate Supplier Quality Score

```python
def calculate_supplier_quality(supplier_id: str,
                                date_range: Tuple[str, str]) -> Dict:
    # Find all lots from supplier
    lots = [lot for lot in material_lots
            if lot['supplier_id'] == supplier_id]

    # Find all issues linked to those lots
    issues = []
    for lot in lots:
        issues.extend(find_issues_by_lot(lot['lot_number']))

    # Calculate metrics
    total_parts_affected = sum(i['parts_affected'] for i in issues)
    total_cost = sum(i['cost_impact']['total_cost'] for i in issues)
    high_severity_count = sum(1 for i in issues if i['severity'] == 'High')

    # Calculate defect rate (parts per million)
    total_parts_produced = calculate_total_production(lots)
    defect_rate_ppm = (total_parts_affected / total_parts_produced) * 1_000_000

    return {
        'supplier_id': supplier_id,
        'total_issues': len(issues),
        'total_parts_affected': total_parts_affected,
        'defect_rate_ppm': defect_rate_ppm,
        'high_severity_issues': high_severity_count,
        'total_cost_impact': total_cost,
        'lots_received': len(lots),
        'rating': calculate_rating(defect_rate_ppm, high_severity_count)
    }
```

---

## 8. Benefits of Expanded Model

### 8.1 Operational Benefits
- **Root Cause Analysis**: Quickly identify if quality issues stem from specific suppliers or material lots
- **Lot Quarantine**: Immediately stop using suspected material lots
- **Customer Impact**: Know which customer orders are affected by quality issues
- **Supplier Accountability**: Track supplier performance and enforce quality requirements
- **Corrective Actions**: Systematically track and close improvement actions

### 8.2 Financial Benefits
- **Cost Recovery**: Charge suppliers for material-caused defects
- **Cost Visibility**: See total cost of quality by supplier, order, or time period
- **Waste Reduction**: Identify and eliminate root causes faster
- **Informed Purchasing**: Make data-driven supplier selection decisions

### 8.3 Compliance Benefits
- **Traceability**: Meet regulatory requirements (FDA, ISO 9001, AS9100)
- **Audit Trail**: Complete record of investigations and actions
- **Recall Capability**: Quickly identify affected products if recall needed
- **Customer Confidence**: Demonstrate quality management to customers

---

## 9. Recommended Approach: Hybrid Schema

After deep analysis, I recommend **Option C: Hybrid Approach**

**Rationale**:
1. **Normalized masters** (suppliers, materials, orders) provide single source of truth
2. **Denormalized traceability** in quality issues enables fast queries without joins
3. **Backward compatible** - existing code continues to work
4. **Scalable** - can add more entities without restructuring
5. **Performant** - no complex joins needed for common queries
6. **Maintainable** - clear separation between reference data and transactional data

**Trade-offs Accepted**:
- Slightly more complex data sync (keep enriched fields updated)
- Larger data file size (~30-40% increase estimated)
- Migration complexity (one-time cost)

**Trade-offs Avoided**:
- ✅ No need to rewrite existing APIs
- ✅ No performance degradation from complex joins
- ✅ No data duplication inconsistency (enrichment is automated)

---

## 10. Next Steps

1. **Review & Approve**: Stakeholder review of this design
2. **Prioritize Features**: Which phases are MVP vs. nice-to-have?
3. **Create Detailed Specs**: Write API specifications for new endpoints
4. **Build Prototypes**: Create sample data and test queries
5. **Implement Phases**: Start with Phase 1 (foundation)
6. **Iterate**: Gather feedback and refine

---

## Questions for Discussion

1. **Scope**: Do we need all features in Phase 1-6, or can we start with a subset?
2. **Suppliers**: How many suppliers should we model? Any specific supplier types?
3. **Orders**: Should orders support multiple part numbers, or one part per order?
4. **Batches**: What's the typical batch size? Should we auto-split by shift?
5. **Costs**: How do we calculate scrap/rework costs? (unit price * quantity?)
6. **Notifications**: Should supplier notifications be automated via email/API?
7. **CAPA System**: Do we need full CAPA (Corrective/Preventive Action) workflow?
8. **Quarantine**: Should material quarantine automatically stop production?
9. **Roles**: Who can create/edit investigations? Quality team only?
10. **Reporting**: What supplier reports are needed? (Monthly scorecard? Annual review?)

---

**Document Version**: 1.0
**Author**: Claude (AI Assistant)
**Date**: 2025-11-08
**Status**: Draft for Review
