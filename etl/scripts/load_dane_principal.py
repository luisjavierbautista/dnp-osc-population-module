"""
ETL Script: Load DANE Principal Demographic Indicators

Loads principal demographic indicators from DCD-PrinInd-camDemNac-2018-2070_VP.xlsx:
- Life expectancy (male, female, total)
- Infant mortality rate
- Other demographic summary indicators

Coverage: 22 DANE regions, years 2018-2070

Usage:
    python etl/scripts/load_dane_principal.py

Source:
    etl/data/DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File path
PRINCIPAL_FILE = Path("/etl/data/DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx") if Path("/etl/data").exists() else Path(__file__).parent.parent / "data" / "DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx"

# Skip metadata rows
SKIP_ROWS = 9


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


def safe_decimal(value, default=None) -> Optional[Decimal]:
    """Safely convert value to Decimal"""
    if pd.isna(value):
        return default
    try:
        return Decimal(str(float(value)))
    except (ValueError, TypeError):
        return default


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
    """
    Load principal demographic indicators into dane_principal_indicators table

    Expected columns (may vary by sheet):
    - SIGLA (region code)
    - REGIÓN (region name)
    - AÑO (year)
    - ÁREA GEOGRÁFICA (area type)
    - Esperanza de vida (various columns for male/female/total)
    - Tasa de mortalidad infantil
    - Other demographic indicators

    Args:
        session: Database session
        df: DataFrame with principal indicators data
        batch_size: Number of records to commit at once

    Returns:
        Number of indicators loaded
    """
    logger.info("Loading DANE principal demographic indicators...")
    logger.info(f"DataFrame columns: {list(df.columns)}")

    count = 0
    batch_count = 0
    skipped_regions = set()

    for idx, row in df.iterrows():
        # Extract basic fields
        region_code = str(row.iloc[0]).strip()  # SIGLA
        year = int(row.iloc[2]) if pd.notna(row.iloc[2]) else None  # AÑO
        area_type = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "Total"

        if year is None:
            continue

        # Verify region exists
        if not verify_region_exists(session, region_code):
            if region_code not in skipped_regions:
                logger.warning(f"Region code '{region_code}' not found. Skipping.")
                skipped_regions.add(region_code)
            continue

        # Extract key indicators from row (column positions may vary - adapt as needed)
        # This is a flexible approach that collects all numeric columns into other_indicators
        other_indicators = {}

        # Try to extract common indicators from columns
        for col_idx, col_name in enumerate(df.columns):
            col_name_str = str(col_name).strip()

            # Skip metadata columns
            if col_idx < 4:  # Skip SIGLA, REGIÓN, AÑO, ÁREA
                continue

            # Get the value
            value = safe_float(row.iloc[col_idx])
            if value is not None:
                # Store with sanitized column name
                key = col_name_str.replace(' ', '_').lower()
                other_indicators[key] = value

        # Check if record already exists
        existing = session.exec(
            select(DanePrincipalIndicator).where(
                DanePrincipalIndicator.region_code == region_code,
                DanePrincipalIndicator.year == year
            )
        ).first()

        if not existing:
            indicator = DanePrincipalIndicator(
                region_code=region_code,
                year=year,
                area_type=area_type,
                life_exp_male=None,  # Will be set from other_indicators if available
                life_exp_female=None,
                life_exp_total=None,
                infant_mortality_rate=None,
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
                logger.debug(f"  Committed batch (total: {count})")
                batch_count = 0

    # Commit remaining
    if batch_count > 0:
        session.commit()

    logger.info(f"✓ Loaded {count} principal demographic indicators")
    if skipped_regions:
        logger.warning(f"Skipped regions: {sorted(skipped_regions)}")

    return count


def main():
    """Main ETL process"""
    logger.info("="*70)
    logger.info("DANE Principal Demographic Indicators ETL Script")
    logger.info("="*70)

    if not PRINCIPAL_FILE.exists():
        logger.error(f"File not found: {PRINCIPAL_FILE}")
        sys.exit(1)

    logger.info(f"Reading file: {PRINCIPAL_FILE}")

    # Try to read the Excel file - it may have multiple sheets
    try:
        xl_file = pd.ExcelFile(PRINCIPAL_FILE)
        logger.info(f"Available sheets: {xl_file.sheet_names}")

        # Use first sheet or a sheet with "Demografico" in the name
        sheet_name = xl_file.sheet_names[0]
        for sheet in xl_file.sheet_names:
            if 'demog' in sheet.lower() or 'indic' in sheet.lower():
                sheet_name = sheet
                break

        logger.info(f"Using sheet: {sheet_name}")
        df = pd.read_excel(PRINCIPAL_FILE, sheet_name=sheet_name, skiprows=SKIP_ROWS)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from Excel")

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        sys.exit(1)

    df = clean_dataframe(df)

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
            logger.info("="*70)

        except Exception as e:
            logger.error(f"Error during ETL: {e}", exc_info=True)
            session.rollback()
            raise


if __name__ == "__main__":
    main()
