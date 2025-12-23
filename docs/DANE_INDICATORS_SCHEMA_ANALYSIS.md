# DANE Indicators Database Schema Analysis

## Executive Summary

This document provides a comprehensive analysis of 6 DANE Excel files containing demographic indicators for Colombia (2018-2070). The analysis includes file structures, data granularities, and recommended database schemas for a FastAPI + PostgreSQL + SQLModel application.

---

## File-by-File Analysis

### FILE 1: Fertility Indicators
**Path:** `/home/luisjavier/Downloads/DANE Indicators/DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx`

**Sheet:** `Fecundidad`

**Structure:**
- **Total Rows:** 779
- **Skip Rows:** 9 (header metadata)
- **Data Columns:** 45
- **Year Range:** 2018-2070
- **Granularity:** Regional/Nacional

**Dimensions:**
- **Region Codes:** 23 unique (ACB, AMG, APC, AQU, ATN, AZN, BGR, BMG, BMR, BQR, CCR, CLR, CRI, ECF, EGS, GSV, MTC, NAL, NPA, SBC, SSS, VDA, VRC)
- **Sex-specific:** NO (fertility is female-only)
- **Age Breakdown:** 40 age groups (ages 10-49)

**Column Structure:**
1. `region_code` - Regional code (VARCHAR(10))
2. `territory` - Territory name (VARCHAR(100))
3. `year` - Year (INTEGER)
4. `area_type` - Geographic area type (VARCHAR(50))
5. `tgf` - Total Fertility Rate / Tasa Global de Fecundidad (DECIMAL(10,6))
6. `age_10` to `age_49` - Age-specific fertility rates (DECIMAL(10,8))

**Data Notes:**
- Contains total fertility rate (TGF) + 40 age-specific rates
- Values are rates/probabilities (typically < 1.0)
- Nacional data: 2018-2070
- Regional data: 2018-2050

---

### FILE 2: Migration Indicators
**Path:** `/home/luisjavier/Downloads/DANE Indicators/DCD-Mig-EstSexNal-Reg-2018-2070_VP (1).xlsx`

**Sheet:** `Migración`

**Structure:**
- **Total Rows:** 4,884
- **Skip Rows:** 9 (header metadata)
- **Data Columns:** 107
- **Year Range:** 2018-2070
- **Granularity:** Regional/Nacional + Sex + Migration Type

**Dimensions:**
- **Region Codes:** 22 unique
- **Sex:** 2 values (Hombres, Mujeres)
- **Migration Type:** 2 values (Internacional, Interna)
- **Age Breakdown:** 101 age groups (ages 0-100+)

**Column Structure:**
1. `region_code` - Regional code (VARCHAR(10))
2. `territory` - Territory name (VARCHAR(100))
3. `year` - Year (INTEGER)
4. `area_type` - Geographic area (VARCHAR(50))
5. `sex` - Sex (VARCHAR(20)) - "Hombres" or "Mujeres"
6. `migration_type` - Migration type (VARCHAR(30)) - "Internacional" or "Interna"
7. `age_0` to `age_100` - Net migration count by age (DECIMAL(10,2))

**Data Notes:**
- Saldo Neto Migratorio (Net Migration Balance)
- Values are counts (can be positive or negative)
- Internacional: International migration
- Interna: Internal/domestic migration
- Each year/region has 4 rows (2 sexes × 2 migration types)

---

### FILE 3: Mortality Indicators
**Path:** `/home/luisjavier/Downloads/DANE Indicators/DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx`

**Sheet:** `Mortalidad`

**Structure:**
- **Total Rows:** 1,558
- **Skip Rows:** 9 (header metadata)
- **Data Columns:** 106
- **Year Range:** 2018-2070
- **Granularity:** Regional/Nacional + Sex

**Dimensions:**
- **Region Codes:** 22 unique
- **Sex:** 2 values (Hombres, Mujeres)
- **Age Breakdown:** 101 age groups (ages 0-100+)

