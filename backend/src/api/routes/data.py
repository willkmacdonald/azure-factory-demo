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
- POST /api/setup: Generate synthetic production data (rate-limited, requires authentication)
- GET /api/stats: Get data statistics (record counts, date ranges)
- GET /api/machines: List available machines
- GET /api/date-range: Get available data date range
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address

from shared.data import (
    initialize_data,
    initialize_data_async,
    load_data,
    load_data_async,
    data_exists,
    MACHINES,
)
from shared.config import RATE_LIMIT_SETUP
from src.api.auth import get_current_user

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

# Create an APIRouter instance for grouping data-related endpoints
# The prefix "/api" is added to all routes in this router
# The "tags" parameter groups these endpoints in the auto-generated docs
router = APIRouter(prefix="/api", tags=["Data"])

# Create limiter instance for this router
# Used to apply rate limits to the setup endpoint (prevents spam data generation)
limiter = Limiter(key_func=get_remote_address)

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class SetupRequest(BaseModel):
    """Request model for data generation endpoint.

    Attributes:
        days: Number of days of production data to generate (1-365, default: 30)
    """
    days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days of production data to generate (1-365)"
    )


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
        supplier_count: Number of suppliers (traceability)
        material_lot_count: Number of material lots (traceability)
        order_count: Number of customer orders (traceability)
        batch_count: Number of production batches (traceability)
    """
    exists: bool
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_days: Optional[int] = None
    total_machines: Optional[int] = None
    total_records: Optional[int] = None
    supplier_count: Optional[int] = None
    material_lot_count: Optional[int] = None
    order_count: Optional[int] = None
    batch_count: Optional[int] = None


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
@limiter.limit(RATE_LIMIT_SETUP)
async def setup_data(
    request: Request,
    setup_request: SetupRequest = SetupRequest(),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> SetupResponse:
    """Generate synthetic production data.

    This endpoint generates synthetic factory production data for testing
    and demonstration purposes. The data includes:
    - Production counts per machine per day
    - Quality issues and scrap rates
    - Downtime events
    - Shift-level metrics
    - Planted scenarios for interesting analysis

    Security (PR24B): This endpoint requires Azure AD authentication to prevent
    unauthorized data generation. Only authenticated users can generate data,
    which protects against:
    - Unauthorized data overwrites
    - Resource exhaustion from spam data generation
    - Malicious data corruption

    Rate limiting (PR7): This endpoint is rate-limited to prevent abuse.
    Default limit is 5 requests per minute per IP address (configurable via
    RATE_LIMIT_SETUP environment variable). Data generation is computationally
    expensive, so this prevents spam.

    Flow:
    1. Validate Azure AD JWT token (via get_current_user dependency)
    2. Receive request with optional 'days' parameter
    3. Call initialize_data() to generate synthetic data
    4. Load generated data to extract metadata
    5. Return summary statistics

    Args:
        request: FastAPI Request object (required for rate limiting - slowapi)
        setup_request: SetupRequest with optional days parameter (default: 30)
        current_user: Authenticated user information (injected by get_current_user)

    Returns:
        SetupResponse: Summary of generated data

    Raises:
        HTTPException: 401 if not authenticated (via get_current_user dependency)
        HTTPException: 500 if data generation fails
        RateLimitExceeded: If rate limit is exceeded (returns 429 status)

    Example:
        POST /api/setup
        Headers: Authorization: Bearer <azure_ad_token>
        Body: {"days": 60}

        Response:
        {
            "message": "Data generated successfully",
            "days": 60,
            "start_date": "2024-12-03T00:00:00",
            "end_date": "2025-01-31T00:00:00",
            "machines": 4
        }
    """
    # Log authenticated user for audit trail
    logger.info(
        f"Data generation initiated by authenticated user: {current_user.get('email')} "
        f"(days={setup_request.days})"
    )

    try:
        # Generate and save data asynchronously, get metadata directly from return value
        result = await initialize_data_async(days=setup_request.days)

        logger.info(
            f"Data generation completed successfully by {current_user.get('email')} "
            f"(days={result['days']}, start={result['start_date']}, end={result['end_date']})"
        )

        return SetupResponse(
            message="Data generated successfully",
            days=result["days"],
            start_date=result["start_date"],
            end_date=result["end_date"],
            machines=result["machines"]
        )
    except Exception as e:
        logger.error(
            f"Data generation failed for user {current_user.get('email')}: {e}",
            exc_info=True
        )
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
            "total_records": 240,
            "supplier_count": 10,
            "material_lot_count": 45,
            "order_count": 15,
            "batch_count": 120
        }

        Response (no data):
        {
            "exists": false,
            "start_date": null,
            "end_date": null,
            "total_days": null,
            "total_machines": null,
            "total_records": null,
            "supplier_count": null,
            "material_lot_count": null,
            "order_count": null,
            "batch_count": null
        }
    """
    try:
        data = await load_data_async()
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

        # Traceability counts (Phase 2 enhancement)
        supplier_count = len(data.get("suppliers", []))
        material_lot_count = len(data.get("material_lots", []))
        order_count = len(data.get("orders", []))
        batch_count = len(data.get("production_batches", []))

        return StatsResponse(
            exists=True,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            total_days=total_days,
            total_machines=total_machines,
            total_records=total_records,
            supplier_count=supplier_count,
            material_lot_count=material_lot_count,
            order_count=order_count,
            batch_count=batch_count
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
    try:
        data = await load_data_async()
        if data is None:
            raise HTTPException(
                status_code=404,
                detail="No data available. Generate data using POST /api/setup"
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
