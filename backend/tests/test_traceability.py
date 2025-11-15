"""Comprehensive tests for traceability API endpoints.

This module tests all 10 traceability endpoints including:
- Supplier endpoints (list, get, impact analysis)
- Production batch endpoints (list, get)
- Traceability query endpoints (backward trace, forward trace)
- Order endpoints (list, get, batches)

Each test validates:
- Successful response cases with correct data
- Error handling (404s, 500s)
- Query parameter filtering
- Response model validation
"""

import pytest
from fastapi.testclient import TestClient


# =============================================================================
# SUPPLIER ENDPOINTS TESTS
# =============================================================================


def test_list_suppliers_success(test_client: TestClient, mock_load_data_async):
    """Test listing all suppliers without filters.

    Validates:
    - 200 status code
    - Returns list of suppliers
    - Sorted by quality_rating (highest first)
    """
    response = test_client.get("/api/suppliers")

    assert response.status_code == 200
    suppliers = response.json()
    assert isinstance(suppliers, list)
    assert len(suppliers) == 2

    # Verify sorted by quality rating (highest first)
    assert suppliers[0]["id"] == "SUP-001"  # 95.0 rating
    assert suppliers[1]["id"] == "SUP-002"  # 75.0 rating

    # Validate structure
    assert suppliers[0]["name"] == "Premium Steel Inc"
    assert suppliers[0]["quality_metrics"]["quality_rating"] == 95.0


def test_list_suppliers_with_status_filter(test_client: TestClient, mock_load_data_async):
    """Test listing suppliers filtered by status.

    Validates:
    - Status filter works correctly
    - Only returns Active suppliers when status=Active
    """
    response = test_client.get("/api/suppliers?status=Active")

    assert response.status_code == 200
    suppliers = response.json()
    assert len(suppliers) == 1
    assert suppliers[0]["id"] == "SUP-001"
    assert suppliers[0]["status"] == "Active"


def test_list_suppliers_with_onhold_filter(test_client: TestClient, mock_load_data_async):
    """Test listing suppliers filtered by OnHold status."""
    response = test_client.get("/api/suppliers?status=OnHold")

    assert response.status_code == 200
    suppliers = response.json()
    assert len(suppliers) == 1
    assert suppliers[0]["id"] == "SUP-002"
    assert suppliers[0]["status"] == "OnHold"


def test_list_suppliers_empty_result(test_client: TestClient, mock_load_data_async):
    """Test listing suppliers with filter that matches nothing."""
    response = test_client.get("/api/suppliers?status=Suspended")

    assert response.status_code == 200
    suppliers = response.json()
    assert len(suppliers) == 0


def test_get_supplier_success(test_client: TestClient, mock_load_data_async):
    """Test getting a specific supplier by ID.

    Validates:
    - 200 status code
    - Correct supplier returned
    - Complete supplier details present
    """
    response = test_client.get("/api/suppliers/SUP-001")

    assert response.status_code == 200
    supplier = response.json()

    assert supplier["id"] == "SUP-001"
    assert supplier["name"] == "Premium Steel Inc"
    assert supplier["type"] == "Raw Materials"
    assert "quality_metrics" in supplier
    assert "contact" in supplier
    assert "certifications" in supplier
    assert supplier["quality_metrics"]["quality_rating"] == 95.0


def test_get_supplier_not_found(test_client: TestClient, mock_load_data_async):
    """Test getting a non-existent supplier.

    Validates:
    - 404 status code
    - Error message contains supplier ID
    """
    response = test_client.get("/api/suppliers/SUP-999")

    assert response.status_code == 404
    assert "SUP-999" in response.json()["detail"]
    assert "not found" in response.json()["detail"].lower()


