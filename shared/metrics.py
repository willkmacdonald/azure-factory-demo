"""Analysis and metrics calculation functions for factory production data."""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .data import load_data, load_data_async, MACHINES
from .config import OEE_PERFORMANCE_FACTOR
from .models import (
    OEEMetrics,
    ScrapMetrics,
    QualityIssues,
    QualityIssue,
    DowntimeAnalysis,
    MajorDowntimeEvent,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration Constants
# ============================================================================

# Date format pattern for validation (YYYY-MM-DD)
DATE_FORMAT_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# DEMO SIMPLIFICATION: Performance factor for OEE calculation (PR24D)
# This value is configurable via the OEE_PERFORMANCE_FACTOR environment variable.
# See shared/config.py for configuration, validation, and default value (0.95).
#
# In production, performance should be calculated as:
#   performance = (actual_output / theoretical_maximum_output)
# where theoretical_maximum_output = ideal_cycle_time * uptime
#
# Implementation steps for production:
# 1. Add ideal_cycle_time to machine configuration (e.g., 60 seconds per part)
# 2. Calculate: theoretical_output = uptime_hours * (3600 / ideal_cycle_time)
# 3. Calculate: performance = total_parts / theoretical_output
#
# The 0.95 default represents typical speed efficiency in well-maintained manufacturing:
# - Equipment rarely runs at 100% theoretical speed due to minor slowdowns
# - 95% is industry-typical for well-maintained equipment
# - Accounts for micro-stops, reduced speed periods, and quality checks


def validate_date_format(date_str: str) -> bool:
    """Validate that a date string matches YYYY-MM-DD format.

    This function provides defense-in-depth validation for date inputs
    before they are passed to datetime parsing functions. It prevents
    malformed inputs that could cause unexpected behavior or errors.

    Args:
        date_str: Date string to validate

    Returns:
        True if format matches YYYY-MM-DD, False otherwise

    Examples:
        >>> validate_date_format("2024-01-15")
        True
        >>> validate_date_format("01-15-2024")
        False
        >>> validate_date_format("2024/01/15")
        False
        >>> validate_date_format("invalid")
        False
    """
    if not date_str or not isinstance(date_str, str):
        return False
    return bool(DATE_FORMAT_PATTERN.match(date_str))


class DateValidationError(ValueError):
    """Exception raised when date format validation fails.

    Provides clear error messages for invalid date inputs to metrics functions.
    """

    def __init__(self, date_str: str, param_name: str = "date"):
        self.date_str = date_str
        self.param_name = param_name
        super().__init__(
            f"Invalid {param_name} format: '{date_str}'. "
            f"Expected format: YYYY-MM-DD (e.g., '2024-01-15')"
        )


def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Get list of dates in range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)

    Returns:
        List of date strings in YYYY-MM-DD format

    Raises:
        DateValidationError: If date format is invalid (not YYYY-MM-DD)
    """
    # Validate date formats before parsing (defense-in-depth - PR24D)
    if not validate_date_format(start_date):
        raise DateValidationError(start_date, "start_date")
    if not validate_date_format(end_date):
        raise DateValidationError(end_date, "end_date")

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


async def calculate_oee(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> OEEMetrics | Dict[str, str]:
    """
    Calculate Overall Equipment Effectiveness (OEE) for date range (async for FastAPI).

    OEE = Availability × Performance × Quality

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        OEEMetrics model or error dictionary

    Raises:
        RuntimeError: If data loading or processing fails
    """
    try:
        data = await load_data_async()
        if not data:
            return {"error": "No data available"}

        dates = get_date_range(start_date, end_date)

        # Filter dates within data range
        valid_dates = [d for d in dates if d in data["production"]]
        if not valid_dates:
            return {"error": "No data for specified date range"}

        # Aggregate metrics
        total_parts = 0
        total_good = 0
        total_uptime = 0
        total_planned_time = 0

        for date in valid_dates:
            day_data = data["production"][date]

            # Filter by machine if specified
            machines_to_process = [machine_name] if machine_name else day_data.keys()

            for machine in machines_to_process:
                if machine not in day_data:
                    continue

                m_data = day_data[machine]
                total_parts += m_data["parts_produced"]
                total_good += m_data["good_parts"]
                total_uptime += m_data["uptime_hours"]
                total_planned_time += 16  # 2 shifts * 8 hours

        if total_planned_time == 0:
            return {"error": "No valid data found"}

        # Calculate OEE components
        availability = total_uptime / total_planned_time if total_planned_time > 0 else 0
        quality = total_good / total_parts if total_parts > 0 else 0

        # Performance (simplified for demo - uses configurable constant)
        # See shared/config.py OEE_PERFORMANCE_FACTOR for:
        # - Configuration via environment variable
        # - Validation of range [0.0, 1.0]
        # See DEFAULT_PERFORMANCE_FACTOR at module level for:
        # - Production implementation steps with cycle time calculations
        # - Industry context (95% = typical speed efficiency)
        performance = OEE_PERFORMANCE_FACTOR

        oee = availability * performance * quality

        return OEEMetrics(
            oee=round(oee, 3),
            availability=round(availability, 3),
            performance=round(performance, 3),
            quality=round(quality, 3),
            total_parts=total_parts,
            good_parts=total_good,
            scrap_parts=total_parts - total_good,
        )
    except RuntimeError:
        # Re-raise RuntimeErrors from load_data_async (already have context)
        raise
    except Exception as e:
        # Catch unexpected errors during calculation
        logger.error(f"Unexpected error calculating OEE for {start_date} to {end_date}: {e}")
        raise RuntimeError(f"Failed to calculate OEE metrics: {e}") from e


async def get_scrap_metrics(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> ScrapMetrics | Dict[str, str]:
    """
    Get scrap metrics for date range (async for FastAPI).

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        ScrapMetrics model or error dictionary

    Raises:
        RuntimeError: If data loading or processing fails
    """
    try:
        data = await load_data_async()
        if not data:
            return {"error": "No data available"}

        dates = get_date_range(start_date, end_date)
        valid_dates = [d for d in dates if d in data["production"]]

        total_scrap = 0
        total_parts = 0
        scrap_by_machine: Dict[str, int] = {}

        for date in valid_dates:
            day_data = data["production"][date]
            machines_to_process = [machine_name] if machine_name else day_data.keys()

            for machine in machines_to_process:
                if machine not in day_data:
                    continue

                m_data = day_data[machine]
                scrap = m_data["scrap_parts"]
                parts = m_data["parts_produced"]

                total_scrap += scrap
                total_parts += parts

                if not machine_name:
                    scrap_by_machine[machine] = scrap_by_machine.get(machine, 0) + scrap

        scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0

        return ScrapMetrics(
            total_scrap=total_scrap,
            total_parts=total_parts,
            scrap_rate=round(scrap_rate, 2),
            scrap_by_machine=scrap_by_machine if scrap_by_machine else None,
        )
    except RuntimeError:
        # Re-raise RuntimeErrors from load_data_async (already have context)
        raise
    except Exception as e:
        # Catch unexpected errors during calculation
        logger.error(f"Unexpected error calculating scrap metrics for {start_date} to {end_date}: {e}")
        raise RuntimeError(f"Failed to calculate scrap metrics: {e}") from e


async def get_quality_issues(
    start_date: str,
    end_date: str,
    severity: Optional[str] = None,
    machine_name: Optional[str] = None,
) -> QualityIssues | Dict[str, str]:
    """
    Get quality issues for date range (async for FastAPI).

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        severity: Optional severity filter (Low, Medium, High)
        machine_name: Optional machine name filter

    Returns:
        QualityIssues model or error dictionary

    Raises:
        RuntimeError: If data loading or processing fails
    """
    try:
        data = await load_data_async()
        if not data:
            return {"error": "No data available"}

        dates = get_date_range(start_date, end_date)
        valid_dates = [d for d in dates if d in data["production"]]

        issues: List[QualityIssue] = []
        severity_breakdown: Dict[str, int] = {}
        total_parts_affected = 0

        for date in valid_dates:
            day_data = data["production"][date]
            machines_to_process = [machine_name] if machine_name else day_data.keys()

            for machine in machines_to_process:
                if machine not in day_data:
                    continue

                m_data = day_data[machine]
                for issue in m_data.get("quality_issues", []):
                    # Filter by severity if specified
                    if severity and issue["severity"] != severity:
                        continue

                    quality_issue = QualityIssue(
                        type=issue["type"],
                        description=issue["description"],
                        parts_affected=issue["parts_affected"],
                        severity=issue["severity"],
                        date=date,
                        machine=machine,
                        # PR19: Material-supplier root cause linkage
                        material_id=issue.get("material_id"),
                        lot_number=issue.get("lot_number"),
                        supplier_id=issue.get("supplier_id"),
                        supplier_name=issue.get("supplier_name"),
                        root_cause=issue.get("root_cause", "unknown"),
                    )
                    issues.append(quality_issue)

                    total_parts_affected += issue["parts_affected"]
                    sev = issue["severity"]
                    severity_breakdown[sev] = severity_breakdown.get(sev, 0) + 1

        return QualityIssues(
            issues=issues,
            total_issues=len(issues),
            total_parts_affected=total_parts_affected,
            severity_breakdown=severity_breakdown,
        )
    except RuntimeError:
        # Re-raise RuntimeErrors from load_data_async (already have context)
        raise
    except Exception as e:
        # Catch unexpected errors during calculation
        logger.error(f"Unexpected error fetching quality issues for {start_date} to {end_date}: {e}")
        raise RuntimeError(f"Failed to fetch quality issues: {e}") from e


async def get_downtime_analysis(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> DowntimeAnalysis | Dict[str, str]:
    """
    Analyze downtime events (async for FastAPI).

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        DowntimeAnalysis model or error dictionary

    Raises:
        RuntimeError: If data loading or processing fails
    """
    try:
        data = await load_data_async()
        if not data:
            return {"error": "No data available"}

        dates = get_date_range(start_date, end_date)
        valid_dates = [d for d in dates if d in data["production"]]

        total_downtime = 0
        downtime_by_reason: Dict[str, float] = {}
        major_events: List[MajorDowntimeEvent] = []

        for date in valid_dates:
            day_data = data["production"][date]
            machines_to_process = [machine_name] if machine_name else day_data.keys()

            for machine in machines_to_process:
                if machine not in day_data:
                    continue

                m_data = day_data[machine]
                total_downtime += m_data["downtime_hours"]

                for event in m_data.get("downtime_events", []):
                    reason = event["reason"]
                    hours = event["duration_hours"]

                    downtime_by_reason[reason] = downtime_by_reason.get(reason, 0) + hours

                    # Track major events (> 2 hours)
                    if hours > 2.0:
                        major_event = MajorDowntimeEvent(
                            date=date,
                            machine=machine,
                            reason=reason,
                            description=event["description"],
                            duration_hours=hours,
                        )
                        major_events.append(major_event)

        return DowntimeAnalysis(
            total_downtime_hours=round(total_downtime, 2),
            downtime_by_reason={k: round(v, 2) for k, v in downtime_by_reason.items()},
            major_events=major_events,
        )
    except RuntimeError:
        # Re-raise RuntimeErrors from load_data_async (already have context)
        raise
    except Exception as e:
        # Catch unexpected errors during calculation
        logger.error(f"Unexpected error analyzing downtime for {start_date} to {end_date}: {e}")
        raise RuntimeError(f"Failed to analyze downtime: {e}") from e
