# DNP Population Module - Implementation Plan
## Comprehensive Improvement Roadmap

**Project**: Módulo de Población - Observatorio del Sistema de Ciudades (DNP)
**Date**: November 2025
**Authors**: Luis Javier & Yurley feedback consolidation

---

## 📊 Data Sources Analysis

### Current Data
- **Population Data**: DANE 2018-2050 (departments) / 2018-2042 (municipalities)
- **Tables**: `territorio`, `poblacion_edad`, `poblacion_total`
- **Coverage**: 33 departments + 1,103 municipalities + 20 non-municipalized areas (ANM)

### New Data to Load

#### 1. **DANE Regiones Poblacionales**
**File**: `/home/luisjavier/Downloads/Regiones DANE.xlsx`

**Structure**:
- **Columns**: SIGLA DE LA REGIÓN, REGIÓN, DP, DPNOM, MPIO, DPMP, ÁREA GEOGRÁFICA
- **Regions**: 23 population regions (VDA, AQU, SBC, BQR, BMG, BGR, ACB, CRI, SSS, GSV, EGS, ATN, ECF, AZN, VRC, NPA, APC, AMG, MTC, CCR, BMR, CLR)
- **Format**: Municipality-level mapping to regions
- **Areas**: Cabecera Municipal, Centros Poblados y Rural Disperso

**Database Schema**:
```sql
CREATE TABLE regiones_dane (
    id SERIAL PRIMARY KEY,
    region_sigla TEXT NOT NULL,
    region_nombre TEXT NOT NULL,
    territorio_id TEXT NOT NULL REFERENCES territorio(territorio_id),
    area_geografica TEXT NOT NULL,
    UNIQUE(region_sigla, territorio_id, area_geografica)
);
CREATE INDEX idx_regiones_sigla ON regiones_dane(region_sigla);
CREATE INDEX idx_regiones_territorio ON regiones_dane(territorio_id);
```

#### 2. **DANE Demographic Change Indicators**
**Location**: `/home/luisjavier/Downloads/DANE Indicators/`

##### A) Fertility (Fecundidad)
**File**: `DCD-Fec-EstNal-Reg-2018-2070_VP (1).xlsx`
**Sheet**: "Fecundidad" (skiprows=9)

**Structure**:
- **Columns**: SIGLA DE LA REGIÓN, TERRITORIO, AÑO, Área Geográfica, TGF, [15-49] (35 age columns)
- **Period**: 2018-2070 (national), 2018-2050 (regional)
- **Indicator**: TGF (Tasa Global de Fecundidad) + Age-specific fertility rates (15-49 years)

**Schema**:
```sql
CREATE TABLE indicadores_fecundidad (
    id SERIAL PRIMARY KEY,
    region_sigla TEXT,
    territorio_nombre TEXT,
    anio INTEGER NOT NULL,
    area_geografica TEXT NOT NULL,
    tgf NUMERIC(10,6),  -- Tasa Global de Fecundidad
    edad_15 NUMERIC(10,8),
    edad_16 NUMERIC(10,8),
    -- ... edad_17 through edad_48
    edad_49 NUMERIC(10,8),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_fec_region_anio ON indicadores_fecundidad(region_sigla, anio);
```

##### B) Mortality (Mortalidad)
**File**: `DCD-Mor-EstSexNal-Reg-2018-2070_VP (1).xlsx`
**Sheet**: "Mortalidad" (skiprows=9)

**Structure**:
- **Columns**: SIGLA DE LA REGIÓN, TERRITORIO, AÑO, Área Geográfica, Sexo, [0-100] (101 age columns)
- **Period**: 2018-2070 (national), 2018-2050 (regional)
- **Sex**: Hombres, Mujeres
- **Indicator**: Age-specific mortality rates (qx - probability of death)

**Schema**:
```sql
CREATE TABLE indicadores_mortalidad (
    id SERIAL PRIMARY KEY,
    region_sigla TEXT,
    territorio_nombre TEXT,
    anio INTEGER NOT NULL,
    area_geografica TEXT NOT NULL,
    sexo TEXT NOT NULL,  -- 'Hombres', 'Mujeres'
    edad_0 NUMERIC(10,8),
    edad_1 NUMERIC(10,8),
    -- ... edad_2 through edad_99
    edad_100 NUMERIC(10,8),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_mor_region_anio_sexo ON indicadores_mortalidad(region_sigla, anio, sexo);
```

##### C) Migration (Migración)
**File**: `DCD-Mig-EstSexNal-Reg-2018-2070_VP (1).xlsx`
**Sheet**: "Migración" (skiprows=9)