**Column Structure:**
1. `region_code` - Regional code (VARCHAR(10))
2. `territory` - Territory name (VARCHAR(100))
3. `year` - Year (INTEGER)
4. `area_type` - Geographic area (VARCHAR(50))
5. `sex` - Sex (VARCHAR(20)) - "Hombres" or "Mujeres"
6. `age_0` to `age_100` - Mortality rates by age (DECIMAL(10,8))

**Data Notes:**
- Values are mortality rates/probabilities (0 to 1)
- Represents probability of death at each age
- Each year/region has 2 rows (one per sex)
- Higher precision needed (8 decimal places)

---

### FILE 4: Principal Demographic Indicators (Cambio Demográfico)
**Path:** `/home/luisjavier/Downloads/DANE Indicators/DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx`

**Sheet:** `Cambio Demográfico`

**Structure:**
- **Total Rows:** 779
- **Skip Rows:** 8 (header metadata)
- **Data Columns:** 13
- **Year Range:** 2018-2070
- **Granularity:** Regional/Nacional

**Column Structure:**
1. `region_code` - SIGLA DE LA REGIÓN (VARCHAR(10))
2. `territory` - TERRITORIO (VARCHAR(100))
3. `year` - AÑO (INTEGER)
4. `area_type` - Área Geográfica (VARCHAR(50))
5. `life_expectancy` - Esperanza_vida_al nacer (DECIMAL(10,6))
6. `life_expectancy_male` - Esperanza_vida al nacer_hombres (DECIMAL(10,6))
7. `life_expectancy_female` - Esperanza_vida_al nacer mujeres (DECIMAL(10,6))
8. `infant_mortality_rate` - Tasa_mortalidad_infantil por mil hab. (DECIMAL(10,6))
9. `infant_mortality_rate_male` - Tasa_mortalidad_infantil_hombres por mil hab. (DECIMAL(10,6))
10. `infant_mortality_rate_female` - Tasa_mortalidad_infantil_mujeres por mil hab. (DECIMAL(10,6))
11. `fertility_rate` - Tasa_fecundidad_edad simple (DECIMAL(10,6))
12. `sex_differential_e0` - Diferencial por sexo_(e0) (DECIMAL(10,6))
13. `sex_ratio_tmi` - Hombres/Mujeres_(TMI) (DECIMAL(10,6))

**Data Notes:**
- Summary indicators (not age-specific)
- Life expectancy in years
- Infant mortality rate per 1,000 habitants
- One row per region/year

---

### FILE 5: Population Growth Indicators (Crecimiento Poblacional)
**Path:** `/home/luisjavier/Downloads/DANE Indicators/DCD-PrinInd-crecPobNac-2018-2070_VP (1).xlsx`

**Sheet:** `Crecimiento Poblacional`

**Structure:**
- **Total Rows:** 779
- **Skip Rows:** 8 (header metadata)
- **Data Columns:** 11
- **Year Range:** 2018-2070
- **Granularity:** Regional/Nacional

**Column Structure:**
1. `region_code` - SIGLA DE LA REGIÓN (VARCHAR(10))
2. `territory` - TERRITORIO (VARCHAR(100))
3. `year` - AÑO (INTEGER)
4. `area_type` - Área Geográfica (VARCHAR(50))
5. `population` - Población (BIGINT)
6. `growth_rate` - Tasa crecimiento exponencial x 100 (DECIMAL(10,6))
7. `births` - Estimación Nacimientos (INTEGER)
8. `birth_rate` - Tasa Bruta de Natalidad (x mil hab.) (DECIMAL(10,6))
9. `deaths` - Estimación Defunciones (INTEGER)
10. `death_rate` - Tasa Bruta de Mortalidad (x mil hab.) (DECIMAL(10,6))
11. `intl_migration_rate` - Total Migración Internacional Neta (tasa x mil hab.) (DECIMAL(10,6))

**Data Notes:**
- Summary population statistics
- Growth rate is exponential (percentage)
- Birth/death rates per 1,000 habitants
- One row per region/year

---

### FILE 6: DANE Regions (Regionalización)
**Path:** `/home/luisjavier/Downloads/Regiones DANE.xlsx`

**Sheet:** `Regionalización`

