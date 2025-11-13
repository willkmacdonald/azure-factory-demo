"""Unit tests for supply chain traceability Pydantic models."""

import pytest
from pydantic import ValidationError

from shared.models import (
    MaterialLot,
    MaterialSpec,
    MaterialUsage,
    Order,
    OrderItem,
    ProductionBatch,
    QualityIssue,
    Supplier,
)


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


class TestMaterialUsage:
    """Test MaterialUsage model validation (PR14)."""

    def test_valid_material_usage(self):
        """Test that valid material usage data is accepted."""
        usage = MaterialUsage(
            material_id="MAT-001",
            material_name="Steel Bar 304",
            lot_number="LOT-20240115-001",
            quantity_used=25.5,
            unit="kg",
        )

        assert usage.material_id == "MAT-001"
        assert usage.material_name == "Steel Bar 304"
        assert usage.lot_number == "LOT-20240115-001"
        assert usage.quantity_used == 25.5
        assert usage.unit == "kg"

    def test_material_usage_zero_quantity(self):
        """Test that zero quantity is allowed."""
        usage = MaterialUsage(
            material_id="MAT-002",
            material_name="Aluminum Bar",
            lot_number="LOT-20240116-001",
            quantity_used=0.0,
            unit="kg",
        )

        assert usage.quantity_used == 0.0

    def test_material_usage_negative_quantity(self):
        """Test that negative quantity raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MaterialUsage(
                material_id="MAT-003",
                material_name="Steel Plate",
                lot_number="LOT-20240117-001",
                quantity_used=-10.5,
                unit="kg",
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("quantity_used",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_material_usage_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MaterialUsage(
                material_id="MAT-004",
                # Missing material_name, lot_number, quantity_used, unit
            )

        errors = exc_info.value.errors()
        assert len(errors) == 4
        error_fields = {err["loc"][0] for err in errors}
        assert "material_name" in error_fields
        assert "lot_number" in error_fields
        assert "quantity_used" in error_fields
        assert "unit" in error_fields


class TestProductionBatch:
    """Test ProductionBatch model validation (PR14)."""

    def test_valid_production_batch_minimal(self):
        """Test that valid minimal batch data is accepted."""
        batch = ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC001-Day-01",
            date="2024-01-15",
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            part_number="PART-001",
            operator="John Smith",
            parts_produced=120,
            good_parts=115,
            scrap_parts=5,
        )

        assert batch.batch_id == "BATCH-2024-01-15-CNC001-Day-01"
        assert batch.machine_id == 1
        assert batch.parts_produced == 120
        assert batch.good_parts == 115
        assert batch.scrap_parts == 5
        assert batch.order_id is None
        assert batch.serial_start is None
        assert batch.serial_end is None
        assert len(batch.materials_consumed) == 0
        assert len(batch.quality_issues) == 0

    def test_valid_production_batch_full(self):
        """Test that valid full batch data is accepted."""
        quality_issue = QualityIssue(
            type="dimensional",
            description="Out of tolerance",
            parts_affected=3,
            severity="Medium",
            date="2024-01-15",
            machine="CNC-001",
        )

        material_usage = MaterialUsage(
            material_id="MAT-001",
            material_name="Steel Bar 304",
            lot_number="LOT-20240115-001",
            quantity_used=45.2,
            unit="kg",
        )

        batch = ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC001-Day-01",
            date="2024-01-15",
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            order_id="ORD-001",
            part_number="PART-001",
            operator="John Smith",
            parts_produced=120,
            good_parts=115,
            scrap_parts=5,
            serial_start=1000,
            serial_end=1119,
            materials_consumed=[material_usage],
            quality_issues=[quality_issue],
            process_parameters={"temperature": 850.0, "pressure": 120.5},
            start_time="06:15",
            end_time="09:45",
            duration_hours=3.5,
        )

        assert batch.order_id == "ORD-001"
        assert batch.serial_start == 1000
        assert batch.serial_end == 1119
        assert len(batch.materials_consumed) == 1
        assert batch.materials_consumed[0].material_id == "MAT-001"
        assert len(batch.quality_issues) == 1
        assert batch.quality_issues[0].type == "dimensional"
        assert batch.process_parameters["temperature"] == 850.0
        assert batch.start_time == "06:15"
        assert batch.duration_hours == 3.5

    def test_production_batch_negative_parts(self):
        """Test that negative parts values raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProductionBatch(
                batch_id="BATCH-2024-01-15-CNC001-Day-01",
                date="2024-01-15",
                machine_id=1,
                machine_name="CNC-001",
                shift_id=1,
                shift_name="Day",
                part_number="PART-001",
                operator="John Smith",
                parts_produced=-10,
                good_parts=0,
                scrap_parts=0,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("parts_produced",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_production_batch_invalid_machine_id(self):
        """Test that zero/negative machine_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProductionBatch(
                batch_id="BATCH-2024-01-15-CNC001-Day-01",
                date="2024-01-15",
                machine_id=0,
                machine_name="CNC-001",
                shift_id=1,
                shift_name="Day",
                part_number="PART-001",
                operator="John Smith",
                parts_produced=100,
                good_parts=95,
                scrap_parts=5,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("machine_id",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_production_batch_negative_duration(self):
        """Test that negative duration raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProductionBatch(
                batch_id="BATCH-2024-01-15-CNC001-Day-01",
                date="2024-01-15",
                machine_id=1,
                machine_name="CNC-001",
                shift_id=1,
                shift_name="Day",
                part_number="PART-001",
                operator="John Smith",
                parts_produced=100,
                good_parts=95,
                scrap_parts=5,
                duration_hours=-1.5,
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("duration_hours",)
        assert "greater_than_equal" in errors[0]["type"]

    def test_production_batch_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProductionBatch(
                batch_id="BATCH-2024-01-15-CNC001-Day-01",
                date="2024-01-15",
                # Missing machine_id, machine_name, shift_id, shift_name,
                # part_number, operator, parts_produced, good_parts, scrap_parts
            )

        errors = exc_info.value.errors()
        assert len(errors) == 9
        error_fields = {err["loc"][0] for err in errors}
        assert "machine_id" in error_fields
        assert "machine_name" in error_fields
        assert "shift_id" in error_fields
        assert "shift_name" in error_fields
        assert "part_number" in error_fields
        assert "operator" in error_fields
        assert "parts_produced" in error_fields
        assert "good_parts" in error_fields
        assert "scrap_parts" in error_fields

    def test_production_batch_with_multiple_materials(self):
        """Test batch with multiple materials consumed."""
        materials = [
            MaterialUsage(
                material_id="MAT-001",
                material_name="Steel Bar 304",
                lot_number="LOT-20240115-001",
                quantity_used=25.5,
                unit="kg",
            ),
            MaterialUsage(
                material_id="MAT-005",
                material_name="M8 Hex Bolt",
                lot_number="LOT-20240115-002",
                quantity_used=150.0,
                unit="pieces",
            ),
        ]

        batch = ProductionBatch(
            batch_id="BATCH-2024-01-15-Assembly001-Day-01",
            date="2024-01-15",
            machine_id=2,
            machine_name="Assembly-001",
            shift_id=1,
            shift_name="Day",
            part_number="PART-002",
            operator="Sarah Johnson",
            parts_produced=80,
            good_parts=78,
            scrap_parts=2,
            materials_consumed=materials,
        )

        assert len(batch.materials_consumed) == 2
        assert batch.materials_consumed[0].material_id == "MAT-001"
        assert batch.materials_consumed[0].unit == "kg"
        assert batch.materials_consumed[1].material_id == "MAT-005"
        assert batch.materials_consumed[1].unit == "pieces"

    def test_production_batch_with_multiple_quality_issues(self):
        """Test batch with multiple quality issues."""
        issues = [
            QualityIssue(
                type="dimensional",
                description="Out of tolerance",
                parts_affected=2,
                severity="Medium",
                date="2024-01-15",
                machine="CNC-001",
            ),
            QualityIssue(
                type="surface",
                description="Surface finish issues",
                parts_affected=3,
                severity="Low",
                date="2024-01-15",
                machine="CNC-001",
            ),
        ]

        batch = ProductionBatch(
            batch_id="BATCH-2024-01-15-CNC001-Day-01",
            date="2024-01-15",
            machine_id=1,
            machine_name="CNC-001",
            shift_id=1,
            shift_name="Day",
            part_number="PART-001",
            operator="John Smith",
            parts_produced=120,
            good_parts=115,
            scrap_parts=5,
            quality_issues=issues,
        )

        assert len(batch.quality_issues) == 2
        assert batch.quality_issues[0].type == "dimensional"
        assert batch.quality_issues[0].severity == "Medium"
        assert batch.quality_issues[1].type == "surface"
        assert batch.quality_issues[1].severity == "Low"