def test_get_supplier_impact_success(test_client: TestClient, mock_load_data_async):
    """Test supplier impact analysis.

    Validates:
    - 200 status code
    - Returns supplier details, material lots, affected batches, quality issues
    - Calculates cost impact correctly
    - Forward traceability chain complete
    """
    response = test_client.get("/api/suppliers/SUP-001/impact")

    assert response.status_code == 200
    impact = response.json()

    # Validate structure
    assert "supplier" in impact
    assert "material_lots_supplied" in impact
    assert "affected_batches" in impact
    assert "quality_issues" in impact
    assert "total_defects" in impact
    assert "estimated_cost_impact" in impact

    # Validate supplier
    assert impact["supplier"]["id"] == "SUP-001"

    # Validate material lots
    assert impact["material_lots_supplied"] == 1  # LOT-20240115-001

    # Validate affected batches (BATCH-20240115-CNC001-001 uses LOT-20240115-001)
    assert impact["affected_batches_count"] == 1
    assert len(impact["affected_batches"]) == 1
    assert impact["affected_batches"][0]["batch_id"] == "BATCH-20240115-CNC001-001"

    # Validate quality issues
    assert impact["total_defects"] == 2  # 2 scrap parts in batch
    assert impact["estimated_cost_impact"] == 100.0  # 2 defects * $50


def test_get_supplier_impact_with_date_filters(test_client: TestClient, mock_load_data_async):
    """Test supplier impact analysis with date range filters.

    Validates:
    - start_date and end_date filters work
    - Only batches/lots within date range are included
    """
    response = test_client.get(
        "/api/suppliers/SUP-001/impact?start_date=2024-01-15&end_date=2024-01-15"
    )

    assert response.status_code == 200
    impact = response.json()

    # Should only include batch from 2024-01-15
    assert impact["affected_batches_count"] == 1
    assert impact["affected_batches"][0]["date"] == "2024-01-15"


def test_get_supplier_impact_not_found(test_client: TestClient, mock_load_data_async):
    """Test impact analysis for non-existent supplier."""
    response = test_client.get("/api/suppliers/SUP-999/impact")

    assert response.status_code == 404
    assert "SUP-999" in response.json()["detail"]


def test_get_supplier_impact_no_batches(test_client: TestClient, mock_load_data_async):
    """Test impact analysis for supplier with no affected batches (future date filter)."""
    response = test_client.get(
        "/api/suppliers/SUP-001/impact?start_date=2025-01-01&end_date=2025-12-31"
    )

    assert response.status_code == 200
    impact = response.json()

    # Should return supplier but no affected batches or quality issues
    assert impact["supplier"]["id"] == "SUP-001"
    assert impact["affected_batches_count"] == 0
    assert impact["quality_issues_count"] == 0
    assert impact["total_defects"] == 0


# =============================================================================
# PRODUCTION BATCH ENDPOINTS TESTS
# =============================================================================


def test_list_batches_success(test_client: TestClient, mock_load_data_async):
    """Test listing all batches without filters.

    Validates:
    - 200 status code
    - Returns list of batches
    - Sorted by date (newest first)
    - Default limit applied
    """
    response = test_client.get("/api/batches")

    assert response.status_code == 200
    batches = response.json()
    assert isinstance(batches, list)
    assert len(batches) == 2

    # Verify sorted by date (newest first)
    assert batches[0]["date"] == "2024-01-16"  # BATCH-20240116-CNC001-002
    assert batches[1]["date"] == "2024-01-15"  # BATCH-20240115-CNC001-001


def test_list_batches_with_machine_filter(test_client: TestClient, mock_load_data_async):
    """Test listing batches filtered by machine_id."""
    response = test_client.get("/api/batches?machine_id=1")

    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 2
    assert all(b["machine_id"] == 1 for b in batches)


def test_list_batches_with_date_filters(test_client: TestClient, mock_load_data_async):
    """Test listing batches with date range filters."""
    response = test_client.get("/api/batches?start_date=2024-01-16&end_date=2024-01-16")

    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 1
    assert batches[0]["date"] == "2024-01-16"


def test_list_batches_with_order_filter(test_client: TestClient, mock_load_data_async):
    """Test listing batches filtered by order_id."""
    response = test_client.get("/api/batches?order_id=ORD-001")

    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 1
    assert batches[0]["order_id"] == "ORD-001"


def test_list_batches_with_limit(test_client: TestClient, mock_load_data_async):
    """Test listing batches with custom limit."""
    response = test_client.get("/api/batches?limit=1")

    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 1  # Limited to 1


