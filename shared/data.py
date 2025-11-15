"""Data storage and management for factory production metrics.

This module supports two storage modes:
1. Local mode (default): Stores data in local JSON file (data/production.json)
2. Azure mode: Stores data in Azure Blob Storage (requires AZURE_STORAGE_CONNECTION_STRING)

Storage mode is controlled by the STORAGE_MODE environment variable.

Async/Sync Pattern (Hybrid Project Design):
This module provides both synchronous and asynchronous versions of data access functions
to support the hybrid CLI+API architecture:
- Sync functions (load_data, save_data, initialize_data): Used by CLI tools (src/main.py, dashboard)
- Async functions (load_data_async, save_data_async, initialize_data_async): Used by FastAPI routes
This separation follows CLAUDE.md guidelines for hybrid CLI+API projects, where CLI operations
use synchronous I/O for simplicity, while FastAPI routes use async/await for proper concurrent
request handling.
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import json
import random
from pathlib import Path
import logging
import aiofiles
from .config import DATA_FILE, STORAGE_MODE
from .blob_storage import BlobStorageClient
from .data_generator import (
    generate_materials_catalog,
    generate_material_lots,
    generate_orders,
    generate_production_batches,
    generate_suppliers,
)

logger = logging.getLogger(__name__)

# Simple in-memory data structures
MACHINES = [
    {
        "id": 1,
        "name": "CNC-001",
        "type": "CNC Machining Center",
        "ideal_cycle_time": 45,
    },
    {
        "id": 2,
        "name": "Assembly-001",
        "type": "Assembly Station",
        "ideal_cycle_time": 120,
    },
    {
        "id": 3,
        "name": "Packaging-001",
        "type": "Automated Packaging Line",
        "ideal_cycle_time": 30,
    },
    {
        "id": 4,
        "name": "Testing-001",
        "type": "Quality Testing Station",
        "ideal_cycle_time": 90,
    },
]

SHIFTS = [
    {"id": 1, "name": "Day", "start_hour": 6, "end_hour": 14},
    {"id": 2, "name": "Night", "start_hour": 14, "end_hour": 22},
]

DEFECT_TYPES = {
    "dimensional": {"severity": "High", "description": "Out of tolerance"},
    "surface": {"severity": "Medium", "description": "Surface defect"},
    "assembly": {"severity": "High", "description": "Assembly issue"},
    "material": {"severity": "Low", "description": "Material quality"},
}

DOWNTIME_REASONS = {
    "mechanical": "Mechanical failure",
    "electrical": "Electrical issue",
    "material": "Material shortage",
    "changeover": "Product changeover",
    "maintenance": "Scheduled maintenance",
}


def get_data_path() -> Path:
    """Get path to data file, creating directory if needed."""
    path = Path(DATA_FILE)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    except (IOError, OSError, PermissionError) as e:
        logger.error(f"Failed to create data directory {path.parent}: {e}")
        raise RuntimeError(f"Failed to create data directory {path.parent}: {e}")


def save_data(data: Dict[str, Any]) -> None:
    """Save production data to JSON file."""
    path = get_data_path()
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Successfully saved data to {path}")
    except (IOError, OSError) as e:
        logger.error(f"Failed to save data to {path}: {e}")
        raise RuntimeError(f"Failed to save data to {path}: {e}")


def load_data() -> Optional[Dict[str, Any]]:
    """
    Load production data from JSON file (synchronous for CLI use).

    Returns:
        Dictionary containing production data, or None if file doesn't exist.
    """
    path = get_data_path()
    if not path.exists():
        logger.info(f"No data file found at {path}")
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        logger.info(f"Successfully loaded data from {path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {path}: {e}")
        raise RuntimeError(f"Failed to parse JSON from {path}: {e}")
    except (IOError, OSError) as e:
        logger.error(f"Failed to read data from {path}: {e}")
        raise RuntimeError(f"Failed to read data from {path}: {e}")


async def load_data_async() -> Optional[Dict[str, Any]]:
    """
    Load production data asynchronously (for FastAPI use).

    Supports two storage modes:
    - Local mode: Reads from JSON file (data/production.json)
    - Azure mode: Reads from Azure Blob Storage

    Returns:
        Dictionary containing production data, or None if file/blob doesn't exist.

    Raises:
        RuntimeError: If data loading fails
    """
    storage_mode = STORAGE_MODE.lower()
    logger.info(f"Loading data in {storage_mode} storage mode")

    if storage_mode == "azure":
        # Azure Blob Storage mode
        blob_client = BlobStorageClient()
        try:
            exists = await blob_client.blob_exists()

            if not exists:
                logger.warning(
                    "Production data blob not found in Azure Storage. "
                    "Generating fresh data and uploading to blob."
                )
                # Generate fresh data and save to blob
                data = generate_production_data()
                await blob_client.upload_blob(data)
                return data

            # Download from blob
            data = await blob_client.download_blob()
            return data
        except RuntimeError:
            # Re-raise RuntimeErrors from blob_storage (already have context)
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading data from Azure Blob Storage: {e}")
            raise RuntimeError(
                f"Failed to load data from Azure Blob Storage: {e}"
            ) from e
        finally:
            # Always close client, even on error
            await blob_client.close()
    else:
        # Local file mode (default)
        path = get_data_path()
        if not path.exists():
            return None
        try:
            async with aiofiles.open(path, "r") as f:
                content = await f.read()
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON from {path}: {e}") from e
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to read data from {path}: {e}") from e


async def save_data_async(data: Dict[str, Any]) -> None:
    """
    Save production data asynchronously (for FastAPI use).

    Supports two storage modes:
    - Local mode: Writes to JSON file (data/production.json)
    - Azure mode: Writes to Azure Blob Storage

    Args:
        data: Dictionary containing production data

    Raises:
        RuntimeError: If data saving fails
    """
    storage_mode = STORAGE_MODE.lower()
    logger.info(f"Saving data in {storage_mode} storage mode")

    if storage_mode == "azure":
        # Azure Blob Storage mode
        blob_client = BlobStorageClient()
        try:
            await blob_client.upload_blob(data)
            logger.info("Successfully saved data to Azure Blob Storage")
        except RuntimeError:
            # Re-raise RuntimeErrors from blob_storage (already have context)
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving data to Azure Blob Storage: {e}")
            raise RuntimeError(f"Failed to save data to Azure Blob Storage: {e}") from e
        finally:
            # Always close client, even on error
            await blob_client.close()
    else:
        # Local file mode (default)
        path = get_data_path()
        try:
            json_data = json.dumps(data, indent=2, default=str)
            async with aiofiles.open(path, "w") as f:
                await f.write(json_data)
            logger.info(f"Successfully saved data to {path}")
        except (IOError, OSError) as e:
            raise RuntimeError(f"Failed to save data to {path}: {e}") from e


def data_exists() -> bool:
    """Check if data file exists."""
    return get_data_path().exists()


def aggregate_batches_to_production(
    production_batches: List[Union["ProductionBatch", Dict[str, Any]]],
    machines: List[Dict[str, Any]],
    shifts: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Aggregate production batches into production[date][machine] structure.

    This function derives the production[date][machine] structure from ProductionBatch
    instances, maintaining backward compatibility with existing metrics and frontend code.

    Args:
        production_batches: List of ProductionBatch instances (can be Pydantic models or dicts).
                           Each batch must have: date, machine_name, parts_produced, good_parts,
                           scrap_parts, quality_issues, shift_name, batch_id, duration_hours (optional).
        machines: List of machine dictionaries with keys: id (int), name (str).
        shifts: List of shift dictionaries with keys: name (str).

    Returns:
        Dictionary mapping date -> machine_name -> aggregated metrics.
        Structure:
        {
            "YYYY-MM-DD": {
                "Machine-Name": {
                    "parts_produced": int,
                    "good_parts": int,
                    "scrap_parts": int,
                    "scrap_rate": float,
                    "uptime_hours": float,
                    "downtime_hours": float,
                    "downtime_events": List[Dict[str, Any]],
                    "quality_issues": List[Dict[str, Any]],
                    "shifts": Dict[str, Dict[str, Union[int, float]]],
                    "batches": List[str]
                }
            }
        }

    Logic:
        - Group batches by date and machine
        - Sum parts_produced, good_parts, scrap_parts across batches
        - Calculate scrap_rate as percentage
        - Aggregate quality_issues from all batches
        - Estimate uptime/downtime from batch durations (simplified for demo)
        - Aggregate shift-level metrics (Day/Night)
        - Track batch IDs for traceability linkage
    """
    from collections import defaultdict
    from typing import Union

    logger.info("Aggregating production batches to production structure...")

    # Initialize production data structure
    production: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(dict))

    # Create machine name lookup
    machine_map = {m["id"]: m["name"] for m in machines}

    # Group batches by date and machine
    batches_by_date_machine: Dict[str, Dict[str, List[Any]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for batch in production_batches:
        # Handle both Pydantic models and dicts
        if hasattr(batch, "model_dump"):
            batch_dict = batch.model_dump()
        elif isinstance(batch, dict):
            batch_dict = batch
        else:
            logger.warning(f"Skipping invalid batch type: {type(batch)}")
            continue

        date = batch_dict["date"]
        machine_name = batch_dict["machine_name"]
        batches_by_date_machine[date][machine_name].append(batch_dict)

    # Aggregate batches into production structure
    for date_str, machines_data in batches_by_date_machine.items():
        for machine_name, machine_batches in machines_data.items():
            # Initialize aggregated metrics
            total_parts = 0
            total_good = 0
            total_scrap = 0
            total_uptime = 0.0
            total_downtime = 0.0
            all_quality_issues = []
            batch_ids = []

            # Aggregate shift-level metrics
            shift_metrics: Dict[str, Dict[str, Union[int, float]]] = {}
            for shift in shifts:
                shift_name = shift["name"]
                shift_metrics[shift_name] = {
                    "parts_produced": 0,
                    "good_parts": 0,
                    "scrap_parts": 0,
                    "uptime_hours": 0.0,
                    "downtime_hours": 0.0,
                }

            # Process each batch
            for batch in machine_batches:
                # Aggregate totals
                total_parts += batch["parts_produced"]
                total_good += batch["good_parts"]
                total_scrap += batch["scrap_parts"]
                batch_ids.append(batch["batch_id"])

                # Aggregate quality issues
                for issue in batch.get("quality_issues", []):
                    # Convert QualityIssue Pydantic model to dict if needed
                    if hasattr(issue, "model_dump"):
                        issue_dict = issue.model_dump()
                    else:
                        issue_dict = issue
                    all_quality_issues.append(issue_dict)

                # Estimate uptime from batch duration (simplified for demo)
                batch_duration = batch.get("duration_hours", 0.0)
                if batch_duration > 0:
                    total_uptime += batch_duration
                else:
                    # Fallback: estimate 3 hours per batch if no duration
                    total_uptime += 3.0

                # Aggregate shift metrics
                shift_name = batch["shift_name"]
                if shift_name in shift_metrics:
                    shift_metrics[shift_name]["parts_produced"] += batch[
                        "parts_produced"
                    ]
                    shift_metrics[shift_name]["good_parts"] += batch["good_parts"]
                    shift_metrics[shift_name]["scrap_parts"] += batch["scrap_parts"]
                    if batch_duration > 0:
                        shift_metrics[shift_name]["uptime_hours"] += batch_duration
                    else:
                        shift_metrics[shift_name]["uptime_hours"] += 3.0

            # Calculate derived metrics
            scrap_rate = (total_scrap / total_parts * 100) if total_parts > 0 else 0.0

            # Estimate downtime (simplified: 16 total hours - uptime)
            planned_hours = 16.0  # 2 shifts × 8 hours
            total_downtime = max(0.0, planned_hours - total_uptime)

            # Distribute downtime across shifts proportionally
            for shift_name, shift_data in shift_metrics.items():
                shift_uptime = shift_data["uptime_hours"]
                shift_planned = 8.0  # Standard shift duration
                shift_data["downtime_hours"] = max(0.0, shift_planned - shift_uptime)

            # Generate downtime events to match total downtime hours
            # Distribute downtime across 1-2 reasons for realistic categorization
            downtime_events: List[Dict[str, Any]] = []
            if total_downtime > 0:
                num_events = random.randint(1, 2)
                remaining_hours = total_downtime

                for i in range(num_events):
                    reason = random.choice(list(DOWNTIME_REASONS.keys()))
                    # Last event gets remaining hours, others get random split
                    if i == num_events - 1:
                        event_hours = remaining_hours
                    else:
                        event_hours = remaining_hours * random.uniform(0.3, 0.7)
                        remaining_hours -= event_hours

                    downtime_events.append({
                        "reason": reason,
                        "description": DOWNTIME_REASONS[reason],
                        "duration_hours": round(event_hours, 2),
                    })

            # Build aggregated machine data for this date
            production[date_str][machine_name] = {
                "parts_produced": total_parts,
                "good_parts": total_good,
                "scrap_parts": total_scrap,
                "scrap_rate": round(scrap_rate, 2),
                "uptime_hours": round(total_uptime, 2),
                "downtime_hours": round(total_downtime, 2),
                "downtime_events": downtime_events,
                "quality_issues": all_quality_issues,
                "shifts": shift_metrics,
                "batches": batch_ids,  # Traceability linkage
            }

    # Convert defaultdict to regular dict for JSON serialization
    production_dict = {date: dict(machines) for date, machines in production.items()}

    logger.info(
        f"Aggregated {len(production_batches)} batches into "
        f"{len(production_dict)} days of production data"
    )

    return production_dict


def generate_production_data(days: int = 30) -> Dict[str, Any]:
    """
    Generate simple production data with planted scenarios.

    Args:
        days: Number of days of data to generate (default: 30)

    Returns:
        Dictionary containing production data with planted scenarios:
        - Scenario 1: Quality spike on day 15 for Assembly-001
        - Scenario 2: Major breakdown on day 22 for Packaging-001
        - Scenario 3: Performance improvement from 65% to 80% OEE
        - Scenario 4: Night shift 5-8% lower performance
    """
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days - 1)

    production_data: Dict[str, Dict[str, Any]] = {}

    current_date = start_date
    for day_num in range(days):
        date_str = current_date.strftime("%Y-%m-%d")
        production_data[date_str] = {}

        for machine in MACHINES:
            machine_name = machine["name"]

            # Base metrics
            base_parts = 800 + random.randint(-50, 50)

            # Scenario 3: Performance improvement over time (65% -> 80% OEE)
            improvement_factor = 1.0 + (0.23 * day_num / days)  # 23% improvement
            parts_produced = int(base_parts * improvement_factor)

            # Scenario 1: Quality spike on day 15 for Assembly-001
            # PR19: Changed to material defects to enable supplier root cause traceability
            if day_num == 14 and machine_name == "Assembly-001":
                scrap_rate = 0.12  # 12% defect rate (vs normal 3%)
                quality_issues = [
                    {
                        "type": "material",  # Changed from "assembly" to enable supplier linkage
                        "description": "Defective fasteners causing assembly failures",
                        "parts_affected": random.randint(8, 15),
                        "severity": "High",
                    },
                    {
                        "type": "material",
                        "description": "Poor material quality in fastener batch",
                        "parts_affected": random.randint(6, 12),
                        "severity": "High",
                    },
                    {
                        "type": "material",
                        "description": "Material spec deviation - fastener hardness out of range",
                        "parts_affected": random.randint(5, 10),
                        "severity": "Medium",
                    },
                    {
                        "type": "assembly",  # Keep one assembly issue for variety
                        "description": "Assembly tooling misalignment",
                        "parts_affected": random.randint(3, 8),
                        "severity": "Medium",
                    },
                ]
            else:
                scrap_rate = 0.03  # Normal 3% defect rate
                quality_issues = []
                if random.random() < 0.15:  # 15% chance of minor issue
                    defect_type = random.choice(list(DEFECT_TYPES.keys()))
                    quality_issues = [
                        {
                            "type": defect_type,
                            "description": DEFECT_TYPES[defect_type]["description"],
                            "parts_affected": random.randint(1, 5),
                            "severity": DEFECT_TYPES[defect_type]["severity"],
                        }
                    ]

            # Scenario 2: Major breakdown on day 22 for Packaging-001
            if day_num == 21 and machine_name == "Packaging-001":
                downtime_hours = 4.0
                downtime_events = [
                    {
                        "reason": "mechanical",
                        "description": "Critical bearing failure requiring emergency replacement",
                        "duration_hours": 4.0,
                    }
                ]
                parts_produced = int(parts_produced * 0.5)  # Major production loss
            else:
                downtime_hours = random.uniform(0.2, 0.8)  # Normal minor downtime
                # Always create downtime events to match total downtime hours
                # Distribute downtime across 1-2 reasons
                num_events = random.randint(1, 2)
                downtime_events = []
                remaining_hours = downtime_hours

                for i in range(num_events):
                    reason = random.choice(list(DOWNTIME_REASONS.keys()))
                    # Last event gets remaining hours, others get random split
                    if i == num_events - 1:
                        event_hours = remaining_hours
                    else:
                        event_hours = remaining_hours * random.uniform(0.3, 0.7)
                        remaining_hours -= event_hours

                    downtime_events.append({
                        "reason": reason,
                        "description": DOWNTIME_REASONS[reason],
                        "duration_hours": round(event_hours, 2),
                    })

            # Calculate derived metrics
            scrap_parts = int(parts_produced * scrap_rate)
            good_parts = parts_produced - scrap_parts

            # Scenario 4: Shift differences (night shift 5-8% lower)
            shift_metrics = {}
            for shift in SHIFTS:
                shift_name = shift["name"]
                shift_factor = 0.93 if shift_name == "Night" else 1.0
                shift_parts = int(parts_produced * 0.5 * shift_factor)
                shift_scrap = int(scrap_parts * 0.5 * shift_factor)

                shift_metrics[shift_name] = {
                    "parts_produced": shift_parts,
                    "scrap_parts": shift_scrap,
                    "good_parts": shift_parts - shift_scrap,
                    "uptime_hours": 8.0 - (downtime_hours * 0.5),
                    "downtime_hours": downtime_hours * 0.5,
                }

            # Store machine data for this day
            production_data[date_str][machine_name] = {
                "parts_produced": parts_produced,
                "good_parts": good_parts,
                "scrap_parts": scrap_parts,
                "scrap_rate": round(scrap_rate * 100, 2),
                "uptime_hours": 16.0 - downtime_hours,
                "downtime_hours": downtime_hours,
                "downtime_events": downtime_events,
                "quality_issues": quality_issues,
                "shifts": shift_metrics,
            }

        current_date += timedelta(days=1)

    # Generate supply chain entities (PR13)
    try:
        logger.info("Generating supply chain entities...")

        suppliers = generate_suppliers()
        logger.debug(f"Generated {len(suppliers)} suppliers")

        materials_catalog = generate_materials_catalog()
        logger.debug(f"Generated {len(materials_catalog)} materials")

        material_lots = generate_material_lots(
            suppliers, materials_catalog, start_date, days
        )
        logger.debug(f"Generated {len(material_lots)} material lots")

        orders = generate_orders(start_date, days)
        logger.info(
            f"Generated {len(suppliers)} suppliers, {len(materials_catalog)} materials, "
            f"{len(material_lots)} lots, {len(orders)} orders"
        )
    except (ValueError, RuntimeError) as e:
        # These are expected errors with good context - re-raise as-is
        logger.error(f"Supply chain data generation failed: {e}")
        raise
    except Exception as e:
        # Unexpected errors - log with full stack trace
        logger.exception(f"Unexpected error during supply chain generation: {e}")
        raise RuntimeError(f"Supply chain generation failed unexpectedly: {e}") from e

    # Generate production batches with traceability (PR14)
    try:
        logger.info("Generating production batches with traceability...")
        base_data = {
            "generated_at": datetime.now().isoformat(),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "machines": MACHINES,
            "shifts": SHIFTS,
            "production": production_data,
        }

        production_batches = generate_production_batches(
            base_data,
            materials_catalog,
            material_lots,
            orders,
            suppliers,
        )
        logger.info(f"Generated {len(production_batches)} production batches")
    except (ValueError, RuntimeError, KeyError, TypeError) as e:
        logger.error(f"Failed to generate production batches: {e}")
        raise RuntimeError(f"Production batch generation failed: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during batch generation: {e}")
        raise RuntimeError(f"Batch generation failed: {e}") from e

    # Convert Pydantic models to dicts for JSON serialization
    suppliers_dict = [s.model_dump() for s in suppliers]
    materials_catalog_dict = [m.model_dump() for m in materials_catalog]
    material_lots_dict = [lot.model_dump() for lot in material_lots]
    orders_dict = [o.model_dump() for o in orders]
    production_batches_dict = [batch.model_dump() for batch in production_batches]

    # Aggregate batches back to production structure (PR15)
    # This makes production_batches the SOURCE OF TRUTH and production[date][machine] DERIVED
    try:
        logger.info("Aggregating batches to production structure (PR15)...")
        aggregated_production = aggregate_batches_to_production(
            production_batches, MACHINES, SHIFTS
        )
        logger.info(
            f"Aggregation complete: replaced original production data with aggregated version"
        )
    except Exception as e:
        logger.error(f"Failed to aggregate batches to production: {e}")
        raise RuntimeError(f"Batch aggregation failed: {e}") from e

    return {
        "generated_at": datetime.now().isoformat(),
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "machines": MACHINES,
        "shifts": SHIFTS,
        "production": aggregated_production,  # DERIVED from batches (PR15)
        # Supply chain entities (PR13)
        "suppliers": suppliers_dict,
        "materials_catalog": materials_catalog_dict,
        "material_lots": material_lots_dict,
        "orders": orders_dict,
        # Production batches (PR14) - SOURCE OF TRUTH
        "production_batches": production_batches_dict,
    }


def initialize_data(days: int = 30) -> Dict[str, Any]:
    """
    Generate and save production data (synchronous for CLI use).

    Args:
        days: Number of days of data to generate (default: 30)

    Returns:
        Dictionary containing metadata about the generated data:
        - days: Number of days generated
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - machines: Number of machines
        - file_path: Path to saved data file
    """
    logger.info(f"Generating {days} days of production data...")
    data = generate_production_data(days)
    save_data(data)

    total_days = len(data["production"])
    logger.info(
        f"Generated {total_days} days from {data['start_date']} to {data['end_date']}"
    )
    logger.info(f"Data saved to {DATA_FILE}")

    return {
        "days": total_days,
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "machines": len(MACHINES),
        "file_path": str(DATA_FILE),
    }


async def initialize_data_async(days: int = 30) -> Dict[str, Any]:
    """
    Generate and save production data asynchronously (for FastAPI use).

    Supports two storage modes:
    - Local mode: Saves to JSON file (data/production.json)
    - Azure mode: Saves to Azure Blob Storage

    Args:
        days: Number of days of data to generate (default: 30)

    Returns:
        Dictionary containing metadata about the generated data:
        - days: Number of days generated
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - machines: Number of machines
        - storage_mode: Storage mode used ("local" or "azure")
    """
    logger.info(f"Generating {days} days of production data...")
    data = generate_production_data(days)
    await save_data_async(data)

    total_days = len(data["production"])
    logger.info(
        f"Generated {total_days} days from {data['start_date']} to {data['end_date']}"
    )
    logger.info(f"Data saved using {STORAGE_MODE} storage mode")

    return {
        "days": total_days,
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "machines": len(MACHINES),
        "storage_mode": STORAGE_MODE,
    }
