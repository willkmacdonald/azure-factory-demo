"""Metrics API endpoints for factory production data.

This module provides REST endpoints for accessing factory metrics including:
- OEE (Overall Equipment Effectiveness)
- Scrap metrics
- Quality issues
- Downtime analysis
"""

from typing import Optional, Union, Dict
from fastapi import APIRouter, Query
from shared.models import (
    OEEMetrics,
    ScrapMetrics,
    QualityIssues,
    DowntimeAnalysis,
)
from shared.metrics import (
    calculate_oee,
    get_scrap_metrics,
    get_quality_issues,
    get_downtime_analysis,
)

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("/oee", response_model=Union[OEEMetrics, Dict[str, str]])
async def get_oee(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[OEEMetrics, Dict[str, str]]:
    """Get Overall Equipment Effectiveness (OEE) metrics.

    OEE is calculated as: Availability × Performance × Quality

    Args:
        start_date: Start date for metrics calculation (YYYY-MM-DD)
        end_date: End date for metrics calculation (YYYY-MM-DD)
        machine: Optional machine name to filter results

    Returns:
        OEEMetrics containing OEE components and production counts,
        or error dictionary if no data available

    Example:
        GET /api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31
        GET /api/metrics/oee?start_date=2024-01-01&end_date=2024-01-31&machine=CNC-001
    """
    return calculate_oee(start_date, end_date, machine)


@router.get("/scrap", response_model=Union[ScrapMetrics, Dict[str, str]])
async def get_scrap(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[ScrapMetrics, Dict[str, str]]:
    """Get scrap and waste metrics.

    Args:
        start_date: Start date for metrics calculation (YYYY-MM-DD)
        end_date: End date for metrics calculation (YYYY-MM-DD)
        machine: Optional machine name to filter results

    Returns:
        ScrapMetrics containing scrap counts, rates, and machine breakdown,
        or error dictionary if no data available

    Example:
        GET /api/metrics/scrap?start_date=2024-01-01&end_date=2024-01-31
        GET /api/metrics/scrap?start_date=2024-01-01&end_date=2024-01-31&machine=Assembly-001
    """
    return get_scrap_metrics(start_date, end_date, machine)


@router.get("/quality", response_model=Union[QualityIssues, Dict[str, str]])
async def get_quality(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    severity: Optional[str] = Query(
        None, description="Filter by severity (Low, Medium, High)"
    ),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[QualityIssues, Dict[str, str]]:
    """Get quality issues and defects.

    Args:
        start_date: Start date for metrics calculation (YYYY-MM-DD)
        end_date: End date for metrics calculation (YYYY-MM-DD)
        severity: Optional severity filter (Low, Medium, High)
        machine: Optional machine name to filter results

    Returns:
        QualityIssues containing list of issues and statistics,
        or error dictionary if no data available

    Example:
        GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31
        GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31&severity=High
        GET /api/metrics/quality?start_date=2024-01-01&end_date=2024-01-31&machine=Testing-001&severity=Medium
    """
    return get_quality_issues(start_date, end_date, severity, machine)


@router.get("/downtime", response_model=Union[DowntimeAnalysis, Dict[str, str]])
async def get_downtime(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[DowntimeAnalysis, Dict[str, str]]:
    """Get downtime analysis and major events.

    Args:
        start_date: Start date for metrics calculation (YYYY-MM-DD)
        end_date: End date for metrics calculation (YYYY-MM-DD)
        machine: Optional machine name to filter results

    Returns:
        DowntimeAnalysis containing downtime breakdowns and major events (>2 hours),
        or error dictionary if no data available

    Example:
        GET /api/metrics/downtime?start_date=2024-01-01&end_date=2024-01-31
        GET /api/metrics/downtime?start_date=2024-01-01&end_date=2024-01-31&machine=Packaging-001
    """
    return get_downtime_analysis(start_date, end_date, machine)