**Structure**: Similar to mortality (by age and sex)

##### D) Principal Indicators - Demographic Change
**File**: `DCD-PrinInd-camDemNac-2018-2070_VP (1).xlsx`
**Sheet**: "Cambio Demográfico" (skiprows=9)

**Potential Indicators**:
- Life expectancy (Esperanza de vida)
- Dependency ratio components
- Aging index
- Other demographic transition indicators

##### E) Principal Indicators - Population Growth
**File**: `DCD-PrinInd-crecPobNac-2018-2070_VP (1).xlsx`
**Sheet**: "Crecimiento Poblacional" (skiprows=9)

---

## 🎯 Implementation Phases

### PHASE 1: Foundation & Data (2-3 weeks)

#### 1.1 Database Schema Updates
**Priority**: 🔴 Critical

**Tasks**:
- [ ] Create `regiones_dane` table
- [ ] Create `indicadores_fecundidad` table
- [ ] Create `indicadores_mortalidad` table
- [ ] Create `indicadores_migracion` table
- [ ] Create `indicadores_demograficos` table (principal indicators)
- [ ] Create `poblacion_nacional` table (national aggregations)
- [ ] Add migration scripts (Alembic)

**Files to Create**:
- `backend/app/models/regiones.py`
- `backend/app/models/indicadores.py`
- `backend/alembic/versions/XXX_add_dane_indicators.py`

#### 1.2 ETL Scripts for New Data
**Priority**: 🔴 Critical

**Tasks**:
- [ ] ETL: Load Regiones DANE (`etl/scripts/load_regiones_dane.py`)
- [ ] ETL: Load Fertility indicators (`etl/scripts/load_fecundidad.py`)
- [ ] ETL: Load Mortality indicators (`etl/scripts/load_mortalidad.py`)
- [ ] ETL: Load Migration indicators (`etl/scripts/load_migracion.py`)
- [ ] ETL: Load Principal Indicators (`etl/scripts/load_indicadores_principales.py`)
- [ ] ETL: Calculate and store national totals (`etl/scripts/calculate_national_totals.py`)
- [ ] Validation scripts for all new data
- [ ] Data quality checks

**Implementation Details**:
```python
# Example ETL structure
def load_fecundidad_dane():
    """Load DANE fertility indicators."""
    file_path = "/path/to/DCD-Fec-EstNal-Reg-2018-2070_VP.xlsx"
    df = pd.read_excel(file_path, sheet_name='Fecundidad', skiprows=9)
    df = df.dropna(subset=['SIGLA DE LA REGIÓN', 'AÑO'])

    # Transform wide to long format if needed
    # Insert into database
    # Validate data
```

#### 1.3 Backend API Endpoints
**Priority**: 🔴 Critical

**New Endpoints**:
```python
# Regiones
GET  /api/v1/regiones/                    # List all regions
GET  /api/v1/regiones/{sigla}             # Region details
GET  /api/v1/regiones/{sigla}/territorios # Territories in region

# National aggregations
GET  /api/v1/national/pyramid             # National pyramid
GET  /api/v1/national/total               # National totals
GET  /api/v1/national/indicators          # National indicators

# DANE Indicators
GET  /api/v1/indicators/fertility         # Fertility indicators
GET  /api/v1/indicators/mortality         # Mortality indicators (life tables)
GET  /api/v1/indicators/migration         # Migration indicators
GET  /api/v1/indicators/demographic       # Demographic change indicators
GET  /api/v1/indicators/life-expectancy   # Life expectancy
```

**Files to Create**:
- `backend/app/api/v1/endpoints/regiones.py`
- `backend/app/api/v1/endpoints/national.py`
- `backend/app/api/v1/endpoints/indicators.py`
- `backend/app/services/regiones_service.py`
- `backend/app/services/national_service.py`
- `backend/app/services/indicators_service.py`
- `backend/app/schemas/regiones.py`
- `backend/app/schemas/indicators.py`

---

### PHASE 2: Global Improvements (1-2 weeks)

#### 2.1 Data Source Attribution
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Add DANE source footer component to all pages
- [ ] Display: "Fuente: DANE - Proyecciones de Población 2018-2050"
- [ ] Display: "Actualizado: 30 de Julio 2025"
- [ ] Make it configurable via backend config

**Files**:
- `frontend/src/components/layout/DataSourceFooter.tsx` (new)
- `frontend/src/components/layout/MainLayout.tsx` (update)
- `backend/app/core/config.py` (add DANE_SOURCE_DATE)

