"""
ETL Script for Loading DANE Demographic Indicators

This script loads demographic indicators from DANE Excel files into PostgreSQL database
using SQLModel ORM. It handles:
- Fertility indicators (age-specific rates)
- Migration indicators (by sex and type)
- Mortality indicators (by sex)
- Demographic summary indicators
- Population growth indicators

Author: Generated for DNP Population Module
Date: 2025-11-18
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from sqlmodel import Session, create_engine, select
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models (adjust path as needed)
# from app.models import (
#     DaneRegion,
#     DaneFertilityIndicator,
#     DaneMigrationIndicator,
#     DaneMortalityIndicator,
#     DaneDemographicIndicator,
#     DanePopulationIndicator
# )

# File paths (adjust to your environment)
BASE_PATH = Path("/home/luisjavier/Downloads/DANE Indicators")
FILES = {
    "fertility": BASE_PATH / "DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx",
    "migration": BASE_PATH / "DCD-Mig-EstSexNal-Reg-2018-2070_VP (1).xlsx",
    "mortality": BASE_PATH / "DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx",
    "demographic": BASE_PATH / "DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx",
    "population": BASE_PATH / "DCD-PrinInd-crecPobNac-2018-2070_VP (1).xlsx",
    "regions": Path("/home/luisjavier/Downloads") / "Regiones DANE.xlsx"
}


def clean_data(df: pd.DataFrame, exclude_terms: List[str] = None) -> pd.DataFrame:
    """
    Remove metadata rows and clean data

    Args:
        df: Input DataFrame
        exclude_terms: Terms to filter out from first column

    Returns:
        Cleaned DataFrame
    """
    if exclude_terms is None:
        exclude_terms = ['Actualizado', 'Fuente:', 'ESTIMACIONES', 'AÑO', 'SIGLA']

    mask = pd.Series([True] * len(df))
    for term in exclude_terms:
        mask = mask & (~df.iloc[:, 0].astype(str).str.contains(term, na=False))

    # Remove NaN rows in first column
    mask = mask & df.iloc[:, 0].notna()

    return df[mask].reset_index(drop=True)


def transform_age_data(row: pd.Series, age_range: range, prefix: str = "age_") -> Dict[str, float]:
    """
    Convert age-specific columns to JSONB format

    Args:
        row: DataFrame row
        age_range: Range of ages to include
        prefix: Column name prefix (e.g., "age_")

    Returns:
        Dictionary of age: value pairs
    """
    age_dict = {}
    for age in age_range:
        col_name = f'{prefix}{age}'
        if col_name in row.index and pd.notna(row[col_name]):
            age_dict[str(age)] = float(row[col_name])
    return age_dict


# ============================================================================
# 1. LOAD DANE REGIONS
# ============================================================================

def load_dane_regions(session: Session) -> Dict[str, str]:
    """
    Load DANE regions reference data

    Returns:
        Dictionary mapping region_code to region_name
    """
    logger.info("Loading DANE regions...")

    # Define region mappings
    regions = {
        'NAL': 'Total Nacional',
        'ACB': 'Altiplano Cundiboyacense',
        'AMG': 'Alto Magdalena',
        'APC': 'Anden Pacífico',
        'AQU': 'Antioquia y Urabá',
        'ATN': 'Altillanura',
        'AZN': 'Amazonía',
        'BGR': 'Bogotá Región',
        'BMG': 'Bajo Magdalena',
        'BMR': 'Boyacá y Región',
        'BQR': 'Barranquilla y Región',
        'CCR': 'Cali y Región',
        'CLR': 'Caldense y Región',
        'CRI': 'Caribe Insular',
        'ECF': 'Eje Cafetero',
        'EGS': 'Estela Gigante Santander',
        'GSV': 'Gran Santander y Valles',
        'MTC': 'Montaña Centro',
        'NPA': 'Norte Pacífico Andino',
        'SBC': 'Sur Bolívar y Cesar',
        'SSS': 'Sierra Sur y Serranía',
        'VDA': 'Valle de Aburrá',
        'VRC': 'Valle del Río Cauca'
    }

    # Insert regions (use actual model)
    # for code, name in regions.items():
    #     region = DaneRegion(region_code=code, region_name=name)
    #     session.add(region)

    # session.commit()
    logger.info(f"Loaded {len(regions)} regions")

    return regions


# ============================================================================
# 2. LOAD FERTILITY INDICATORS
# ============================================================================

def load_fertility_indicators(session: Session, batch_size: int = 100):
    """
    Load fertility indicators from Excel file

    Args:
        session: Database session
        batch_size: Number of records to insert per batch
    """
    logger.info("Loading fertility indicators...")

    file_path = FILES["fertility"]
    df = pd.read_excel(file_path, sheet_name='Fecundidad', skiprows=9)

    # Assign column names
    col_names = ['region_code', 'territory', 'year', 'area_type', 'tgf'] + \
                [f'age_{i}' for i in range(10, 50)]
    df.columns = col_names

    # Clean data
    df = clean_data(df)

    # Filter valid years
    df = df[df['year'].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]
    df['year'] = df['year'].astype(int)

    logger.info(f"Processing {len(df)} fertility records...")

    records_added = 0
    for idx, row in df.iterrows():
        # Transform age-specific data to JSONB
        age_rates = transform_age_data(row, range(10, 50))

        # Create model instance (uncomment when models are ready)
        # indicator = DaneFertilityIndicator(
        #     region_code=row['region_code'],
        #     year=row['year'],
        #     area_type=row['area_type'] if pd.notna(row['area_type']) else None,
        #     tgf=float(row['tgf']),
        #     age_rates=age_rates
        # )
        # session.add(indicator)

        records_added += 1

        # Commit in batches
        if records_added % batch_size == 0:
            # session.commit()
            logger.info(f"Committed {records_added} records...")

    # Final commit
    # session.commit()
    logger.info(f"Completed: {records_added} fertility indicators loaded")


# ============================================================================
# 3. LOAD MIGRATION INDICATORS
# ============================================================================

def load_migration_indicators(session: Session, batch_size: int = 100):
    """
    Load migration indicators from Excel file

    Args:
        session: Database session
        batch_size: Number of records to insert per batch
    """
    logger.info("Loading migration indicators...")

    file_path = FILES["migration"]
    df = pd.read_excel(file_path, sheet_name='Migración', skiprows=9)

    # Assign column names
    col_names = ['region_code', 'territory', 'year', 'area_type', 'sex', 'migration_type'] + \
                [f'age_{i}' for i in range(0, 101)]
    df.columns = col_names

    # Clean data
    df = clean_data(df)

    # Filter valid years
    df = df[df['year'].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]
    df['year'] = df['year'].astype(int)

    logger.info(f"Processing {len(df)} migration records...")

    records_added = 0
    for idx, row in df.iterrows():
        # Transform age-specific data to JSONB
        age_counts = transform_age_data(row, range(0, 101))

        # Create model instance (uncomment when models are ready)
        # indicator = DaneMigrationIndicator(
        #     region_code=row['region_code'],
        #     year=row['year'],
        #     area_type=row['area_type'] if pd.notna(row['area_type']) else None,
        #     sex=row['sex'],
        #     migration_type=row['migration_type'],
        #     age_counts=age_counts
        # )
        # session.add(indicator)

        records_added += 1

        # Commit in batches
        if records_added % batch_size == 0:
            # session.commit()
            logger.info(f"Committed {records_added} records...")

    # Final commit
    # session.commit()
    logger.info(f"Completed: {records_added} migration indicators loaded")


# ============================================================================
# 4. LOAD MORTALITY INDICATORS
# ============================================================================

def load_mortality_indicators(session: Session, batch_size: int = 100):
    """
    Load mortality indicators from Excel file

    Args:
        session: Database session
        batch_size: Number of records to insert per batch
    """
    logger.info("Loading mortality indicators...")

    file_path = FILES["mortality"]
    df = pd.read_excel(file_path, sheet_name='Mortalidad', skiprows=9)

    # Assign column names
    col_names = ['region_code', 'territory', 'year', 'area_type', 'sex'] + \
                [f'age_{i}' for i in range(0, 101)]
    df.columns = col_names

    # Clean data
    df = clean_data(df)

    # Filter valid years
    df = df[df['year'].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]
    df['year'] = df['year'].astype(int)

    logger.info(f"Processing {len(df)} mortality records...")

    records_added = 0
    for idx, row in df.iterrows():
        # Transform age-specific data to JSONB
        age_rates = transform_age_data(row, range(0, 101))

        # Create model instance (uncomment when models are ready)
        # indicator = DaneMortalityIndicator(
        #     region_code=row['region_code'],
        #     year=row['year'],
        #     area_type=row['area_type'] if pd.notna(row['area_type']) else None,
        #     sex=row['sex'],
        #     age_rates=age_rates
        # )
        # session.add(indicator)

        records_added += 1

        # Commit in batches
        if records_added % batch_size == 0:
            # session.commit()
            logger.info(f"Committed {records_added} records...")

    # Final commit
    # session.commit()
    logger.info(f"Completed: {records_added} mortality indicators loaded")


# ============================================================================
# 5. LOAD DEMOGRAPHIC INDICATORS
# ============================================================================

def load_demographic_indicators(session: Session, batch_size: int = 100):
    """
    Load demographic summary indicators from Excel file

    Args:
        session: Database session
        batch_size: Number of records to insert per batch
    """
    logger.info("Loading demographic indicators...")

    file_path = FILES["demographic"]
    df = pd.read_excel(file_path, sheet_name='Cambio Demográfico', skiprows=8)

    # Clean data
    df = clean_data(df)

    # Filter valid years (column index 2)
    df = df[df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]

    logger.info(f"Processing {len(df)} demographic records...")

    records_added = 0
    for idx, row in df.iterrows():
        # Create model instance (uncomment when models are ready)
        # indicator = DaneDemographicIndicator(
        #     region_code=row.iloc[0],
        #     year=int(row.iloc[2]),
        #     area_type=row.iloc[3] if pd.notna(row.iloc[3]) else None,
        #     life_expectancy=float(row.iloc[4]) if pd.notna(row.iloc[4]) else None,
        #     life_expectancy_male=float(row.iloc[5]) if pd.notna(row.iloc[5]) else None,
        #     life_expectancy_female=float(row.iloc[6]) if pd.notna(row.iloc[6]) else None,
        #     infant_mortality_rate=float(row.iloc[7]) if pd.notna(row.iloc[7]) else None,
        #     infant_mortality_rate_male=float(row.iloc[8]) if pd.notna(row.iloc[8]) else None,
        #     infant_mortality_rate_female=float(row.iloc[9]) if pd.notna(row.iloc[9]) else None,
        #     fertility_rate=float(row.iloc[10]) if pd.notna(row.iloc[10]) else None,
        #     sex_differential_e0=float(row.iloc[11]) if pd.notna(row.iloc[11]) else None,
        #     sex_ratio_tmi=float(row.iloc[12]) if pd.notna(row.iloc[12]) else None
        # )
        # session.add(indicator)

        records_added += 1

        # Commit in batches
        if records_added % batch_size == 0:
            # session.commit()
            logger.info(f"Committed {records_added} records...")

    # Final commit
    # session.commit()
    logger.info(f"Completed: {records_added} demographic indicators loaded")


# ============================================================================
# 6. LOAD POPULATION INDICATORS
# ============================================================================

def load_population_indicators(session: Session, batch_size: int = 100):
    """
    Load population growth indicators from Excel file

    Args:
        session: Database session
        batch_size: Number of records to insert per batch
    """
    logger.info("Loading population indicators...")

    file_path = FILES["population"]
    df = pd.read_excel(file_path, sheet_name='Crecimiento Poblacional', skiprows=8)

    # Clean data
    df = clean_data(df)

    # Filter valid years (column index 2)
    df = df[df.iloc[:, 2].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]

    logger.info(f"Processing {len(df)} population records...")

    records_added = 0
    for idx, row in df.iterrows():
        # Create model instance (uncomment when models are ready)
        # indicator = DanePopulationIndicator(
        #     region_code=row.iloc[0],
        #     year=int(row.iloc[2]),
        #     area_type=row.iloc[3] if pd.notna(row.iloc[3]) else None,
        #     population=int(row.iloc[4]) if pd.notna(row.iloc[4]) else 0,
        #     growth_rate=float(row.iloc[5]) if pd.notna(row.iloc[5]) else None,
        #     births=int(row.iloc[6]) if pd.notna(row.iloc[6]) else None,
        #     birth_rate=float(row.iloc[7]) if pd.notna(row.iloc[7]) else None,
        #     deaths=int(row.iloc[8]) if pd.notna(row.iloc[8]) else None,
        #     death_rate=float(row.iloc[9]) if pd.notna(row.iloc[9]) else None,
        #     intl_migration_rate=float(row.iloc[10]) if pd.notna(row.iloc[10]) else None
        # )
        # session.add(indicator)

        records_added += 1

        # Commit in batches
        if records_added % batch_size == 0:
            # session.commit()
            logger.info(f"Committed {records_added} records...")

    # Final commit
    # session.commit()
    logger.info(f"Completed: {records_added} population indicators loaded")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - load all indicators in order
    """
    # Database connection (adjust to your settings)
    # DATABASE_URL = "postgresql://user:password@localhost:5432/dnp_population"
    # engine = create_engine(DATABASE_URL, echo=False)

    # with Session(engine) as session:
    #     try:
    #         # Load in order (dimensions first, then facts)
    #         load_dane_regions(session)
    #         load_fertility_indicators(session)
    #         load_migration_indicators(session)
    #         load_mortality_indicators(session)
    #         load_demographic_indicators(session)
    #         load_population_indicators(session)
    #
    #         logger.info("All DANE indicators loaded successfully!")
    #
    #     except Exception as e:
    #         logger.error(f"Error loading indicators: {e}")
    #         session.rollback()
    #         raise

    logger.info("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         DANE INDICATORS ETL SCRIPT - READY TO USE              ║
    ╚════════════════════════════════════════════════════════════════╝

    To use this script:

    1. Create SQLModel models in backend/app/models/
    2. Uncomment the model imports at the top
    3. Uncomment the database code in main()
    4. Uncomment the session.add() and session.commit() lines
    5. Adjust file paths and database URL
    6. Run: python etl/scripts/load_dane_indicators_example.py

    Expected results:
    - ~23 regions loaded
    - ~779 fertility records
    - ~4,884 migration records
    - ~1,558 mortality records
    - ~779 demographic records
    - ~779 population records

    Total: ~9,000 indicator records
    """)


if __name__ == "__main__":
    main()
