"""Synchronous wrappers for metrics functions (Streamlit compatibility).

This module provides synchronous wrappers around the async metrics functions
in shared/metrics.py. Streamlit does not support async/await at the page level,
so these wrappers use asyncio.run() to execute async functions synchronously.

Note: This is specifically for the Streamlit dashboard. FastAPI routes should
import directly from shared.metrics and use await with the async functions.
"""

import asyncio
from typing import Dict, Optional, Union

from shared.metrics import (
    calculate_oee as async_calculate_oee,
    get_scrap_metrics as async_get_scrap_metrics,
    get_quality_issues as async_get_quality_issues,
    get_downtime_analysis as async_get_downtime_analysis,
)
from shared.models import OEEMetrics, ScrapMetrics, QualityIssues, DowntimeAnalysis


def calculate_oee(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> Union[OEEMetrics, Dict[str, str]]:
    """Calculate Overall Equipment Effectiveness (synchronous wrapper for Streamlit).

    This is a synchronous wrapper around the async calculate_oee function.
    Use this in Streamlit dashboard code. For FastAPI routes, use the async
    version from shared.metrics directly.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        machine_name: Optional machine name filter

    Returns:
        OEEMetrics object or error dict
    """
    return asyncio.run(async_calculate_oee(start_date, end_date, machine_name))


def get_scrap_metrics(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> Union[ScrapMetrics, Dict[str, str]]:
    """Get scrap and waste metrics (synchronous wrapper for Streamlit).

    This is a synchronous wrapper around the async get_scrap_metrics function.
    Use this in Streamlit dashboard code. For FastAPI routes, use the async
    version from shared.metrics directly.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        machine_name: Optional machine name filter

    Returns:
        ScrapMetrics object or error dict
    """
    return asyncio.run(async_get_scrap_metrics(start_date, end_date, machine_name))


def get_quality_issues(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> Union[QualityIssues, Dict[str, str]]:
    """Get quality issues and defects (synchronous wrapper for Streamlit).

    This is a synchronous wrapper around the async get_quality_issues function.
    Use this in Streamlit dashboard code. For FastAPI routes, use the async
    version from shared.metrics directly.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        machine_name: Optional machine name filter

    Returns:
        QualityIssues object or error dict
    """
    return asyncio.run(async_get_quality_issues(start_date, end_date, machine_name))


def get_downtime_analysis(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> Union[DowntimeAnalysis, Dict[str, str]]:
    """Get downtime analysis (synchronous wrapper for Streamlit).

    This is a synchronous wrapper around the async get_downtime_analysis function.
    Use this in Streamlit dashboard code. For FastAPI routes, use the async
    version from shared.metrics directly.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        machine_name: Optional machine name filter

    Returns:
        DowntimeAnalysis object or error dict
    """
    return asyncio.run(async_get_downtime_analysis(start_date, end_date, machine_name))