**Structure:**
- **Total Rows:** 2,244
- **Skip Rows:** 6 (header metadata)
- **Data Columns:** 7
- **Granularity:** Municipality + Area Type

**Dimensions:**
- **Unique Regions:** 22
- **Unique Departments:** 33
- **Unique Municipalities:** 1,123 (1,103 municipalities + 20 non-municipalized areas)
- **Area Types:** 2 (Cabecera Municipal, Centros Poblados y Rural Disperso)

**Column Structure:**
1. `region_code` - SIGLA DE LA REGIÓN (VARCHAR(10))
2. `region_name` - REGIÓN (VARCHAR(100))
3. `dept_code` - DP (VARCHAR(10))
4. `dept_name` - DPNOM (VARCHAR(100))
5. `muni_code` - MPIO (VARCHAR(10))
6. `muni_name` - DPMP (VARCHAR(100))
7. `area_type` - ÁREA GEOGRÁFICA (VARCHAR(100))

**Data Notes:**
- Maps municipalities to regions
- Each municipality has 2 rows (Cabecera + Rural)
- Provides hierarchical geographic structure: Region → Department → Municipality → Area

**Region Codes:**
- ACB: Altiplano Cundiboyacense
- AMG: Alto Magdalena
- APC: Anden Pacífico
- AQU: Antioquia y Urabá
- ATN: Altillanura
- AZN: Amazonía
- BGR: Bogotá Región
- BMG: Bajo Magdalena
- BMR: Boyacá y Región
- BQR: Barranquilla y Región
- CCR: Cali y Región
- CLR: Caldense y Región
- CRI: Caribe Insular
- ECF: Eje Cafetero
- EGS: Estela Gigante Santander
- GSV: Gran Santander y Valles
- MTC: Montaña Centro
- NPA: Norte Pacífico Andino
- SBC: Sur Bolivar y Cesar
- SSS: Sierra Sur y Serranía
- VDA: Valle de Aburrá
- VRC: Valle del Río Cauca

---

## Recommended Database Schemas

### Schema Design Principles

1. **Normalized Structure**: Separate dimension tables (regions, territories) from fact tables (indicators)
2. **Composite Keys**: Use (region_code, year, sex, etc.) for unique identification
3. **Data Types**: Use appropriate precision for rates vs counts
4. **Indexes**: Add indexes on frequently queried columns (region_code, year)
5. **Constraints**: Foreign keys to ensure referential integrity

---

### Schema 1: Dimension Tables (Reference Data)

#### Table: `dane_regions`
**Purpose:** Master table for DANE region codes and names

```sql
CREATE TABLE dane_regions (
    region_code VARCHAR(10) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO dane_regions (region_code, region_name) VALUES
    ('NAL', 'Total Nacional'),
    ('ACB', 'Altiplano Cundiboyacense'),
    ('VDA', 'Valle de Aburrá'),
    -- ... etc
```

**SQLModel (Python):**
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class DaneRegion(SQLModel, table=True):
    __tablename__ = "dane_regions"

    region_code: str = Field(primary_key=True, max_length=10)
    region_name: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

#### Table: `dane_departments`
**Purpose:** Department reference table

```sql
CREATE TABLE dane_departments (
    dept_code VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**SQLModel (Python):**
```python
class DaneDepartment(SQLModel, table=True):
    __tablename__ = "dane_departments"

    dept_code: str = Field(primary_key=True, max_length=10)
    dept_name: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

#### Table: `dane_municipalities`
**Purpose:** Municipality reference table with region mapping

```sql
CREATE TABLE dane_municipalities (
    muni_code VARCHAR(10) PRIMARY KEY,
    muni_name VARCHAR(100) NOT NULL,
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_code) REFERENCES dane_departments(dept_code),
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX idx_municipalities_dept ON dane_municipalities(dept_code);
CREATE INDEX idx_municipalities_region ON dane_municipalities(region_code);
```

