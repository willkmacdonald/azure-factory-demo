"""Unit tests for supply chain data generation functions."""

from datetime import datetime

import pytest

from shared.data_generator import (
    generate_material_lots,
    generate_materials_catalog,
    generate_orders,
    generate_suppliers,
)


class TestGenerateSuppliers:
    """Test supplier generation function."""

    def test_generates_correct_count(self):
        """Test that generate_suppliers returns 5 suppliers."""
        suppliers = generate_suppliers()
        assert len(suppliers) == 5

    def test_all_suppliers_have_required_fields(self):
        """Test that all generated suppliers have required fields."""
        suppliers = generate_suppliers()

        for supplier in suppliers:
            assert supplier.id is not None
            assert supplier.name is not None
            assert supplier.type is not None
            assert isinstance(supplier.materials_supplied, list)
            assert isinstance(supplier.contact, dict)
            assert isinstance(supplier.quality_metrics, dict)
            assert isinstance(supplier.certifications, list)
            assert supplier.status in ["Active", "OnHold", "Suspended"]

    def test_suppliers_have_unique_ids(self):
        """Test that supplier IDs are unique."""
        suppliers = generate_suppliers()
        ids = [s.id for s in suppliers]
        assert len(ids) == len(set(ids))

    def test_suppliers_have_quality_metrics(self):
        """Test that suppliers have quality metrics populated."""
        suppliers = generate_suppliers()

        for supplier in suppliers:
            assert "quality_rating" in supplier.quality_metrics
            assert "on_time_delivery_rate" in supplier.quality_metrics
            assert "defect_rate" in supplier.quality_metrics

            # Check value ranges
            assert 0 <= supplier.quality_metrics["quality_rating"] <= 100
            assert 0 <= supplier.quality_metrics["on_time_delivery_rate"] <= 100
            assert supplier.quality_metrics["defect_rate"] >= 0


class TestGenerateMaterialsCatalog:
    """Test materials catalog generation function."""

    def test_generates_materials(self):
        """Test that generate_materials_catalog returns materials."""
        materials = generate_materials_catalog()
        assert len(materials) >= 8  # At least 8 materials defined

    def test_all_materials_have_required_fields(self):
        """Test that all generated materials have required fields."""
        materials = generate_materials_catalog()

        for material in materials:
            assert material.id is not None
            assert material.name is not None
            assert material.category is not None
            assert material.specification is not None
            assert material.unit is not None
            assert isinstance(material.preferred_suppliers, list)
            assert isinstance(material.quality_requirements, dict)

    def test_materials_have_unique_ids(self):
        """Test that material IDs are unique."""
        materials = generate_materials_catalog()
        ids = [m.id for m in materials]
        assert len(ids) == len(set(ids))

    def test_materials_have_valid_categories(self):
        """Test that materials have valid categories."""
        materials = generate_materials_catalog()
        categories = {m.category for m in materials}

        # Expected categories
        assert "Steel" in categories or "Aluminum" in categories
        assert "Fasteners" in categories or "Components" in categories

    def test_materials_reference_valid_suppliers(self):
        """Test that materials reference existing suppliers."""
        materials = generate_materials_catalog()
        suppliers = generate_suppliers()
        supplier_ids = {s.id for s in suppliers}

        for material in materials:
            for supplier_id in material.preferred_suppliers:
                assert (
                    supplier_id in supplier_ids
                ), f"Material {material.id} references non-existent supplier {supplier_id}"


