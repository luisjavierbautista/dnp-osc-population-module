"""
ETL Script: Fix and Reload DANE Mortality Indicators

This script correctly loads mortality data with proper column parsing.
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
from typing import Dict

from app.core.config import settings
from app.models.dane_indicators import DaneMortalityIndicator, DaneRegion

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File configuration
MORTALITY_FILE = Path("/etl/data/DCD-Mor-EstSexNal-Reg-2018-2070_VP.xlsx")
SHEET_NAME = 'Mortalidad'
SKIP_ROWS = 9  # Correct value found by inspection
AGE_MIN = 0
AGE_MAX = 100

def extract_age_mortality_rates(row: pd.Series, age_min: int, age_max: int) -> Dict[str, float]:
    """
    Extract age-specific mortality rates from a row.
    Ages are numeric column indices (5 onwards)
    """
    age_rates = {}

    # The age columns start at column index 5 (after SIGLA, TERRITORIO, AÑO, Área, Sexo)
    for age in range(age_min, age_max + 1):
        col_idx = 5 + age  # Age 0 is at column 5, age 1 at column 6, etc.

        if col_idx < len(row):
            value = row.iloc[col_idx]
            if pd.notna(value):
                try:
                    age_rates[str(age)] = float(value)
                except (ValueError, TypeError):
                    pass

    return age_rates


def verify_region_exists(session: Session, region_code: str) -> bool:
    """Verify that a region code exists in dane_regions table"""
    region = session.exec(
        select(DaneRegion).where(DaneRegion.region_code == region_code)
    ).first()
    return region is not None


def load_mortality_indicators(session: Session, df: pd.DataFrame, batch_size: int = 100) -> int:
    """Load mortality indicators with correct column parsing"""
    logger.info("Loading DANE mortality indicators with fixed ETL...")
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"First 8 columns: {list(df.columns[:8])}")

    # Delete existing data
    logger.info("Clearing existing mortality data...")
    session.exec(select(DaneMortalityIndicator)).all()
    session.query(DaneMortalityIndicator).delete()
    session.commit()
    logger.info("✓ Existing data cleared")

    count = 0
    batch_count = 0
    skipped_regions = set()

    for idx, row in df.iterrows():
        # Skip invalid rows early
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[2]) or pd.isna(row.iloc[4]):
            continue

        # Extract fields
        region_code = str(row.iloc[0]).strip()  # SIGLA DE LA REGIÓN

        try:
            year = int(row.iloc[2])  # AÑO
        except (ValueError, TypeError):
            continue

        area_type = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "Total"  # Área Geográfica
        sex = str(row.iloc[4]).strip()  # Sexo

        # Verify region exists
        if not verify_region_exists(session, region_code):
            if region_code not in skipped_regions:
                logger.warning(f"Region code '{region_code}' not found. Skipping.")
                skipped_regions.add(region_code)
            continue

        # Extract age-specific mortality rates (columns 5 onwards)
        age_mortality_rates = extract_age_mortality_rates(row, AGE_MIN, AGE_MAX)

        if not age_mortality_rates:
            logger.warning(f"No mortality rates found for {region_code} {year} {sex}")
            continue

        # Create indicator
        indicator = DaneMortalityIndicator(
            region_code=region_code,
            year=year,
            area_type=area_type,
            sex=sex,
            age_mortality_rates=age_mortality_rates,
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

    logger.info(f"✓ Loaded {count} mortality indicators")
    if skipped_regions:
        logger.warning(f"Skipped regions: {sorted(skipped_regions)}")

    return count


def main():
    logger.info("="*70)
    logger.info("DANE Mortality Indicators - FIX & RELOAD")
    logger.info("="*70)

    if not MORTALITY_FILE.exists():
        logger.error(f"File not found: {MORTALITY_FILE}")
        sys.exit(1)

    logger.info(f"Reading file: {MORTALITY_FILE}")
    logger.info(f"Sheet: {SHEET_NAME}, Skip rows: {SKIP_ROWS}")

    try:
        df = pd.read_excel(MORTALITY_FILE, sheet_name=SHEET_NAME, skiprows=SKIP_ROWS)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from Excel")
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        sys.exit(1)

    logger.info(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    with Session(engine) as session:
        try:
            indicators_count = load_mortality_indicators(session, df)

            logger.info("="*70)
            logger.info("✓ ETL Complete!")
            logger.info("="*70)
            logger.info(f"Summary:")
            logger.info(f"  - Mortality indicators loaded: {indicators_count}")
            logger.info(f"  - Years: 2018-2070")
            logger.info(f"  - Age range: {AGE_MIN}-{AGE_MAX}")

        except Exception as e:
            logger.error(f"Error during ETL: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
