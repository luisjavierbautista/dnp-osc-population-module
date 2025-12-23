"""
SQLModel models for DANE demographic indicators

These models store DANE demographic indicators for Colombian regions (2018-2070):
- Fertility indicators (TGF and age-specific rates)
- Migration indicators (by sex and type)
- Mortality indicators (by sex and age)
- Principal demographic indicators
- Population growth indicators
"""

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, Dict
from decimal import Decimal


# ============================================================================
# DIMENSION TABLES (Reference Data)
# ============================================================================

class DaneRegion(SQLModel, table=True):
    """
    DANE Population Regions (23 regions)

    Examples:
    - NAL: Total Nacional
    - VDA: Valle de Aburrá
    - ACB: Altiplano Cundiboyacense
    """
    __tablename__ = "dane_regions"

    region_code: str = Field(primary_key=True, max_length=10)
    region_name: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DaneDepartment(SQLModel, table=True):
    """
    Colombian Departments (33 departments)

    Examples:
    - 05: Antioquia
    - 11: Bogotá D.C.
    - 76: Valle del Cauca
    """
    __tablename__ = "dane_departments"

    dept_code: str = Field(primary_key=True, max_length=10)
    dept_name: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DaneMunicipality(SQLModel, table=True):
    """
    Colombian Municipalities (1,122 municipalities)
    Maps municipalities to departments and DANE regions
    """
    __tablename__ = "dane_municipalities"

    muni_code: str = Field(primary_key=True, max_length=10)
    muni_name: str = Field(max_length=100, index=True)
    dept_code: str = Field(foreign_key="dane_departments.dept_code", max_length=10)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# FERTILITY INDICATORS
# ============================================================================

class DaneFertilityIndicator(SQLModel, table=True):
    """
    Fertility indicators by region and year (2018-2070)

    Contains:
    - TGF (Tasa Global de Fecundidad / Total Fertility Rate)
    - Age-specific fertility rates (ages 10-49)

    Data source: DCD-Fec-EstNal-Reg-2018-2070_VP.xlsx
    """
    __tablename__ = "dane_fertility_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    tgf: Decimal = Field(max_digits=10, decimal_places=6)  # Total Fertility Rate
    age_rates: Dict[str, float] = Field(sa_column=Column(JSON))  # {"10": 0.000096, "11": 0.000093, ..., "49": 0.0}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "ACB",
                "year": 2018,
                "area_type": "Total",
                "tgf": 1.868223,
                "age_rates": {
                    "10": 0.000096,
                    "15": 0.027442,
                    "20": 0.104151,
                    "25": 0.125421,
                    "30": 0.099823,
                    "35": 0.062301,
                    "40": 0.024441,
                    "45": 0.004987,
                    "49": 0.0
                }
            }
        }


# ============================================================================
# MIGRATION INDICATORS
# ============================================================================

class DaneMigrationIndicator(SQLModel, table=True):
    """
    Migration indicators by region, year, sex, and type (2018-2070)

    Contains net migration balance (Saldo Neto Migratorio) by age

    Migration Types:
    - Internacional: International migration
    - Interna: Internal/domestic migration

    Data source: DCD-Mig-EstSexNal-Reg-2018-2070_VP.xlsx
    """
    __tablename__ = "dane_migration_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    sex: str = Field(max_length=20, index=True)  # "Hombres" or "Mujeres"
    migration_type: str = Field(max_length=30, index=True)  # "Internacional" or "Interna"
    age_values: Dict[str, float] = Field(sa_column=Column(JSON))  # {"0": 123.45, "1": 234.56, ..., "100": 12.34}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "NAL",
                "year": 2018,
                "area_type": "Total",
                "sex": "Hombres",
                "migration_type": "Internacional",
                "age_values": {
                    "0": 123.45,
                    "20": 5678.90,
                    "40": 3456.78,
                    "100": 12.34
                }
            }
        }


# ============================================================================
# MORTALITY INDICATORS
# ============================================================================

class DaneMortalityIndicator(SQLModel, table=True):
    """
    Mortality indicators by region, year, and sex (2018-2070)

    Contains probability of death (qx) by age

    Data source: DCD-Mor-EstSexNal-Reg-2018-2070_VP.xlsx
    """
    __tablename__ = "dane_mortality_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    sex: str = Field(max_length=20, index=True)  # "Hombres" or "Mujeres"
    age_mortality_rates: Dict[str, float] = Field(sa_column=Column(JSON))  # {"0": 0.012345, "1": 0.001234, ..., "100": 0.999999}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "NAL",
                "year": 2018,
                "area_type": "Total",
                "sex": "Hombres",
                "age_mortality_rates": {
                    "0": 0.012345,
                    "20": 0.001234,
                    "40": 0.002345,
                    "60": 0.012345,
                    "80": 0.089123,
                    "100": 0.999999
                }
            }
        }


# ============================================================================
# PRINCIPAL DEMOGRAPHIC INDICATORS
# ============================================================================

class DanePrincipalIndicator(SQLModel, table=True):
    """
    Principal demographic indicators by region and year (2018-2070)

    Contains key summary indicators:
    - Life expectancy (male, female, total)
    - Infant mortality rate
    - Reproductive health indicators

    Data source: DCD-PrinInd-camDemNac-2018-2070_VP.xlsx
    """
    __tablename__ = "dane_principal_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)

    # Life expectancy
    life_exp_male: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    life_exp_female: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)
    life_exp_total: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2)

    # Mortality indicators
    infant_mortality_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)

    # Other demographic indicators (stored as JSON for flexibility)
    other_indicators: Optional[Dict[str, float]] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "NAL",
                "year": 2018,
                "area_type": "Total",
                "life_exp_male": 74.07,
                "life_exp_female": 80.19,
                "life_exp_total": 77.07,
                "infant_mortality_rate": 12.345,
                "other_indicators": {
                    "tasa_bruta_natalidad": 15.67,
                    "tasa_bruta_mortalidad": 6.23
                }
            }
        }


# ============================================================================
# POPULATION GROWTH INDICATORS
# ============================================================================

class DaneGrowthIndicator(SQLModel, table=True):
    """
    Population growth indicators by region and year (2018-2070)

    Contains:
    - Total population
    - Population growth rate
    - Natural increase
    - Migration balance

    Data source: DCD-PrinInd-crecPobNac-2018-2070_VP.xlsx
    """
    __tablename__ = "dane_growth_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)

    # Population counts
    total_population: Optional[int] = Field(default=None)

    # Growth rates and components
    growth_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    natural_increase: Optional[int] = Field(default=None)
    net_migration: Optional[int] = Field(default=None)

    # Additional indicators (stored as JSON for flexibility)
    other_metrics: Optional[Dict[str, float]] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "NAL",
                "year": 2018,
                "area_type": "Total",
                "total_population": 49648685,
                "growth_rate": 1.23,
                "natural_increase": 234567,
                "net_migration": 12345,
                "other_metrics": {
                    "tasa_crecimiento_anual": 1.23,
                    "nacimientos": 654321,
                    "defunciones": 419754
                }
            }
        }