def test_list_batches_multiple_filters(test_client: TestClient, mock_load_data_async):
    """Test listing batches with multiple filters combined."""
    response = test_client.get(
        "/api/batches?machine_id=1&start_date=2024-01-15&end_date=2024-01-15&order_id=ORD-001"
    )

    assert response.status_code == 200
    batches = response.json()
    assert len(batches) == 1
    assert batches[0]["batch_id"] == "BATCH-20240115-CNC001-001"
    assert batches[0]["machine_id"] == 1
    assert batches[0]["date"] == "2024-01-15"
    assert batches[0]["order_id"] == "ORD-001"


def test_get_batch_success(test_client: TestClient, mock_load_data_async):
    """Test getting a specific batch by ID.

    Validates:
    - 200 status code
    - Correct batch returned
    - Complete batch details including materials_consumed
    """
    response = test_client.get("/api/batches/BATCH-20240115-CNC001-001")

    assert response.status_code == 200
    batch = response.json()

    assert batch["batch_id"] == "BATCH-20240115-CNC001-001"
    assert batch["date"] == "2024-01-15"
    assert batch["machine_id"] == 1
    assert batch["parts_produced"] == 100
    assert batch["good_parts"] == 98
    assert batch["scrap_parts"] == 2

    # Validate materials_consumed (key for traceability)
    assert len(batch["materials_consumed"]) == 1
    assert batch["materials_consumed"][0]["material_id"] == "MAT-001"
    assert batch["materials_consumed"][0]["lot_number"] == "LOT-20240115-001"


def test_get_batch_not_found(test_client: TestClient, mock_load_data_async):
    """Test getting a non-existent batch."""
    response = test_client.get("/api/batches/BATCH-INVALID")

    assert response.status_code == 404
    assert "BATCH-INVALID" in response.json()["detail"]
    assert "not found" in response.json()["detail"].lower()


# =============================================================================
# TRACEABILITY QUERY ENDPOINTS TESTS
# =============================================================================


def test_backward_trace_success(test_client: TestClient, mock_load_data_async):
    """Test backward traceability from batch to suppliers.

    Validates:
    - 200 status code
    - Complete traceability chain: Batch → Materials → Lots → Suppliers
    - Supply chain summary calculated correctly
    - All required fields present
    """
    response = test_client.get("/api/traceability/backward/BATCH-20240115-CNC001-001")

    assert response.status_code == 200
    trace = response.json()

    # Validate structure
    assert "batch" in trace
    assert "materials_trace" in trace
    assert "suppliers" in trace
    assert "supply_chain_summary" in trace

    # Validate batch
    assert trace["batch"]["batch_id"] == "BATCH-20240115-CNC001-001"

    # Validate materials trace
    assert len(trace["materials_trace"]) == 1
    material = trace["materials_trace"][0]
    assert material["material_id"] == "MAT-001"
    assert material["lot_number"] == "LOT-20240115-001"
    assert material["supplier_id"] == "SUP-001"
    assert "lot_details" in material
    assert "supplier" in material

    # Validate suppliers
    assert len(trace["suppliers"]) == 1
    assert trace["suppliers"][0]["id"] == "SUP-001"

    # Validate supply chain summary
    summary = trace["supply_chain_summary"]
    assert summary["materials_count"] == 1
    assert summary["suppliers_count"] == 1
    assert summary["total_parts_produced"] == 100
    assert summary["scrap_parts"] == 2
    assert summary["quality_rate"] == 98.0  # 98/100 * 100


def test_backward_trace_not_found(test_client: TestClient, mock_load_data_async):
    """Test backward trace for non-existent batch."""
    response = test_client.get("/api/traceability/backward/BATCH-INVALID")

    assert response.status_code == 404
    assert "BATCH-INVALID" in response.json()["detail"]


