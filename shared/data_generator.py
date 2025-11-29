"""Data generation functions for supply chain traceability entities."""

import logging
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

from pydantic import ValidationError
from shared.config import DEMO_SEED
from shared.models import MaterialLot, MaterialSpec, Order, OrderItem, Supplier

logger = logging.getLogger(__name__)


def initialize_random_seed() -> None:
    """Initialize random seed for deterministic data generation.

    When DEMO_SEED is set, data generation produces the same results every time.
    This enables scripted walkthroughs and reproducible demos.

    Call this function at the start of data generation (e.g., in POST /api/setup).
    """
    if DEMO_SEED is not None:
        random.seed(DEMO_SEED)
        logger.info(f"Random seed initialized to {DEMO_SEED} for deterministic generation")
    else:
        logger.debug("No DEMO_SEED set, using random data generation")


def generate_suppliers() -> List[Supplier]:
    """
    Generate realistic supplier data for demo.

    Returns:
        List of 5-10 Supplier instances with quality metrics and certifications.
    """
    logger.debug("Generating suppliers...")
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

    suppliers = [Supplier(**data) for data in suppliers_data]
    logger.info(f"Generated {len(suppliers)} suppliers")
    return suppliers


def generate_materials_catalog() -> List[MaterialSpec]:
    """
    Generate materials catalog based on machine types.

    Returns:
        List of 15-20 MaterialSpec instances for various materials.
    """
    logger.debug("Generating materials catalog...")
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

    materials = [MaterialSpec(**data) for data in materials_data]
    logger.info(f"Generated {len(materials)} materials")
    return materials


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
    logger.debug(
        f"Generating orders for {days} days starting {start_date.strftime('%Y-%m-%d')}..."
    )
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

        # Due date 5-25 days after start (or 1-days if days < 5)
        min_offset = min(5, max(1, days - 1))
        max_offset = min(25, max(1, days))
        due_date_offset = random.randint(min_offset, max_offset)
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

    logger.info(f"Generated {len(orders)} customer orders")
    return orders


def _validate_production_data(data: Dict[str, Any]) -> None:
    """
    Validate production_data structure has required keys and correct types.

    Args:
        data: Production data dictionary to validate

    Raises:
        ValueError: If required keys are missing or have wrong types
    """
    required_keys = ["machines", "shifts", "production"]
    for key in required_keys:
        if key not in data:
            raise ValueError(
                f"Production data missing required key '{key}'. "
                f"Expected keys: {required_keys}"
            )

    if not isinstance(data["machines"], list):
        raise ValueError(
            f"'machines' must be a list, got {type(data['machines']).__name__}"
        )
    if not isinstance(data["shifts"], list):
        raise ValueError(
            f"'shifts' must be a list, got {type(data['shifts']).__name__}"
        )
    if not isinstance(data["production"], dict):
        raise ValueError(
            f"'production' must be a dict, got {type(data['production']).__name__}"
        )

    if not data["shifts"]:
        raise ValueError("'shifts' list cannot be empty")

    # Validate shift structure
    required_shift_keys = ["id", "name", "start_hour", "end_hour"]
    for i, shift in enumerate(data["shifts"]):
        if not isinstance(shift, dict):
            raise ValueError(
                f"Shift at index {i} must be a dict, got {type(shift).__name__}"
            )
        for key in required_shift_keys:
            if key not in shift:
                raise ValueError(
                    f"Shift at index {i} missing required key '{key}'. "
                    f"Expected keys: {required_shift_keys}"
                )

    # Validate machine structure (only if not empty)
    if data["machines"]:
        required_machine_keys = ["id", "name"]
        for i, machine in enumerate(data["machines"]):
            if not isinstance(machine, dict):
                raise ValueError(
                    f"Machine at index {i} must be a dict, got {type(machine).__name__}"
                )
            for key in required_machine_keys:
                if key not in machine:
                    raise ValueError(
                        f"Machine at index {i} missing required key '{key}'. "
                        f"Expected keys: {required_machine_keys}"
                    )


