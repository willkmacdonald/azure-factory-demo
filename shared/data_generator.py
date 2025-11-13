"""Data generation functions for supply chain traceability entities."""

import logging
import random
from datetime import datetime, timedelta
from typing import List

from shared.models import MaterialLot, MaterialSpec, Order, OrderItem, Supplier

logger = logging.getLogger(__name__)


def generate_suppliers() -> List[Supplier]:
    """
    Generate realistic supplier data for demo.

    Returns:
        List of 5-10 Supplier instances with quality metrics and certifications.
    """
    suppliers_data = [
        {
            "id": "SUP-001",
            "name": "SteelCorp International",
            "type": "Raw Materials",
            "materials_supplied": ["MAT-001", "MAT-002"],
            "contact": {
                "email": "orders@steelcorp.com",
                "phone": "+1-555-0101",
                "address": "123 Industrial Way, Pittsburgh, PA",
            },
            "quality_metrics": {
                "quality_rating": 92.5,
                "on_time_delivery_rate": 95.0,
                "defect_rate": 1.2,
            },
            "certifications": ["ISO9001", "AS9100"],
            "status": "Active",
        },
        {
            "id": "SUP-002",
            "name": "PrecisionFast LLC",
            "type": "Fasteners",
            "materials_supplied": ["MAT-005", "MAT-006"],
            "contact": {
                "email": "sales@precisionfast.com",
                "phone": "+1-555-0202",
                "address": "456 Bolt Street, Cleveland, OH",
            },
            "quality_metrics": {
                "quality_rating": 88.0,
                "on_time_delivery_rate": 90.0,
                "defect_rate": 2.5,
            },
            "certifications": ["ISO9001"],
            "status": "Active",
        },
        {
            "id": "SUP-003",
            "name": "AluminumWorks Co",
            "type": "Raw Materials",
            "materials_supplied": ["MAT-003"],
            "contact": {
                "email": "info@aluminumworks.com",
                "phone": "+1-555-0303",
                "address": "789 Metal Drive, Detroit, MI",
            },
            "quality_metrics": {
                "quality_rating": 95.0,
                "on_time_delivery_rate": 97.0,
                "defect_rate": 0.8,
            },
            "certifications": ["ISO9001", "ISO14001"],
            "status": "Active",
        },
        {
            "id": "SUP-004",
            "name": "ComponentTech Industries",
            "type": "Components",
            "materials_supplied": ["MAT-007", "MAT-008"],
            "contact": {
                "email": "orders@componenttech.com",
                "phone": "+1-555-0404",
                "address": "321 Circuit Lane, San Jose, CA",
            },
            "quality_metrics": {
                "quality_rating": 85.0,
                "on_time_delivery_rate": 88.0,
                "defect_rate": 3.2,
            },
            "certifications": ["ISO9001"],
            "status": "Active",
        },
        {
            "id": "SUP-005",
            "name": "EcoMaterials Group",
            "type": "Raw Materials",
            "materials_supplied": ["MAT-004"],
            "contact": {
                "email": "contact@ecomaterials.com",
                "phone": "+1-555-0505",
                "address": "654 Green Ave, Portland, OR",
            },
            "quality_metrics": {
                "quality_rating": 78.0,
                "on_time_delivery_rate": 82.0,
                "defect_rate": 4.5,
            },
            "certifications": ["ISO14001"],
            "status": "OnHold",
        },
    ]

    return [Supplier(**data) for data in suppliers_data]


