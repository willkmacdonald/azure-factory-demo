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
