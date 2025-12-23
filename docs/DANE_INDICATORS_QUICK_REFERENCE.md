# DANE Indicators - Quick Reference Guide

## File Summary Table

| File | Rows | Columns | Skip Rows | Sheet Name | Granularity | Age Groups |
|------|------|---------|-----------|------------|-------------|------------|
| **Fertility** | 779 | 45 | 9 | Fecundidad | Regional | 10-49 (40) |
| **Migration** | 4,884 | 107 | 9 | Migración | Regional × Sex × Type | 0-100+ (101) |
| **Mortality** | 1,558 | 106 | 9 | Mortalidad | Regional × Sex | 0-100+ (101) |
| **Demographic** | 779 | 13 | 8 | Cambio Demográfico | Regional | Summary only |
| **Population** | 779 | 11 | 8 | Crecimiento Poblacional | Regional | Summary only |
| **Regions** | 2,244 | 7 | 6 | Regionalización | Municipality × Area | N/A |

## Region Codes (22-23 unique)

| Code | Region Name |
|------|-------------|
| NAL | Total Nacional |
| ACB | Altiplano Cundiboyacense |
| AMG | Alto Magdalena |
| APC | Anden Pacífico |
| AQU | Antioquia y Urabá |
| ATN | Altillanura |
| AZN | Amazonía |
| BGR | Bogotá Región |
| BMG | Bajo Magdalena |
| BMR | Boyacá y Región |
| BQR | Barranquilla y Región |
| CCR | Cali y Región |
| CLR | Caldense y Región |
| CRI | Caribe Insular |
| ECF | Eje Cafetero |
| EGS | Estela Gigante Santander |
| GSV | Gran Santander y Valles |
| MTC | Montaña Centro |
| NPA | Norte Pacífico Andino |
| SBC | Sur Bolívar y Cesar |
| SSS | Sierra Sur y Serranía |
| VDA | Valle de Aburrá |
| VRC | Valle del Río Cauca |

## Table Schemas Quick Reference

### 1. Fertility Indicators
```python
{
    "region_code": "ACB",
    "year": 2018,
    "tgf": 1.868223,  # Total Fertility Rate
    "age_rates": {"10": 0.000096, "15": 0.027442, ..., "49": 0.0}
}
```
**Unique Key:** (region_code, year)

### 2. Migration Indicators
```python
{
    "region_code": "ACB",
    "year": 2018,
    "sex": "Hombres",  # or "Mujeres"
    "migration_type": "Internacional",  # or "Interna"
    "age_counts": {"0": 216, "20": 268, ..., "100": 3}
}
```
**Unique Key:** (region_code, year, sex, migration_type)

### 3. Mortality Indicators
```python
{
    "region_code": "NAL",
    "year": 2018,
    "sex": "Hombres",  # or "Mujeres"
    "age_rates": {"0": 0.01726, "50": 0.00523, ..., "100": 0.5}
}
```
**Unique Key:** (region_code, year, sex)

### 4. Demographic Indicators
```python
{
    "region_code": "NAL",
    "year": 2018,
    "life_expectancy": 75.34,
    "life_expectancy_male": 72.71,
    "life_expectancy_female": 78.11,
    "infant_mortality_rate": 15.74,
    "fertility_rate": 1.88
}
```
**Unique Key:** (region_code, year)

### 5. Population Indicators
```python
{
    "region_code": "NAL",
    "year": 2018,
    "population": 48258494,
    "growth_rate": 1.754464,
    "births": 730370,
    "birth_rate": 15.13,
    "deaths": 347876,
    "death_rate": 7.21
}
```
**Unique Key:** (region_code, year)

## Data Type Mappings