#### 2.2 Territory Display Format (DIVIPOLA - Name (Dept))
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Update all territory selectors to show: `DIVIPOLA - Municipality (DEPT)`
- [ ] Example: `05001 - Medellín (ANT)`, `11001 - Bogotá D.C. (BOG)`
- [ ] Create department abbreviation mapping
- [ ] Update TerritorySelect component
- [ ] Update MultiTerritorySelect component

**Files**:
- `frontend/src/components/filters/TerritorySelect.tsx`
- `frontend/src/components/filters/MultiTerritorySelect.tsx`
- `frontend/src/utils/territoryFormatter.ts` (new)

```typescript
// Example format function
const formatTerritory = (territory) => {
  const deptAbbr = getDepartmentAbbreviation(territory.dp);
  return `${territory.territorio_id} - ${territory.nombre} (${deptAbbr})`;
};
```

#### 2.3 Global Glossary Modal
**Priority**: 🟡 Medium
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Create global glossary modal component
- [ ] Add glossary button to main navigation
- [ ] Populate with demographic terms:
  - Tasa de dependencia
  - Índice de envejecimiento
  - TGF (Tasa Global de Fecundidad)
  - Esperanza de vida
  - Tablas de mortalidad
  - Bono demográfico
  - Población juvenil/activa/mayor
  - Regiones poblacionales DANE
- [ ] Support search/filter in glossary
- [ ] Link terms to relevant sections

**Files**:
- `frontend/src/components/modals/GlossaryModal.tsx` (new)
- `frontend/src/data/glossaryTerms.ts` (new)
- `frontend/src/components/layout/MainLayout.tsx` (add button)

---

### PHASE 3: Pyramid Module Improvements (1 week)

#### 3.1 Invert Pyramid Y-Axis
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Invert Y-axis so ages increase from bottom to top
- [ ] Traditional pyramid format: youngest at bottom, oldest at top
- [ ] Update Recharts configuration

**File**: `frontend/src/app/piramide/page.tsx`

```typescript
// Update chart config
yAxisId="age"
reversed={true}  // Add this
```

#### 3.2 Age Grouping Mode
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Change "Modo" selector to "Agrupación de Edad"
- [ ] Options:
  - **Simple**: Individual years (0, 1, 2, ... 100)
  - **Quinquenal**: 5-year groups (0-4, 5-9, 10-14, ...)
  - **Grupos estándar**: Standard demographic groups (0-14, 15-64, 65+)
- [ ] Create age grouping utility functions
- [ ] Update pyramid visualization to aggregate by selected grouping

**Files**:
- `frontend/src/app/piramide/page.tsx`
- `frontend/src/utils/ageGrouping.ts` (new)
- `backend/app/services/population_service.py` (add grouping option)

```typescript
// Age grouping options
const AGE_GROUPING_OPTIONS = [
  { value: 'simple', label: 'Año a año' },
  { value: 'quinquenal', label: 'Quinquenal (0-4, 5-9, ...)' },
  { value: 'standard', label: 'Grupos estándar (0-14, 15-64, 65+)' }
];
```

#### 3.3 Align Pyramid Bars
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Ensure left (male) and right (female) bars are properly aligned
- [ ] Fix any vertical alignment issues
- [ ] Make bars symmetric and visually balanced

**File**: `frontend/src/app/piramide/page.tsx`

#### 3.4 Show Percentages
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Tasks**:
- [ ] Add toggle: "Mostrar en números absolutos / porcentaje"
- [ ] Calculate: (age group population / total population) × 100
- [ ] Update chart to display percentages when toggled
- [ ] Update tooltips to show both values
- [ ] Update axis labels accordingly

**File**: `frontend/src/app/piramide/page.tsx`

```typescript
const [displayMode, setDisplayMode] = useState<'absolute' | 'percentage'>('absolute');

// Calculate percentage
const calculatePercentage = (agePopulation, totalPopulation) => {
  return (agePopulation / totalPopulation) * 100;
};
```

#### 3.5 Pyramid Comparison (Side-by-Side)
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Add comparison mode toggle
- [ ] Allow selection of comparison type:
  - vs. otro territorio
  - vs. otro período (same territory, different year)
  - vs. nacional
- [ ] Display two pyramids side-by-side
- [ ] Synchronize scales between pyramids
- [ ] Highlight differences

**Files**:
- `frontend/src/app/piramide/page.tsx`
- `frontend/src/components/charts/PyramidComparison.tsx` (new)

---

### PHASE 4: Indicators Module (New) (2 weeks)

#### 4.1 Rename Comparador → Indicadores
**Priority**: ✅ Completed
**User**: Luis Javier, Yurley