class TestGenerateMaterialLots:
    """Test material lot generation function."""

    def test_generates_lots(self):
        """Test that generate_material_lots returns 20-30 lots."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        assert 20 <= len(lots) <= 30

    def test_all_lots_have_required_fields(self):
        """Test that all generated lots have required fields."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        for lot in lots:
            assert lot.lot_number is not None
            assert lot.material_id is not None
            assert lot.supplier_id is not None
            assert lot.received_date is not None
            assert lot.quantity_received >= 0
            assert lot.quantity_remaining >= 0
            assert isinstance(lot.inspection_results, dict)
            assert lot.status in [
                "Available",
                "InUse",
                "Depleted",
                "Quarantine",
                "Rejected",
            ]
            assert isinstance(lot.quarantine, bool)

    def test_lots_have_unique_numbers(self):
        """Test that lot numbers are unique."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        lot_numbers = [lot.lot_number for lot in lots]
        assert len(lot_numbers) == len(set(lot_numbers))

    def test_lots_reference_valid_materials_and_suppliers(self):
        """Test that lots reference existing materials and suppliers."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        material_ids = {m.id for m in materials}
        supplier_ids = {s.id for s in suppliers}

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        for lot in lots:
            assert (
                lot.material_id in material_ids
            ), f"Lot {lot.lot_number} references non-existent material {lot.material_id}"
            assert (
                lot.supplier_id in supplier_ids
            ), f"Lot {lot.lot_number} references non-existent supplier {lot.supplier_id}"

    def test_lots_quantity_remaining_valid(self):
        """Test that quantity_remaining <= quantity_received."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        for lot in lots:
            assert (
                lot.quantity_remaining <= lot.quantity_received
            ), f"Lot {lot.lot_number} has remaining > received"

    def test_depleted_lots_have_zero_remaining(self):
        """Test that depleted lots have quantity_remaining = 0."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        for lot in lots:
            if lot.status == "Depleted":
                assert (
                    lot.quantity_remaining == 0.0
                ), f"Depleted lot {lot.lot_number} has non-zero remaining"

    def test_quarantine_lots_have_flag_set(self):
        """Test that quarantine lots have quarantine flag = True."""
        suppliers = generate_suppliers()
        materials = generate_materials_catalog()
        start_date = datetime(2024, 1, 1)

        lots = generate_material_lots(suppliers, materials, start_date, days=30)

        for lot in lots:
            if lot.status == "Quarantine":
                assert (
                    lot.quarantine is True
                ), f"Quarantine lot {lot.lot_number} has quarantine=False"


class TestGenerateOrders:
    """Test order generation function."""

    def test_generates_orders(self):
        """Test that generate_orders returns 10-15 orders."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        assert 10 <= len(orders) <= 15

    def test_all_orders_have_required_fields(self):
        """Test that all generated orders have required fields."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        for order in orders:
            assert order.id is not None
            assert order.order_number is not None
            assert order.customer is not None
            assert isinstance(order.items, list)
            assert order.due_date is not None
            assert order.status in [
                "Pending",
                "InProgress",
                "Completed",
                "Shipped",
                "Delayed",
            ]
            assert order.priority in ["Low", "Normal", "High", "Urgent"]
            assert order.total_value >= 0

    def test_orders_have_unique_ids(self):
        """Test that order IDs are unique."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        ids = [o.id for o in orders]
        assert len(ids) == len(set(ids))

    def test_order_items_valid(self):
        """Test that all order items have valid fields."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        for order in orders:
            for item in order.items:
                assert item.part_number is not None
                assert item.quantity >= 1
                assert item.unit_price >= 0

    def test_shipped_orders_have_shipping_date(self):
        """Test that shipped orders have a shipping_date."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        for order in orders:
            if order.status == "Shipped":
                assert (
                    order.shipping_date is not None
                ), f"Shipped order {order.id} has no shipping_date"

    def test_order_total_value_reasonable(self):
        """Test that order total_value is reasonable based on items."""
        start_date = datetime(2024, 1, 1)
        orders = generate_orders(start_date, days=30)

        for order in orders:
            if len(order.items) > 0:
                # Calculate expected total (approximately)
                calculated_total = sum(
                    item.quantity * item.unit_price for item in order.items
                )

                # Allow small rounding differences (within 0.5% or $2, whichever is larger)
                tolerance = max(2.0, abs(calculated_total * 0.005))
                assert (
                    abs(order.total_value - calculated_total) < tolerance
                ), f"Order {order.id} total_value mismatch: {order.total_value} vs {calculated_total}"
