"""Pydantic models for tool responses and data validation."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class OEEMetrics(BaseModel):
    """Overall Equipment Effectiveness metrics."""

    oee: float = Field(ge=0, le=1, description="Overall Equipment Effectiveness (0-1)")
    availability: float = Field(
        ge=0, le=1, description="Machine availability component (0-1)"
    )
    performance: float = Field(
        ge=0, le=1, description="Performance efficiency component (0-1)"
    )
    quality: float = Field(ge=0, le=1, description="Quality component (0-1)")
    total_parts: int = Field(ge=0, description="Total parts produced")
    good_parts: int = Field(ge=0, description="Number of good parts")
    scrap_parts: int = Field(ge=0, description="Number of scrapped parts")


class ScrapMetrics(BaseModel):
    """Scrap and waste metrics."""

    total_scrap: int = Field(ge=0, description="Total scrapped parts")
    total_parts: int = Field(ge=0, description="Total parts produced")
    scrap_rate: float = Field(ge=0, le=100, description="Scrap rate as percentage")
    scrap_by_machine: Optional[Dict[str, int]] = Field(
        default=None, description="Scrap breakdown by machine"
    )


class QualityIssue(BaseModel):
    """Individual quality issue record."""

    type: str = Field(description="Type of defect")
    description: str = Field(description="Issue description")
    parts_affected: int = Field(ge=0, description="Number of affected parts")
    severity: str = Field(description="Severity level (Low, Medium, High)")
    date: str = Field(description="Date of issue (YYYY-MM-DD)")
    machine: str = Field(description="Machine name")


class QualityIssues(BaseModel):
    """Collection of quality issues with statistics."""

    issues: List[QualityIssue] = Field(
        default_factory=list, description="List of issues"
    )
    total_issues: int = Field(ge=0, description="Total number of issues")
    total_parts_affected: int = Field(ge=0, description="Total parts affected")
    severity_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Count by severity"
    )


class DowntimeEvent(BaseModel):
    """Individual downtime event record."""

    reason: str = Field(description="Downtime reason category")
    description: str = Field(description="Event description")
    duration_hours: float = Field(ge=0, description="Duration in hours")


class MajorDowntimeEvent(BaseModel):
    """Major downtime event (>2 hours)."""

    date: str = Field(description="Date of event (YYYY-MM-DD)")
    machine: str = Field(description="Machine name")
    reason: str = Field(description="Downtime reason")
    description: str = Field(description="Event description")
    duration_hours: float = Field(gt=2, description="Duration in hours")


class DowntimeAnalysis(BaseModel):
    """Downtime analysis with events and breakdowns."""

    total_downtime_hours: float = Field(ge=0, description="Total downtime hours")
    downtime_by_reason: Dict[str, float] = Field(
        default_factory=dict, description="Downtime hours by reason"
    )
    major_events: List[MajorDowntimeEvent] = Field(
        default_factory=list, description="Major downtime events (>2 hours)"
    )


# ============================================================================
# Supply Chain Traceability Models (PR13)
# ============================================================================


class Supplier(BaseModel):
    """Supplier/vendor information with quality metrics."""

    id: str = Field(description="Unique supplier identifier (e.g., SUP-001)")
    name: str = Field(description="Supplier company name")
    type: str = Field(
        description="Supplier type (e.g., Raw Materials, Components, Fasteners)"
    )
    materials_supplied: List[str] = Field(
        default_factory=list, description="List of material IDs supplied by this vendor"
    )
    contact: Dict[str, str] = Field(
        default_factory=dict,
        description="Contact information (email, phone, address)",
    )
    quality_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Quality metrics (quality_rating 0-100, on_time_delivery_rate 0-100, defect_rate 0-100)",
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="Quality certifications (e.g., ISO9001, AS9100)",
    )
    status: str = Field(
        default="Active",
        description="Supplier status (Active, OnHold, Suspended)",
    )


class MaterialSpec(BaseModel):
    """Material catalog entry for materials used in production."""

    id: str = Field(description="Unique material identifier (e.g., MAT-001)")
    name: str = Field(description="Material name (e.g., Steel Bar 304, M8 Bolt)")
    category: str = Field(
        description="Material category (e.g., Steel, Fasteners, Components)"
    )
    specification: str = Field(description="Technical specification or grade")
    unit: str = Field(description="Unit of measure (e.g., kg, pieces, meters)")
    preferred_suppliers: List[str] = Field(
        default_factory=list,
        description="List of preferred supplier IDs for this material",
    )
    quality_requirements: Dict[str, str] = Field(
        default_factory=dict,
        description="Quality requirements and inspection criteria",
    )


class MaterialLot(BaseModel):
    """Material lot/batch received from supplier with inspection data."""

    lot_number: str = Field(
        description="Unique lot number (e.g., LOT-20240115-001)"
    )
    material_id: str = Field(description="Reference to MaterialSpec.id")
    supplier_id: str = Field(description="Reference to Supplier.id")
    received_date: str = Field(description="Date received (YYYY-MM-DD)")
    quantity_received: float = Field(
        ge=0, description="Quantity received in material units"
    )
    quantity_remaining: float = Field(
        ge=0, description="Quantity remaining (updated as consumed)"
    )
    inspection_results: Dict[str, str] = Field(
        default_factory=dict,
        description="Inspection results (status, inspector, notes, test_results)",
    )
    status: str = Field(
        default="Available",
        description="Lot status (Available, InUse, Depleted, Quarantine, Rejected)",
    )
    quarantine: bool = Field(
        default=False, description="True if lot is flagged for quarantine"
    )


class OrderItem(BaseModel):
    """Individual line item in a customer order."""

    part_number: str = Field(description="Part number ordered")
    quantity: int = Field(ge=1, description="Quantity ordered")
    unit_price: float = Field(ge=0, description="Unit price in dollars")


class Order(BaseModel):
    """Customer order that production fulfills."""

    id: str = Field(description="Unique order identifier (e.g., ORD-001)")
    order_number: str = Field(description="Customer-facing order number")
    customer: str = Field(description="Customer name")
    items: List[OrderItem] = Field(
        default_factory=list, description="List of ordered items"
    )
    due_date: str = Field(description="Order due date (YYYY-MM-DD)")
    status: str = Field(
        default="Pending",
        description="Order status (Pending, InProgress, Completed, Shipped, Delayed)",
    )
    priority: str = Field(
        default="Normal", description="Order priority (Low, Normal, High, Urgent)"
    )
    shipping_date: Optional[str] = Field(
        default=None, description="Actual shipping date (YYYY-MM-DD)"
    )
    total_value: float = Field(ge=0, description="Total order value in dollars")