**Tasks**:
- [x] Created `/indicadores` route for DANE indicators
- [x] Updated navigation menu
- [x] Removed `/comparador` page (comparison now only in Pirámide)

**Files**:
- `frontend/src/app/indicadores/page.tsx`
- `frontend/src/components/layout/MainLayout.tsx`

#### 4.2 Display DANE Demographic Indicators
**Priority**: 🔴 Critical
**User**: Luis Javier, Yurley

**Indicators to Display**:

1. **Mortality Indicators**:
   - Life tables (Tablas de vida)
   - Mortality rates by age and sex (qx)
   - Life expectancy (Esperanza de vida) - total, at birth, by age
   - Infant mortality rate

2. **Fertility Indicators**:
   - TGF (Tasa Global de Fecundidad)
   - Age-specific fertility rates (15-49)
   - Reproductive age population

3. **Migration Indicators**:
   - Net migration rates
   - Migration by age and sex
   - Migration balance

4. **Demographic Change Indicators**:
   - Dependency ratio (already calculated)
   - Aging index (already calculated)
   - Population growth rate
   - Natural increase rate
   - Crude birth rate
   - Crude death rate

**Layout**:
```
+-------------------------------------------+
|  [Territory Selector]  [Year Range]       |
|  [Indicator Selector]                     |
+-------------------------------------------+
|                                           |
|  📊 Chart Visualization                   |
|     (Line chart for time series)          |
|                                           |
+-------------------------------------------+
|  📋 Summary Stats                         |
|     Current Value | Change | Trend        |
+-------------------------------------------+
```

**Files**:
- `frontend/src/app/indicadores/page.tsx`
- `frontend/src/components/charts/IndicatorChart.tsx` (new)
- `frontend/src/components/indicators/IndicatorSelector.tsx` (new)
- `frontend/src/services/indicatorsApi.ts` (new)

#### 4.3 Chart Display (Replace Table)
**Priority**: 🔴 Critical
**User**: Luis Javier

**Tasks**:
- [ ] Replace table view with interactive charts
- [ ] Use Recharts LineChart for time series
- [ ] Support multiple indicators on same chart
- [ ] Add download chart as PNG option
- [ ] Add export data as CSV option

**File**: `frontend/src/components/charts/IndicatorChart.tsx`

```typescript
<ResponsiveContainer width="100%" height={400}>
  <LineChart data={indicatorData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="anio" />
    <YAxis />
    <Tooltip />
    <Legend />
    <Line type="monotone" dataKey="value" stroke="#8884d8" />
  </LineChart>
</ResponsiveContainer>
```

---

### PHASE 5: Regional View Module (New) (1-2 weeks)

#### 5.1 Create Separate Regional Analysis View
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Create new `/regiones` route
- [ ] Add to main navigation
- [ ] Display 23 DANE population regions
- [ ] Region selector with map visualization
- [ ] Regional statistics dashboard
- [ ] Regional demographic indicators
- [ ] Compare regions

**Structure**:
```
/regiones
  ├── Region Selector (23 regions)
  ├── Region Map (highlight selected region)
  ├── Regional Stats Dashboard
  │   ├── Total population
  │   ├── Urban/rural distribution
  │   ├── Demographic indicators
  │   └── Municipalities in region
  └── Regional Comparison Tool
```

**Files**:
- `frontend/src/app/regiones/page.tsx` (new)
- `frontend/src/components/map/RegionMap.tsx` (new)
- `frontend/src/components/regiones/RegionSelector.tsx` (new)
- `frontend/src/components/regiones/RegionStats.tsx` (new)

#### 5.2 DANE Population Regions Integration
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Implement region-based filtering across all modules
- [ ] Add "Ver por región" toggle to existing views
- [ ] Allow pyramid/indicators by region
- [ ] Regional aggregations in API

---

### PHASE 6: Bono Demográfico Module Updates (1 week)

#### 6.1 Rename Index → Dependency Ratio
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Change all references from "índice" to "tasa de dependencia"
- [ ] Update chart labels
- [ ] Update tooltips and descriptions

**File**: `frontend/src/app/bono-demografico/page.tsx`

#### 6.2 Update Age Group Terminology
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Change "población infantil" → "población juvenil" or "población menor"
- [ ] Update all labels, charts, and descriptions
- [ ] Maintain consistency: Juvenil (0-14), Activa (15-64), Mayor (65+)

**File**: `frontend/src/app/bono-demografico/page.tsx`

#### 6.3 Complete Time Series with Quinquenal Toggle
**Priority**: 🟡 Medium
**User**: Luis Javier

