"""Data management endpoints for factory operations.

This module provides REST API endpoints for:
- Generating synthetic production data
- Querying data statistics
- Retrieving available machines
- Getting data date ranges

Code Flow:
1. Client sends request to one of the data endpoints
2. FastAPI routes request to appropriate function
3. Function calls data layer (data.py) for operations
4. Response is serialized to JSON and returned to client

This module provides:
- POST /api/setup: Generate synthetic production data
- GET /api/stats: Get data statistics (record counts, date ranges)
- GET /api/machines: List available machines
- GET /api/date-range: Get available data date range
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.data import (
    initialize_data,
    load_data,
    data_exists,
    MACHINES,
)

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

# Create an APIRouter instance for grouping data-related endpoints
# The prefix "/api" is added to all routes in this router
# The "tags" parameter groups these endpoints in the auto-generated docs
router = APIRouter(prefix="/api", tags=["Data"])

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class SetupRequest(BaseModel):
    """Request model for data generation endpoint.

    Attributes:
        days: Number of days of production data to generate (default: 30)
    """
    days: int = 30


class SetupResponse(BaseModel):
    """Response model for data generation endpoint.

    Attributes:
        message: Success message
        days: Number of days generated
        start_date: ISO format start date
        end_date: ISO format end date
        machines: Number of machines
    """
    message: str
    days: int
    start_date: str
    end_date: str
    machines: int


class StatsResponse(BaseModel):
    """Response model for data statistics endpoint.

    Attributes:
        exists: Whether data file exists
        start_date: ISO format start date (if data exists)
        end_date: ISO format end date (if data exists)
        total_days: Total number of days with data
        total_machines: Total number of machines
        total_records: Total production records
    """
    exists: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = None
    total_machines: Optional[int] = None
    total_records: Optional[int] = None


class MachineInfo(BaseModel):
    """Machine information model.

    Attributes:
        id: Machine ID
        name: Machine name
        type: Machine type
        ideal_cycle_time: Ideal cycle time in seconds
    """
    id: int
    name: str
    type: str
    ideal_cycle_time: int


class DateRangeResponse(BaseModel):
    """Response model for date range endpoint.

    Attributes:
        start_date: ISO format start date
        end_date: ISO format end date
        total_days: Total number of days with data
    """
    start_date: str
    end_date: str
    total_days: int


# =============================================================================
# API ENDPOINTS
# =============================================================================


@router.post("/setup", response_model=SetupResponse)
async def setup_data(request: SetupRequest = SetupRequest()) -> SetupResponse:
    """Generate synthetic production data.

    This endpoint generates synthetic factory production data for testing
    and demonstration purposes. The data includes:
    - Production counts per machine per day
    - Quality issues and scrap rates
    - Downtime events
    - Shift-level metrics
    - Planted scenarios for interesting analysis

    Flow:
    1. Receive request with optional 'days' parameter
    2. Call initialize_data() to generate synthetic data
    3. Load generated data to extract metadata
    4. Return summary statistics

    Args:
        request: SetupRequest with optional days parameter (default: 30)

    Returns:
        SetupResponse: Summary of generated data

    Raises:
        HTTPException: 500 if data generation fails

    Example:
        POST /api/setup
        {"days": 60}

        Response:
        {
            "message": "Data generated successfully",
            "days": 60,
            "start_date": "2024-12-03T00:00:00",
            "end_date": "2025-01-31T00:00:00",
            "machines": 4
        }
    """
    try:
        # Generate and save data
        initialize_data(days=request.days)

        # Load data to get metadata
        data = load_data()
        if data is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to load generated data"
            )

        return SetupResponse(
            message="Data generated successfully",
            days=request.days,
            start_date=data["start_date"],
            end_date=data["end_date"],
            machines=len(data["machines"])
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate data: {str(e)}"
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """Get data statistics.

    This endpoint provides statistics about the currently available
    production data, including date ranges, record counts, and metadata.

    Flow:
    1. Check if data file exists
    2. If exists, load data and calculate statistics
    3. Return statistics (or exists=False if no data)

    Returns:
        StatsResponse: Data statistics or empty stats if no data exists

    Example:
        GET /api/stats

        Response (with data):
        {
            "exists": true,
            "start_date": "2024-12-03T00:00:00",
            "end_date": "2025-01-31T00:00:00",
            "total_days": 60,
            "total_machines": 4,
            "total_records": 240
        }

        Response (no data):
        {
            "exists": false,
            "start_date": null,
            "end_date": null,
            "total_days": null,
            "total_machines": null,
            "total_records": null
        }
    """
    if not data_exists():
        return StatsResponse(exists=False)

    try:
        data = load_data()
        if data is None:
            return StatsResponse(exists=False)

        # Calculate statistics
        production_data = data.get("production", {})
        total_days = len(production_data)
        total_machines = len(data.get("machines", []))

        # Total records = days * machines
        total_records = sum(
            len(day_data) for day_data in production_data.values()
        )

        return StatsResponse(
            exists=True,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            total_days=total_days,
            total_machines=total_machines,
            total_records=total_records
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load data statistics: {str(e)}"
        )


@router.get("/machines", response_model=List[MachineInfo])
async def get_machines() -> List[MachineInfo]:
    """List available machines.

    This endpoint returns a list of all machines in the factory.
    The machine list is static and defined in data.py.

    Flow:
    1. Return MACHINES constant from data.py
    2. FastAPI serializes to JSON using MachineInfo model

    Returns:
        List[MachineInfo]: List of all available machines

    Example:
        GET /api/machines

        Response:
        [
            {
                "id": 1,
                "name": "CNC-001",
                "type": "CNC Machining Center",
                "ideal_cycle_time": 45
            },
            {
                "id": 2,
                "name": "Assembly-001",
                "type": "Assembly Station",
                "ideal_cycle_time": 120
            },
            ...
        ]
    """
    return [MachineInfo(**machine) for machine in MACHINES]


@router.get("/date-range", response_model=DateRangeResponse)
async def get_date_range() -> DateRangeResponse:
    """Get available data date range.

    This endpoint returns the date range covered by the available
    production data. Useful for UI components that need to know
    what date ranges can be queried.

    Flow:
    1. Check if data exists
    2. Load data and extract start/end dates
    3. Calculate total days
    4. Return date range information

    Returns:
        DateRangeResponse: Date range information

    Raises:
        HTTPException: 404 if no data exists

    Example:
        GET /api/date-range

        Response:
        {
            "start_date": "2024-12-03T00:00:00",
            "end_date": "2025-01-31T00:00:00",
            "total_days": 60
        }
    """
    if not data_exists():
        raise HTTPException(
            status_code=404,
            detail="No data available. Generate data using POST /api/setup"
        )

    try:
        data = load_data()
        if data is None:
            raise HTTPException(
                status_code=404,
                detail="No data available"
            )

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not start_date or not end_date:
            raise HTTPException(
                status_code=500,
                detail="Invalid data format: missing date information"
            )

        # Calculate total days
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        total_days = (end - start).days + 1

        return DateRangeResponse(
            start_date=start_date,
            end_date=end_date,
            total_days=total_days
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load date range: {str(e)}"
        )
