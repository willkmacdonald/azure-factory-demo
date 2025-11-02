"""Analysis and metrics calculation functions for factory production data."""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .data import load_data, MACHINES
from .models import (
    OEEMetrics,
    ScrapMetrics,
    QualityIssues,
    QualityIssue,
    DowntimeAnalysis,
    MajorDowntimeEvent,
)


def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Get list of dates in range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)

    Returns:
        List of date strings in YYYY-MM-DD format
    """
    start = datetime.fromisoformat(start_date.split("T")[0])
    end = datetime.fromisoformat(end_date.split("T")[0])
    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def calculate_oee(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> OEEMetrics | Dict[str, str]:
    """
    Calculate Overall Equipment Effectiveness (OEE) for date range.

    OEE = Availability × Performance × Quality

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        OEEMetrics model or error dictionary
    """
    data = load_data()
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

    # Performance (simplified - assume running at 95% of ideal when uptime)
    performance = 0.95

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


def get_scrap_metrics(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> ScrapMetrics | Dict[str, str]:
    """
    Get scrap metrics for date range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        ScrapMetrics model or error dictionary
    """
    data = load_data()
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


def get_quality_issues(
    start_date: str,
    end_date: str,
    severity: Optional[str] = None,
    machine_name: Optional[str] = None,
) -> QualityIssues | Dict[str, str]:
    """
    Get quality issues for date range.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        severity: Optional severity filter (Low, Medium, High)
        machine_name: Optional machine name filter

    Returns:
        QualityIssues model or error dictionary
    """
    data = load_data()
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


def get_downtime_analysis(
    start_date: str, end_date: str, machine_name: Optional[str] = None
) -> DowntimeAnalysis | Dict[str, str]:
    """
    Analyze downtime events.

    Args:
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        machine_name: Optional machine name filter

    Returns:
        DowntimeAnalysis model or error dictionary
    """
    data = load_data()
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