| Column Type | SQL Type | Python Type | Example |
|-------------|----------|-------------|---------|
| Region Code | VARCHAR(10) | str | "ACB" |
| Territory | VARCHAR(100) | str | "Altiplano Cundiboyacense" |
| Year | INTEGER | int | 2018 |
| Sex | VARCHAR(20) | str | "Hombres" / "Mujeres" |
| Migration Type | VARCHAR(30) | str | "Internacional" / "Interna" |
| Population | BIGINT | int | 48258494 |
| Rates | DECIMAL(10,6) | Decimal | 1.868223 |
| Mortality Rates | DECIMAL(10,8) | Decimal | 0.01726543 |
| Age Data | JSONB | Dict[str, float] | {"10": 0.00009} |

## Common Query Patterns

### Get Fertility by Region & Year
```python
from sqlmodel import select

statement = select(DaneFertilityIndicator).where(
    DaneFertilityIndicator.region_code == "NAL",
    DaneFertilityIndicator.year >= 2018,
    DaneFertilityIndicator.year <= 2025
)
results = session.exec(statement).all()
```

### Get Migration by Sex & Type
```python
statement = select(DaneMigrationIndicator).where(
    DaneMigrationIndicator.region_code == "ACB",
    DaneMigrationIndicator.year == 2020,
    DaneMigrationIndicator.sex == "Hombres",
    DaneMigrationIndicator.migration_type == "Internacional"
)
result = session.exec(statement).first()
```

### Get Age-Specific Data from JSONB
```sql
-- PostgreSQL: Get fertility rate for age 25
SELECT region_code, year,
       (age_rates->>'25')::decimal as fertility_rate_age_25
FROM dane_fertility_indicators
WHERE region_code = 'NAL' AND year = 2020;

-- PostgreSQL: Get migration for ages 20-30
SELECT region_code, year, sex,
       jsonb_object_agg(key, value) as migration_20_30
FROM dane_migration_indicators,
     jsonb_each_text(age_counts)
WHERE key::int BETWEEN 20 AND 30
GROUP BY region_code, year, sex;
```

### Summary Statistics
```sql
-- Average life expectancy by region (2020-2030)
SELECT region_code,
       AVG(life_expectancy) as avg_life_expectancy,
       AVG(infant_mortality_rate) as avg_infant_mortality
FROM dane_demographic_indicators
WHERE year BETWEEN 2020 AND 2030
GROUP BY region_code
ORDER BY avg_life_expectancy DESC;

-- Population growth trends
SELECT region_code, year, population,
       LAG(population) OVER (PARTITION BY region_code ORDER BY year) as prev_population,
       population - LAG(population) OVER (PARTITION BY region_code ORDER BY year) as growth
FROM dane_population_indicators
WHERE region_code = 'NAL'
ORDER BY year;
```

## FastAPI Endpoint Examples

### Get Fertility Data
```python
@router.get("/indicators/fertility/{region_code}")
async def get_fertility(
    region_code: str,
    year_start: int = Query(2018, ge=2018, le=2070),
    year_end: int = Query(2070, ge=2018, le=2070),
    session: Session = Depends(get_session)
):
    statement = select(DaneFertilityIndicator).where(
        DaneFertilityIndicator.region_code == region_code,
        DaneFertilityIndicator.year >= year_start,
        DaneFertilityIndicator.year <= year_end
    )
    results = session.exec(statement).all()
    return results
```

### Get Migration Summary
```python
@router.get("/indicators/migration/{region_code}/summary")
async def get_migration_summary(
    region_code: str,
    year: int,
    session: Session = Depends(get_session)
):
    """Get total migration by type and sex for a region/year"""
    statement = select(DaneMigrationIndicator).where(
        DaneMigrationIndicator.region_code == region_code,
        DaneMigrationIndicator.year == year
    )
    results = session.exec(statement).all()

    summary = {}
    for record in results:
        key = f"{record.sex}_{record.migration_type}"
        total = sum(record.age_counts.values())
        summary[key] = total

    return summary
```

