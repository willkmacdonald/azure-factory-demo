"""Metrics API endpoints for factory production data.

This module provides REST endpoints for accessing factory metrics including:
- OEE (Overall Equipment Effectiveness)
- Scrap metrics
- Quality issues
- Downtime analysis

All endpoints have rate limiting applied to prevent API abuse.
"""

from typing import Optional, Union, Dict
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
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

# Initialize rate limiter for metrics endpoints
# Limits: 100 requests per minute per IP address
#
# Note: This local limiter instance is used for decorator-based rate limiting
# on individual routes. The main application limiter is registered in main.py
# (app.state.limiter) for global configuration. Both approaches are valid in SlowAPI:
# - app.state.limiter: Global instance for middleware and shared config
# - Local limiter: Used with @limiter.limit() decorators on routes
#
# This pattern allows per-route customization while maintaining centralized config.
limiter = Limiter(key_func=get_remote_address)


@router.get("/oee", response_model=Union[OEEMetrics, Dict[str, str]])
@limiter.limit("100/minute")
async def get_oee(
    request: Request,
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[OEEMetrics, Dict[str, str]]:
    """Get Overall Equipment Effectiveness (OEE) metrics.

    OEE is calculated as: Availability × Performance × Quality

    Rate limit: 100 requests per minute per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
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
    return await calculate_oee(start_date, end_date, machine)


@router.get("/scrap", response_model=Union[ScrapMetrics, Dict[str, str]])
@limiter.limit("100/minute")
async def get_scrap(
    request: Request,
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[ScrapMetrics, Dict[str, str]]:
    """Get scrap and waste metrics.

    Rate limit: 100 requests per minute per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
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
    return await get_scrap_metrics(start_date, end_date, machine)


@router.get("/quality", response_model=Union[QualityIssues, Dict[str, str]])
@limiter.limit("100/minute")
async def get_quality(
    request: Request,
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    severity: Optional[str] = Query(
        None, description="Filter by severity (Low, Medium, High)"
    ),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[QualityIssues, Dict[str, str]]:
    """Get quality issues and defects.

    Rate limit: 100 requests per minute per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
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
    return await get_quality_issues(start_date, end_date, severity, machine)


@router.get("/downtime", response_model=Union[DowntimeAnalysis, Dict[str, str]])
@limiter.limit("100/minute")
async def get_downtime(
    request: Request,
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    machine: Optional[str] = Query(None, description="Optional machine name filter"),
) -> Union[DowntimeAnalysis, Dict[str, str]]:
    """Get downtime analysis and major events.

    Rate limit: 100 requests per minute per IP address.

    Args:
        request: FastAPI request object (for rate limiting)
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
    return await get_downtime_analysis(start_date, end_date, machine)