**Tasks**:
- [ ] Display all available years (2018-2050 dept, 2018-2042 muni)
- [ ] Add toggle: "Mostrar por año / quinquenal"
- [ ] **Quinquenal**: Show only years ending in 0 or 5 (2020, 2025, 2030, ...)
- [ ] **Anual**: Show all years
- [ ] Apply to all charts in the module

**File**: `frontend/src/app/bono-demografico/page.tsx`

```typescript
const [timeSeriesMode, setTimeSeriesMode] = useState<'annual' | 'quinquennial'>('quinquennial');

const filterYears = (years, mode) => {
  if (mode === 'quinquennial') {
    return years.filter(year => year % 5 === 0);
  }
  return years;
};
```

---

### PHASE 7: Map Module Updates (1 week)

#### 7.1 Regional View in Map
**Priority**: 🟡 Medium

**Tasks**:
- [ ] Add toggle: "Ver por departamento / Ver por región"
- [ ] Display 23 DANE regions on map
- [ ] Color regions by selected indicator
- [ ] Regional boundaries overlay

**File**: `frontend/src/app/mapa/page.tsx`

---

## 📋 Implementation Priority Summary

### 🔴 **CRITICAL (Start Immediately)**
1. Database schema for regions and indicators
2. ETL scripts for DANE data
3. National aggregations calculation
4. Data source attribution (footer)
5. Territory display format (DIVIPOLA - Name (Dept))
6. Pyramid invert Y-axis
7. Pyramid age grouping mode
8. Pyramid show percentages
9. Rename Comparador → Indicadores
10. Display DANE indicators with charts

### 🟡 **MEDIUM (After Critical)**
11. Global glossary modal
12. Pyramid comparison side-by-side
13. Pyramid bar alignment
14. Regional view module
15. DANE regions integration
16. Bono Demográfico terminology updates
17. Complete time series with quinquenal toggle

### 🟢 **LOWER (Nice to Have)**
18. Map regional view
19. Advanced indicator calculations
20. Additional visualizations

---

## 🗓️ Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Foundation & Data | 2-3 weeks | None |
| Phase 2: Global Improvements | 1-2 weeks | Phase 1 (partial) |
| Phase 3: Pyramid Improvements | 1 week | None |
| Phase 4: Indicators Module | 2 weeks | Phase 1 complete |
| Phase 5: Regional View | 1-2 weeks | Phase 1 complete |
| Phase 6: Bono Demográfico | 1 week | None |
| Phase 7: Map Updates | 1 week | Phase 1 complete |

**Total Estimated Time**: 8-11 weeks for complete implementation

---

## 📦 Deliverables Checklist

### Database
- [ ] New tables created and migrated
- [ ] All DANE data loaded and validated
- [ ] National aggregations calculated
- [ ] Indexes optimized

### Backend
- [ ] All new API endpoints implemented
- [ ] Services for regions, national, indicators
- [ ] Updated schemas
- [ ] API documentation updated

### Frontend
- [ ] All modules updated per requirements
- [ ] New Regional view created
- [ ] Indicators module restructured
- [ ] Global components (footer, glossary)
- [ ] Territory formatters updated
- [ ] All charts use new display modes

### Documentation
- [ ] ETL process documented
- [ ] API documentation updated
- [ ] User guide created
- [ ] Glossary populated
- [ ] README updated

### Testing
- [ ] Backend unit tests
- [ ] Frontend component tests
- [ ] Integration tests
- [ ] Data validation tests
- [ ] User acceptance testing

---

## 🎯 Success Metrics

1. **Data Quality**: 100% of DANE indicator data loaded successfully
2. **Performance**: All pages load < 2 seconds
3. **User Experience**: Glossary terms cover all key concepts
4. **Regional Coverage**: All 23 DANE regions properly mapped
5. **National Calculations**: National aggregations match sum of departmental data

---

## 🚀 Getting Started

### Immediate Next Steps:
1. Review this plan with stakeholders
2. Prioritize phases based on business needs
3. Set up development branch: `feature/dane-improvements`
4. Begin Phase 1: Database schema design
5. Create ETL scripts for Regiones DANE
6. Start parallel work on quick wins (data source footer, territory formatting)

### Questions for Stakeholders:
- Are there specific indicators from the DANE files that are higher priority?
- Should we implement phases sequentially or in parallel?
- What is the target release date?
- Are there any missing requirements from user feedback?

---

**Document Version**: 1.0
**Last Updated**: November 18, 2025
**Next Review**: After Phase 1 completion
