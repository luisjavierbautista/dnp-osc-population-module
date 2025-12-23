"""
API endpoints for DANE demographic indicators

Provides access to:
- Fertility indicators (TGF + age-specific rates)
- Migration indicators (by sex and type)
- Mortality indicators (by sex)
- Principal demographic indicators
- DANE regions/departments/municipalities
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, col
from ....db.database import get_session
from ....models.dane_indicators import (
    DaneRegion,
    DaneDepartment,
    DaneMunicipality,
    DaneFertilityIndicator,
    DaneMigrationIndicator,
    DaneMortalityIndicator,
    DanePrincipalIndicator,
)

router = APIRouter()


# ============================================================================
# REFERENCE DATA ENDPOINTS
# ============================================================================

@router.get("/regions", response_model=List[DaneRegion])
def get_dane_regions(
    session: Session = Depends(get_session)
):
    """
    Get all DANE population regions

    Returns 22-23 DANE regions including NAL (Nacional)
    """
    regions = session.exec(select(DaneRegion)).all()
    return regions


@router.get("/departments", response_model=List[DaneDepartment])
def get_dane_departments(
    session: Session = Depends(get_session)
):
    """
    Get all Colombian departments

    Returns 33 departments
    """
    departments = session.exec(select(DaneDepartment)).all()
    return departments


@router.get("/municipalities", response_model=List[DaneMunicipality])
def get_dane_municipalities(
    region_code: Optional[str] = Query(None, description="Filter by region code"),
    dept_code: Optional[str] = Query(None, description="Filter by department code"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
):
    """
    Get Colombian municipalities with optional filtering

    Returns up to 1,121 municipalities
    """
    statement = select(DaneMunicipality)

    if region_code:
        statement = statement.where(DaneMunicipality.region_code == region_code)
    if dept_code:
        statement = statement.where(DaneMunicipality.dept_code == dept_code)

    statement = statement.limit(limit)

    municipalities = session.exec(statement).all()
    return municipalities


# ============================================================================
# FERTILITY INDICATORS ENDPOINTS
# ============================================================================

@router.get("/fertility", response_model=List[DaneFertilityIndicator])
def get_fertility_indicators(
    region_code: Optional[str] = Query(None, description="Region code (e.g., 'NAL', 'VDA')"),
    year_start: Optional[int] = Query(None, ge=2018, le=2070, description="Start year"),
    year_end: Optional[int] = Query(None, ge=2018, le=2070, description="End year"),
    limit: int = Query(100, le=1000, description="Maximum number of results"),
    session: Session = Depends(get_session)
):
    """
    Get fertility indicators (TGF + age-specific rates)

    Returns fertility data for Colombian regions 2018-2070
    """
    statement = select(DaneFertilityIndicator)

    if region_code:
        statement = statement.where(DaneFertilityIndicator.region_code == region_code)
    if year_start:
        statement = statement.where(DaneFertilityIndicator.year >= year_start)
    if year_end:
        statement = statement.where(DaneFertilityIndicator.year <= year_end)

    statement = statement.order_by(
        DaneFertilityIndicator.region_code,
        DaneFertilityIndicator.year
    ).limit(limit)

    indicators = session.exec(statement).all()
    return indicators


@router.get("/fertility/{region_code}/{year}")
def get_fertility_by_region_year(
    region_code: str,
    year: int,
    session: Session = Depends(get_session)
):
    """
    Get fertility indicators for a specific region and year

    Returns TGF and age-specific fertility rates
    """
    indicator = session.exec(
        select(DaneFertilityIndicator).where(
            DaneFertilityIndicator.region_code == region_code,
            DaneFertilityIndicator.year == year
        )
    ).first()

    if not indicator:
        raise HTTPException(
            status_code=404,
            detail=f"Fertility data not found for region {region_code}, year {year}"
        )

    return indicator


# ============================================================================
# MIGRATION INDICATORS ENDPOINTS
# ============================================================================

@router.get("/migration", response_model=List[DaneMigrationIndicator])
def get_migration_indicators(
    region_code: Optional[str] = Query(None, description="Region code"),
    year_start: Optional[int] = Query(None, ge=2018, le=2070),
    year_end: Optional[int] = Query(None, ge=2018, le=2070),
    sex: Optional[str] = Query(None, description="'Hombres' or 'Mujeres'"),
    migration_type: Optional[str] = Query(None, description="'Internacional' or 'Interna'"),
    limit: int = Query(100, le=1000),
    session: Session = Depends(get_session)
):
    """
    Get migration indicators (net migration by age, sex, and type)

    Migration types:
    - Internacional: International migration
    - Interna: Internal/domestic migration
    """
    statement = select(DaneMigrationIndicator)

    if region_code:
        statement = statement.where(DaneMigrationIndicator.region_code == region_code)
    if year_start:
        statement = statement.where(DaneMigrationIndicator.year >= year_start)
    if year_end:
        statement = statement.where(DaneMigrationIndicator.year <= year_end)
    if sex:
        statement = statement.where(DaneMigrationIndicator.sex == sex)
    if migration_type:
        statement = statement.where(DaneMigrationIndicator.migration_type == migration_type)

    statement = statement.order_by(
        DaneMigrationIndicator.region_code,
        DaneMigrationIndicator.year,
        DaneMigrationIndicator.sex,
        DaneMigrationIndicator.migration_type
    ).limit(limit)

    indicators = session.exec(statement).all()
    return indicators


# ============================================================================
# MORTALITY INDICATORS ENDPOINTS
# ============================================================================

@router.get("/mortality", response_model=List[DaneMortalityIndicator])
def get_mortality_indicators(
    region_code: Optional[str] = Query(None, description="Region code"),
    year_start: Optional[int] = Query(None, ge=2018, le=2070),
    year_end: Optional[int] = Query(None, ge=2018, le=2070),
    sex: Optional[str] = Query(None, description="'Hombres' or 'Mujeres'"),
    limit: int = Query(100, le=1000),
    session: Session = Depends(get_session)
):
    """
    Get mortality indicators (probability of death by age and sex)

    Returns mortality rates (qx) for ages 0-100+
    """
    statement = select(DaneMortalityIndicator)

    if region_code:
        statement = statement.where(DaneMortalityIndicator.region_code == region_code)
    if year_start:
        statement = statement.where(DaneMortalityIndicator.year >= year_start)
    if year_end:
        statement = statement.where(DaneMortalityIndicator.year <= year_end)
    if sex:
        statement = statement.where(DaneMortalityIndicator.sex == sex)

    statement = statement.order_by(
        DaneMortalityIndicator.region_code,
        DaneMortalityIndicator.year,
        DaneMortalityIndicator.sex
    ).limit(limit)

    indicators = session.exec(statement).all()
    return indicators


# ============================================================================
# PRINCIPAL DEMOGRAPHIC INDICATORS ENDPOINTS
# ============================================================================

@router.get("/principal", response_model=List[DanePrincipalIndicator])
def get_principal_indicators(
    region_code: Optional[str] = Query(None, description="Region code"),
    year_start: Optional[int] = Query(None, ge=2018, le=2070),
    year_end: Optional[int] = Query(None, ge=2018, le=2070),
    limit: int = Query(100, le=1000),
    session: Session = Depends(get_session)
):
    """
    Get principal demographic indicators

    Includes summary demographic statistics for each region/year
    """
    statement = select(DanePrincipalIndicator)

    if region_code:
        statement = statement.where(DanePrincipalIndicator.region_code == region_code)
    if year_start:
        statement = statement.where(DanePrincipalIndicator.year >= year_start)
    if year_end:
        statement = statement.where(DanePrincipalIndicator.year <= year_end)

    statement = statement.order_by(
        DanePrincipalIndicator.region_code,
        DanePrincipalIndicator.year
    ).limit(limit)

    indicators = session.exec(statement).all()
    return indicators


@router.get("/principal/{region_code}")
def get_principal_time_series(
    region_code: str,
    year_start: int = Query(2018, ge=2018, le=2070),
    year_end: int = Query(2070, ge=2018, le=2070),
    session: Session = Depends(get_session)
):
    """
    Get principal indicators time series for a specific region

    Returns all principal indicators for the region across years
    """
    indicators = session.exec(
        select(DanePrincipalIndicator).where(
            DanePrincipalIndicator.region_code == region_code,
            DanePrincipalIndicator.year >= year_start,
            DanePrincipalIndicator.year <= year_end
        ).order_by(DanePrincipalIndicator.year)
    ).all()

    if not indicators:
        raise HTTPException(
            status_code=404,
            detail=f"No principal indicators found for region {region_code}"
        )

    return indicators


# ============================================================================
# SUMMARY ENDPOINT
# ============================================================================

@router.get("/summary")
def get_indicators_summary(
    session: Session = Depends(get_session)
):
    """
    Get summary statistics about available DANE indicators

    Returns counts and coverage information
    """
    # Count records in each table
    fertility_count = session.exec(select(DaneFertilityIndicator)).all()
    migration_count = session.exec(select(DaneMigrationIndicator)).all()
    mortality_count = session.exec(select(DaneMortalityIndicator)).all()
    principal_count = session.exec(select(DanePrincipalIndicator)).all()
    regions_count = session.exec(select(DaneRegion)).all()

    return {
        "regions": len(regions_count),
        "indicators": {
            "fertility": len(fertility_count),
            "migration": len(migration_count),
            "mortality": len(mortality_count),
            "principal": len(principal_count),
            "total": len(fertility_count) + len(migration_count) + len(mortality_count) + len(principal_count)
        },
        "years": {
            "start": 2018,
            "end": 2070,
            "count": 53
        },
        "data_source": "DANE - Proyecciones de Población 2018-2070",
        "last_updated": "2025-07-30"
    }
