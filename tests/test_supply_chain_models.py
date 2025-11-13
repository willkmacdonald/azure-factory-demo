"""Unit tests for supply chain traceability Pydantic models."""

import pytest
from pydantic import ValidationError

from shared.models import MaterialLot, MaterialSpec, Order, OrderItem, Supplier


class TestSupplier:
    """Test Supplier model validation."""

    def test_valid_supplier(self):
        """Test that valid supplier data is accepted."""
        supplier = Supplier(
            id="SUP-001",
            name="Test Supplier",
            type="Raw Materials",
            materials_supplied=["MAT-001", "MAT-002"],
            contact={"email": "test@example.com", "phone": "+1-555-0123"},
            quality_metrics={
                "quality_rating": 95.0,
                "on_time_delivery_rate": 98.0,
                "defect_rate": 1.5,
            },
            certifications=["ISO9001", "AS9100"],
            status="Active",
        )

        assert supplier.id == "SUP-001"
        assert supplier.name == "Test Supplier"
        assert supplier.type == "Raw Materials"
        assert len(supplier.materials_supplied) == 2
        assert supplier.status == "Active"

    def test_supplier_defaults(self):
        """Test that supplier fields have correct defaults."""
        supplier = Supplier(
            id="SUP-002",
            name="Minimal Supplier",
            type="Components",
        )

        assert supplier.materials_supplied == []
        assert supplier.contact == {}
        assert supplier.quality_metrics == {}
        assert supplier.certifications == []
        assert supplier.status == "Active"

    def test_supplier_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Supplier(name="No ID Supplier", type="Components")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("id",)
        assert errors[0]["type"] == "missing"


class TestMaterialSpec:
    """Test MaterialSpec model validation."""

    def test_valid_material(self):
        """Test that valid material spec is accepted."""
        material = MaterialSpec(
            id="MAT-001",
            name="Steel Bar 304",
            category="Steel",
            specification="ASTM A479 Grade 304",
            unit="kg",
            preferred_suppliers=["SUP-001", "SUP-002"],
            quality_requirements={
                "hardness": "HRC 20-25",
                "tensile_strength": "≥515 MPa",
            },
        )

        assert material.id == "MAT-001"
        assert material.name == "Steel Bar 304"
        assert material.unit == "kg"
        assert len(material.preferred_suppliers) == 2

    def test_material_defaults(self):
        """Test that material fields have correct defaults."""
        material = MaterialSpec(
            id="MAT-002",
            name="Test Material",
            category="Test",
            specification="Test Spec",
            unit="pieces",
        )

        assert material.preferred_suppliers == []
        assert material.quality_requirements == {}

    def test_material_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MaterialSpec(
                id="MAT-003",
                name="Incomplete Material",
                category="Test",
                # Missing specification and unit
            )

        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = {err["loc"][0] for err in errors}
        assert "specification" in error_fields
        assert "unit" in error_fields


