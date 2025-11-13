"""Tests for batch aggregation to production structure (PR15)."""

import pytest
from datetime import datetime, timedelta
from shared.data import aggregate_batches_to_production
from shared.models import ProductionBatch, MaterialUsage, QualityIssue


@pytest.fixture
def sample_machines():
    """Sample machine data for testing."""
    return [
        {"id": 1, "name": "CNC-001", "type": "CNC Machining Center"},
        {"id": 2, "name": "Assembly-001", "type": "Assembly Station"},
    ]


@pytest.fixture
def sample_shifts():
    """Sample shift data for testing."""
    return [
        {"id": 1, "name": "Day", "start_hour": 6, "end_hour": 14},
        {"id": 2, "name": "Night", "start_hour": 14, "end_hour": 22},
    ]


@pytest.fixture
def sample_batches():
    """Sample production batches for testing."""
    date_str = "2024-01-15"
    return [
        ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC-001-Day-01",
            date=date_str,
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            order_id="ORD-001",
            part_number="PART-001",
            operator="John Smith",
            parts_produced=100,
            good_parts=95,
            scrap_parts=5,
            serial_start=1000,
            serial_end=1099,
            materials_consumed=[
                MaterialUsage(
                    material_id="MAT-001",
                    material_name="Steel Bar",
                    lot_number="LOT-001",
                    quantity_used=25.5,
                    unit="kg",
                )
            ],
            quality_issues=[
                QualityIssue(
                    type="dimensional",
                    description="Out of tolerance",
                    parts_affected=3,
                    severity="High",
                    date=date_str,
                    machine="CNC-001",
                )
            ],
            start_time="06:00",
            end_time="09:30",
            duration_hours=3.5,
        ),
        ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC-001-Day-02",
            date=date_str,
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            order_id="ORD-001",
            part_number="PART-001",
            operator="Sarah Johnson",
            parts_produced=120,
            good_parts=117,
            scrap_parts=3,
            serial_start=1100,
            serial_end=1219,
            materials_consumed=[
                MaterialUsage(
                    material_id="MAT-001",
                    material_name="Steel Bar",
                    lot_number="LOT-002",
                    quantity_used=30.0,
                    unit="kg",
                )
            ],
            quality_issues=[],
            start_time="10:00",
            end_time="13:00",
            duration_hours=3.0,
        ),
        ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC-001-Night-01",
            date=date_str,
            machine_id=1,
            machine_name="CNC-001",
            shift_id=2,
            shift_name="Night",
            order_id="ORD-002",
            part_number="PART-001",
            operator="Mike Chen",
            parts_produced=110,
            good_parts=108,
            scrap_parts=2,
            serial_start=1220,
            serial_end=1329,
            materials_consumed=[
                MaterialUsage(
                    material_id="MAT-002",
                    material_name="Aluminum Bar",
                    lot_number="LOT-003",
                    quantity_used=28.0,
                    unit="kg",
                )
            ],
            quality_issues=[],
            start_time="14:00",
            end_time="17:30",
            duration_hours=3.5,
        ),
    ]


def test_aggregate_batches_basic_structure(
    sample_batches, sample_machines, sample_shifts
):
    """Test that aggregation produces correct basic structure."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    # Check structure
    assert isinstance(result, dict)
    assert "2024-01-15" in result
    assert "CNC-001" in result["2024-01-15"]

    machine_data = result["2024-01-15"]["CNC-001"]
    expected_keys = [
        "parts_produced",
        "good_parts",
        "scrap_parts",
        "scrap_rate",
        "uptime_hours",
        "downtime_hours",
        "downtime_events",
        "quality_issues",
        "shifts",
        "batches",
    ]
    for key in expected_keys:
        assert key in machine_data, f"Missing key: {key}"


def test_aggregate_batches_totals(sample_batches, sample_machines, sample_shifts):
    """Test that totals are correctly aggregated."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    machine_data = result["2024-01-15"]["CNC-001"]

    # Total parts = 100 + 120 + 110 = 330
    assert machine_data["parts_produced"] == 330

    # Total good parts = 95 + 117 + 108 = 320
    assert machine_data["good_parts"] == 320

    # Total scrap = 5 + 3 + 2 = 10
    assert machine_data["scrap_parts"] == 10

    # Scrap rate = 10 / 330 * 100 = 3.03%
    assert abs(machine_data["scrap_rate"] - 3.03) < 0.01


