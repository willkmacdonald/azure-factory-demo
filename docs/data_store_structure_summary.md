# Data Store Structure Summary

## 📊 Current Architecture Overview

The Azure Factory Demo currently uses a **hierarchical JSON-based data store** with dual storage modes:

### Storage Modes
```
┌─────────────────────────────────────┐
│ Local Mode (Default)                │
│ File: /data/production.json         │
└─────────────────────────────────────┘
              OR
┌─────────────────────────────────────┐
│ Azure Mode                          │
│ Blob: factory-data/production.json  │
└─────────────────────────────────────┘
```

### Current Data Hierarchy (v1.0)

```
production.json
├── metadata
│   ├── generated_at: timestamp
│   ├── start_date
│   └── end_date
│
├── machines: [static config]
│   └── {id, name, type, ideal_cycle_time}
│
├── shifts: [static config]
│   └── {id, name, start_hour, end_hour}
│
└── production: {
      [date]: {
        [machine_name]: {
          ├── parts_produced
          ├── good_parts
          ├── scrap_parts
          ├── uptime_hours
          ├── downtime_hours
          │
          ├── quality_issues: [
          │     {type, description, parts_affected, severity}
          │   ]
          │
          ├── downtime_events: [
          │     {reason, description, duration_hours}
          │   ]
          │
          └── shifts: {
                [shift_name]: {
                  parts_produced, good_parts, scrap_parts,
                  uptime_hours, downtime_hours
                }
              }
        }
      }
    }
```

---

## 🎯 Key Entities

| Entity | Location | Type | Purpose |
|--------|----------|------|---------|
| **Machine** | `machines[]` | Static | Equipment configuration |
| **Shift** | `shifts[]` | Static | Work schedule definition |
| **Production Record** | `production[date][machine]` | Dynamic | Daily metrics per machine |
| **Quality Issue** | `production[date][machine].quality_issues[]` | Dynamic | Defects found |
| **Downtime Event** | `production[date][machine].downtime_events[]` | Dynamic | Stoppages |

---

## 🔍 Current Limitations (Why We Need Expansion)

### ❌ Missing Traceability

```
Current State:
┌─────────────────┐
│ Quality Issue   │
│ - type          │  ← ISOLATED: No context!
│ - severity      │     Cannot answer:
│ - parts_affected│     • Which supplier?
└─────────────────┘     • Which order?
                         • Which customer?
                         • Which material lot?
```

### ❌ Cannot Answer Critical Questions

1. **"Which supplier caused these defects?"**
   - No supplier entity exists
   - Quality issues have no supplier linkage

2. **"Which customer orders are affected?"**
   - No order tracking
   - Production is aggregated by machine/date only

3. **"Should we quarantine this material lot?"**
   - No lot/batch tracking
   - Cannot trace materials to parts

4. **"What's our supplier quality performance?"**
   - No supplier metrics
   - No cost of quality by supplier

5. **"Which parts should we recall?"**
   - No serial number tracking
   - Cannot identify specific parts

---

## 🚀 Proposed Expansion (v2.0)

### New Entity Relationship Diagram

```
                    SUPPLY CHAIN TRACEABILITY

    ┌──────────┐          ┌──────────┐          ┌──────────┐
    │ Supplier │─supplies→│Material  │─consumed→│Production│
    │          │          │   Lot    │    by    │  Batch   │
    └──────────┘          └──────────┘          └──────────┘
         ↓                      ↓                      ↓
      notified             suspected              produces
         ↓                      ↓                      ↓
    ┌────────────────────────────────────────────────────┐
    │                  Quality Issue                     │
    │  ┌──────────────────────────────────────────┐     │
    │  │ Traceability Object (Denormalized)       │     │
    │  │  • order_number                          │     │
    │  │  • customer                              │     │
    │  │  • affected_serials                      │     │
    │  │  • materials_used (with supplier info)   │     │
    │  │  • root_cause                            │     │
    │  │  • cost_impact                           │     │
    │  └──────────────────────────────────────────┘     │
    └────────────────────────────────────────────────────┘
                           ↓
                      impacts
                           ↓
                    ┌──────────┐
                    │  Order   │
                    │          │
                    └──────────┘
                           ↓
                      fulfills
                           ↓
                    ┌──────────┐
                    │ Customer │
                    └──────────┘
```

