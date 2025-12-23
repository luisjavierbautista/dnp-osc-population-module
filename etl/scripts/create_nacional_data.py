"""
ETL Script: Create Nacional-Level Data

This script creates nacional (00) territory and aggregates all population data
to create nacional totals for visualization.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add backend to path
backend_path = Path("/app") if Path("/app/app").exists() else Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

import logging
from sqlmodel import Session, create_engine, select, func
from datetime import datetime

from app.core.config import settings
from app.models import Territorio, NivelTerritorial, PoblacionEdad, PoblacionTotal, AreaGeografica, Sexo

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_nacional_territory(session: Session) -> None:
    """Create nacional territory if it doesn't exist"""
    logger.info("Checking for nacional territory...")

    nacional = session.exec(
        select(Territorio).where(Territorio.territorio_id == '00')
    ).first()

    if nacional:
        logger.info(f"✓ Nacional territory already exists: {nacional.nombre}")
        return

    logger.info("Creating nacional territory...")
    nacional = Territorio(
        territorio_id='00',
        nombre='Colombia',
        nivel=NivelTerritorial.NACIONAL,
        dp=None,
        mpio=None
    )
    session.add(nacional)
    session.commit()
    logger.info("✓ Nacional territory created")


def aggregate_poblacion_edad(session: Session, batch_size: int = 100) -> int:
    """
    Aggregate population by age from all territories to create nacional totals
    """
    logger.info("="*70)
    logger.info("Aggregating PoblacionEdad for nacional level...")
    logger.info("="*70)

    # Delete existing nacional data
    logger.info("Deleting existing nacional PoblacionEdad data...")
    deleted = session.query(PoblacionEdad).filter(PoblacionEdad.territorio_id == '00').delete()
    session.commit()
    logger.info(f"✓ Deleted {deleted} existing records")

    # Get distinct combinations of (anio, area_geografica, sexo, edad)
    logger.info("Finding distinct combinations...")
    combinations = session.exec(
        select(
            PoblacionEdad.anio,
            PoblacionEdad.area_geografica,
            PoblacionEdad.sexo,
            PoblacionEdad.edad,
            PoblacionEdad.mayores_100
        ).distinct()
    ).all()

    logger.info(f"Found {len(combinations)} distinct combinations to aggregate")

    count = 0
    batch_count = 0

    for anio, area_geo, sexo, edad, mayores_100 in combinations:
        # Sum population across all territories for this combination
        total_pob = session.exec(
            select(func.sum(PoblacionEdad.poblacion)).where(
                PoblacionEdad.anio == anio,
                PoblacionEdad.area_geografica == area_geo,
                PoblacionEdad.sexo == sexo,
                PoblacionEdad.edad == edad,
                PoblacionEdad.mayores_100 == mayores_100
            )
        ).one()

        if total_pob is None or total_pob == 0:
            continue

        # Create nacional record
        nacional_record = PoblacionEdad(
            territorio_id='00',
            anio=anio,
            area_geografica=area_geo,
            sexo=sexo,
            edad=edad,
            mayores_100=mayores_100,
            poblacion=Decimal(str(total_pob))
        )
        session.add(nacional_record)
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

    logger.info(f"✓ Created {count} nacional PoblacionEdad records")
    return count


def aggregate_poblacion_total(session: Session, batch_size: int = 100) -> int:
    """
    Aggregate total population from all territories to create nacional totals
    """
    logger.info("="*70)
    logger.info("Aggregating PoblacionTotal for nacional level...")
    logger.info("="*70)

    # Delete existing nacional data
    logger.info("Deleting existing nacional PoblacionTotal data...")
    deleted = session.query(PoblacionTotal).filter(PoblacionTotal.territorio_id == '00').delete()
    session.commit()
    logger.info(f"✓ Deleted {deleted} existing records")

    # Get distinct combinations of (anio, area_geografica)
    logger.info("Finding distinct combinations...")
    combinations = session.exec(
        select(
            PoblacionTotal.anio,
            PoblacionTotal.area_geografica
        ).distinct()
    ).all()

    logger.info(f"Found {len(combinations)} distinct combinations to aggregate")

    count = 0
    batch_count = 0

    for anio, area_geo in combinations:
        # Sum population metrics across all territories
        totals = session.exec(
            select(
                func.sum(PoblacionTotal.pob_total),
                func.sum(PoblacionTotal.pob_hombres),
                func.sum(PoblacionTotal.pob_mujeres)
            ).where(
                PoblacionTotal.anio == anio,
                PoblacionTotal.area_geografica == area_geo
            )
        ).one()

        total, hombres, mujeres = totals

        if total is None or total == 0:
            continue

        # Calculate percentages for "Total" area
        pct_urbana = None
        pct_rural = None

        if area_geo == AreaGeografica.TOTAL:
            # Get cabecera (urban) and cprd (rural) totals
            cabecera_total = session.exec(
                select(func.sum(PoblacionTotal.pob_total)).where(
                    PoblacionTotal.anio == anio,
                    PoblacionTotal.area_geografica == AreaGeografica.CABECERA
                )
            ).one()

            cprd_total = session.exec(
                select(func.sum(PoblacionTotal.pob_total)).where(
                    PoblacionTotal.anio == anio,
                    PoblacionTotal.area_geografica == AreaGeografica.CPRD
                )
            ).one()

            if cabecera_total and total:
                pct_urbana = Decimal(str(cabecera_total)) / Decimal(str(total))
            if cprd_total and total:
                pct_rural = Decimal(str(cprd_total)) / Decimal(str(total))

        # Create nacional record
        nacional_record = PoblacionTotal(
            territorio_id='00',
            anio=anio,
            area_geografica=area_geo,
            pob_total=Decimal(str(total)),
            pob_hombres=Decimal(str(hombres)),
            pob_mujeres=Decimal(str(mujeres)),
            pct_urbana=pct_urbana,
            pct_rural=pct_rural
        )
        session.add(nacional_record)
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

    logger.info(f"✓ Created {count} nacional PoblacionTotal records")
    return count


def main():
    logger.info("="*70)
    logger.info("CREATE NACIONAL-LEVEL DATA")
    logger.info("="*70)

    logger.info(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)

    with Session(engine) as session:
        try:
            # Step 1: Create nacional territory
            create_nacional_territory(session)

            # Step 2: Aggregate PoblacionEdad
            edad_count = aggregate_poblacion_edad(session)

            # Step 3: Aggregate PoblacionTotal
            total_count = aggregate_poblacion_total(session)

            logger.info("="*70)
            logger.info("✓ NACIONAL DATA CREATION COMPLETE!")
            logger.info("="*70)
            logger.info(f"Summary:")
            logger.info(f"  - PoblacionEdad records: {edad_count}")
            logger.info(f"  - PoblacionTotal records: {total_count}")

            # Verify
            logger.info("\nVerifying nacional data...")
            nacional = session.exec(select(Territorio).where(Territorio.territorio_id == '00')).first()
            logger.info(f"  ✓ Territory: {nacional.nombre} ({nacional.nivel})")

            sample_edad = session.exec(
                select(PoblacionEdad).where(PoblacionEdad.territorio_id == '00').limit(3)
            ).all()
            logger.info(f"  ✓ Sample PoblacionEdad records: {len(sample_edad)}")

            sample_total = session.exec(
                select(PoblacionTotal).where(PoblacionTotal.territorio_id == '00').limit(3)
            ).all()
            logger.info(f"  ✓ Sample PoblacionTotal records: {len(sample_total)}")

        except Exception as e:
            logger.error(f"Error during aggregation: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