def generate_materials_catalog() -> List[MaterialSpec]:
    """
    Generate materials catalog based on machine types.

    Returns:
        List of 15-20 MaterialSpec instances for various materials.
    """
    materials_data = [
        # Steel materials for CNC machines
        {
            "id": "MAT-001",
            "name": "Steel Bar 304 Stainless",
            "category": "Steel",
            "specification": "ASTM A479 Grade 304",
            "unit": "kg",
            "preferred_suppliers": ["SUP-001"],
            "quality_requirements": {
                "hardness": "HRC 20-25",
                "tensile_strength": "≥515 MPa",
                "inspection": "Visual + Hardness test",
            },
        },
        {
            "id": "MAT-002",
            "name": "Steel Bar 4140 Alloy",
            "category": "Steel",
            "specification": "ASTM A29 Grade 4140",
            "unit": "kg",
            "preferred_suppliers": ["SUP-001"],
            "quality_requirements": {
                "hardness": "HRC 28-32",
                "tensile_strength": "≥655 MPa",
                "inspection": "Visual + Hardness + Ultrasonic",
            },
        },
        {
            "id": "MAT-003",
            "name": "Aluminum Bar 6061-T6",
            "category": "Aluminum",
            "specification": "ASTM B221 Grade 6061-T6",
            "unit": "kg",
            "preferred_suppliers": ["SUP-003"],
            "quality_requirements": {
                "hardness": "HB 95",
                "tensile_strength": "≥310 MPa",
                "inspection": "Visual + Dimensional",
            },
        },
        {
            "id": "MAT-004",
            "name": "Steel Plate A36",
            "category": "Steel",
            "specification": "ASTM A36 Carbon Steel",
            "unit": "kg",
            "preferred_suppliers": ["SUP-005"],
            "quality_requirements": {
                "tensile_strength": "≥400 MPa",
                "yield_strength": "≥250 MPa",
                "inspection": "Visual + Tensile test",
            },
        },
        # Fasteners for assembly lines
        {
            "id": "MAT-005",
            "name": "M8x1.25 Hex Bolt Grade 8.8",
            "category": "Fasteners",
            "specification": "ISO 4017 Grade 8.8",
            "unit": "pieces",
            "preferred_suppliers": ["SUP-002"],
            "quality_requirements": {
                "hardness": "HRC 22-32",
                "torque": "25 Nm ±2",
                "inspection": "Visual + Dimensional + Sample torque test",
            },
        },
        {
            "id": "MAT-006",
            "name": "M10x1.5 Socket Cap Screw",
            "category": "Fasteners",
            "specification": "ISO 4762 Grade 12.9",
            "unit": "pieces",
            "preferred_suppliers": ["SUP-002"],
            "quality_requirements": {
                "hardness": "HRC 39-44",
                "torque": "50 Nm ±3",
                "inspection": "Visual + Dimensional + Sample torque test",
            },
        },
        # Components for assembly
        {
            "id": "MAT-007",
            "name": "Electronic Control Module ECM-2000",
            "category": "Components",
            "specification": "Custom OEM Part #ECM2000",
            "unit": "pieces",
            "preferred_suppliers": ["SUP-004"],
            "quality_requirements": {
                "functional_test": "100% tested",
                "visual": "No cosmetic defects",
                "inspection": "Functional + Visual",
            },
        },
        {
            "id": "MAT-008",
            "name": "Hydraulic Pump Assembly HP-150",
            "category": "Components",
            "specification": "Custom OEM Part #HP150",
            "unit": "pieces",
            "preferred_suppliers": ["SUP-004"],
            "quality_requirements": {
                "pressure_test": "150 bar minimum",
                "leak_test": "Zero leakage at 200 bar",
                "inspection": "Pressure + Leak + Visual",
            },
        },
    ]

    return [MaterialSpec(**data) for data in materials_data]


def generate_material_lots(
    suppliers: List[Supplier],
    materials: List[MaterialSpec],
    start_date: datetime,
    days: int = 30,
) -> List[MaterialLot]:
    """
    Generate material lot receipts spanning the date range.

    Args:
        suppliers: List of suppliers
        materials: List of material specifications
        start_date: Start date for lot generation
        days: Number of days to generate lots for

    Returns:
        List of 20-30 MaterialLot instances with inspection results.
    """
    lots = []
    lot_counter = 1

    # Generate 20-30 lots spread across the date range
    num_lots = random.randint(20, 30)

    for _ in range(num_lots):
        # Random material
        material = random.choice(materials)

        # Find supplier for this material
        matching_suppliers = [
            s for s in suppliers if material.id in s.materials_supplied
        ]
        if not matching_suppliers:
            logger.warning(
                f"No suppliers found for material {material.id}, skipping lot generation"
            )
            continue
        supplier = random.choice(matching_suppliers)

        # Random date within range
        days_offset = random.randint(0, days - 1)
        received_date = start_date + timedelta(days=days_offset)

        # Quantity based on material type
        if material.unit == "kg":
            quantity = random.randint(500, 2000)
        elif material.unit == "pieces":
            quantity = random.randint(1000, 5000)
        else:
            quantity = random.randint(100, 1000)

        # Determine lot status based on supplier quality
        quality_rating = supplier.quality_metrics.get("quality_rating", 90)
        if quality_rating < 80:
            # Lower quality suppliers have higher chance of issues
            status_weights = [0.6, 0.2, 0.1, 0.05, 0.05]
            status = random.choices(
                ["Available", "InUse", "Depleted", "Quarantine", "Rejected"],
                weights=status_weights,
            )[0]
        else:
            # Higher quality suppliers rarely have issues
            status_weights = [0.7, 0.25, 0.04, 0.005, 0.005]
            status = random.choices(
                ["Available", "InUse", "Depleted", "Quarantine", "Rejected"],
                weights=status_weights,
            )[0]

        quarantine = status == "Quarantine"

        # Inspection results
        if status == "Rejected":
            inspection_status = "Failed"
            notes = "Material did not meet specification requirements"
        elif status == "Quarantine":
            inspection_status = "Hold"
            notes = "Suspect quality - pending further investigation"
        else:
            inspection_status = "Passed"
            notes = "All tests within specification"

        inspection_results = {
            "status": inspection_status,
            "inspector": f"Inspector-{random.randint(1, 5)}",
            "notes": notes,
            "test_results": "See attached report",
        }

        # Quantity remaining (some lots partially consumed)
        if status == "Depleted":
            quantity_remaining = 0.0
        elif status in ["InUse", "Available"]:
            quantity_remaining = quantity * random.uniform(0.3, 1.0)
        else:
            quantity_remaining = float(quantity)

        lot_number = f"LOT-{received_date.strftime('%Y%m%d')}-{lot_counter:03d}"
        lot_counter += 1

        lot = MaterialLot(
            lot_number=lot_number,
            material_id=material.id,
            supplier_id=supplier.id,
            received_date=received_date.strftime("%Y-%m-%d"),
            quantity_received=float(quantity),
            quantity_remaining=quantity_remaining,
            inspection_results=inspection_results,
            status=status,
            quarantine=quarantine,
        )
        lots.append(lot)

    return lots