### Enhanced Data Structure (v2.0)

```json
{
  "_meta": {
    "schema_version": "2.0",
    "generated_at": "...",
    "start_date": "...",
    "end_date": "..."
  },

  "suppliers": [
    {
      "id": "SUP-001",
      "name": "Acme Steel Co.",
      "quality_rating": 4.2,
      "defect_rate_ppm": 250,
      "certifications": ["ISO 9001"]
    }
  ],

  "material_lots": [
    {
      "lot_number": "LOT-2025-001",
      "material_id": "MAT-001",
      "supplier_id": "SUP-001",
      "quantity_received": 5000,
      "quarantine": false,
      "inspection_passed": true
    }
  ],

  "orders": [
    {
      "id": "ORD-1001",
      "customer": "ABC Manufacturing",
      "part_number": "PART-A123",
      "quantity_ordered": 500,
      "status": "completed"
    }
  ],

  "production": {
    "2025-10-03": {
      "CNC-001": {
        "batches": [
          {
            "batch_id": "BATCH-2025-1003-001",
            "order_id": "ORD-1001",
            "shift": "Day",
            "operator": "Mike Johnson",
            "serial_range": {"start": 1000, "end": 1424},
            "materials_consumed": [
              {
                "material_id": "MAT-001",
                "lot_number": "LOT-2025-001",
                "quantity": 150.5
              }
            ]
          }
        ],

        "quality_issues": [
          {
            "issue_id": "QI-2025-1003-001",
            "type": "dimensional",
            "severity": "High",
            "parts_affected": 5,

            "traceability": {
              "batch_id": "BATCH-2025-1003-001",
              "order_id": "ORD-1001",
              "customer": "ABC Manufacturing",
              "affected_serials": [1023, 1045, 1067]
            },

            "materials_used": [
              {
                "lot_number": "LOT-2025-001",
                "supplier_id": "SUP-001",
                "supplier_name": "Acme Steel Co."
              }
            ],

            "investigation": {
              "root_cause_category": "material",
              "suspected_lots": ["LOT-2025-001"],
              "status": "closed"
            },

            "cost_impact": {
              "total_cost": 1175.00,
              "charged_to_supplier": false
            }
          }
        ]
      }
    }
  }
}
```

---

## 🔗 Traceability Capabilities (Post-Expansion)

### 1️⃣ Backward Trace: Defect → Root Cause

```
Quality Issue #QI-2025-1003-001
         ↓
   (batch_id)
         ↓
Batch #BATCH-2025-1003-001
         ↓
   (order_id, materials_consumed)
         ↓
Order #ORD-1001 + Material Lot #LOT-2025-001
         ↓
   (customer, supplier_id)
         ↓
Customer: ABC Manufacturing + Supplier: Acme Steel Co.

ANSWER: "Defects caused by material from Acme Steel,
         affecting ABC Manufacturing's order"
```

### 2️⃣ Forward Trace: Supplier → Impact

```
Supplier: Acme Steel Co. (SUP-001)
         ↓
   (find all lots)
         ↓
Material Lots: [LOT-2025-001, LOT-2025-015, ...]
         ↓
   (find batches using lots)
         ↓
Production Batches: [BATCH-001, BATCH-047, ...]
         ↓
   (find issues in batches)
         ↓
Quality Issues: [QI-001, QI-023, ...]
         ↓
   (aggregate)
         ↓
ANSWER: "Acme Steel has 5 quality issues,
         affecting 23 parts, costing $5,850"
```

### 3️⃣ Lot Trace: Material → Usage

```
Material Lot: LOT-2025-001
         ↓
   (find batches consuming lot)
         ↓
Used in Batches: [BATCH-001, BATCH-002, ...]
         ↓
   (extract serials from batches)
         ↓
Parts Produced: Serials 1000-1849
         ↓
   (find issues)
         ↓
Quality Issues: 1 issue, serials [1023, 1045, 1067, 1089, 1102]
         ↓
   (quarantine check)
         ↓
ANSWER: "Quarantine recommended.
         Affects 825 parts, 5 defects found."
```

### 4️⃣ Serial Trace: Part → History

