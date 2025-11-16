"""
Traceability Query Examples for Data Store v2.0

This module demonstrates how to perform supply chain traceability queries
with the expanded data model.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime


# ==============================================================================
# EXAMPLE DATA STRUCTURES
# ==============================================================================

# Simplified data store structure for examples
data_store = {
    "suppliers": [
        {
            "id": "SUP-001",
            "name": "Acme Steel Co.",
            "quality_rating": 4.2
        }
    ],
    "material_lots": [
        {
            "lot_number": "LOT-2025-001",
            "material_id": "MAT-001",
            "supplier_id": "SUP-001",
            "received_date": "2025-10-01"
        }
    ],
    "orders": [
        {
            "id": "ORD-1001",
            "customer": "ABC Manufacturing",
            "part_number": "PART-A123",
            "quantity_ordered": 500
        }
    ],
    "production": {
        "2025-10-03": {
            "CNC-001": {
                "batches": [
                    {
                        "batch_id": "BATCH-2025-1003-001",
                        "order_id": "ORD-1001",
                        "materials_consumed": [
                            {
                                "material_id": "MAT-001",
                                "lot_number": "LOT-2025-001",
                                "quantity": 150.5
                            }
                        ],
                        "serial_range": {"start": 1000, "end": 1424}
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
                            "affected_serials": [1023, 1045, 1067, 1089, 1102]
                        },
                        "materials_used": [
                            {
                                "material_id": "MAT-001",
                                "lot_number": "LOT-2025-001",
                                "supplier_id": "SUP-001"
                            }
                        ],
                        "investigation": {
                            "root_cause_category": "material",
                            "suspected_lots": ["LOT-2025-001"]
                        },
                        "cost_impact": {
                            "total_cost": 1175.00
                        }
                    }
                ]
            }
        }
    }
}


# ==============================================================================
# TRACEABILITY QUERY 1: BACKWARD TRACE (Defect → Root Cause)
# ==============================================================================

def trace_backward_from_issue(issue_id: str) -> Dict[str, Any]:
    """
    Trace backward from a quality issue to find root cause supplier/material

    Use case: A quality issue is found. Need to identify:
    - Which production batch was it from?
    - Which order was affected?
    - Which materials were used?
    - Which supplier provided the material?

    Returns complete traceability chain.
    """

    # Step 1: Find the quality issue
    issue = None
    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for qi in metrics.get("quality_issues", []):
                if qi.get("issue_id") == issue_id:
                    issue = qi
                    break

    if not issue:
        raise ValueError(f"Quality issue {issue_id} not found")

    # Step 2: Find the production batch
    batch_id = issue.get("traceability", {}).get("batch_id")
    batch = None
    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for b in metrics.get("batches", []):
                if b["batch_id"] == batch_id:
                    batch = b
                    break

    # Step 3: Find the order
    order_id = batch.get("order_id")
    order = next(
        (o for o in data_store["orders"] if o["id"] == order_id),
        None
    )

    # Step 4: Find materials and suppliers
    materials_trace = []
    for material in batch.get("materials_consumed", []):
        # Find material lot
        lot = next(
            (l for l in data_store["material_lots"]
             if l["lot_number"] == material["lot_number"]),
            None
        )

        # Find supplier
        supplier = next(
            (s for s in data_store["suppliers"]
             if s["id"] == lot["supplier_id"]),
            None
        ) if lot else None

        materials_trace.append({
            "material_id": material["material_id"],
            "lot_number": material["lot_number"],
            "quantity_used": material["quantity"],
            "lot_info": lot,
            "supplier": supplier
        })

    return {
        "issue": {
            "id": issue_id,
            "type": issue["type"],
            "severity": issue["severity"],
            "parts_affected": issue["parts_affected"],
            "affected_serials": issue["traceability"]["affected_serials"],
            "root_cause": issue["investigation"]["root_cause_category"],
            "cost": issue["cost_impact"]["total_cost"]
        },
        "batch": {
            "id": batch_id,
            "serial_range": batch["serial_range"],
            "materials_consumed": len(batch["materials_consumed"])
        },
        "order": {
            "id": order_id,
            "customer": order["customer"],
            "part_number": order["part_number"]
        },
        "materials": materials_trace,
        "root_cause_supplier": materials_trace[0]["supplier"]["name"]
        if materials_trace and materials_trace[0].get("supplier")
        else "Unknown"
    }


# ==============================================================================
# TRACEABILITY QUERY 2: FORWARD TRACE (Supplier → Impact)
# ==============================================================================

def trace_forward_from_supplier(supplier_id: str,
                                  date_range: Optional[Tuple[str, str]] = None
                                  ) -> Dict[str, Any]:
    """
    Trace forward from a supplier to find all quality impacts

    Use case: Supplier audit or performance review. Need to identify:
    - Which material lots were received from this supplier?
    - Which production batches used those materials?
    - Which quality issues are linked to this supplier?
    - What's the total cost impact?

    Returns complete impact analysis.
    """

    # Step 1: Find all material lots from this supplier
    lots = [
        lot for lot in data_store["material_lots"]
        if lot["supplier_id"] == supplier_id
    ]

    if date_range:
        start_date, end_date = date_range
        lots = [
            lot for lot in lots
            if start_date <= lot["received_date"] <= end_date
        ]

    lot_numbers = {lot["lot_number"] for lot in lots}

    # Step 2: Find all batches that used these lots
    batches_using_lots = []
    for date, machines in data_store["production"].items():
        if date_range and not (date_range[0] <= date <= date_range[1]):
            continue

        for machine, metrics in machines.items():
            for batch in metrics.get("batches", []):
                for material in batch.get("materials_consumed", []):
                    if material["lot_number"] in lot_numbers:
                        batches_using_lots.append({
                            "batch_id": batch["batch_id"],
                            "date": date,
                            "machine": machine,
                            "order_id": batch["order_id"],
                            "lot_number": material["lot_number"]
                        })
                        break  # Count batch once even if multiple lots

    # Step 3: Find all quality issues linked to this supplier
    quality_issues = []
    total_cost = 0
    total_parts_affected = 0

    for date, machines in data_store["production"].items():
        if date_range and not (date_range[0] <= date <= date_range[1]):
            continue

        for machine, metrics in machines.items():
            for issue in metrics.get("quality_issues", []):
                # Check if any material in the issue is from this supplier
                for material in issue.get("materials_used", []):
                    if material.get("supplier_id") == supplier_id:
                        quality_issues.append({
                            "issue_id": issue.get("issue_id"),
                            "date": date,
                            "type": issue["type"],
                            "severity": issue["severity"],
                            "parts_affected": issue["parts_affected"],
                            "lot_number": material["lot_number"],
                            "cost": issue["cost_impact"]["total_cost"]
                        })
                        total_cost += issue["cost_impact"]["total_cost"]
                        total_parts_affected += issue["parts_affected"]
                        break  # Count issue once

    # Step 4: Find affected orders
    affected_order_ids = {b["order_id"] for b in batches_using_lots}
    affected_orders = [
        order for order in data_store["orders"]
        if order["id"] in affected_order_ids
    ]

    # Step 5: Calculate supplier quality metrics
    supplier = next(
        (s for s in data_store["suppliers"] if s["id"] == supplier_id),
        None
    )

    return {
        "supplier": {
            "id": supplier_id,
            "name": supplier["name"] if supplier else "Unknown",
            "quality_rating": supplier.get("quality_rating", 0) if supplier else 0
        },
        "material_lots": {
            "count": len(lots),
            "lot_numbers": [lot["lot_number"] for lot in lots]
        },
        "production_batches": {
            "count": len(batches_using_lots),
            "batches": batches_using_lots
        },
        "quality_issues": {
            "count": len(quality_issues),
            "total_parts_affected": total_parts_affected,
            "total_cost_impact": total_cost,
            "issues": quality_issues
        },
        "affected_orders": {
            "count": len(affected_orders),
            "customers": list({o["customer"] for o in affected_orders}),
            "orders": [
                {
                    "order_id": o["id"],
                    "customer": o["customer"],
                    "part_number": o["part_number"]
                }
                for o in affected_orders
            ]
        },
        "summary": {
            "lots_received": len(lots),
            "batches_produced": len(batches_using_lots),
            "quality_issues": len(quality_issues),
            "total_cost": total_cost,
            "average_cost_per_issue": total_cost / len(quality_issues)
            if quality_issues else 0
        }
    }


# ==============================================================================
# TRACEABILITY QUERY 3: LOT TRACE (Material Lot → Usage)
# ==============================================================================

def trace_material_lot(lot_number: str) -> Dict[str, Any]:
    """
    Trace a material lot through production

    Use case: Material lot suspected of defects. Need to identify:
    - Where was this lot used? (which batches)
    - Which parts were produced? (serial numbers)
    - Any quality issues linked to this lot?
    - Should we quarantine this lot?

    Returns complete lot usage trace.
    """

    # Step 1: Find the material lot
    lot = next(
        (l for l in data_store["material_lots"]
         if l["lot_number"] == lot_number),
        None
    )

    if not lot:
        raise ValueError(f"Material lot {lot_number} not found")

    # Step 2: Find supplier
    supplier = next(
        (s for s in data_store["suppliers"]
         if s["id"] == lot["supplier_id"]),
        None
    )

    # Step 3: Find all batches that used this lot
    batches_using_lot = []
    total_quantity_used = 0

    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for batch in metrics.get("batches", []):
                for material in batch.get("materials_consumed", []):
                    if material["lot_number"] == lot_number:
                        batches_using_lot.append({
                            "batch_id": batch["batch_id"],
                            "date": date,
                            "machine": machine,
                            "order_id": batch["order_id"],
                            "quantity_used": material["quantity"],
                            "serial_range": batch["serial_range"]
                        })
                        total_quantity_used += material["quantity"]

    # Step 4: Find quality issues linked to this lot
    related_issues = []
    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for issue in metrics.get("quality_issues", []):
                suspected = issue.get("investigation", {}).get("suspected_lots", [])
                if lot_number in suspected:
                    related_issues.append({
                        "issue_id": issue.get("issue_id"),
                        "type": issue["type"],
                        "severity": issue["severity"],
                        "parts_affected": issue["parts_affected"],
                        "cost": issue["cost_impact"]["total_cost"],
                        "batch_id": issue["traceability"]["batch_id"]
                    })

    # Step 5: Determine quarantine recommendation
    quarantine_recommended = (
        len(related_issues) > 0 and
        any(i["severity"] == "High" for i in related_issues)
    )

    return {
        "lot": {
            "lot_number": lot_number,
            "material_id": lot["material_id"],
            "received_date": lot["received_date"],
            "quantity_received": lot.get("quantity_received", 0),
            "quantity_used": total_quantity_used,
            "quantity_remaining": lot.get("quantity_remaining", 0)
        },
        "supplier": {
            "id": supplier["id"],
            "name": supplier["name"]
        } if supplier else None,
        "usage": {
            "batches_count": len(batches_using_lot),
            "total_quantity_used": total_quantity_used,
            "batches": batches_using_lot
        },
        "quality_issues": {
            "count": len(related_issues),
            "issues": related_issues,
            "total_cost": sum(i["cost"] for i in related_issues)
        },
        "affected_serials": [
            serial
            for batch in batches_using_lot
            for serial in range(
                batch["serial_range"]["start"],
                batch["serial_range"]["end"] + 1
            )
        ],
        "quarantine_recommendation": {
            "should_quarantine": quarantine_recommended,
            "reason": "High severity issues linked to this lot"
            if quarantine_recommended else "No critical issues",
            "affected_batches": [
                i["batch_id"] for i in related_issues
            ] if quarantine_recommended else []
        }
    }


# ==============================================================================
# TRACEABILITY QUERY 4: SERIAL NUMBER TRACE (Part → Complete History)
# ==============================================================================

def trace_serial_number(serial_number: int) -> Dict[str, Any]:
    """
    Trace a specific part by serial number to its complete history

    Use case: Customer returns defective part. Need to identify:
    - Which batch was it from?
    - Which order was it for?
    - Which materials were used?
    - Which supplier provided materials?
    - Any quality issues during production?

    Returns complete part history.
    """

    # Find which batch contains this serial number
    batch_info = None
    date_produced = None
    machine_produced = None

    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for batch in metrics.get("batches", []):
                serial_range = batch["serial_range"]
                if serial_range["start"] <= serial_number <= serial_range["end"]:
                    batch_info = batch
                    date_produced = date
                    machine_produced = machine
                    break

    if not batch_info:
        raise ValueError(f"Serial number {serial_number} not found in production")

    # Find order
    order = next(
        (o for o in data_store["orders"]
         if o["id"] == batch_info["order_id"]),
        None
    )

    # Find materials and suppliers
    materials_used = []
    for material in batch_info.get("materials_consumed", []):
        lot = next(
            (l for l in data_store["material_lots"]
             if l["lot_number"] == material["lot_number"]),
            None
        )
        supplier = next(
            (s for s in data_store["suppliers"]
             if s["id"] == lot["supplier_id"]),
            None
        ) if lot else None

        materials_used.append({
            "material_id": material["material_id"],
            "lot_number": material["lot_number"],
            "supplier": supplier["name"] if supplier else "Unknown"
        })

    # Find any quality issues affecting this serial
    quality_issues_affecting = []
    for date, machines in data_store["production"].items():
        for machine, metrics in machines.items():
            for issue in metrics.get("quality_issues", []):
                affected = issue.get("traceability", {}).get("affected_serials", [])
                if serial_number in affected:
                    quality_issues_affecting.append({
                        "issue_id": issue.get("issue_id"),
                        "type": issue["type"],
                        "severity": issue["severity"],
                        "root_cause": issue["investigation"]["root_cause_category"]
                    })

    return {
        "serial_number": serial_number,
        "production": {
            "date": date_produced,
            "machine": machine_produced,
            "batch_id": batch_info["batch_id"],
            "shift": batch_info.get("shift", "Unknown"),
            "operator": batch_info.get("operator", "Unknown")
        },
        "order": {
            "order_id": order["id"],
            "customer": order["customer"],
            "part_number": order["part_number"]
        } if order else None,
        "materials": materials_used,
        "quality_issues": quality_issues_affecting,
        "status": "DEFECTIVE" if quality_issues_affecting else "OK"
    }


# ==============================================================================
# ANALYTICS QUERY: SUPPLIER SCORECARD
# ==============================================================================

def generate_supplier_scorecard(supplier_id: str,
                                  date_range: Tuple[str, str]
                                  ) -> Dict[str, Any]:
    """
    Generate comprehensive supplier quality scorecard

    Metrics included:
    - Total lots received
    - Defect rate (PPM)
    - Quality issues count by severity
    - Cost of quality
    - On-time delivery (if tracked)
    - Overall rating
    """

    # Get forward trace for comprehensive data
    trace = trace_forward_from_supplier(supplier_id, date_range)

    # Calculate PPM (parts per million defects)
    # Assuming each batch produces ~400 parts (rough estimate)
    total_parts_produced = trace["production_batches"]["count"] * 400
    defect_rate_ppm = (
        (trace["quality_issues"]["total_parts_affected"] / total_parts_produced)
        * 1_000_000
    ) if total_parts_produced > 0 else 0

    # Count issues by severity
    severity_breakdown = {
        "High": 0,
        "Medium": 0,
        "Low": 0
    }
    for issue in trace["quality_issues"]["issues"]:
        severity_breakdown[issue["severity"]] += 1

    # Calculate performance score (0-100)
    # Formula: 100 - (defect_ppm / 1000) - (high_severity_count * 5)
    performance_score = max(
        0,
        100 - (defect_rate_ppm / 1000) - (severity_breakdown["High"] * 5)
    )

    return {
        "supplier": trace["supplier"],
        "date_range": {
            "start": date_range[0],
            "end": date_range[1]
        },
        "metrics": {
            "lots_received": trace["material_lots"]["count"],
            "batches_produced": trace["production_batches"]["count"],
            "total_parts_produced": total_parts_produced,
            "defect_rate_ppm": round(defect_rate_ppm, 2),
            "quality_issues": {
                "total": trace["quality_issues"]["count"],
                "by_severity": severity_breakdown,
                "parts_affected": trace["quality_issues"]["total_parts_affected"]
            },
            "cost_of_quality": {
                "total": trace["quality_issues"]["total_cost_impact"],
                "average_per_issue": trace["summary"]["average_cost_per_issue"]
            },
            "performance_score": round(performance_score, 1)
        },
        "grade": (
            "A" if performance_score >= 90 else
            "B" if performance_score >= 80 else
            "C" if performance_score >= 70 else
            "D" if performance_score >= 60 else
            "F"
        ),
        "recommendation": (
            "Excellent supplier, maintain relationship"
            if performance_score >= 90 else
            "Good supplier, minor improvements needed"
            if performance_score >= 80 else
            "Acceptable supplier, quality improvement plan required"
            if performance_score >= 70 else
            "Poor supplier, consider alternative sources"
        )
    }


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TRACEABILITY QUERY EXAMPLES")
    print("=" * 80)

    # Example 1: Backward trace from quality issue
    print("\n1. BACKWARD TRACE: Quality Issue → Root Cause Supplier")
    print("-" * 80)
    result = trace_backward_from_issue("QI-2025-1003-001")
    print(f"Issue: {result['issue']['type']} ({result['issue']['severity']})")
    print(f"Parts Affected: {result['issue']['parts_affected']}")
    print(f"Affected Serials: {result['issue']['affected_serials']}")
    print(f"Root Cause: {result['issue']['root_cause']}")
    print(f"Batch: {result['batch']['id']}")
    print(f"Order: {result['order']['id']} for {result['order']['customer']}")
    print(f"Root Cause Supplier: {result['root_cause_supplier']}")
    print(f"Cost Impact: ${result['issue']['cost']:.2f}")

    # Example 2: Forward trace from supplier
    print("\n\n2. FORWARD TRACE: Supplier → Quality Impact")
    print("-" * 80)
    result = trace_forward_from_supplier("SUP-001", ("2025-10-01", "2025-10-31"))
    print(f"Supplier: {result['supplier']['name']}")
    print(f"Material Lots Received: {result['material_lots']['count']}")
    print(f"Production Batches: {result['production_batches']['count']}")
    print(f"Quality Issues: {result['quality_issues']['count']}")
    print(f"Total Cost Impact: ${result['quality_issues']['total_cost_impact']:.2f}")
    print(f"Affected Customers: {', '.join(result['affected_orders']['customers'])}")

    # Example 3: Material lot trace
    print("\n\n3. MATERIAL LOT TRACE: Lot → Usage & Issues")
    print("-" * 80)
    result = trace_material_lot("LOT-2025-001")
    print(f"Lot Number: {result['lot']['lot_number']}")
    print(f"Supplier: {result['supplier']['name']}")
    print(f"Quantity Used: {result['usage']['total_quantity_used']} kg")
    print(f"Batches: {result['usage']['batches_count']}")
    print(f"Quality Issues: {result['quality_issues']['count']}")
    print(f"Quarantine Recommended: {result['quarantine_recommendation']['should_quarantine']}")
    print(f"Reason: {result['quarantine_recommendation']['reason']}")

    # Example 4: Serial number trace
    print("\n\n4. SERIAL NUMBER TRACE: Part → Complete History")
    print("-" * 80)
    result = trace_serial_number(1023)
    print(f"Serial Number: {result['serial_number']}")
    print(f"Status: {result['status']}")
    print(f"Produced: {result['production']['date']} on {result['production']['machine']}")
    print(f"Batch: {result['production']['batch_id']}")
    print(f"Customer: {result['order']['customer']}")
    print(f"Materials: {len(result['materials'])} types")
    for material in result['materials']:
        print(f"  - {material['lot_number']} from {material['supplier']}")
    print(f"Quality Issues: {len(result['quality_issues'])}")

    # Example 5: Supplier scorecard
    print("\n\n5. SUPPLIER SCORECARD: Performance Analysis")
    print("-" * 80)
    result = generate_supplier_scorecard("SUP-001", ("2025-10-01", "2025-10-31"))
    print(f"Supplier: {result['supplier']['name']}")
    print(f"Performance Score: {result['metrics']['performance_score']}/100")
    print(f"Grade: {result['grade']}")
    print(f"Defect Rate: {result['metrics']['defect_rate_ppm']} PPM")
    print(f"Quality Issues: {result['metrics']['quality_issues']['total']}")
    print(f"  - High: {result['metrics']['quality_issues']['by_severity']['High']}")
    print(f"  - Medium: {result['metrics']['quality_issues']['by_severity']['Medium']}")
    print(f"  - Low: {result['metrics']['quality_issues']['by_severity']['Low']}")
    print(f"Cost of Quality: ${result['metrics']['cost_of_quality']['total']:.2f}")
    print(f"Recommendation: {result['recommendation']}")

    print("\n" + "=" * 80)
