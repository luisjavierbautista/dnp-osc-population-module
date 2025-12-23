"""
ETL Script: Load DANE Regions, Departments, and Municipalities

Loads reference/dimension data from Regiones DANE.xlsx into PostgreSQL:
- dane_regions: 22-23 DANE population regions
- dane_departments: 33 Colombian departments
- dane_municipalities: 1,122+ Colombian municipalities with region mappings

Usage:
    python etl/scripts/load_dane_regions.py

Source:
    /home/luisjavier/Downloads/Regiones DANE.xlsx
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

from app.core.config import settings
from app.models.dane_indicators import (
    DaneRegion,
    DaneDepartment,
    DaneMunicipality,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# File path - works both in Docker (/etl) and locally (relative path)
REGIONS_FILE = Path("/etl/data/Regiones DANE.xlsx") if Path("/etl/data").exists() else Path(__file__).parent.parent / "data" / "Regiones DANE.xlsx"


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the DataFrame by removing metadata rows

    Args:
        df: Raw DataFrame from Excel

    Returns:
        Cleaned DataFrame with actual data
    """
    # Remove rows that contain metadata keywords
    exclude_keywords = ['Actualizado', 'Fuente:', 'SIGLA', 'REGION', 'ÁREA']

    mask = pd.Series([True] * len(df))
    for keyword in exclude_keywords:
        # Check if first column contains the keyword
        mask = mask & (~df.iloc[:, 0].astype(str).str.contains(keyword, case=False, na=False))

    # Also remove rows where region code (SIGLA) is NaN
    mask = mask & df.iloc[:, 0].notna()

    cleaned_df = df[mask].reset_index(drop=True)
    logger.info(f"Cleaned DataFrame: {len(df)} → {len(cleaned_df)} rows")

    return cleaned_df


def load_dane_regions(session: Session, df: pd.DataFrame) -> int:
    """
    Load DANE regions into dane_regions table

    Args:
        session: Database session
        df: DataFrame with regions data

    Returns:
        Number of regions loaded
    """
    logger.info("Loading DANE regions...")

    # Get unique regions from the DataFrame (SIGLA and REGIÓN columns)
    regions_data = df[['SIGLA', 'REGIÓN']].drop_duplicates()

    count = 0
    for _, row in regions_data.iterrows():
        region_code = str(row['SIGLA']).strip()
        region_name = str(row['REGIÓN']).strip()

        # Check if region already exists
        existing = session.exec(
            select(DaneRegion).where(DaneRegion.region_code == region_code)
        ).first()

        if not existing:
            region = DaneRegion(
                region_code=region_code,
                region_name=region_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(region)
            count += 1
            logger.debug(f"  Added region: {region_code} - {region_name}")

    session.commit()
    logger.info(f"✓ Loaded {count} regions")

    return count


def load_dane_departments(session: Session, df: pd.DataFrame) -> int:
    """
    Load Colombian departments into dane_departments table

    Args:
        session: Database session
        df: DataFrame with departments data

    Returns:
        Number of departments loaded
    """
    logger.info("Loading DANE departments...")

    # Get unique departments (DP and DPNOM columns)
    depts_data = df[['DP', 'DPNOM']].drop_duplicates()

    count = 0
    for _, row in depts_data.iterrows():
        dept_code = str(row['DP']).strip()
        dept_name = str(row['DPNOM']).strip()

        # Check if department already exists
        existing = session.exec(
            select(DaneDepartment).where(DaneDepartment.dept_code == dept_code)
        ).first()

        if not existing:
            dept = DaneDepartment(
                dept_code=dept_code,
                dept_name=dept_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(dept)
            count += 1
            logger.debug(f"  Added department: {dept_code} - {dept_name}")

    session.commit()
    logger.info(f"✓ Loaded {count} departments")

    return count


def load_dane_municipalities(session: Session, df: pd.DataFrame) -> int:
    """
    Load Colombian municipalities into dane_municipalities table
    with mappings to departments and regions

    Args:
        session: Database session
        df: DataFrame with municipalities data

    Returns:
        Number of municipalities loaded
    """
    logger.info("Loading DANE municipalities...")

    # Get unique municipalities (ignore area_type - we just need municipality-region mapping)
    munis_data = df[['MPIO', 'DPMP', 'DP', 'SIGLA']].drop_duplicates(subset=['MPIO'])

    count = 0
    for _, row in munis_data.iterrows():
        muni_code = str(row['MPIO']).strip()
        muni_name = str(row['DPMP']).strip()
        dept_code = str(row['DP']).strip()
        region_code = str(row['SIGLA']).strip()

        # Check if municipality already exists
        existing = session.exec(
            select(DaneMunicipality).where(DaneMunicipality.muni_code == muni_code)
        ).first()

        if not existing:
            muni = DaneMunicipality(
                muni_code=muni_code,
                muni_name=muni_name,
                dept_code=dept_code,
                region_code=region_code,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(muni)
            count += 1

            if count % 100 == 0:
                logger.debug(f"  Processed {count} municipalities...")

    session.commit()
    logger.info(f"✓ Loaded {count} municipalities")

    return count


def main():
    """Main ETL process"""
    logger.info("="*70)
    logger.info("DANE Regions ETL Script")
    logger.info("="*70)

    # Check if file exists
    if not REGIONS_FILE.exists():
        logger.error(f"File not found: {REGIONS_FILE}")
        sys.exit(1)

    # Read Excel file
    logger.info(f"Reading file: {REGIONS_FILE}")
    try:
        df = pd.read_excel(REGIONS_FILE, skiprows=9)  # Skip metadata rows
        logger.info(f"Loaded {len(df)} rows from Excel")

        # Rename columns for easier access
        df.columns = ['SIGLA', 'REGIÓN', 'DP', 'DPNOM', 'MPIO', 'DPMP', 'ÁREA GEOGRÁFICA']

    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        sys.exit(1)

    # Clean data
    df = clean_dataframe(df)

    # Connect to database
    logger.info(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)

    # Load data
    with Session(engine) as session:
        try:
            # Load in order (respecting foreign keys)
            regions_count = load_dane_regions(session, df)
            depts_count = load_dane_departments(session, df)
            munis_count = load_dane_municipalities(session, df)

            logger.info("="*70)
            logger.info("✓ ETL Complete!")
            logger.info("="*70)
            logger.info(f"Summary:")
            logger.info(f"  - Regions:        {regions_count}")
            logger.info(f"  - Departments:    {depts_count}")
            logger.info(f"  - Municipalities: {munis_count}")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"Error during ETL: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    main()