```
Serial Number: 1023
         ↓
   (find batch containing serial)
         ↓
Batch: BATCH-2025-1003-001
         ↓
   (extract batch data)
         ↓
Details:
  • Produced: 2025-10-03 on CNC-001
  • Operator: Mike Johnson
  • Order: ORD-1001 for ABC Manufacturing
  • Materials: LOT-2025-001 from Acme Steel
  • Quality Issues: 1 (dimensional defect)
         ↓
ANSWER: "Part #1023 is DEFECTIVE.
         Root cause: material from Acme Steel."
```

---

## 📈 New API Capabilities

### Supplier APIs
```http
GET /api/suppliers
GET /api/suppliers/{id}/quality-metrics
GET /api/suppliers/{id}/issues
```

### Traceability APIs
```http
GET /api/traceability/forward/{batch_id}
GET /api/traceability/backward/{serial}
GET /api/traceability/lot/{lot_number}
GET /api/traceability/supplier/{supplier_id}
```

### Enhanced Quality APIs
```http
GET /api/metrics/quality?supplier_id=SUP-001
GET /api/metrics/quality?order_id=ORD-1001
GET /api/metrics/quality?lot_number=LOT-2025-001
GET /api/metrics/quality?root_cause=material
```

### Analytics APIs
```http
GET /api/analytics/supplier-performance
GET /api/analytics/root-cause-pareto
GET /api/analytics/cost-of-quality
```

---

## 📊 Use Case Examples

### Use Case 1: Customer Complaint Investigation

**Scenario**: Customer reports defective part #1089

**Query**: `GET /api/traceability/backward/1089`

**Result**:
```json
{
  "serial_number": 1089,
  "status": "DEFECTIVE",
  "production": {
    "date": "2025-10-03",
    "machine": "CNC-001",
    "batch_id": "BATCH-2025-1003-001"
  },
  "order": {
    "order_id": "ORD-1001",
    "customer": "ABC Manufacturing"
  },
  "materials": [
    {
      "lot_number": "LOT-2025-001",
      "supplier": "Acme Steel Co."
    }
  ],
  "quality_issues": [
    {
      "type": "dimensional",
      "root_cause": "material"
    }
  ]
}
```

**Action**:
1. Notify customer: "We identified the root cause"
2. Quarantine lot LOT-2025-001
3. Contact supplier Acme Steel
4. Recall other parts from same batch (serials 1000-1849)

---

### Use Case 2: Supplier Audit

**Scenario**: Annual review of Acme Steel Co.

**Query**: `GET /api/suppliers/SUP-001/quality-metrics?start=2025-01-01&end=2025-12-31`

**Result**:
```json
{
  "supplier": {
    "id": "SUP-001",
    "name": "Acme Steel Co."
  },
  "metrics": {
    "lots_received": 45,
    "defect_rate_ppm": 250,
    "quality_issues": {
      "total": 12,
      "high_severity": 3,
      "medium_severity": 6,
      "low_severity": 3
    },
    "cost_of_quality": {
      "total": 14100.00,
      "average_per_issue": 1175.00
    },
    "performance_score": 82.5,
    "grade": "B"
  },
  "recommendation": "Good supplier, minor improvements needed"
}
```

**Action**:
1. Schedule supplier meeting
2. Discuss 3 high-severity issues
3. Request corrective action plan
4. Tighten material specifications
5. Continue relationship

---

### Use Case 3: Material Lot Quarantine

**Scenario**: Suspect defects from lot LOT-2025-001

**Query**: `GET /api/materials/lots/LOT-2025-001/usage`

**Result**:
```json
{
  "lot": {
    "lot_number": "LOT-2025-001",
    "supplier": "Acme Steel Co.",
    "quantity_received": 5000,
    "quantity_used": 2660,
    "quantity_remaining": 2340
  },
  "usage": {
    "batches_count": 18,
    "batches": ["BATCH-001", "BATCH-002", ...]
  },
  "quality_issues": {
    "count": 3,
    "total_cost": 3525.00
  },
  "affected_serials": [1000, 1001, ..., 7824],
  "quarantine_recommendation": {
    "should_quarantine": true,
    "reason": "High severity issues linked to this lot"
  }
}
```