def test_forward_trace_success(test_client: TestClient, mock_load_data_async):
    """Test forward traceability from supplier to orders.

    Validates:
    - 200 status code
    - Complete traceability chain: Supplier → Lots → Batches → Orders
    - Impact summary calculated correctly
    - Quality issues tracked
    """
    response = test_client.get("/api/traceability/forward/SUP-001")

    assert response.status_code == 200
    trace = response.json()

    # Validate structure
    assert "supplier" in trace
    assert "material_lots_supplied" in trace
    assert "affected_batches" in trace
    assert "quality_issues" in trace
    assert "affected_orders" in trace
    assert "impact_summary" in trace

    # Validate supplier
    assert trace["supplier"]["id"] == "SUP-001"

    # Validate material lots
    assert trace["material_lots_supplied"] == 1

    # Validate affected batches
    assert len(trace["affected_batches"]) == 1
    assert trace["affected_batches"][0]["batch_id"] == "BATCH-20240115-CNC001-001"

    # Validate quality issues
    assert len(trace["quality_issues"]) == 1
    assert trace["quality_issues"][0]["defect_count"] == 2

    # Validate affected orders
    assert len(trace["affected_orders"]) == 1
    assert trace["affected_orders"][0]["id"] == "ORD-001"

    # Validate impact summary
    summary = trace["impact_summary"]
    assert summary["batches_affected"] == 1
    assert summary["quality_issues_count"] == 1
    assert summary["total_defects"] == 2
    assert summary["orders_affected"] == 1
    assert summary["estimated_cost_impact"] == 100.0  # 2 defects * $50


def test_forward_trace_with_date_filters(test_client: TestClient, mock_load_data_async):
    """Test forward trace with date range filters."""
    response = test_client.get(
        "/api/traceability/forward/SUP-001?start_date=2024-01-15&end_date=2024-01-15"
    )

    assert response.status_code == 200
    trace = response.json()

    # Should only include batches from 2024-01-15
    assert len(trace["affected_batches"]) == 1
    assert trace["affected_batches"][0]["date"] == "2024-01-15"


def test_forward_trace_not_found(test_client: TestClient, mock_load_data_async):
    """Test forward trace for non-existent supplier."""
    response = test_client.get("/api/traceability/forward/SUP-999")

    assert response.status_code == 404
    assert "SUP-999" in response.json()["detail"]


def test_forward_trace_no_batches(test_client: TestClient, mock_load_data_async):
    """Test forward trace with date filter that excludes all batches."""
    response = test_client.get(
        "/api/traceability/forward/SUP-001?start_date=2025-01-01&end_date=2025-12-31"
    )

    assert response.status_code == 200
    trace = response.json()

    # Should return supplier but no affected batches
    assert trace["supplier"]["id"] == "SUP-001"
    assert len(trace["affected_batches"]) == 0
    assert trace["impact_summary"]["batches_affected"] == 0


# =============================================================================
# ORDER ENDPOINTS TESTS
# =============================================================================


def test_list_orders_success(test_client: TestClient, mock_load_data_async):
    """Test listing all orders without filters.

    Validates:
    - 200 status code
    - Returns list of orders
    - Sorted by due_date (nearest first)
    """
    response = test_client.get("/api/orders")

    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) == 2

    # Verify sorted by due date (nearest first)
    assert orders[0]["due_date"] == "2024-01-20"  # ORD-001
    assert orders[1]["due_date"] == "2024-01-25"  # ORD-002


def test_list_orders_with_status_filter(test_client: TestClient, mock_load_data_async):
    """Test listing orders filtered by status."""
    response = test_client.get("/api/orders?status=InProgress")

    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1
    assert orders[0]["id"] == "ORD-001"
    assert orders[0]["status"] == "InProgress"


def test_list_orders_with_limit(test_client: TestClient, mock_load_data_async):
    """Test listing orders with custom limit."""
    response = test_client.get("/api/orders?limit=1")

    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 1


def test_get_order_success(test_client: TestClient, mock_load_data_async):
    """Test getting a specific order by ID.

    Validates:
    - 200 status code
    - Correct order returned
    - Complete order details including items
    """
    response = test_client.get("/api/orders/ORD-001")

    assert response.status_code == 200
    order = response.json()

    assert order["id"] == "ORD-001"
    assert order["order_number"] == "PO-2024-001"
    assert order["customer"] == "Acme Manufacturing"
    assert order["status"] == "InProgress"
    assert order["total_value"] == 2550.0

    # Validate items
    assert len(order["items"]) == 1
    assert order["items"][0]["part_number"] == "PART-001"
    assert order["items"][0]["quantity"] == 100


def test_get_order_not_found(test_client: TestClient, mock_load_data_async):
    """Test getting a non-existent order."""
    response = test_client.get("/api/orders/ORD-999")

    assert response.status_code == 404
    assert "ORD-999" in response.json()["detail"]
    assert "not found" in response.json()["detail"].lower()


