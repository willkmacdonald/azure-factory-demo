"""Memory API routes for Factory Agent (PR27).

This module provides REST API endpoints for accessing agent memory data,
including investigations, actions, and shift handoff summaries.

Endpoints:
- GET /api/memory/summary - Overall memory statistics
- GET /api/memory/investigations - List investigations with optional filters
- GET /api/memory/actions - List actions with optional filters
- GET /api/memory/shift-summary - Generate shift handoff summary
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from shared.memory_service import (
    generate_shift_summary,
    get_relevant_memories,
    load_memory_store,
)
from shared.models import Action, Investigation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory", tags=["Memory"])


# =============================================================================
# Response Models
# =============================================================================


class MemorySummaryResponse(BaseModel):
    """Response model for memory summary endpoint."""

    total_investigations: int = Field(description="Total number of investigations")
    total_actions: int = Field(description="Total number of actions")
    open_investigations: int = Field(description="Count of open investigations")
    in_progress_investigations: int = Field(
        description="Count of in-progress investigations"
    )
    resolved_investigations: int = Field(description="Count of resolved investigations")
    pending_followups: int = Field(description="Count of actions pending follow-up")
    last_updated: str = Field(description="Last memory store update timestamp")


class InvestigationsResponse(BaseModel):
    """Response model for investigations list endpoint."""

    investigations: List[Investigation] = Field(description="List of investigations")
    total: int = Field(description="Total count of returned investigations")


class ActionsResponse(BaseModel):
    """Response model for actions list endpoint."""

    actions: List[Action] = Field(description="List of actions")
    total: int = Field(description="Total count of returned actions")


class ShiftSummaryResponse(BaseModel):
    """Response model for shift summary endpoint."""

    date: str = Field(description="Summary date (YYYY-MM-DD)")
    active_investigations: List[Dict[str, Any]] = Field(
        description="Active investigations summary"
    )
    todays_actions: List[Dict[str, Any]] = Field(
        description="Actions taken today"
    )
    pending_followups: List[Dict[str, Any]] = Field(
        description="Actions pending follow-up"
    )
    counts: Dict[str, int] = Field(description="Summary counts")


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/summary", response_model=MemorySummaryResponse)
async def get_memory_summary() -> MemorySummaryResponse:
    """Get overall memory statistics.

    Returns summary counts of investigations and actions, including status
    breakdowns for monitoring agent memory health.

    Returns:
        MemorySummaryResponse: Summary statistics for memory store

    Raises:
        HTTPException: If memory store access fails
    """
    try:
        memory = await load_memory_store()

        # Count investigation statuses
        open_count = sum(
            1 for i in memory.investigations if i.status == "open"
        )
        in_progress_count = sum(
            1 for i in memory.investigations if i.status == "in_progress"
        )
        resolved_count = sum(
            1 for i in memory.investigations if i.status == "resolved"
        )

        # Count pending follow-ups (actions with follow_up_date but no actual_impact)
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        pending_followups = sum(
            1
            for a in memory.actions
            if a.follow_up_date and a.follow_up_date <= today and a.actual_impact is None
        )

        logger.info(
            f"Memory summary: {len(memory.investigations)} investigations, "
            f"{len(memory.actions)} actions"
        )

        return MemorySummaryResponse(
            total_investigations=len(memory.investigations),
            total_actions=len(memory.actions),
            open_investigations=open_count,
            in_progress_investigations=in_progress_count,
            resolved_investigations=resolved_count,
            pending_followups=pending_followups,
            last_updated=memory.last_updated,
        )

    except RuntimeError as e:
        logger.error(f"Failed to load memory store: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in memory summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve memory summary"
        )


@router.get("/investigations", response_model=InvestigationsResponse)
async def get_investigations(
    machine_id: Optional[str] = Query(
        default=None, description="Filter by machine ID"
    ),
    supplier_id: Optional[str] = Query(
        default=None, description="Filter by supplier ID"
    ),
    status: Optional[str] = Query(
        default=None,
        description="Filter by status (open, in_progress, resolved, closed)",
    ),
) -> InvestigationsResponse:
    """List investigations with optional filters.

    Returns investigations filtered by machine, supplier, or status.
    Use this endpoint to display investigation history in the frontend.

    Args:
        machine_id: Filter by machine ID (e.g., "CNC-001")
        supplier_id: Filter by supplier ID (e.g., "SUP-001")
        status: Filter by status (open, in_progress, resolved, closed)

    Returns:
        InvestigationsResponse: List of investigations matching filters

    Raises:
        HTTPException: If memory store access fails
    """
    # Validate status if provided
    valid_statuses = {"open", "in_progress", "resolved", "closed"}
    if status and status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{status}'. Valid values: {', '.join(valid_statuses)}",
        )

    try:
        result = await get_relevant_memories(
            machine_id=machine_id, supplier_id=supplier_id, status=status
        )

        # Convert dicts back to Investigation models for validation
        investigations = [
            Investigation.model_validate(inv) for inv in result["investigations"]
        ]

        logger.info(
            f"Fetched {len(investigations)} investigations "
            f"(filters: machine_id={machine_id}, supplier_id={supplier_id}, status={status})"
        )

        return InvestigationsResponse(
            investigations=investigations, total=len(investigations)
        )

    except RuntimeError as e:
        logger.error(f"Failed to load investigations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching investigations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve investigations"
        )


@router.get("/actions", response_model=ActionsResponse)
async def get_actions(
    machine_id: Optional[str] = Query(
        default=None, description="Filter by machine ID"
    ),
) -> ActionsResponse:
    """List actions with optional filters.

    Returns actions filtered by machine. Use this endpoint to display
    action history and track impact of changes.

    Args:
        machine_id: Filter by machine ID (e.g., "CNC-001")

    Returns:
        ActionsResponse: List of actions matching filters

    Raises:
        HTTPException: If memory store access fails
    """
    try:
        result = await get_relevant_memories(machine_id=machine_id)

        # Convert dicts back to Action models for validation
        actions = [Action.model_validate(act) for act in result["actions"]]

        logger.info(
            f"Fetched {len(actions)} actions (filter: machine_id={machine_id})"
        )

        return ActionsResponse(actions=actions, total=len(actions))

    except RuntimeError as e:
        logger.error(f"Failed to load actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error fetching actions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve actions")


@router.get("/shift-summary", response_model=ShiftSummaryResponse)
async def get_shift_summary() -> ShiftSummaryResponse:
    """Generate shift handoff summary.

    Returns a summary of today's activities for shift handoff, including:
    - Active investigations requiring attention
    - Actions taken today
    - Pending follow-ups that need checking

    This endpoint is designed for shift changes to ensure continuity
    of factory operations and investigations.

    Returns:
        ShiftSummaryResponse: Shift handoff summary

    Raises:
        HTTPException: If memory store access fails
    """
    try:
        summary = await generate_shift_summary()

        logger.info(
            f"Generated shift summary: {summary['counts']['active_investigations']} active, "
            f"{summary['counts']['todays_actions']} actions, "
            f"{summary['counts']['pending_followups']} follow-ups"
        )

        return ShiftSummaryResponse(
            date=summary["date"],
            active_investigations=summary["active_investigations"],
            todays_actions=summary["todays_actions"],
            pending_followups=summary["pending_followups"],
            counts=summary["counts"],
        )

    except RuntimeError as e:
        logger.error(f"Failed to generate shift summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in shift summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate shift summary"
        )