**Action**:
1. **Immediately** quarantine remaining 2340 kg
2. Stop production using this lot
3. Inspect all 7,825 parts produced
4. Notify customers with parts from this lot
5. Return quarantined material to supplier
6. File supplier CAPA (Corrective Action)

---

## 💡 Benefits Summary

| Benefit | Before (v1.0) | After (v2.0) |
|---------|---------------|--------------|
| **Supplier Accountability** | ❌ Cannot identify supplier | ✅ Full supplier traceability |
| **Customer Impact** | ❌ Cannot identify affected orders | ✅ Know exactly which customers |
| **Root Cause Analysis** | ❌ Limited to machine/process | ✅ Material, supplier, lot tracking |
| **Cost Recovery** | ❌ No supplier cost tracking | ✅ Charge suppliers for defects |
| **Lot Quarantine** | ❌ Not possible | ✅ Immediate quarantine capability |
| **Compliance** | ⚠️ Partial (machine tracking only) | ✅ Full traceability (FDA, ISO 9001) |
| **Recall Capability** | ❌ Cannot identify specific parts | ✅ Serial-level identification |

---

## 🛠️ Implementation Roadmap

```
Phase 1: Foundation (Weeks 1-2)
├─ Add supplier, material, order entities
├─ Generate synthetic reference data
└─ Verify backward compatibility

Phase 2: Batch Tracking (Weeks 2-3)
├─ Create production batch entity
├─ Link batches to orders
└─ Link batches to materials

Phase 3: Quality Enhancement (Weeks 3-4)
├─ Add traceability to quality issues
├─ Add investigation tracking
└─ Add cost impact tracking

Phase 4: API Expansion (Weeks 4-5)
├─ Build supplier APIs
├─ Build traceability APIs
└─ Enhance quality APIs

Phase 5: Analytics (Weeks 5-6)
├─ Supplier scorecards
├─ Root cause analysis
└─ Cost of quality dashboards

Phase 6: Frontend (Weeks 6-8)
├─ Supplier management UI
├─ Traceability viewer
└─ Enhanced quality dashboard
```

---

## 📁 Reference Files

1. **Full Schema**: `data_store_expansion_schema.json`
   - Complete example of v2.0 data structure
   - Real-world sample data

2. **Analysis Document**: `data_store_expansion_analysis.md`
   - Detailed design decisions
   - Entity relationships
   - Implementation phases

3. **Code Examples**: `traceability_examples.py`
   - Working Python code for traceability queries
   - 5 example query functions
   - Sample output

---

## 🎓 Key Concepts

### Normalization vs. Denormalization

**Normalized Data** (Suppliers, Orders):
```json
{
  "suppliers": [
    {"id": "SUP-001", "name": "Acme Steel"}
  ]
}
// Reference: "supplier_id": "SUP-001"
```
**Pro**: Single source of truth, easy to update
**Con**: Requires joins to get supplier name

**Denormalized Data** (Quality Issues):
```json
{
  "quality_issues": [
    {
      "supplier_id": "SUP-001",
      "supplier_name": "Acme Steel"  ← Cached copy
    }
  ]
}
```
**Pro**: Fast queries, no joins needed
**Con**: Must keep cached data in sync

**Our Approach**: Hybrid - normalize masters, denormalize for performance

---

### Traceability Chain

```
Supplier → Material Lot → Production Batch → Parts → Quality Issues → Orders → Customers

Every link is tracked. Can traverse in EITHER direction.
```

---

### Batch Concept

**Before**: Production aggregated by day/machine
```
CNC-001 on 2025-10-03: 850 parts produced
```
Cannot answer: "Which order?" "Which materials?"

**After**: Production tracked in batches
```
BATCH-001: 175 parts (serials 1000-1174)
  ├─ Order: ORD-1001
  ├─ Shift: Day
  ├─ Operator: Mike Johnson
  └─ Materials: LOT-2025-001 (150.5 kg)
```
Can answer ALL questions!

---

## ✅ Recommended Next Steps

1. **Review** this summary with stakeholders
2. **Prioritize** which phases are MVP
3. **Validate** sample data structure matches your needs
4. **Prototype** one traceability query end-to-end
5. **Iterate** based on feedback

---

**Questions? Let's discuss!** 🚀