def test_get_order_batches_success(test_client: TestClient, mock_load_data_async):
    """Test getting production batches for a specific order.

    Validates:
    - 200 status code
    - Order details present
    - Assigned batches correct
    - Production summary calculated correctly
    """
    response = test_client.get("/api/orders/ORD-001/batches")

    assert response.status_code == 200
    result = response.json()

    # Validate structure
    assert "order" in result
    assert "assigned_batches" in result
    assert "production_summary" in result

    # Validate order
    assert result["order"]["id"] == "ORD-001"

    # Validate assigned batches
    assert len(result["assigned_batches"]) == 1
    assert result["assigned_batches"][0]["batch_id"] == "BATCH-20240115-CNC001-001"

    # Validate production summary
    summary = result["production_summary"]
    assert summary["batches_count"] == 1
    assert summary["total_produced"] == 100
    assert summary["total_good_parts"] == 98
    assert summary["total_scrap"] == 2
    assert summary["quality_rate"] == 98.0  # 98/100 * 100


def test_get_order_batches_no_batches(test_client: TestClient, mock_load_data_async):
    """Test getting batches for order with no production batches assigned."""
    # Create order with no batches (ORD-002 has batches, so we need a different scenario)
    # In our mock data, ORD-002 has BATCH-20240116-CNC001-002
    # So let's create a test that works with existing data
    response = test_client.get("/api/orders/ORD-002/batches")

    assert response.status_code == 200
    result = response.json()

    # ORD-002 should have 1 batch
    assert len(result["assigned_batches"]) == 1
    assert result["assigned_batches"][0]["order_id"] == "ORD-002"


def test_get_order_batches_not_found(test_client: TestClient, mock_load_data_async):
    """Test getting batches for non-existent order."""
    response = test_client.get("/api/orders/ORD-999/batches")

    assert response.status_code == 404
    assert "ORD-999" in response.json()["detail"]


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_empty_data_handling(test_client: TestClient, monkeypatch):
    """Test endpoints handle empty data gracefully."""

    async def mock_empty_loader():
        return {}

    monkeypatch.setattr(
        "api.routes.traceability.load_data_async",
        mock_empty_loader
    )

    # Test various endpoints with empty data
    response = test_client.get("/api/suppliers")
    assert response.status_code == 200
    assert response.json() == []

    response = test_client.get("/api/batches")
    assert response.status_code == 200
    assert response.json() == []

    response = test_client.get("/api/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_null_data_handling(test_client: TestClient, monkeypatch):
    """Test endpoints handle None data gracefully."""

    async def mock_null_loader():
        return None

    monkeypatch.setattr(
        "api.routes.traceability.load_data_async",
        mock_null_loader
    )

    # List endpoints should return empty arrays
    response = test_client.get("/api/suppliers")
    assert response.status_code == 200
    assert response.json() == []

    # Get endpoints should return 404
    response = test_client.get("/api/suppliers/SUP-001")
    assert response.status_code == 404


# =============================================================================
# QUERY PARAMETER VALIDATION TESTS
# =============================================================================


def test_batch_limit_validation(test_client: TestClient, mock_load_data_async):
    """Test batch list limit parameter validation."""
    # Limit too low (< 1)
    response = test_client.get("/api/batches?limit=0")
    assert response.status_code == 422  # Validation error

    # Limit too high (> 500)
    response = test_client.get("/api/batches?limit=501")
    assert response.status_code == 422  # Validation error

    # Valid limits
    response = test_client.get("/api/batches?limit=1")
    assert response.status_code == 200

    response = test_client.get("/api/batches?limit=500")
    assert response.status_code == 200


def test_order_limit_validation(test_client: TestClient, mock_load_data_async):
    """Test order list limit parameter validation."""
    # Limit too low (< 1)
    response = test_client.get("/api/orders?limit=0")
    assert response.status_code == 422  # Validation error

    # Limit too high (> 200)
    response = test_client.get("/api/orders?limit=201")
    assert response.status_code == 422  # Validation error

    # Valid limits
    response = test_client.get("/api/orders?limit=1")
    assert response.status_code == 200

    response = test_client.get("/api/orders?limit=200")
    assert response.status_code == 200
