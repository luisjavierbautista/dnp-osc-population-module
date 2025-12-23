"""
ETL Script: Load DANE Mortality Indicators

Loads mortality indicators from DCD-Mor-EstSexNal-Reg-2018-2070_VP.xlsx:
- Probability of death (qx) by age
- By sex (Hombres, Mujeres)

Coverage: 22 DANE regions, years 2018-2070, ages 0-100+

Usage:
    python etl/scripts/load_dane_mortality.py

Source:
    etl/data/DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File path
MORTALITY_FILE = Path("/etl/data/DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx") if Path("/etl/data").exists() else Path(__file__).parent.parent / "data" / "DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx"

# Sheet name
SHEET_NAME = "Mortalidad"

# Skip metadata rows
SKIP_ROWS = 9

# Age range (0-100+)
AGE_MIN = 0
AGE_MAX = 100


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame by removing metadata rows"""
    exclude_keywords = ['Actualizado', 'Fuente:', 'ESTIMACIONES', 'AÑO', 'SIGLA']

    mask = pd.Series([True] * len(df))
    for keyword in exclude_keywords:
        mask = mask & (~df.iloc[:, 0].astype(str).str.contains(keyword, case=False, na=False))

    mask = mask & df.iloc[:, 0].notna()
    cleaned_df = df[mask].reset_index(drop=True)

    logger.info(f"Cleaned DataFrame: {len(df)} → {len(cleaned_df)} rows")
    return cleaned_df


def extract_age_mortality_rates(row: pd.Series, age_min: int, age_max: int) -> Dict[str, float]:
    """
    Extract age-specific mortality rates (qx) from a row into JSON format

    Args:
        row: DataFrame row
        age_min: Minimum age (0)
        age_max: Maximum age (100)

    Returns:
        Dictionary of {age: mortality_rate} pairs
    """
    age_rates = {}

    for age in range(age_min, age_max + 1):
        # Try different column name patterns
        possible_cols = [str(age), f"age_{age}", f"{age}"]

        rate = None
        for col in possible_cols:
            if col in row.index:
                rate = row[col]
                break

        # If we found a value and it's not NaN, add it
        if rate is not None and pd.notna(rate):
            age_rates[str(age)] = float(rate)

    return age_rates


def verify_region_exists(session: Session, region_code: str) -> bool:
    """Verify that a region code exists in dane_regions table"""
    region = session.exec(
        select(DaneRegion).where(DaneRegion.region_code == region_code)
    ).first()
    return region is not None


def load_mortality_indicators(session: Session, df: pd.DataFrame, batch_size: int = 100) -> int:
    """
    Load mortality indicators into dane_mortality_indicators table

    Args:
        session: Database session
        df: DataFrame with mortality data
        batch_size: Number of records to commit at once

    Returns:
        Number of indicators loaded
    """
    logger.info("Loading DANE mortality indicators...")

    count = 0
    batch_count = 0
    skipped_regions = set()

    for idx, row in df.iterrows():
        # Extract fields (column positions based on schema analysis)
        region_code = str(row.iloc[0]).strip()  # SIGLA
        year = int(row.iloc[2])  # AÑO
        area_type = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "Total"  # ÁREA
        sex = str(row.iloc[4]).strip()  # SEXO (Hombres/Mujeres)

        # Verify region exists
        if not verify_region_exists(session, region_code):
            if region_code not in skipped_regions:
                logger.warning(f"Region code '{region_code}' not found. Skipping.")
                skipped_regions.add(region_code)
            continue

        # Extract age-specific mortality rates
        age_mortality_rates = extract_age_mortality_rates(row, AGE_MIN, AGE_MAX)

        # Check if record already exists
        existing = session.exec(
            select(DaneMortalityIndicator).where(
                DaneMortalityIndicator.region_code == region_code,
                DaneMortalityIndicator.year == year,
                DaneMortalityIndicator.sex == sex
            )
        ).first()

        if not existing:
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
                logger.debug(f"  Committed batch (total: {count})")
                batch_count = 0

    # Commit remaining
    if batch_count > 0:
        session.commit()

    logger.info(f"✓ Loaded {count} mortality indicators")
    if skipped_regions:
        logger.warning(f"Skipped regions: {sorted(skipped_regions)}")

    return count


def main():
    """Main ETL process"""
    logger.info("="*70)
    logger.info("DANE Mortality Indicators ETL Script")
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

    df = clean_dataframe(df)

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
            logger.info(f"  - Dimensions: Sex (2 per year/region)")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"Error during ETL: {e}", exc_info=True)
            session.rollback()
            raise


if __name__ == "__main__":
    main()
