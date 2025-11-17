"""Pytest configuration and shared fixtures for backend tests.

This module provides reusable test fixtures including:
- Mock production data with complete traceability chain
- FastAPI test client configuration
- Data mocking utilities
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any
from fastapi.testclient import TestClient

# Add backend/src and shared to Python path for imports
backend_src_path = Path(__file__).parent.parent / "src"
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.insert(0, str(backend_src_path))
sys.path.insert(0, str(shared_path))

from api.main import app


@pytest.fixture
def anyio_backend():
    """Configure pytest-anyio to use only asyncio backend (not trio).

    This project uses FastAPI which is built on asyncio. We don't need
    trio support, so we configure pytest-anyio to only test with asyncio.
    This prevents the "ModuleNotFoundError: No module named 'trio'" errors.

    Returns:
        str: The backend name ('asyncio')
    """
    return 'asyncio'


@pytest.fixture
def test_client() -> TestClient:
    """Create FastAPI TestClient for synchronous testing.

    Returns:
        TestClient instance configured with the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def mock_production_data() -> Dict[str, Any]:
    """Generate mock production data with complete traceability chain.

    Creates a minimal but complete dataset including:
    - 2 suppliers (one high quality, one low quality)
    - Materials catalog
    - Material lots linked to suppliers
    - Production batches using material lots
    - Customer orders linked to batches

    Returns:
        Dictionary containing all production data structures
    """
    return {
        "suppliers": [
            {
                "id": "SUP-001",
                "name": "Premium Steel Inc",
                "type": "Raw Materials",
                "materials_supplied": ["MAT-001", "MAT-002"],
                "contact": {
                    "email": "sales@premiumsteel.com",
                    "phone": "+1-555-0100",
                    "address": "123 Industry Ave, Pittsburgh, PA 15222"
                },
                "quality_metrics": {
                    "quality_rating": 95.0,
                    "on_time_delivery_rate": 98.5,
                    "defect_rate": 0.5
                },
                "certifications": ["ISO9001", "AS9100"],
                "status": "Active"
            },
            {
                "id": "SUP-002",
                "name": "Budget Fasteners Ltd",
                "type": "Fasteners",
                "materials_supplied": ["MAT-003"],
                "contact": {
                    "email": "info@budgetfasteners.com",
                    "phone": "+1-555-0200",
                    "address": "456 Commerce St, Detroit, MI 48201"
                },
                "quality_metrics": {
                    "quality_rating": 75.0,
                    "on_time_delivery_rate": 85.0,
                    "defect_rate": 3.2
                },
                "certifications": ["ISO9001"],
                "status": "OnHold"
            }
        ],
        "materials_catalog": [
            {
                "id": "MAT-001",
                "name": "Steel Bar 304",
                "category": "Steel",
                "specification": "AISI 304 Stainless Steel",
                "unit": "kg",
                "preferred_suppliers": ["SUP-001"],
                "quality_requirements": {
                    "grade": "304",
                    "finish": "2B"
                }
            },
            {
                "id": "MAT-002",
                "name": "Aluminum Sheet 6061",
                "category": "Aluminum",
                "specification": "6061-T6 Aluminum",
                "unit": "kg",
                "preferred_suppliers": ["SUP-001"],
                "quality_requirements": {
                    "grade": "6061-T6",
                    "thickness": "3mm"
                }
            },
            {
                "id": "MAT-003",
                "name": "M8 Hex Bolts",
                "category": "Fasteners",
                "specification": "ISO 4017 Grade 8.8",
                "unit": "pieces",
                "preferred_suppliers": ["SUP-002"],
                "quality_requirements": {
                    "grade": "8.8",
                    "coating": "Zinc"
                }
            }
        ],
        "material_lots": [
            {
                "lot_number": "LOT-20240115-001",
                "material_id": "MAT-001",
                "supplier_id": "SUP-001",
                "received_date": "2024-01-15",
                "quantity_received": 500.0,
                "quantity_remaining": 250.0,
                "inspection_results": {
                    "status": "Passed",
                    "inspector": "QC-001",
                    "notes": "All specifications met"
                },
                "status": "Available",
                "quarantine": False
            },
            {
                "lot_number": "LOT-20240116-002",
                "material_id": "MAT-003",
                "supplier_id": "SUP-002",
                "received_date": "2024-01-16",
                "quantity_received": 1000.0,
                "quantity_remaining": 500.0,
                "inspection_results": {
                    "status": "Conditional",
                    "inspector": "QC-002",
                    "notes": "Minor surface defects on 5% of batch"
                },
                "status": "Available",
                "quarantine": False
            }
        ],
        "production_batches": [
            {
                "batch_id": "BATCH-20240115-CNC001-001",
                "date": "2024-01-15",
                "machine_id": 1,
                "machine_name": "CNC-001",
                "shift_id": 1,
                "shift_name": "Day",
                "order_id": "ORD-001",
                "part_number": "PART-001",
                "operator": "OP-001",
                "parts_produced": 100,
                "good_parts": 98,
                "scrap_parts": 2,
                "serial_start": 1000,
                "serial_end": 1099,
                "materials_consumed": [
                    {
                        "material_id": "MAT-001",
                        "material_name": "Steel Bar 304",
                        "lot_number": "LOT-20240115-001",
                        "quantity_used": 50.0,
                        "unit": "kg"
                    }
                ],
                "quality_issues": [],
                "process_parameters": {
                    "spindle_speed": 2500.0,
                    "feed_rate": 150.0
                },
                "start_time": "08:00:00",
                "end_time": "12:00:00",
                "duration_hours": 4.0
            },
            {
                "batch_id": "BATCH-20240116-CNC001-002",
                "date": "2024-01-16",
                "machine_id": 1,
                "machine_name": "CNC-001",
                "shift_id": 1,
                "shift_name": "Day",
                "order_id": "ORD-002",
                "part_number": "PART-002",
                "operator": "OP-002",
                "parts_produced": 50,
                "good_parts": 45,
                "scrap_parts": 5,
                "serial_start": 2000,
                "serial_end": 2049,
                "materials_consumed": [
                    {
                        "material_id": "MAT-003",
                        "material_name": "M8 Hex Bolts",
                        "lot_number": "LOT-20240116-002",
                        "quantity_used": 200.0,
                        "unit": "pieces"
                    }
                ],
                "quality_issues": [],
                "process_parameters": {
                    "spindle_speed": 3000.0,
                    "feed_rate": 200.0
                },
                "start_time": "08:00:00",
                "end_time": "10:00:00",
                "duration_hours": 2.0
            }
        ],
        "orders": [
            {
                "id": "ORD-001",
                "order_number": "PO-2024-001",
                "customer": "Acme Manufacturing",
                "items": [
                    {
                        "part_number": "PART-001",
                        "quantity": 100,
                        "unit_price": 25.50
                    }
                ],
                "due_date": "2024-01-20",
                "status": "InProgress",
                "priority": "High",
                "shipping_date": None,
                "total_value": 2550.0
            },
            {
                "id": "ORD-002",
                "order_number": "PO-2024-002",
                "customer": "Industrial Solutions Inc",
                "items": [
                    {
                        "part_number": "PART-002",
                        "quantity": 50,
                        "unit_price": 15.75
                    }
                ],
                "due_date": "2024-01-25",
                "status": "Completed",
                "priority": "Normal",
                "shipping_date": "2024-01-17",
                "total_value": 787.50
            }
        ]
    }


@pytest.fixture
def mock_load_data_async(monkeypatch, mock_production_data):
    """Mock the load_data_async function to return test data.

    This fixture patches the data loading function to avoid
    file I/O during tests and provides predictable test data.

    Args:
        monkeypatch: pytest's monkeypatch fixture
        mock_production_data: The mock data fixture
    """
    async def mock_loader():
        return mock_production_data

    monkeypatch.setattr(
        "api.routes.traceability.load_data_async",
        mock_loader
    )