### Get Demographic Trends
```python
@router.get("/indicators/demographic/{region_code}/trends")
async def get_demographic_trends(
    region_code: str,
    session: Session = Depends(get_session)
):
    """Get life expectancy and infant mortality trends"""
    statement = select(DaneDemographicIndicator).where(
        DaneDemographicIndicator.region_code == region_code
    ).order_by(DaneDemographicIndicator.year)

    results = session.exec(statement).all()

    return {
        "region_code": region_code,
        "trends": [
            {
                "year": r.year,
                "life_expectancy": r.life_expectancy,
                "infant_mortality": r.infant_mortality_rate
            }
            for r in results
        ]
    }
```

## Data Validation Rules

### Required Validations
- Year: Must be between 2018-2070
- Region Code: Must exist in `dane_regions` table
- Sex: Must be "Hombres" or "Mujeres"
- Migration Type: Must be "Internacional" or "Interna"
- Age Data: All values must be numeric, keys must be valid ages

### Example Validation Function
```python
from pydantic import validator

class FertilityIndicatorCreate(BaseModel):
    region_code: str
    year: int
    tgf: Decimal
    age_rates: Dict[str, float]

    @validator('year')
    def validate_year(cls, v):
        if not 2018 <= v <= 2070:
            raise ValueError('Year must be between 2018 and 2070')
        return v

    @validator('age_rates')
    def validate_age_rates(cls, v):
        for age_str, rate in v.items():
            age = int(age_str)
            if not 10 <= age <= 49:
                raise ValueError(f'Invalid age for fertility: {age}')
            if not 0 <= rate <= 1:
                raise ValueError(f'Fertility rate must be between 0 and 1')
        return v
```

## Common Pitfalls & Solutions

### 1. Metadata Rows in Data
**Problem:** Excel files contain metadata rows mixed with data
**Solution:** Use `skiprows=9` and filter with `clean_data()` function

### 2. JSONB Query Performance
**Problem:** Slow queries on JSONB columns
**Solution:** Create GIN indexes on JSONB columns
```sql
CREATE INDEX idx_fertility_age_rates ON dane_fertility_indicators USING GIN (age_rates);
```

### 3. Year Data Type Issues
**Problem:** Year column contains strings or floats
**Solution:** Filter and convert explicitly
```python
df = df[df['year'].apply(lambda x: isinstance(x, (int, float)) and not pd.isna(x))]
df['year'] = df['year'].astype(int)
```

### 4. Missing Age Data
**Problem:** Some ages have NaN values
**Solution:** Use `pd.notna()` check before adding to age_dict
```python
if col_name in row.index and pd.notna(row[col_name]):
    age_dict[str(age)] = float(row[col_name])
```

## Performance Optimization Tips

1. **Batch Inserts:** Use batch_size=100 for commits
2. **Index Common Queries:** Add indexes on (region_code, year)
3. **JSONB Indexes:** Use GIN indexes for JSONB columns
4. **Connection Pooling:** Use SQLAlchemy connection pooling
5. **Async Queries:** Use async database drivers for concurrent requests

## Testing Checklist

- [ ] Regions load correctly (23 regions)
- [ ] Fertility data loads (779 records)
- [ ] Migration data loads (4,884 records)
- [ ] Mortality data loads (1,558 records)
- [ ] Demographic data loads (779 records)
- [ ] Population data loads (779 records)
- [ ] JSONB age data is queryable
- [ ] Foreign key constraints work
- [ ] Unique constraints prevent duplicates
- [ ] API endpoints return expected data
- [ ] Year range filtering works
- [ ] Sex filtering works (migration/mortality)
- [ ] Migration type filtering works

## Next Steps

1. Create SQLModel models in `backend/app/models/dane_indicators.py`
2. Create database migration (Alembic)
3. Update ETL script with actual model references
4. Create API endpoints in `backend/app/api/v1/endpoints/`
5. Add Pydantic schemas for validation
6. Create unit tests
7. Add frontend components for visualization
