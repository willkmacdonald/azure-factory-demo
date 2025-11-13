"""Shared package for common code between CLI and backend API."""

from shared.models import (
    DowntimeAnalysis,
    DowntimeEvent,
    MajorDowntimeEvent,
    MaterialLot,
    MaterialSpec,
    OEEMetrics,
    Order,
    OrderItem,
    QualityIssue,
    QualityIssues,
    ScrapMetrics,
    Supplier,
)

__version__ = "0.1.0"

__all__ = [
    "DowntimeAnalysis",
    "DowntimeEvent",
    "MajorDowntimeEvent",
    "MaterialLot",
    "MaterialSpec",
    "OEEMetrics",
    "Order",
    "OrderItem",
    "QualityIssue",
    "QualityIssues",
    "ScrapMetrics",
    "Supplier",
]