def test_aggregate_batches_shift_metrics(
    sample_batches, sample_machines, sample_shifts
):
    """Test that shift-level metrics are correctly aggregated."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    machine_data = result["2024-01-15"]["CNC-001"]
    shifts = machine_data["shifts"]

    # Check Day shift (batches 1 and 2)
    assert "Day" in shifts
    day_shift = shifts["Day"]
    assert day_shift["parts_produced"] == 220  # 100 + 120
    assert day_shift["good_parts"] == 212  # 95 + 117
    assert day_shift["scrap_parts"] == 8  # 5 + 3
    assert day_shift["uptime_hours"] == 6.5  # 3.5 + 3.0

    # Check Night shift (batch 3)
    assert "Night" in shifts
    night_shift = shifts["Night"]
    assert night_shift["parts_produced"] == 110
    assert night_shift["good_parts"] == 108
    assert night_shift["scrap_parts"] == 2
    assert night_shift["uptime_hours"] == 3.5


def test_aggregate_batches_quality_issues(
    sample_batches, sample_machines, sample_shifts
):
    """Test that quality issues are aggregated correctly."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    machine_data = result["2024-01-15"]["CNC-001"]
    quality_issues = machine_data["quality_issues"]

    # Should have 1 quality issue (from batch 1)
    assert len(quality_issues) == 1
    assert quality_issues[0]["type"] == "dimensional"
    assert quality_issues[0]["parts_affected"] == 3


def test_aggregate_batches_traceability(
    sample_batches, sample_machines, sample_shifts
):
    """Test that batch IDs are tracked for traceability."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    machine_data = result["2024-01-15"]["CNC-001"]
    batch_ids = machine_data["batches"]

    # Should have 3 batch IDs
    assert len(batch_ids) == 3
    assert "BATCH-2024-01-15-CNC-001-Day-01" in batch_ids
    assert "BATCH-2024-01-15-CNC-001-Day-02" in batch_ids
    assert "BATCH-2024-01-15-CNC-001-Night-01" in batch_ids


def test_aggregate_batches_uptime_downtime(
    sample_batches, sample_machines, sample_shifts
):
    """Test that uptime and downtime are calculated correctly."""
    result = aggregate_batches_to_production(
        sample_batches, sample_machines, sample_shifts
    )

    machine_data = result["2024-01-15"]["CNC-001"]

    # Total uptime = 3.5 + 3.0 + 3.5 = 10.0 hours
    assert machine_data["uptime_hours"] == 10.0

    # Total downtime = 16.0 (planned) - 10.0 (uptime) = 6.0 hours
    assert machine_data["downtime_hours"] == 6.0


def test_aggregate_batches_empty_list(sample_machines, sample_shifts):
    """Test that empty batch list returns empty production."""
    result = aggregate_batches_to_production([], sample_machines, sample_shifts)

    assert isinstance(result, dict)
    assert len(result) == 0


def test_aggregate_batches_multiple_machines(sample_machines, sample_shifts):
    """Test aggregation with multiple machines."""
    date_str = "2024-01-15"
    batches = [
        ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC-001-Day-01",
            date=date_str,
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            order_id="ORD-001",
            part_number="PART-001",
            operator="John Smith",
            parts_produced=100,
            good_parts=95,
            scrap_parts=5,
            serial_start=1000,
            serial_end=1099,
            materials_consumed=[],
            quality_issues=[],
            start_time="06:00",
            end_time="09:30",
            duration_hours=3.5,
        ),
        ProductionBatch(
            batch_id="BATCH-2024-01-15-Assembly-001-Day-01",
            date=date_str,
            machine_id=2,
            machine_name="Assembly-001",
            shift_id=1,
            shift_name="Day",
            order_id="ORD-001",
            part_number="PART-002",
            operator="Sarah Johnson",
            parts_produced=150,
            good_parts=145,
            scrap_parts=5,
            serial_start=2000,
            serial_end=2149,
            materials_consumed=[],
            quality_issues=[],
            start_time="06:00",
            end_time="10:00",
            duration_hours=4.0,
        ),
    ]

    result = aggregate_batches_to_production(batches, sample_machines, sample_shifts)

    assert "CNC-001" in result[date_str]
    assert "Assembly-001" in result[date_str]
    assert result[date_str]["CNC-001"]["parts_produced"] == 100
    assert result[date_str]["Assembly-001"]["parts_produced"] == 150


def test_aggregate_batches_handles_dict_input(
    sample_batches, sample_machines, sample_shifts
):
    """Test that aggregation handles both Pydantic models and dicts."""
    # Convert first batch to dict
    batch_dicts = [sample_batches[0].model_dump()] + sample_batches[1:]

    result = aggregate_batches_to_production(
        batch_dicts, sample_machines, sample_shifts
    )

    # Should still work correctly
    assert "2024-01-15" in result
    assert "CNC-001" in result["2024-01-15"]
    assert result["2024-01-15"]["CNC-001"]["parts_produced"] == 330