**SQLModel (Python):**
```python
class DaneMunicipality(SQLModel, table=True):
    __tablename__ = "dane_municipalities"

    muni_code: str = Field(primary_key=True, max_length=10)
    muni_name: str = Field(max_length=100, index=True)
    dept_code: str = Field(foreign_key="dane_departments.dept_code", max_length=10)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Schema 2: Fertility Indicators

#### Table: `dane_fertility_indicators`
**Purpose:** Store fertility rates by region, year, and age

**Design Decision:** Store as JSONB for age-specific rates to avoid 40+ columns

```sql
CREATE TABLE dane_fertility_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    tgf DECIMAL(10,6) NOT NULL,  -- Total Fertility Rate
    age_rates JSONB NOT NULL,  -- {"10": 0.000096, "11": 0.000093, ..., "49": 0.0}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year)
);

CREATE INDEX idx_fertility_region_year ON dane_fertility_indicators(region_code, year);
CREATE INDEX idx_fertility_year ON dane_fertility_indicators(year);
```

**SQLModel (Python):**
```python
from typing import Dict
from decimal import Decimal

class DaneFertilityIndicator(SQLModel, table=True):
    __tablename__ = "dane_fertility_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    tgf: Decimal = Field(max_digits=10, decimal_places=6)  # Total Fertility Rate
    age_rates: Dict[str, float] = Field(sa_column=Column(JSON))  # Age-specific rates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "ACB",
                "year": 2018,
                "area_type": "Total",
                "tgf": 1.868223,
                "age_rates": {"10": 0.000096, "15": 0.027442, "20": 0.104151, "49": 0.0}
            }
        }
```

**Alternative: Normalized Design (if age-specific queries are frequent)**

```sql
CREATE TABLE dane_fertility_indicators_normalized (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    age INTEGER NOT NULL,  -- 10-49
    area_type VARCHAR(50),
    fertility_rate DECIMAL(10,8) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year, age)
);

CREATE INDEX idx_fertility_norm_region_year ON dane_fertility_indicators_normalized(region_code, year);
```

---

### Schema 3: Migration Indicators

#### Table: `dane_migration_indicators`
**Purpose:** Store net migration by region, year, sex, migration type, and age

```sql
CREATE TABLE dane_migration_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    sex VARCHAR(20) NOT NULL,  -- 'Hombres', 'Mujeres'
    migration_type VARCHAR(30) NOT NULL,  -- 'Internacional', 'Interna'
    age_counts JSONB NOT NULL,  -- {"0": 216, "1": 202, ..., "100": 3}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year, sex, migration_type)
);

CREATE INDEX idx_migration_region_year ON dane_migration_indicators(region_code, year);
CREATE INDEX idx_migration_sex ON dane_migration_indicators(sex);
CREATE INDEX idx_migration_type ON dane_migration_indicators(migration_type);
```

**SQLModel (Python):**
```python
class DaneMigrationIndicator(SQLModel, table=True):
    __tablename__ = "dane_migration_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    sex: str = Field(max_length=20, index=True)  # 'Hombres', 'Mujeres'
    migration_type: str = Field(max_length=30, index=True)  # 'Internacional', 'Interna'
    age_counts: Dict[str, float] = Field(sa_column=Column(JSON))  # Age-specific migration counts
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "ACB",
                "year": 2018,
                "sex": "Hombres",
                "migration_type": "Internacional",
                "age_counts": {"0": 216, "20": 268, "50": 53, "100": 3}
            }
        }
```

---

### Schema 4: Mortality Indicators

#### Table: `dane_mortality_indicators`
**Purpose:** Store mortality rates by region, year, sex, and age

```sql
CREATE TABLE dane_mortality_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    sex VARCHAR(20) NOT NULL,  -- 'Hombres', 'Mujeres'
    age_rates JSONB NOT NULL,  -- {"0": 0.01726, "1": 0.00107, ..., "100": 0.5}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year, sex)
);

