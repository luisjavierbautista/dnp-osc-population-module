# Database Filter Values

This document describes all available filter values in the DNP Population Module database.

**Last Updated**: 2025-11-10
**Database**: population_db
**Total Records**: 47,254,749 (poblacion_edad table)

---

## 1. Territorios (Territories)

### Available Values
- **Total territories**: 1,156
  - **DEPARTAMENTAL**: 33 departments
  - **MUNICIPAL**: 1,123 (1,103 municipalities + 20 non-municipalized areas)

### Usage
- API Endpoint: `/api/v1/population/territories`
- Filter by `nivel`: `DEPARTAMENTAL` | `MUNICIPAL`
- Search by `search`: name or territory code
- Example: `GET /api/v1/population/territories?nivel=DEPARTAMENTAL&search=Antioquia`

### Data Distribution
- Departmental records: 1,583,175
- Municipal records: 45,671,574

---

## 2. Años (Years)

### Available Values
- **Minimum Year**: 2018
- **Maximum Year**: 2050
- **Total Years**: 33

### Usage
- Year range queries: `anio_from` and `anio_to`
- Single year queries: `anio`
- Example: `GET /api/v1/population/age?territorio_id=05001&anio=2025`

---

## 3. Área Geográfica (Geographic Areas)

### Available Values
1. **Total** (~15,773,803 records)
2. **Cabecera Municipal** (~15,740,473 records)
3. **Centros Poblados y Rural Disperso** (~15,740,473 records)

### Usage
- Parameter: `area`
- Default: `"Total"`
- Example: `GET /api/v1/population/pyramid?territorio_id=05001&anio=2025&area=Cabecera Municipal`

### Notes
- All three values are available for all territories
- "Total" includes both urban and rural populations
- "Cabecera Municipal" represents urban areas
- "Centros Poblados y Rural Disperso" represents rural areas

---

## 4. Sexo (Sex)

### Available Values
1. **H** - Hombres (Males) - 18,686,037 records
2. **M** - Mujeres (Females) - 18,686,037 records
3. **T** - Total (Both) - 9,882,675 records

### Usage
- Parameter: `sexo`
- Default: `"T"`
- Pattern: `^[HMT]$`
- Example: `GET /api/v1/population/age?territorio_id=05001&anio=2025&sexo=H`

---

## 5. Edad (Age Range)

### Available Values
- **Minimum Age**: 0
- **Maximum Age**: 100
- **Total Ages**: 101

### Usage Modes

#### Simple Mode
- Individual ages: 0, 1, 2, 3, ..., 98, 99, 100
- Parameter: `modo=simple`
- Use for detailed age analysis

#### Quinquenal Mode
- 5-year groups: 0-4, 5-9, 10-14, ..., 95-99, 100+
- Parameter: `modo=quinquenal`
- Use for population pyramids
- Can also use `quinquenios=true` in `/age` endpoint

### Example
```
GET /api/v1/population/pyramid?territorio_id=05001&anio=2025&modo=quinquenal
```

---

## 6. Additional Parameters

### Quinquenios (5-year grouping)
- **Type**: Boolean
- **Default**: `false`
- **Usage**: Groups ages into 5-year ranges
- **Example**: `GET /api/v1/population/age?territorio_id=05001&anio=2025&quinquenios=true`

### Período (Growth Period)
- **Values**:
  - `hasta_2019`: From 2018 to 2019
  - `desde_2020`: From 2020 to 2050
- **Usage**: For growth calculations
- **Example**: `GET /api/v1/population/growth?territorio_id=05001&periodo=desde_2020`

---

## Data Volume Summary

### Tables
- **poblacion_edad**: 47,254,749 records
  - Departamental: 1,583,175 records
  - Municipal: 45,671,574 records
- **poblacion_total**: 201,507 records
- **territorio**: 1,156 records

### Dimensions
- **Territories**: 1,156 (33 departments + 1,103 municipalities + 20 non-municipalized areas)
- **Years**: 33 (2018-2050)
- **Geographic Areas**: 3 (Total, Cabecera, Rural)
- **Sex Categories**: 3 (H, M, T)
- **Ages**: 101 (0-100)

---

## Query Examples

### 1. Get population by age for a single territory
```
GET /api/v1/population/age?territorio_id=05001&anio=2025&area=Total&sexo=T
```

### 2. Get population pyramid data
```
GET /api/v1/population/pyramid?territorio_id=05001&anio=2025&area=Total&modo=quinquenal
```

### 3. Get urban-rural distribution
```
GET /api/v1/population/urban_rural?territorio_id=05&anio=2025
```

### 4. Calculate growth
```
GET /api/v1/population/growth?territorio_id=05001&periodo=desde_2020&area=Total
```

### 5. Compare multiple territories
```
POST /api/v1/population/compare
{
  "territorios": ["05001", "11001", "76001"],
  "anio": 2025,
  "area": "Total",
  "metricas": ["poblacion_total", "pct_urbana", "envejecimiento"]
}
```

### 6. Get demographic indicators
```
GET /api/v1/population/indicators?territorio_id=05001&anio=2025&area=Total
```

### 7. Search territories
```
GET /api/v1/population/territories?nivel=MUNICIPAL&search=Medellín&limit=100
```

---

## Frontend Components

### Filter Components

1. **TerritorySelect** (`/components/filters/TerritorySelect.tsx`)
   - Filters: nivel (ALL, DEPARTAMENTAL, MUNICIPAL)
   - Search: by name or code
   - Limit: 1000 results

2. **YearSlider** (`/components/filters/YearSlider.tsx`)
   - Range: 2018-2050
   - Step: 1 year
   - Default: 2025

3. **AreaSelect** (`/components/filters/AreaSelect.tsx`)
   - Options: Total, Cabecera Municipal, Centros Poblados y Rural Disperso
   - Default: Total

### Usage in Pages

- **Pirámide Page** (`/app/piramide/page.tsx`): Territory, Year, Area, Modo (simple/quinquenal)
- **Dashboard**: Territory, Year, Area filters
- **Comparación**: Multiple territories, Year, Area

---

## Notes

- All filter values are validated on the backend
- Invalid values will return 400 errors with descriptive messages
- Missing required parameters will return 400 errors
- No data found returns 404 errors
- All responses follow consistent error format:
  ```json
  {
    "code": "ERROR_CODE",
    "message": "Descriptive error message"
  }
  ```
