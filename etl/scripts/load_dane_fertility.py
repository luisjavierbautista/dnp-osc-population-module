"""
ETL Script: Load DANE Fertility Indicators

Loads fertility indicators from DCD-Fec-EstNal-Reg-2018-2070_VP.xlsx:
- TGF (Tasa Global de Fecundidad / Total Fertility Rate)
- Age-specific fertility rates (ages 10-49)

Coverage: 22-23 DANE regions, years 2018-2070

Usage:
    python etl/scripts/load_dane_fertility.py

Source:
    etl/data/DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx
"""

import sys
from pathlib import Path

# Add backend to path - works both in Docker and locally
backend_path = Path("/app") if Path("/app/app").exists() else Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

import pandas as pd
import logging
from sqlmodel import Session, create_engine, select
from datetime import datetime
from decimal import Decimal
from typing import Dict

from app.core.config import settings
from app.models.dane_indicators import DaneFertilityIndicator, DaneRegion

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File path - works both in Docker (/etl) and locally (relative path)
FERTILITY_FILE = Path("/etl/data/DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx") if Path("/etl/data").exists() else Path(__file__).parent.parent / "data" / "DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx"

# Sheet name
SHEET_NAME = "Fecundidad"

# Skip metadata rows
SKIP_ROWS = 9

# Age range for fertility (10-49 years)
AGE_MIN = 10
AGE_MAX = 49


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the DataFrame by removing metadata rows

    Args:
        df: Raw DataFrame from Excel

    Returns:
        Cleaned DataFrame with actual data
    """
    # Remove rows that contain metadata keywords in first column
    exclude_keywords = ['Actualizado', 'Fuente:', 'ESTIMACIONES', 'AÑO', 'SIGLA']

    mask = pd.Series([True] * len(df))
    for keyword in exclude_keywords:
        mask = mask & (~df.iloc[:, 0].astype(str).str.contains(keyword, case=False, na=False))

    # Also remove rows where region code (SIGLA) is NaN
    mask = mask & df.iloc[:, 0].notna()

    cleaned_df = df[mask].reset_index(drop=True)
    logger.info(f"Cleaned DataFrame: {len(df)} → {len(cleaned_df)} rows")

    return cleaned_df


def extract_age_rates(row: pd.Series, age_min: int, age_max: int) -> Dict[str, float]:
    """
    Extract age-specific fertility rates from a row into JSON format

    Args:
        row: DataFrame row
        age_min: Minimum age (10)
        age_max: Maximum age (49)

    Returns:
        Dictionary of {age: rate} pairs
    """
    age_rates = {}

    for age in range(age_min, age_max + 1):
        # Column names might be just numbers or have prefixes
        # Try different column name patterns
        possible_cols = [str(age), f"age_{age}", f"{age}"]

        rate_value = None
        for col in possible_cols:
            if col in row.index:
                rate_value = row[col]
                break

        # If we found a value and it's not NaN, add it
        if rate_value is not None and pd.notna(rate_value):
            age_rates[str(age)] = float(rate_value)

    return age_rates


def verify_region_exists(session: Session, region_code: str) -> bool:
    """
    Verify that a region code exists in dane_regions table

    Args:
        session: Database session
        region_code: Region code to check

    Returns:
        True if region exists, False otherwise
    """
    region = session.exec(
        select(DaneRegion).where(DaneRegion.region_code == region_code)
    ).first()

    return region is not None


def load_fertility_indicators(session: Session, df: pd.DataFrame, batch_size: int = 100) -> int:
    """
    Load fertility indicators into dane_fertility_indicators table

    Args:
        session: Database session
        df: DataFrame with fertility data
        batch_size: Number of records to commit at once

    Returns:
        Number of indicators loaded
    """
    logger.info("Loading DANE fertility indicators...")

    count = 0
    batch_count = 0
    skipped_regions = set()

    for idx, row in df.iterrows():
        # Extract fields
        region_code = str(row.iloc[0]).strip()  # SIGLA column
        year = int(row.iloc[2])  # AÑO column
        area_type = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "Total"  # ÁREA GEOGRÁFICA
        tgf = float(row.iloc[4])  # TGF column

        # Verify region exists
        if not verify_region_exists(session, region_code):
            if region_code not in skipped_regions:
                logger.warning(f"Region code '{region_code}' not found in dane_regions table. Skipping records for this region.")
                skipped_regions.add(region_code)
            continue

        # Extract age-specific rates
        age_rates = extract_age_rates(row, AGE_MIN, AGE_MAX)

        # Check if record already exists
        existing = session.exec(
            select(DaneFertilityIndicator).where(
                DaneFertilityIndicator.region_code == region_code,
                DaneFertilityIndicator.year == year
            )
        ).first()

        if not existing:
            indicator = DaneFertilityIndicator(
                region_code=region_code,
                year=year,
                area_type=area_type,
                tgf=Decimal(str(tgf)),
                age_rates=age_rates,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(indicator)
            count += 1
            batch_count += 1

            # Commit in batches
            if batch_count >= batch_size:
                session.commit()
                logger.debug(f"  Committed batch of {batch_count} records (total: {count})")
                batch_count = 0

    # Commit remaining records
    if batch_count > 0:
        session.commit()
        logger.debug(f"  Committed final batch of {batch_count} records")

    logger.info(f"✓ Loaded {count} fertility indicators")
    if skipped_regions:
        logger.warning(f"Skipped {len(skipped_regions)} regions not found in dane_regions: {sorted(skipped_regions)}")

    return count


def main():
    """Main ETL process"""
    logger.info("="*70)
    logger.info("DANE Fertility Indicators ETL Script")
    logger.info("="*70)

    # Check if file exists
    if not FERTILITY_FILE.exists():
        logger.error(f"File not found: {FERTILITY_FILE}")
        sys.exit(1)

    # Read Excel file
    logger.info(f"Reading file: {FERTILITY_FILE}")
    logger.info(f"Sheet: {SHEET_NAME}, Skip rows: {SKIP_ROWS}")

    try:
        df = pd.read_excel(FERTILITY_FILE, sheet_name=SHEET_NAME, skiprows=SKIP_ROWS)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from Excel")
        logger.debug(f"Columns: {list(df.columns)[:10]}...")  # Show first 10 columns

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        sys.exit(1)

    # Clean data
    df = clean_dataframe(df)

    # Connect to database
    logger.info(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    # Load data
    with Session(engine) as session:
        try:
            indicators_count = load_fertility_indicators(session, df)

            logger.info("="*70)
            logger.info("✓ ETL Complete!")
            logger.info("="*70)
            logger.info(f"Summary:")
            logger.info(f"  - Fertility indicators loaded: {indicators_count}")
            logger.info(f"  - Years covered: 2018-2070")
            logger.info(f"  - Age range: {AGE_MIN}-{AGE_MAX}")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"Error during ETL: {e}", exc_info=True)
            session.rollback()
            raise


if __name__ == "__main__":
    main()
