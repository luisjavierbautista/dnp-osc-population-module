"""
ETL Script: Fix and Reload DANE Principal Demographic Indicators

This script correctly loads principal indicators with proper column parsing.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path("/app") if Path("/app/app").exists() else Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

import pandas as pd
import logging
from sqlmodel import Session, create_engine, select
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from app.core.config import settings
from app.models.dane_indicators import DanePrincipalIndicator, DaneRegion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File configuration
PRINCIPAL_FILE = Path("/etl/data/DCD-PrinInd-camDemNac-2018-2070_VP.xlsx")
SHEET_NAME = 'Cambio Demográfico'
SKIP_ROWS = 7  # Correct value found by inspection

def safe_float(value, default=None) -> Optional[float]:
    """Safely convert value to float"""
    if pd.isna(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def verify_region_exists(session: Session, region_code: str) -> bool:
    """Verify that a region code exists in dane_regions table"""
    region = session.exec(
        select(DaneRegion).where(DaneRegion.region_code == region_code)
    ).first()
    return region is not None


def load_principal_indicators(session: Session, df: pd.DataFrame, batch_size: int = 100) -> int:
    """Load principal indicators with correct column parsing"""
    logger.info("Loading DANE principal demographic indicators with fixed ETL...")
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")

    # Delete existing data
    logger.info("Clearing existing principal indicators data...")
    session.query(DanePrincipalIndicator).delete()
    session.commit()
    logger.info("✓ Existing data cleared")

    count = 0
    batch_count = 0
    skipped_regions = set()
    skipped_duplicate_headers = 0

    for idx, row in df.iterrows():
        # Extract basic fields using column names
        region_code = str(row['SIGLA DE LA REGIÓN']).strip() if pd.notna(row['SIGLA DE LA REGIÓN']) else None
        year_val = row['AÑO']

        # Skip invalid rows (missing year or header rows)
        if pd.isna(year_val) or str(year_val).strip() == 'AÑO':
            skipped_duplicate_headers += 1
            continue

        # Try to convert to int
        try:
            year = int(float(year_val))  # Convert float to int
        except (ValueError, TypeError):
            skipped_duplicate_headers += 1
            continue
        area_type = str(row['Área Geográfica']).strip() if pd.notna(row['Área Geográfica']) else "Total"

        if not region_code:
            continue

        # Verify region exists
        if not verify_region_exists(session, region_code):
            if region_code not in skipped_regions:
                logger.warning(f"Region code '{region_code}' not found. Skipping.")
                skipped_regions.add(region_code)
            continue

        # Extract specific indicators
        life_exp_total = safe_float(row.get('Esperanza_vida_al nacer'))
        life_exp_male = safe_float(row.get('Esperanza_vida al nacer_hombres'))
        life_exp_female = safe_float(row.get('Esperanza_vida_al nacer mujeres'))
        infant_mortality_rate = safe_float(row.get('Tasa_mortalidad_infantil por mil hab.'))

        # Collect other indicators
        other_indicators = {}
        indicator_columns = [
            'Esperanza_vida_al nacer',
            'Esperanza_vida al nacer_hombres',
            'Esperanza_vida_al nacer mujeres',
            'Tasa_mortalidad_infantil por mil hab.',
            'Tasa_mortalidad_infantil_hombres por mil hab.',
            'Tasa_mortalidad_infantil_mujeres por mil hab.',
            'Tasa_fecundidad_edad simple',
            'Diferencial por sexo_(e0)',
            'Hombres/Mujeres_(TMI)'
        ]

        for col in indicator_columns:
            if col in row.index:
                value = safe_float(row[col])
                if value is not None:
                    # Create clean key name
                    key = col.replace(' ', '_').replace('_(', '_').replace(')', '').replace('/', '_').lower()
                    other_indicators[key] = value

        # Create indicator
        indicator = DanePrincipalIndicator(
            region_code=region_code,
            year=year,
            area_type=area_type,
            life_exp_male=life_exp_male,
            life_exp_female=life_exp_female,
            life_exp_total=life_exp_total,
            infant_mortality_rate=infant_mortality_rate,
            other_indicators=other_indicators,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(indicator)
        count += 1
        batch_count += 1

        # Commit in batches
        if batch_count >= batch_size:
            session.commit()
            logger.info(f"  Committed batch (total: {count})")
            batch_count = 0

    # Commit remaining
    if batch_count > 0:
        session.commit()

    logger.info(f"✓ Loaded {count} principal demographic indicators")
    logger.info(f"  Skipped {skipped_duplicate_headers} duplicate header rows")
    if skipped_regions:
        logger.warning(f"Skipped regions: {sorted(skipped_regions)}")

    return count


def main():
    logger.info("="*70)
    logger.info("DANE Principal Demographic Indicators - FIX & RELOAD")
    logger.info("="*70)

    if not PRINCIPAL_FILE.exists():
        logger.error(f"File not found: {PRINCIPAL_FILE}")
        sys.exit(1)

    logger.info(f"Reading file: {PRINCIPAL_FILE}")
    logger.info(f"Sheet: {SHEET_NAME}, Skip rows: {SKIP_ROWS}")

    try:
        df = pd.read_excel(PRINCIPAL_FILE, sheet_name=SHEET_NAME, skiprows=SKIP_ROWS)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from Excel")
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        sys.exit(1)

    logger.info(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    with Session(engine) as session:
        try:
            indicators_count = load_principal_indicators(session, df)

            logger.info("="*70)
            logger.info("✓ ETL Complete!")
            logger.info("="*70)
            logger.info(f"Summary:")
            logger.info(f"  - Principal indicators loaded: {indicators_count}")
            logger.info(f"  - Years: 2018-2070")

        except Exception as e:
            logger.error(f"Error during ETL: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