CREATE INDEX idx_mortality_region_year ON dane_mortality_indicators(region_code, year);
CREATE INDEX idx_mortality_sex ON dane_mortality_indicators(sex);
```

**SQLModel (Python):**
```python
class DaneMortalityIndicator(SQLModel, table=True):
    __tablename__ = "dane_mortality_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    sex: str = Field(max_length=20, index=True)  # 'Hombres', 'Mujeres'
    age_rates: Dict[str, float] = Field(sa_column=Column(JSON))  # Age-specific mortality rates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "region_code": "NAL",
                "year": 2018,
                "sex": "Hombres",
                "age_rates": {"0": 0.01726, "20": 0.00103, "50": 0.00523, "100": 0.5}
            }
        }
```

---

### Schema 5: Demographic Change Indicators

#### Table: `dane_demographic_indicators`
**Purpose:** Store summary demographic indicators (life expectancy, infant mortality, fertility)

```sql
CREATE TABLE dane_demographic_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    life_expectancy DECIMAL(10,6),
    life_expectancy_male DECIMAL(10,6),
    life_expectancy_female DECIMAL(10,6),
    infant_mortality_rate DECIMAL(10,6),  -- per 1,000
    infant_mortality_rate_male DECIMAL(10,6),
    infant_mortality_rate_female DECIMAL(10,6),
    fertility_rate DECIMAL(10,6),
    sex_differential_e0 DECIMAL(10,6),
    sex_ratio_tmi DECIMAL(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year)
);

CREATE INDEX idx_demographic_region_year ON dane_demographic_indicators(region_code, year);
```

**SQLModel (Python):**
```python
class DaneDemographicIndicator(SQLModel, table=True):
    __tablename__ = "dane_demographic_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    life_expectancy: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    life_expectancy_male: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    life_expectancy_female: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    infant_mortality_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    infant_mortality_rate_male: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    infant_mortality_rate_female: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    fertility_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    sex_differential_e0: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    sex_ratio_tmi: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### Schema 6: Population Growth Indicators

#### Table: `dane_population_indicators`
**Purpose:** Store population and growth statistics

```sql
CREATE TABLE dane_population_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    population BIGINT NOT NULL,
    growth_rate DECIMAL(10,6),  -- exponential rate × 100
    births INTEGER,
    birth_rate DECIMAL(10,6),  -- per 1,000
    deaths INTEGER,
    death_rate DECIMAL(10,6),  -- per 1,000
    intl_migration_rate DECIMAL(10,6),  -- per 1,000
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code),
    UNIQUE (region_code, year)
);

CREATE INDEX idx_population_region_year ON dane_population_indicators(region_code, year);
```

**SQLModel (Python):**
```python
class DanePopulationIndicator(SQLModel, table=True):
    __tablename__ = "dane_population_indicators"

    id: Optional[int] = Field(default=None, primary_key=True)
    region_code: str = Field(foreign_key="dane_regions.region_code", max_length=10, index=True)
    year: int = Field(index=True)
    area_type: Optional[str] = Field(default=None, max_length=50)
    population: int
    growth_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    births: Optional[int] = None
    birth_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    deaths: Optional[int] = None
    death_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    intl_migration_rate: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=6)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

## Data Transformation Requirements

### 1. Header Rows & Metadata
- **Skip rows:** All files have 7-9 rows of metadata/headers to skip
- **Validation:** Filter out rows with text headers that leak into data (e.g., "Actualizado el...", "Fuente: DANE...")

### 2. Column Name Mapping
- Spanish column names → English snake_case
- Handle special characters in headers (spaces, underscores, parentheses)

### 3. Data Type Conversions
- **Year columns:** Convert to INTEGER
- **Rate columns:** Convert to DECIMAL with appropriate precision
- **Count columns:** Convert to INTEGER or BIGINT
- **Age-specific data:** Parse into JSONB format

### 4. Data Validation
- Check year ranges (2018-2070)
- Validate region codes against master list
- Ensure sex values are only "Hombres" or "Mujeres"
- Validate migration types are only "Internacional" or "Interna"

### 5. JSONB Age Data Format
```python
# Example transformation for age-specific data
def transform_age_data(row_df, age_range):
    """Convert age columns to JSONB format"""
    age_dict = {}
    for age in age_range:
        col_name = f'age_{age}'
        if col_name in row_df and pd.notna(row_df[col_name]):
            age_dict[str(age)] = float(row_df[col_name])
    return age_dict

