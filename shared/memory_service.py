"""Memory service for Factory Agent persistence (PR25).

This module provides async functions for persisting and retrieving agent memory
entities (investigations and actions) to/from Azure Blob Storage.

Key capabilities:
- Load/save MemoryStore to Azure Blob Storage
- Create and update investigations
- Log actions with baseline metrics
- Filter memories by machine/supplier/status
- Generate shift handoff summaries
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .blob_storage import BlobStorageClient
from .config import MEMORY_BLOB_NAME, STORAGE_MODE
from .models import Action, Investigation, MemoryStore

logger = logging.getLogger(__name__)


def _generate_investigation_id() -> str:
    """Generate a unique investigation ID based on timestamp.

    Returns:
        Investigation ID in format INV-YYYYMMDD-HHMMSS
    """
    return f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _generate_action_id() -> str:
    """Generate a unique action ID based on timestamp.

    Returns:
        Action ID in format ACT-YYYYMMDD-HHMMSS
    """
    return f"ACT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _get_timestamp() -> str:
    """Get current ISO timestamp.

    Returns:
        ISO format timestamp string
    """
    return datetime.now().isoformat()


async def load_memory_store() -> MemoryStore:
    """Load memory store from Azure Blob Storage.

    If the memory blob doesn't exist, returns an empty MemoryStore.

    Returns:
        MemoryStore containing all investigations and actions

    Raises:
        RuntimeError: If blob storage access fails (after retries)
    """
    if STORAGE_MODE.lower() != "azure":
        logger.warning("Memory service requires STORAGE_MODE='azure'. Returning empty store.")
        return MemoryStore(last_updated=_get_timestamp())

    try:
        blob_client = BlobStorageClient(blob_name=MEMORY_BLOB_NAME)

        # Check if blob exists
        exists = await blob_client.blob_exists()
        if not exists:
            logger.info(f"Memory blob '{MEMORY_BLOB_NAME}' not found. Starting fresh.")
            return MemoryStore(last_updated=_get_timestamp())

        # Download and parse
        data = await blob_client.download_blob()
        memory = MemoryStore.model_validate(data)
        logger.info(
            f"Loaded memory store: {len(memory.investigations)} investigations, "
            f"{len(memory.actions)} actions"
        )
        return memory

    except Exception as e:
        logger.error(f"Failed to load memory store: {e}")
        raise RuntimeError(f"Failed to load memory store: {e}") from e


async def save_memory_store(memory: MemoryStore) -> None:
    """Save memory store to Azure Blob Storage.

    Args:
        memory: MemoryStore to persist

    Raises:
        RuntimeError: If blob storage access fails (after retries)
    """
    if STORAGE_MODE.lower() != "azure":
        logger.warning("Memory service requires STORAGE_MODE='azure'. Not saving.")
        return

    try:
        # Update timestamp
        memory.last_updated = _get_timestamp()

        blob_client = BlobStorageClient(blob_name=MEMORY_BLOB_NAME)
        await blob_client.upload_blob(memory.model_dump())

        logger.info(
            f"Saved memory store: {len(memory.investigations)} investigations, "
            f"{len(memory.actions)} actions"
        )

    except Exception as e:
        logger.error(f"Failed to save memory store: {e}")
        raise RuntimeError(f"Failed to save memory store: {e}") from e


async def save_investigation(
    title: str,
    initial_observation: str,
    machine_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
) -> Investigation:
    """Create and save a new investigation.

    Args:
        title: Brief investigation title
        initial_observation: What triggered this investigation
        machine_id: Related machine ID if applicable
        supplier_id: Related supplier ID if applicable

    Returns:
        The created Investigation with generated ID and timestamps

    Raises:
        RuntimeError: If storage access fails
    """
    now = _get_timestamp()
    investigation = Investigation(
        id=_generate_investigation_id(),
        title=title,
        machine_id=machine_id,
        supplier_id=supplier_id,
        status="open",
        initial_observation=initial_observation,
        findings=[],
        hypotheses=[],
        created_at=now,
        updated_at=now,
    )

    memory = await load_memory_store()
    memory.investigations.append(investigation)
    await save_memory_store(memory)

    logger.info(f"Created investigation: {investigation.id} - {title}")
    return investigation


async def update_investigation(
    investigation_id: str,
    updates: Dict[str, Any],
) -> Investigation:
    """Update an existing investigation.

    Args:
        investigation_id: ID of investigation to update
        updates: Dict of fields to update (status, findings, hypotheses, etc.)

    Returns:
        The updated Investigation

    Raises:
        ValueError: If investigation not found
        RuntimeError: If storage access fails
    """
    memory = await load_memory_store()

    # Find investigation
    investigation: Optional[Investigation] = None
    for inv in memory.investigations:
        if inv.id == investigation_id:
            investigation = inv
            break

    if investigation is None:
        raise ValueError(f"Investigation not found: {investigation_id}")

    # Apply updates
    for key, value in updates.items():
        if hasattr(investigation, key):
            if key == "findings" and isinstance(value, str):
                # Append to findings list if string provided
                investigation.findings.append(value)
            elif key == "hypotheses" and isinstance(value, str):
                # Append to hypotheses list if string provided
                investigation.hypotheses.append(value)
            else:
                setattr(investigation, key, value)

    investigation.updated_at = _get_timestamp()
    await save_memory_store(memory)

    logger.info(f"Updated investigation: {investigation_id}")
    return investigation


async def log_action(
    description: str,
    action_type: str,
    expected_impact: str,
    machine_id: Optional[str] = None,
    baseline_metrics: Optional[Dict[str, float]] = None,
    follow_up_date: Optional[str] = None,
) -> Action:
    """Log an action with baseline metrics for impact tracking.

    Args:
        description: What action was taken
        action_type: Category (parameter_change, maintenance, process_change)
        expected_impact: What improvement is expected
        machine_id: Related machine ID if applicable
        baseline_metrics: Metrics before action (e.g., {"oee": 0.72})
        follow_up_date: When to check results (ISO date)

    Returns:
        The created Action with generated ID and timestamp

    Raises:
        RuntimeError: If storage access fails
    """
    action = Action(
        id=_generate_action_id(),
        description=description,
        action_type=action_type,  # type: ignore
        machine_id=machine_id,
        baseline_metrics=baseline_metrics or {},
        expected_impact=expected_impact,
        actual_impact=None,
        follow_up_date=follow_up_date,
        created_at=_get_timestamp(),
    )

    memory = await load_memory_store()
    memory.actions.append(action)
    await save_memory_store(memory)

    logger.info(f"Logged action: {action.id} - {description}")
    return action


async def get_relevant_memories(
    machine_id: Optional[str] = None,
    supplier_id: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """Get memories filtered by entity or status.

    Args:
        machine_id: Filter by machine ID
        supplier_id: Filter by supplier ID
        status: Filter investigations by status

    Returns:
        Dict with filtered investigations and actions
    """
    memory = await load_memory_store()

    # Filter investigations
    investigations = memory.investigations
    if machine_id:
        investigations = [i for i in investigations if i.machine_id == machine_id]
    if supplier_id:
        investigations = [i for i in investigations if i.supplier_id == supplier_id]
    if status:
        investigations = [i for i in investigations if i.status == status]

    # Filter actions
    actions = memory.actions
    if machine_id:
        actions = [a for a in actions if a.machine_id == machine_id]

    return {
        "investigations": [i.model_dump() for i in investigations],
        "actions": [a.model_dump() for a in actions],
        "total_investigations": len(investigations),
        "total_actions": len(actions),
    }


async def generate_shift_summary() -> Dict[str, Any]:
    """Generate a summary of today's activities for shift handoff.

    Returns:
        Dict with summary of open investigations, recent actions, and key metrics
    """
    memory = await load_memory_store()
    today = datetime.now().strftime("%Y-%m-%d")

    # Get open/in-progress investigations
    active_investigations = [
        i for i in memory.investigations
        if i.status in ("open", "in_progress")
    ]

    # Get today's actions
    todays_actions = [
        a for a in memory.actions
        if a.created_at.startswith(today)
    ]

    # Get pending follow-ups
    pending_followups = [
        a for a in memory.actions
        if a.follow_up_date and a.follow_up_date <= today and a.actual_impact is None
    ]

    summary = {
        "date": today,
        "active_investigations": [
            {
                "id": i.id,
                "title": i.title,
                "status": i.status,
                "machine_id": i.machine_id,
                "findings_count": len(i.findings),
            }
            for i in active_investigations
        ],
        "todays_actions": [
            {
                "id": a.id,
                "description": a.description,
                "action_type": a.action_type,
                "machine_id": a.machine_id,
            }
            for a in todays_actions
        ],
        "pending_followups": [
            {
                "id": a.id,
                "description": a.description,
                "expected_impact": a.expected_impact,
                "follow_up_date": a.follow_up_date,
            }
            for a in pending_followups
        ],
        "counts": {
            "active_investigations": len(active_investigations),
            "todays_actions": len(todays_actions),
            "pending_followups": len(pending_followups),
        },
    }

    logger.info(
        f"Generated shift summary: {len(active_investigations)} active investigations, "
        f"{len(todays_actions)} actions today, {len(pending_followups)} pending follow-ups"
    )

    return summary