def generate_orders(start_date: datetime, days: int = 30) -> List[Order]:
    """
    Generate customer orders spanning production dates.

    Args:
        start_date: Start date for order generation
        days: Number of days to generate orders for

    Returns:
        List of 10-15 Order instances with line items.
    """
    orders = []

    # Customer names
    customers = [
        "Acme Manufacturing",
        "TechParts Inc",
        "Industrial Solutions Ltd",
        "Global Assembly Corp",
        "Precision Industries",
        "AutoComponents Co",
        "MegaProd Systems",
    ]

    # Part numbers (matching production capabilities)
    part_numbers = [
        "PART-A100",
        "PART-B200",
        "PART-C300",
        "PART-D400",
        "PART-E500",
    ]

    num_orders = random.randint(10, 15)

    for i in range(num_orders):
        order_id = f"ORD-{i+1:03d}"
        order_number = f"PO-2024-{i+1000}"

        customer = random.choice(customers)

        # Generate 1-3 line items per order
        num_items = random.randint(1, 3)
        items = []
        total_value = 0.0

        for _ in range(num_items):
            part_number = random.choice(part_numbers)
            quantity = random.randint(50, 500)
            unit_price = random.uniform(10.0, 100.0)

            items.append(
                OrderItem(
                    part_number=part_number,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                )
            )
            total_value += quantity * unit_price

        # Due date 5-25 days after start
        due_date_offset = random.randint(5, min(25, days))
        due_date = start_date + timedelta(days=due_date_offset)

        # Status based on due date
        current_date = start_date + timedelta(days=days)
        if due_date < current_date - timedelta(days=5):
            status_weights = [0.05, 0.1, 0.5, 0.3, 0.05]
            status = random.choices(
                ["Pending", "InProgress", "Completed", "Shipped", "Delayed"],
                weights=status_weights,
            )[0]
        else:
            status_weights = [0.2, 0.5, 0.2, 0.08, 0.02]
            status = random.choices(
                ["Pending", "InProgress", "Completed", "Shipped", "Delayed"],
                weights=status_weights,
            )[0]

        # Shipping date if shipped
        shipping_date = None
        if status == "Shipped":
            ship_offset = random.randint(0, due_date_offset - 1)
            shipping_date = (start_date + timedelta(days=ship_offset)).strftime(
                "%Y-%m-%d"
            )

        # Priority
        priority_weights = [0.1, 0.6, 0.25, 0.05]
        priority = random.choices(
            ["Low", "Normal", "High", "Urgent"], weights=priority_weights
        )[0]

        order = Order(
            id=order_id,
            order_number=order_number,
            customer=customer,
            items=items,
            due_date=due_date.strftime("%Y-%m-%d"),
            status=status,
            priority=priority,
            shipping_date=shipping_date,
            total_value=round(total_value, 2),
        )
        orders.append(order)

    return orders
