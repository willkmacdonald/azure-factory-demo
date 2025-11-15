"""
Simple script to regenerate production data with PR19 material-supplier linkage.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from shared.data import generate_production_data
from shared.data_generator import (
    generate_materials_catalog,
    generate_suppliers,
    generate_material_lots,
    generate_production_batches,
    generate_orders,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Regenerate all production data with material-supplier linkage."""
    logger.info("Starting data regeneration with PR19 material-supplier linkage...")

    # Generate traceability entities
    logger.info("Generating suppliers...")
    suppliers = generate_suppliers()

    logger.info("Generating materials catalog...")
    materials_catalog = generate_materials_catalog()

    # Calculate start date (60 days before today)
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=60)

    logger.info("Generating material lots...")
    material_lots = generate_material_lots(
        suppliers=suppliers,
        materials=materials_catalog,
        start_date=start_date,
        days=60
    )

    logger.info("Generating customer orders...")
    orders = generate_orders(start_date, days=30)

    logger.info("Generating base production data...")
    base_data = generate_production_data(days=30)

    logger.info("Generating production batches with material linkage...")
    production_batches = generate_production_batches(
        production_data=base_data,
        materials_catalog=materials_catalog,
        material_lots=material_lots,
        orders=orders,
        suppliers=suppliers,
    )

    # Save to data/production.json
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    production_data = {
        "suppliers": [s.model_dump() for s in suppliers],
        "materials_catalog": [m.model_dump() for m in materials_catalog],
        "material_lots": [lot.model_dump() for lot in material_lots],
        "production_batches": [batch.model_dump() for batch in production_batches],
        "orders": [order.model_dump() for order in orders],
    }

    output_file = data_dir / "production.json"
    logger.info(f"Saving data to {output_file}...")

    with open(output_file, "w") as f:
        json.dump(production_data, f, indent=2)

    logger.info("✅ Data regeneration complete!")
    logger.info(f"Generated:")
    logger.info(f"  - {len(suppliers)} suppliers")
    logger.info(f"  - {len(materials_catalog)} materials")
    logger.info(f"  - {len(material_lots)} material lots")
    logger.info(f"  - {len(production_batches)} production batches")
    logger.info(f"  - {len(orders)} customer orders")

    # Count quality issues with material linkage
    total_issues = sum(len(batch.quality_issues) for batch in production_batches)
    linked_issues = sum(
        1
        for batch in production_batches
        for issue in batch.quality_issues
        if issue.material_id is not None
    )

    logger.info(f"\nQuality Issues:")
    logger.info(f"  - Total: {total_issues}")
    logger.info(f"  - With material linkage: {linked_issues}")
    logger.info(f"  - Linkage rate: {100 * linked_issues / total_issues if total_issues > 0 else 0:.1f}%")


if __name__ == "__main__":
    main()