class TestMaterialLot:
    """Test MaterialLot model validation."""

    def test_valid_lot(self):
        """Test that valid material lot is accepted."""
        lot = MaterialLot(
            lot_number="LOT-20240115-001",
            material_id="MAT-001",
            supplier_id="SUP-001",
            received_date="2024-01-15",
            quantity_received=1000.0,
            quantity_remaining=850.0,
            inspection_results={
                "status": "Passed",
                "inspector": "Inspector-1",
                "notes": "All tests within spec",
            },
            status="Available",
            quarantine=False,
        )

        assert lot.lot_number == "LOT-20240115-001"
        assert lot.material_id == "MAT-001"
        assert lot.quantity_received == 1000.0
        assert lot.quantity_remaining == 850.0
        assert lot.status == "Available"
        assert lot.quarantine is False

    def test_lot_quantity_constraints(self):
        """Test that negative quantities are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MaterialLot(
                lot_number="LOT-20240115-002",
                material_id="MAT-001",
                supplier_id="SUP-001",
                received_date="2024-01-15",
                quantity_received=-100.0,  # Invalid: negative
                quantity_remaining=0.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("quantity_received",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_lot_defaults(self):
        """Test that lot fields have correct defaults."""
        lot = MaterialLot(
            lot_number="LOT-20240115-003",
            material_id="MAT-001",
            supplier_id="SUP-001",
            received_date="2024-01-15",
            quantity_received=500.0,
            quantity_remaining=500.0,
        )

        assert lot.inspection_results == {}
        assert lot.status == "Available"
        assert lot.quarantine is False

    def test_lot_quarantine_status(self):
        """Test quarantine lot configuration."""
        lot = MaterialLot(
            lot_number="LOT-20240115-004",
            material_id="MAT-001",
            supplier_id="SUP-001",
            received_date="2024-01-15",
            quantity_received=1000.0,
            quantity_remaining=1000.0,
            status="Quarantine",
            quarantine=True,
        )

        assert lot.status == "Quarantine"
        assert lot.quarantine is True


class TestOrderItem:
    """Test OrderItem model validation."""

    def test_valid_order_item(self):
        """Test that valid order item is accepted."""
        item = OrderItem(
            part_number="PART-A100",
            quantity=100,
            unit_price=25.50,
        )

        assert item.part_number == "PART-A100"
        assert item.quantity == 100
        assert item.unit_price == 25.50

    def test_order_item_quantity_constraint(self):
        """Test that quantity must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                part_number="PART-B200",
                quantity=0,  # Invalid: must be >= 1
                unit_price=30.0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("quantity",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_order_item_price_constraint(self):
        """Test that unit_price must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItem(
                part_number="PART-C300",
                quantity=50,
                unit_price=-10.0,  # Invalid: negative price
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("unit_price",)
        assert "greater_than_equal" in errors[0]["type"]


class TestOrder:
    """Test Order model validation."""

    def test_valid_order(self):
        """Test that valid order is accepted."""
        order = Order(
            id="ORD-001",
            order_number="PO-2024-1001",
            customer="Test Customer Inc",
            items=[
                OrderItem(part_number="PART-A100", quantity=100, unit_price=25.50),
                OrderItem(part_number="PART-B200", quantity=50, unit_price=40.00),
            ],
            due_date="2024-02-15",
            status="InProgress",
            priority="High",
            shipping_date=None,
            total_value=4550.00,
        )

        assert order.id == "ORD-001"
        assert order.order_number == "PO-2024-1001"
        assert order.customer == "Test Customer Inc"
        assert len(order.items) == 2
        assert order.status == "InProgress"
        assert order.priority == "High"
        assert order.total_value == 4550.00

    def test_order_defaults(self):
        """Test that order fields have correct defaults."""
        order = Order(
            id="ORD-002",
            order_number="PO-2024-1002",
            customer="Default Customer",
            due_date="2024-03-01",
            total_value=1000.00,
        )

        assert order.items == []
        assert order.status == "Pending"
        assert order.priority == "Normal"
        assert order.shipping_date is None

    def test_order_total_value_constraint(self):
        """Test that total_value must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Order(
                id="ORD-003",
                order_number="PO-2024-1003",
                customer="Test Customer",
                due_date="2024-03-01",
                total_value=-100.00,  # Invalid: negative value
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("total_value",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_order_with_shipping_date(self):
        """Test order with shipping_date set."""
        order = Order(
            id="ORD-004",
            order_number="PO-2024-1004",
            customer="Shipped Customer",
            due_date="2024-02-20",
            status="Shipped",
            shipping_date="2024-02-18",
            total_value=2500.00,
        )

        assert order.status == "Shipped"
        assert order.shipping_date == "2024-02-18"

    def test_order_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Order(
                id="ORD-005",
                order_number="PO-2024-1005",
                # Missing customer, due_date, total_value
            )

        errors = exc_info.value.errors()
        assert len(errors) == 3
        error_fields = {err["loc"][0] for err in errors}
        assert "customer" in error_fields
        assert "due_date" in error_fields
        assert "total_value" in error_fields
