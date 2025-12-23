"""
Initialize DANE indicators tables in the database

This script creates the necessary tables for storing DANE demographic indicators.

Usage:
    python -m app.db.init_dane_tables
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings
from app.models.dane_indicators import (
    DaneRegion,
    DaneDepartment,
    DaneMunicipality,
    DaneFertilityIndicator,
    DaneMigrationIndicator,
    DaneMortalityIndicator,
    DanePrincipalIndicator,
    DaneGrowthIndicator,
)


def init_db():
    """Create all DANE indicator tables"""
    print("Connecting to database...")
    print(f"Database URL: {settings.get_database_url()}")

    engine = create_engine(settings.get_database_url(), echo=True)

    print("\nCreating DANE indicator tables...")

    # Create all tables
    SQLModel.metadata.create_all(engine, tables=[
        DaneRegion.__table__,
        DaneDepartment.__table__,
        DaneMunicipality.__table__,
        DaneFertilityIndicator.__table__,
        DaneMigrationIndicator.__table__,
        DaneMortalityIndicator.__table__,
        DanePrincipalIndicator.__table__,
        DaneGrowthIndicator.__table__,
    ])

    print("\n✓ DANE indicator tables created successfully!")
    print("\nTables created:")
    print("  - dane_regions (dimension)")
    print("  - dane_departments (dimension)")
    print("  - dane_municipalities (dimension)")
    print("  - dane_fertility_indicators (fact)")
    print("  - dane_migration_indicators (fact)")
    print("  - dane_mortality_indicators (fact)")
    print("  - dane_principal_indicators (fact)")
    print("  - dane_growth_indicators (fact)")

    # Show sample data instructions
    print("\n" + "="*70)
    print("Next steps:")
    print("="*70)
    print("1. Load DANE regions data:")
    print("   python etl/scripts/load_dane_regions.py")
    print("\n2. Load fertility indicators:")
    print("   python etl/scripts/load_dane_fertility.py")
    print("\n3. Load migration indicators:")
    print("   python etl/scripts/load_dane_migration.py")
    print("\n4. Load mortality indicators:")
    print("   python etl/scripts/load_dane_mortality.py")
    print("\n5. Load principal indicators:")
    print("   python etl/scripts/load_dane_principal.py")
    print("\n6. Load growth indicators:")
    print("   python etl/scripts/load_dane_growth.py")
    print("="*70)


if __name__ == "__main__":
    init_db()
