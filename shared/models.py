"""Pydantic models for tool responses and data validation."""

from typing import Dict, List, Literal, Optional
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
    """Individual quality issue record with optional material-supplier root cause linkage."""

    type: str = Field(description="Type of defect")
    description: str = Field(description="Issue description")
    parts_affected: int = Field(ge=0, description="Number of affected parts")
    severity: str = Field(description="Severity level (Low, Medium, High)")
    date: str = Field(description="Date of issue (YYYY-MM-DD)")
    machine: str = Field(description="Machine name")

    # Material-Supplier Root Cause Linkage (PR19)
    material_id: Optional[str] = Field(
        default=None, description="Material ID if issue is material-related"
    )
    lot_number: Optional[str] = Field(
        default=None, description="Specific material lot number that caused the issue"
    )
    supplier_id: Optional[str] = Field(
        default=None, description="Supplier ID if issue is traced to supplier quality"
    )
    supplier_name: Optional[str] = Field(
        default=None, description="Supplier name for readability"
    )
    root_cause: Optional[str] = Field(
        default="unknown",
        description="Root cause category (material_defect, supplier_quality, process_issue, machine_issue, unknown)"
    )


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


# ============================================================================
# Production Batch Traceability Models (PR14)
# ============================================================================


class MaterialUsage(BaseModel):
    """Material consumed in a production batch with lot traceability."""

    material_id: str = Field(description="Reference to MaterialSpec.id")
    material_name: str = Field(description="Material name for readability")
    lot_number: str = Field(description="Reference to MaterialLot.lot_number")
    quantity_used: float = Field(ge=0, description="Quantity consumed in batch")
    unit: str = Field(description="Unit of measure (kg, pieces, meters)")


class ProductionBatch(BaseModel):
    """
    Detailed production batch with full traceability to materials, suppliers, and orders.

    This is the source of truth for production data. The production[date][machine]
    structure becomes a DERIVED/AGGREGATED view from batches.
    """

    batch_id: str = Field(description="Unique batch identifier (e.g., BATCH-20240115-CNC001-001)")
    date: str = Field(description="Production date (YYYY-MM-DD)")
    machine_id: int = Field(ge=1, description="Reference to machine ID")
    machine_name: str = Field(description="Machine name for readability")
    shift_id: int = Field(ge=1, description="Reference to shift ID (1=Day, 2=Night)")
    shift_name: str = Field(description="Shift name for readability (Day/Night)")
    order_id: Optional[str] = Field(
        default=None, description="Reference to Order.id that this batch fulfills"
    )
    part_number: str = Field(description="Part number produced in this batch")
    operator: str = Field(description="Operator name/ID")

    # Production quantities
    parts_produced: int = Field(ge=0, description="Total parts produced in batch")
    good_parts: int = Field(ge=0, description="Number of good parts")
    scrap_parts: int = Field(ge=0, description="Number of scrapped parts")

    # Serial number tracking
    serial_start: Optional[int] = Field(
        default=None, description="Starting serial number (e.g., 1000)"
    )
    serial_end: Optional[int] = Field(
        default=None, description="Ending serial number (e.g., 1120)"
    )

    # Material traceability
    materials_consumed: List[MaterialUsage] = Field(
        default_factory=list,
        description="Materials used in this batch with lot traceability"
    )

    # Quality tracking (moved from production[date][machine])
    quality_issues: List[QualityIssue] = Field(
        default_factory=list,
        description="Quality issues specific to this batch"
    )

    # Process parameters (optional for demo)
    process_parameters: Optional[Dict[str, float]] = Field(
        default=None,
        description="Process parameters (temperature, pressure, speed, etc.)"
    )

    # Timing
    start_time: Optional[str] = Field(
        default=None, description="Batch start time (HH:MM)"
    )
    end_time: Optional[str] = Field(
        default=None, description="Batch end time (HH:MM)"
    )
    duration_hours: Optional[float] = Field(
        default=None, ge=0, description="Batch duration in hours"
    )


# ============================================================================
# Factory Agent Memory Models (PR25)
# ============================================================================


class Investigation(BaseModel):
    """
    Track ongoing issue investigations.

    Investigations capture the agent's analysis of factory issues, including
    initial observations, findings, and hypotheses. Used for:
    - Following up on issues across sessions
    - Providing continuity ("Following up on the CNC-001 issue...")
    - Shift handoff summaries
    """

    id: str = Field(description="Unique investigation ID (e.g., INV-20241126-001)")
    title: str = Field(description="Brief investigation title")
    machine_id: Optional[str] = Field(
        default=None, description="Related machine ID if applicable"
    )
    supplier_id: Optional[str] = Field(
        default=None, description="Related supplier ID if applicable"
    )
    status: Literal["open", "in_progress", "resolved", "closed"] = Field(
        default="open", description="Current investigation status"
    )
    initial_observation: str = Field(
        description="What triggered this investigation"
    )
    findings: List[str] = Field(
        default_factory=list, description="Discovered findings during investigation"
    )
    hypotheses: List[str] = Field(
        default_factory=list, description="Working hypotheses for root cause"
    )
    created_at: str = Field(description="ISO timestamp of creation")
    updated_at: str = Field(description="ISO timestamp of last update")


class Action(BaseModel):
    """
    Track actions taken and their outcomes.

    Actions record parameter changes, maintenance activities, or process
    modifications along with baseline metrics for impact measurement. Used for:
    - Tracking expected vs actual impact
    - Proactive follow-up ("Your temperature adjustment improved OEE by 8%")
    - Learning from past actions
    """

    id: str = Field(description="Unique action ID (e.g., ACT-20241126-001)")
    description: str = Field(description="What action was taken")
    action_type: Literal["parameter_change", "maintenance", "process_change"] = Field(
        description="Category of action"
    )
    machine_id: Optional[str] = Field(
        default=None, description="Related machine ID if applicable"
    )
    baseline_metrics: Dict[str, float] = Field(
        default_factory=dict,
        description="Metrics captured before action (e.g., oee, quality_rate)"
    )
    expected_impact: str = Field(description="What improvement is expected")
    actual_impact: Optional[str] = Field(
        default=None, description="Measured impact after follow-up (set later)"
    )
    follow_up_date: Optional[str] = Field(
        default=None, description="When to check results (ISO date)"
    )
    created_at: str = Field(description="ISO timestamp of creation")


class MemoryStore(BaseModel):
    """
    Container for all memory entities persisted to Azure Blob Storage.

    The MemoryStore holds investigations and actions, enabling the factory
    agent to maintain context across sessions and provide continuity.
    Stored in the factory-data container as memory.json.
    """

    version: str = Field(default="1.0", description="Schema version for migrations")
    investigations: List[Investigation] = Field(
        default_factory=list, description="Active and historical investigations"
    )
    actions: List[Action] = Field(
        default_factory=list, description="Recorded actions with outcomes"
    )
    last_updated: str = Field(description="ISO timestamp of last modification")