def generate_production_batches(
    production_data: Dict[str, Any],
    materials_catalog: List[MaterialSpec],
    material_lots: List[MaterialLot],
    orders: List[Order],
    suppliers: List[Supplier],
) -> List["ProductionBatch"]:
    """
    Generate production batches with full traceability to materials, suppliers, and orders.

    This function converts daily production aggregates into individual batches with
    complete material traceability, order linkage, and serial number tracking.

    Args:
        production_data: Production data structure from generate_production_data().
            Must contain 'machines', 'shifts', and 'production' keys.
        materials_catalog: List of MaterialSpec instances for material lookup.
        material_lots: List of MaterialLot instances for lot traceability.
        orders: List of Order instances for batch-to-order assignment.
        suppliers: List of Supplier instances for quality issue root cause linkage.

    Returns:
        List of ProductionBatch instances (~1.5 batches per shift per machine).
        For 4 machines × 2 shifts × 30 days = ~360 batches expected.

    Raises:
        ValueError: If production_data is missing required 'shifts' key.
        RuntimeError: If batch generation encounters data structure errors.
        KeyError: If production_data is missing expected keys.
        TypeError: If data types are incompatible.

    Logic:
        - Convert daily production totals into batches (~1.5 batches per shift per machine)
        - Assign batches to orders (round-robin through available orders)
        - Select material lots for each batch based on machine type:
          * CNC: Steel/aluminum (MAT-001, MAT-002, MAT-003)
          * Assembly: Fasteners (MAT-005, MAT-006)
          * Packaging: Components (MAT-007, MAT-008)
          * Testing: Components (MAT-008)
        - Move quality_issues from production[date][machine] to batches
        - Assign sequential, non-overlapping serial number ranges
        - Generate batch timing (start/end times, duration)

    Note:
        This function does NOT update material_lot.quantity_remaining or order.status.
        Those updates should be handled by a separate inventory management function.
    """
    from shared.models import MaterialUsage, ProductionBatch, QualityIssue

    # Validate production_data structure early
    _validate_production_data(production_data)

    logger.info("Generating production batches with traceability...")

    try:
        batches: List[ProductionBatch] = []
        machines = production_data.get("machines", [])
        shifts = production_data.get("shifts", [])
        production = production_data.get("production", {})

        # Check for empty data (allowed, returns empty list)
        if not machines:
            logger.warning(
                "No machines found in production data, returning empty batch list"
            )
            return []

        if not production:
            logger.warning("No production data found, returning empty batch list")
            return []

        # Create machine and material lookup maps
        machine_map = {m["id"]: m for m in machines}
        material_map = {mat.id: mat for mat in materials_catalog}

        # Create supplier lookup map
        supplier_map = {sup.id: sup for sup in suppliers}

        # Create material lot lookup by lot_number for quality issue linkage
        lot_map = {lot.lot_number: lot for lot in material_lots}

        # Create material lots by material_id for efficient lookup
        lots_by_material: Dict[str, List[MaterialLot]] = {}
        for lot in material_lots:
            if lot.material_id not in lots_by_material:
                lots_by_material[lot.material_id] = []
            lots_by_material[lot.material_id].append(lot)

        # Track available orders by part number
        available_orders = [o for o in orders if o.status in ["Pending", "InProgress"]]
        order_index = 0

        # Track serial number sequence
        serial_counter = 1000

        # Operator names for variety
        operators = [
            "John Smith",
            "Sarah Johnson",
            "Mike Chen",
            "Emily Davis",
            "Carlos Rodriguez",
            "Lisa Anderson",
        ]

        # Process each date in production data
        for date_str in sorted(production.keys()):
            date_data = production[date_str]

            for machine in machines:
                machine_id = machine["id"]
                machine_name = machine["name"]

                if machine_name not in date_data:
                    continue

                daily_data = date_data[machine_name]
                shifts_data = daily_data.get("shifts", {})

                # Get quality issues for this machine/date (to distribute to batches)
                quality_issues_list = daily_data.get("quality_issues", [])

                # Generate batches for each shift
                for shift in shifts:
                    shift_id = shift["id"]
                    shift_name = shift["name"]

                    if shift_name not in shifts_data:
                        continue

                    shift_data = shifts_data[shift_name]
                    shift_parts = shift_data["parts_produced"]
                    shift_scrap = shift_data["scrap_parts"]
                    shift_good = shift_data["good_parts"]

                    if shift_parts == 0:
                        continue

                    # Generate 1-2 batches per shift (avg 1.5)
                    num_batches = random.choice([1, 2])

                    for batch_num in range(num_batches):
                        batch_id = f"BATCH-{date_str}-{machine_name}-{shift_name}-{batch_num + 1:02d}"

                        # Distribute parts across batches
                        if batch_num == num_batches - 1:
                            # Last batch gets remaining parts
                            batch_parts = shift_parts
                            batch_scrap = shift_scrap
                        else:
                            # Split evenly
                            batch_parts = shift_parts // num_batches
                            batch_scrap = shift_scrap // num_batches
                            shift_parts -= batch_parts
                            shift_scrap -= batch_scrap

                        batch_good = batch_parts - batch_scrap

                        # Assign to order (round-robin)
                        order_id = None
                        part_number = f"PART-{machine_id:03d}"
                        if available_orders:
                            order = available_orders[
                                order_index % len(available_orders)
                            ]
                            order_id = order.id
                            # Use part number from order if available
                            if order.items:
                                part_number = order.items[0].part_number
                            order_index += 1

                        # Select materials based on machine type
                        materials_consumed = []
                        if machine_name.startswith("CNC"):
                            # CNC uses steel/aluminum
                            mat_ids = ["MAT-001", "MAT-002", "MAT-003"]
                        elif machine_name.startswith("Assembly"):
                            # Assembly uses fasteners + components
                            mat_ids = ["MAT-005", "MAT-006", "MAT-007"]
                        elif machine_name.startswith("Packaging"):
                            # Packaging uses components (simplified for demo)
                            mat_ids = ["MAT-007", "MAT-008"]
                        else:
                            # Testing uses components (simplified for demo)
                            mat_ids = ["MAT-008"]

                        for mat_id in mat_ids:
                            if mat_id in material_map and mat_id in lots_by_material:
                                material = material_map[mat_id]
                                available_lots = [
                                    lot
                                    for lot in lots_by_material[mat_id]
                                    if lot.status in ["Available", "InUse"]
                                    and lot.quantity_remaining > 0
                                ]
                                if available_lots:
                                    # Select random available lot
                                    lot = random.choice(available_lots)
                                    quantity_used = random.uniform(10.0, 50.0)

                                    materials_consumed.append(
                                        MaterialUsage(
                                            material_id=mat_id,
                                            material_name=material.name,
                                            lot_number=lot.lot_number,
                                            quantity_used=round(quantity_used, 2),
                                            unit=material.unit,
                                        )
                                    )

                        # Distribute quality issues to batches
                        batch_quality_issues = []
                        if quality_issues_list and batch_num == 0:
                            # Assign all quality issues to first batch of shift
                            for issue_data in quality_issues_list:
                                # PR19: Link material-type quality issues to specific materials and suppliers
                                material_id = None
                                lot_number = None
                                supplier_id = None
                                supplier_name = None
                                root_cause = "unknown"

                                if issue_data.get("type") == "material" and materials_consumed:
                                    # For material defects, link to a material lot from this batch
                                    # Bias toward lower-quality suppliers (defect rate > 3%)
                                    material_usage = random.choice(materials_consumed)
                                    lot_number = material_usage.lot_number
                                    material_id = material_usage.material_id

                                    # Look up the lot to get supplier info
                                    if lot_number in lot_map:
                                        lot = lot_map[lot_number]
                                        supplier_id = lot.supplier_id
                                        if supplier_id in supplier_map:
                                            supplier = supplier_map[supplier_id]
                                            supplier_name = supplier.name
                                            # Determine root cause based on supplier quality
                                            defect_rate = supplier.quality_metrics.get("defect_rate", 0)
                                            if defect_rate > 3.0:
                                                root_cause = "supplier_quality"
                                            else:
                                                root_cause = "material_defect"

                                batch_quality_issues.append(
                                    QualityIssue(
                                        type=issue_data["type"],
                                        description=issue_data["description"],
                                        parts_affected=issue_data["parts_affected"],
                                        severity=issue_data["severity"],
                                        date=date_str,
                                        machine=machine_name,
                                        material_id=material_id,
                                        lot_number=lot_number,
                                        supplier_id=supplier_id,
                                        supplier_name=supplier_name,
                                        root_cause=root_cause,
                                    )
                                )

                        # Assign serial numbers
                        serial_start = serial_counter
                        serial_end = serial_counter + batch_parts - 1
                        serial_counter = serial_end + 1

                        # Generate batch start/end times based on shift
                        start_hour = shift["start_hour"]
                        batch_duration = random.uniform(2.0, 4.0)
                        start_time = f"{start_hour:02d}:{random.randint(0, 59):02d}"
                        end_hour = start_hour + int(batch_duration)
                        end_time = f"{end_hour:02d}:{random.randint(0, 59):02d}"

                        # Select random operator
                        operator = random.choice(operators)

                        # Create batch with error handling
                        try:
                            batch = ProductionBatch(
                                batch_id=batch_id,
                                date=date_str,
                                machine_id=machine_id,
                                machine_name=machine_name,
                                shift_id=shift_id,
                                shift_name=shift_name,
                                order_id=order_id,
                                part_number=part_number,
                                operator=operator,
                                parts_produced=batch_parts,
                                good_parts=batch_good,
                                scrap_parts=batch_scrap,
                                serial_start=serial_start,
                                serial_end=serial_end,
                                materials_consumed=materials_consumed,
                                quality_issues=batch_quality_issues,
                                start_time=start_time,
                                end_time=end_time,
                                duration_hours=round(batch_duration, 2),
                            )
                            batches.append(batch)
                        except ValidationError as e:
                            logger.warning(
                                f"Skipping invalid batch {batch_id} for {machine_name} "
                                f"on {date_str} shift {shift_name}: {e}"
                            )
                            continue  # Skip this batch but continue processing others

        logger.info(f"Generated {len(batches)} production batches")
        return batches

    except KeyError as e:
        logger.error(f"Missing required key in production data: {e}")
        raise RuntimeError(f"Failed to generate batches: missing key {e}") from e
    except (TypeError, AttributeError) as e:
        logger.error(f"Invalid data structure in production data: {e}")
        raise RuntimeError(
            f"Failed to generate batches: invalid data structure {e}"
        ) from e
    except ValueError as e:
        logger.error(f"Invalid value encountered during batch generation: {e}")
        raise RuntimeError(f"Failed to generate batches: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error generating production batches: {e}")
        raise RuntimeError(f"Failed to generate batches: {e}") from e
