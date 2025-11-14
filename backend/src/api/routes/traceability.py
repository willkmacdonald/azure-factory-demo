"""Traceability API endpoints for supply chain tracking.

This module provides REST endpoints for supply chain traceability including:
- Supplier management and quality impact analysis
- Production batch tracking with full material traceability
- Customer order tracking with production status
- Backward traceability (batch → materials → suppliers)
- Forward traceability (supplier → batches → quality issues → orders)

All endpoints use async/await patterns for non-blocking I/O operations,
following FastAPI best practices for concurrent request handling.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException, Path
from shared.models import Supplier, ProductionBatch, Order
from shared.data import load_data_async

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Traceability"])


# =============================================================================
# SUPPLIER ENDPOINTS
# =============================================================================


@router.get("/suppliers", response_model=List[Supplier])
async def list_suppliers(
    status: Optional[str] = Query(
        None,
        description="Filter by supplier status (Active, OnHold, Suspended)",
    ),
) -> List[Supplier]:
    """List all suppliers with quality metrics.

    Retrieves all suppliers from the system with their quality ratings,
    on-time delivery rates, and defect rates. Optionally filter by status.

    Args:
        status: Optional status filter (Active, OnHold, Suspended)

    Returns:
        List of Supplier objects with quality metrics

    Raises:
        HTTPException: 500 if data loading fails

    Example:
        GET /api/suppliers
        GET /api/suppliers?status=Active
    """
    try:
        data = await load_data_async()
        if not data or "suppliers" not in data:
            return []

        suppliers = [Supplier(**s) for s in data["suppliers"]]

        # Filter by status if provided
        if status:
            suppliers = [s for s in suppliers if s.status == status]

        # Sort by quality rating (highest first)
        suppliers.sort(
            key=lambda s: s.quality_metrics.get("quality_rating", 0),
            reverse=True,
        )

        return suppliers

    except Exception as e:
        logger.error(f"Failed to load suppliers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load suppliers: {str(e)}")


@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier(
    supplier_id: str = Path(..., description="Supplier ID (e.g., SUP-001)"),
) -> Supplier:
    """Get detailed information for a specific supplier.

    Retrieves complete supplier information including contact details,
    quality metrics, certifications, and materials supplied.

    Args:
        supplier_id: Unique supplier identifier

    Returns:
        Supplier object with complete details

    Raises:
        HTTPException: 404 if supplier not found, 500 if data loading fails

    Example:
        GET /api/suppliers/SUP-001
    """
    try:
        data = await load_data_async()
        if not data or "suppliers" not in data:
            raise HTTPException(status_code=404, detail="No suppliers data available")

        # Find supplier by ID
        supplier_dict = next(
            (s for s in data["suppliers"] if s["id"] == supplier_id),
            None,
        )

        if not supplier_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier {supplier_id} not found",
            )

        return Supplier(**supplier_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load supplier: {str(e)}",
        )


@router.get("/suppliers/{supplier_id}/impact")
async def get_supplier_impact(
    supplier_id: str = Path(..., description="Supplier ID (e.g., SUP-001)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> Dict[str, Any]:
    """Analyze quality issues linked to a specific supplier.

    Performs forward traceability from supplier to identify quality issues
    in production batches that used materials from this supplier. Useful
    for root cause analysis and supplier performance evaluation.

    Args:
        supplier_id: Unique supplier identifier
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Dictionary containing:
        - supplier: Supplier details
        - material_lots: Lots supplied
        - affected_batches: Production batches using supplier's materials
        - quality_issues: Quality problems linked to supplier
        - total_defects: Total defect count
        - estimated_cost_impact: Estimated cost of quality issues

    Raises:
        HTTPException: 404 if supplier not found, 500 if analysis fails

    Example:
        GET /api/suppliers/SUP-001/impact
        GET /api/suppliers/SUP-001/impact?start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        data = await load_data_async()
        if not data:
            raise HTTPException(status_code=404, detail="No data available")

        # Get supplier
        supplier_dict = next(
            (s for s in data.get("suppliers", []) if s["id"] == supplier_id),
            None,
        )
        if not supplier_dict:
            raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")

        supplier = Supplier(**supplier_dict)

        # Find material lots from this supplier
        material_lots = [
            lot for lot in data.get("material_lots", [])
            if lot["supplier_id"] == supplier_id
        ]

        # Apply date filters to material lots
        if start_date:
            material_lots = [
                lot for lot in material_lots
                if lot["received_date"] >= start_date
            ]
        if end_date:
            material_lots = [
                lot for lot in material_lots
                if lot["received_date"] <= end_date
            ]

        lot_numbers = {lot["lot_number"] for lot in material_lots}

        # Find batches using materials from these lots
        affected_batches = []
        quality_issues = []
        total_defects = 0

        for batch in data.get("production_batches", []):
            # Apply date filters to batches
            if start_date and batch["date"] < start_date:
                continue
            if end_date and batch["date"] > end_date:
                continue

            # Check if batch uses any of supplier's material lots
            batch_lot_numbers = {
                mat["lot_number"]
                for mat in batch.get("materials_consumed", [])
            }

            if batch_lot_numbers & lot_numbers:  # Intersection
                affected_batches.append({
                    "batch_id": batch["batch_id"],
                    "date": batch["date"],
                    "machine_name": batch["machine_name"],
                    "parts_produced": batch["parts_produced"],
                    "scrap_parts": batch["scrap_parts"],
                    "materials_consumed": batch.get("materials_consumed", []),
                })

                # Count quality issues
                batch_defects = batch.get("scrap_parts", 0)
                if batch_defects > 0:
                    quality_issues.append({
                        "batch_id": batch["batch_id"],
                        "date": batch["date"],
                        "defect_count": batch_defects,
                        "defect_types": batch.get("defect_types", []),
                    })
                    total_defects += batch_defects

        # Estimate cost impact (assuming $50 per defect as example)
        estimated_cost_impact = total_defects * 50.0

        return {
            "supplier": supplier.model_dump(),
            "material_lots_supplied": len(material_lots),
            "affected_batches_count": len(affected_batches),
            "quality_issues_count": len(quality_issues),
            "total_defects": total_defects,
            "estimated_cost_impact": estimated_cost_impact,
            "material_lots": material_lots,
            "affected_batches": affected_batches[:10],  # Limit to 10 for response size
            "quality_issues": quality_issues[:10],  # Limit to 10 for response size
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze supplier impact for {supplier_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze supplier impact: {str(e)}",
        )


# =============================================================================
# PRODUCTION BATCH ENDPOINTS
# =============================================================================


@router.get("/batches", response_model=List[ProductionBatch])
async def list_batches(
    machine_id: Optional[int] = Query(None, description="Filter by machine ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    order_id: Optional[str] = Query(None, description="Filter by order ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of batches to return"),
) -> List[ProductionBatch]:
    """List production batches with optional filtering.

    Retrieves production batches with full traceability information including
    materials used, operators, quality data, and order assignment. Supports
    filtering by machine, date range, and order.

    Args:
        machine_id: Optional machine ID filter
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        order_id: Optional order ID filter
        limit: Maximum number of batches to return (1-500)

    Returns:
        List of ProductionBatch objects (newest first)

    Raises:
        HTTPException: 500 if data loading fails

    Example:
        GET /api/batches
        GET /api/batches?machine_id=1&start_date=2024-01-01
        GET /api/batches?order_id=ORD-001
    """
    try:
        data = await load_data_async()
        if not data or "production_batches" not in data:
            return []

        batches = [ProductionBatch(**b) for b in data["production_batches"]]

        # Apply filters
        if machine_id is not None:
            batches = [b for b in batches if b.machine_id == machine_id]
        if start_date:
            batches = [b for b in batches if b.date >= start_date]
        if end_date:
            batches = [b for b in batches if b.date <= end_date]
        if order_id:
            batches = [b for b in batches if b.order_id == order_id]

        # Sort by date (newest first)
        batches.sort(key=lambda b: b.date, reverse=True)

        # Apply limit
        batches = batches[:limit]

        return batches

    except Exception as e:
        logger.error(f"Failed to load batches: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load batches: {str(e)}")


@router.get("/batches/{batch_id}", response_model=ProductionBatch)
async def get_batch(
    batch_id: str = Path(..., description="Batch ID (e.g., BATCH-20240115-CNC001-001)"),
) -> ProductionBatch:
    """Get detailed information for a specific production batch.

    Retrieves complete batch information including all materials used with
    lot traceability, quality data, operator information, and order assignment.
    This endpoint provides the entry point for backward traceability queries.

    Args:
        batch_id: Unique batch identifier

    Returns:
        ProductionBatch object with complete traceability details

    Raises:
        HTTPException: 404 if batch not found, 500 if data loading fails

    Example:
        GET /api/batches/BATCH-20240115-CNC001-001
    """
    try:
        data = await load_data_async()
        if not data or "production_batches" not in data:
            raise HTTPException(status_code=404, detail="No batch data available")

        # Find batch by ID
        batch_dict = next(
            (b for b in data["production_batches"] if b["batch_id"] == batch_id),
            None,
        )

        if not batch_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Batch {batch_id} not found",
            )

        return ProductionBatch(**batch_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load batch {batch_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load batch: {str(e)}",
        )


# =============================================================================
# TRACEABILITY QUERY ENDPOINTS
# =============================================================================


@router.get("/traceability/backward/{batch_id}")
async def backward_trace(
    batch_id: str = Path(..., description="Batch ID to trace backward from"),
) -> Dict[str, Any]:
    """Perform backward traceability from batch to materials to suppliers.

    Traces a production batch back through the supply chain to identify
    all materials used and their suppliers. Essential for root cause analysis
    when quality issues are detected. Answers: "Where did these parts come from?"

    Flow: Batch → Materials Used → Material Lots → Suppliers

    Args:
        batch_id: Unique batch identifier

    Returns:
        Dictionary containing:
        - batch: Production batch details
        - materials_trace: List of materials with lot and supplier info
        - suppliers: Unique suppliers involved
        - supply_chain_summary: Summary statistics

    Raises:
        HTTPException: 404 if batch not found, 500 if trace fails

    Example:
        GET /api/traceability/backward/BATCH-20240115-CNC001-001
    """
    try:
        data = await load_data_async()
        if not data:
            raise HTTPException(status_code=404, detail="No data available")

        # Get the batch
        batch_dict = next(
            (b for b in data.get("production_batches", []) if b["batch_id"] == batch_id),
            None,
        )
        if not batch_dict:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")

        batch = ProductionBatch(**batch_dict)

        # Trace materials consumed in this batch
        materials_trace = []
        supplier_ids = set()

        for material_usage in batch.materials_consumed:
            # Find the material lot
            lot = next(
                (
                    l for l in data.get("material_lots", [])
                    if l["lot_number"] == material_usage.lot_number
                ),
                None,
            )

            if lot:
                supplier_id = lot["supplier_id"]
                supplier_ids.add(supplier_id)

                # Find the supplier
                supplier = next(
                    (
                        s for s in data.get("suppliers", [])
                        if s["id"] == supplier_id
                    ),
                    None,
                )

                # Find material spec
                material_spec = next(
                    (
                        m for m in data.get("materials_catalog", [])
                        if m["id"] == material_usage.material_id
                    ),
                    None,
                )

                materials_trace.append({
                    "material_id": material_usage.material_id,
                    "material_name": material_usage.material_name,
                    "material_spec": material_spec,
                    "quantity_used": material_usage.quantity_used,
                    "unit": material_usage.unit,
                    "lot_number": material_usage.lot_number,
                    "lot_details": lot,
                    "supplier_id": supplier_id,
                    "supplier": supplier,
                })

        # Get unique suppliers
        suppliers = [
            Supplier(**s).model_dump()
            for s in data.get("suppliers", [])
            if s["id"] in supplier_ids
        ]

        return {
            "batch": batch.model_dump(),
            "materials_trace": materials_trace,
            "suppliers": suppliers,
            "supply_chain_summary": {
                "materials_count": len(materials_trace),
                "suppliers_count": len(suppliers),
                "total_parts_produced": batch.parts_produced,
                "scrap_parts": batch.scrap_parts,
                "quality_rate": (
                    (batch.good_parts / batch.parts_produced * 100)
                    if batch.parts_produced > 0
                    else 0
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform backward trace for {batch_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform backward trace: {str(e)}",
        )


@router.get("/traceability/forward/{supplier_id}")
async def forward_trace(
    supplier_id: str = Path(..., description="Supplier ID to trace forward from"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> Dict[str, Any]:
    """Perform forward traceability from supplier to batches to orders.

    Traces a supplier forward through the supply chain to identify all
    production batches that used their materials, associated quality issues,
    and affected customer orders. Essential for impact analysis when supplier
    issues are detected. Answers: "What was affected by this supplier?"

    Flow: Supplier → Material Lots → Batches → Quality Issues → Orders

    Args:
        supplier_id: Unique supplier identifier
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        Dictionary containing:
        - supplier: Supplier details
        - material_lots: Lots supplied
        - affected_batches: Production batches using supplier's materials
        - quality_issues: Summary of quality problems
        - affected_orders: Customer orders impacted
        - impact_summary: Summary statistics

    Raises:
        HTTPException: 404 if supplier not found, 500 if trace fails

    Example:
        GET /api/traceability/forward/SUP-001
        GET /api/traceability/forward/SUP-001?start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        data = await load_data_async()
        if not data:
            raise HTTPException(status_code=404, detail="No data available")

        # Get supplier
        supplier_dict = next(
            (s for s in data.get("suppliers", []) if s["id"] == supplier_id),
            None,
        )
        if not supplier_dict:
            raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found")

        supplier = Supplier(**supplier_dict)

        # Find material lots from this supplier
        material_lots = [
            lot for lot in data.get("material_lots", [])
            if lot["supplier_id"] == supplier_id
        ]

        # Apply date filters
        if start_date:
            material_lots = [
                lot for lot in material_lots
                if lot["received_date"] >= start_date
            ]
        if end_date:
            material_lots = [
                lot for lot in material_lots
                if lot["received_date"] <= end_date
            ]

        lot_numbers = {lot["lot_number"] for lot in material_lots}

        # Find affected batches and quality issues
        affected_batches = []
        quality_issues = []
        order_ids = set()
        total_defects = 0

        for batch in data.get("production_batches", []):
            # Apply date filters
            if start_date and batch["date"] < start_date:
                continue
            if end_date and batch["date"] > end_date:
                continue

            # Check if batch uses any of supplier's material lots
            batch_lot_numbers = {
                mat["lot_number"]
                for mat in batch.get("materials_consumed", [])
            }

            if batch_lot_numbers & lot_numbers:  # Intersection
                affected_batches.append({
                    "batch_id": batch["batch_id"],
                    "date": batch["date"],
                    "machine_name": batch["machine_name"],
                    "parts_produced": batch["parts_produced"],
                    "scrap_parts": batch["scrap_parts"],
                    "order_id": batch.get("order_id"),
                })

                # Track quality issues
                if batch.get("scrap_parts", 0) > 0:
                    quality_issues.append({
                        "batch_id": batch["batch_id"],
                        "date": batch["date"],
                        "defect_count": batch["scrap_parts"],
                    })
                    total_defects += batch["scrap_parts"]

                # Track affected orders
                if batch.get("order_id"):
                    order_ids.add(batch["order_id"])

        # Get affected orders
        affected_orders = [
            Order(**o).model_dump()
            for o in data.get("orders", [])
            if o["id"] in order_ids
        ]

        return {
            "supplier": supplier.model_dump(),
            "material_lots_supplied": len(material_lots),
            "affected_batches": affected_batches,
            "quality_issues": quality_issues,
            "affected_orders": affected_orders,
            "impact_summary": {
                "batches_affected": len(affected_batches),
                "quality_issues_count": len(quality_issues),
                "total_defects": total_defects,
                "orders_affected": len(affected_orders),
                "estimated_cost_impact": total_defects * 50.0,  # $50 per defect estimate
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to perform forward trace for {supplier_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform forward trace: {str(e)}",
        )


# =============================================================================
# ORDER ENDPOINTS
# =============================================================================


@router.get("/orders", response_model=List[Order])
async def list_orders(
    status: Optional[str] = Query(
        None,
        description="Filter by order status (Pending, InProgress, Completed, Shipped, Delayed)",
    ),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of orders to return"),
) -> List[Order]:
    """List customer orders with production status.

    Retrieves customer orders with their fulfillment status. Optionally
    filter by order status to see pending, in-progress, or completed orders.

    Args:
        status: Optional status filter (Pending, InProgress, Completed, Shipped, Delayed)
        limit: Maximum number of orders to return (1-200)

    Returns:
        List of Order objects (newest first by due date)

    Raises:
        HTTPException: 500 if data loading fails

    Example:
        GET /api/orders
        GET /api/orders?status=InProgress
    """
    try:
        data = await load_data_async()
        if not data or "orders" not in data:
            return []

        orders = [Order(**o) for o in data["orders"]]

        # Filter by status if provided
        if status:
            orders = [o for o in orders if o.status == status]

        # Sort by due date (nearest first)
        orders.sort(key=lambda o: o.due_date)

        # Apply limit
        orders = orders[:limit]

        return orders

    except Exception as e:
        logger.error(f"Failed to load orders: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load orders: {str(e)}")


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: str = Path(..., description="Order ID (e.g., ORD-001)"),
) -> Order:
    """Get detailed information for a specific customer order.

    Retrieves complete order information including line items, due dates,
    and fulfillment status. Use this as the entry point for understanding
    which production batches are assigned to fulfill the order.

    Args:
        order_id: Unique order identifier

    Returns:
        Order object with complete details

    Raises:
        HTTPException: 404 if order not found, 500 if data loading fails

    Example:
        GET /api/orders/ORD-001
    """
    try:
        data = await load_data_async()
        if not data or "orders" not in data:
            raise HTTPException(status_code=404, detail="No orders data available")

        # Find order by ID
        order_dict = next(
            (o for o in data["orders"] if o["id"] == order_id),
            None,
        )

        if not order_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Order {order_id} not found",
            )

        return Order(**order_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load order: {str(e)}",
        )


@router.get("/orders/{order_id}/batches")
async def get_order_batches(
    order_id: str = Path(..., description="Order ID (e.g., ORD-001)"),
) -> Dict[str, Any]:
    """Get production batches assigned to fulfill a specific order.

    Links customer orders to their production batches, showing progress
    toward order fulfillment. Includes quality issues that may affect
    delivery timelines.

    Args:
        order_id: Unique order identifier

    Returns:
        Dictionary containing:
        - order: Order details
        - assigned_batches: Production batches for this order
        - production_summary: Summary of progress and quality

    Raises:
        HTTPException: 404 if order not found, 500 if query fails

    Example:
        GET /api/orders/ORD-001/batches
    """
    try:
        data = await load_data_async()
        if not data:
            raise HTTPException(status_code=404, detail="No data available")

        # Get order
        order_dict = next(
            (o for o in data.get("orders", []) if o["id"] == order_id),
            None,
        )
        if not order_dict:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        order = Order(**order_dict)

        # Find batches assigned to this order
        assigned_batches = [
            ProductionBatch(**b).model_dump()
            for b in data.get("production_batches", [])
            if b.get("order_id") == order_id
        ]

        # Calculate production summary
        total_produced = sum(b["parts_produced"] for b in assigned_batches)
        total_good = sum(b["good_parts"] for b in assigned_batches)
        total_scrap = sum(b["scrap_parts"] for b in assigned_batches)

        return {
            "order": order.model_dump(),
            "assigned_batches": assigned_batches,
            "production_summary": {
                "batches_count": len(assigned_batches),
                "total_produced": total_produced,
                "total_good_parts": total_good,
                "total_scrap": total_scrap,
                "quality_rate": (
                    (total_good / total_produced * 100) if total_produced > 0 else 0
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get batches for order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get order batches: {str(e)}",
        )