# Usage examples:
# Fertility: transform_age_data(row, range(10, 50))
# Migration: transform_age_data(row, range(0, 101))
# Mortality: transform_age_data(row, range(0, 101))
```

---

## ETL Script Structure

### Recommended Approach

```python
# etl/scripts/load_dane_indicators.py

import pandas as pd
from sqlmodel import Session, create_engine
from app.models import (
    DaneRegion,
    DaneFertilityIndicator,
    DaneMigrationIndicator,
    DaneMortalityIndicator,
    DaneDemographicIndicator,
    DanePopulationIndicator
)

# 1. Load dimension tables first
def load_regions():
    """Load DANE regions from Regiones DANE.xlsx"""
    pass

# 2. Load fertility indicators
def load_fertility_indicators():
    """Load from DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx"""
    df = pd.read_excel(file_path, sheet_name='Fecundidad', skiprows=9)
    # Transform and load
    pass

# 3. Load migration indicators
def load_migration_indicators():
    """Load from DCD-Mig-EstSexNal-Reg-2018-2070_VP (1).xlsx"""
    pass

# 4. Load mortality indicators
def load_mortality_indicators():
    """Load from DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx"""
    pass

# 5. Load demographic indicators
def load_demographic_indicators():
    """Load from DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx"""
    pass

# 6. Load population indicators
def load_population_indicators():
    """Load from DCD-PrinInd-crecPobNac-2018-2070_VP (1).xlsx"""
    pass

if __name__ == "__main__":
    # Execute in order
    load_regions()
    load_fertility_indicators()
    load_migration_indicators()
    load_mortality_indicators()
    load_demographic_indicators()
    load_population_indicators()
```

---

## API Endpoint Recommendations

### FastAPI Endpoints Structure

```python
# app/api/v1/endpoints/dane_indicators.py

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import Optional, List

router = APIRouter()

@router.get("/fertility/{region_code}")
def get_fertility_indicators(
    region_code: str,
    year_start: Optional[int] = Query(None, ge=2018, le=2070),
    year_end: Optional[int] = Query(None, ge=2018, le=2070),
    session: Session = Depends(get_session)
):
    """Get fertility indicators for a region"""
    pass

@router.get("/migration/{region_code}")
def get_migration_indicators(
    region_code: str,
    year: int,
    sex: Optional[str] = None,
    migration_type: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get migration indicators with filters"""
    pass

@router.get("/mortality/{region_code}")
def get_mortality_indicators(
    region_code: str,
    year: int,
    sex: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get mortality indicators"""
    pass

@router.get("/demographic/{region_code}")
def get_demographic_indicators(
    region_code: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get demographic summary indicators"""
    pass

@router.get("/population/{region_code}")
def get_population_indicators(
    region_code: str,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get population growth indicators"""
    pass

@router.get("/regions")
def list_regions(
    session: Session = Depends(get_session)
) -> List[DaneRegion]:
    """List all available regions"""
    pass
```

---

## Summary

This analysis provides:
1. **Detailed file structures** for all 6 DANE indicator files
2. **Recommended database schemas** using both SQL and SQLModel
3. **Data transformation requirements** and validation rules
4. **ETL script structure** for loading data
5. **API endpoint recommendations** for FastAPI

### Key Design Decisions:
- **JSONB for age-specific data**: Avoids 40-101 columns per table, maintains flexibility
- **Separate indicator tables**: Better query performance, clear data organization
- **Dimension tables first**: Enforce referential integrity
- **Composite unique keys**: Prevent duplicate data
- **Appropriate precision**: DECIMAL(10,6) for rates, DECIMAL(10,8) for mortality

### Next Steps:
1. Create SQLModel models in `/home/luisjavier/dev/projects/dnp/dnp-osc-population-module/backend/app/models/`
2. Create ETL scripts in `/home/luisjavier/dev/projects/dnp/dnp-osc-population-module/etl/scripts/`
3. Generate database migrations (Alembic)
4. Implement API endpoints
5. Test data loading with sample files
