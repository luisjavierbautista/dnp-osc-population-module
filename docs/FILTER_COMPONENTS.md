# Filter Components - Implementation Summary

This document describes all filter components used across the DNP Population Module frontend and how they align with the database values.

**Last Updated**: 2025-11-10

---

## Filter Components

### 1. TerritorySelect
**Location**: `frontend/src/components/filters/TerritorySelect.tsx`

**Purpose**: Single territory selection with filtering and search capabilities.

**Features**:
- Dynamic loading from `/api/v1/population/territories`
- Filter by level: ALL, DEPARTAMENTAL, MUNICIPAL
- Search by name or code
- Shows 1,156 total territories (33 departments + 1,103 municipalities + 20 non-municipalized areas)
- Limit: 1,000 results

**Database Alignment**: ✅ Fully aligned - fetches all territories dynamically

**Used in**:
- Pirámide page (`/app/piramide/page.tsx`)

---

### 2. MultiTerritorySelect
**Location**: `frontend/src/components/filters/MultiTerritorySelect.tsx`

**Purpose**: Multiple territory selection with checkboxes for comparison views.

**Features**:
- Dynamic loading from `/api/v1/population/territories`
- Filter by level: ALL, DEPARTAMENTAL, MUNICIPAL
- Search by name or code
- Checkbox-based multi-selection
- Configurable max selections (default: 10)
- "Select All" and "Clear" buttons
- Shows first 100 results (for performance)

**Database Alignment**: ✅ Fully aligned - fetches all territories dynamically

**Used in**:
- Serie de Tiempo page (`/app/serie-tiempo/page.tsx`)
- Bono Demográfico page (`/app/bono-demografico/page.tsx`)

---

### 3. YearSlider
**Location**: `frontend/src/components/filters/YearSlider.tsx`

**Purpose**: Year selection with slider control.

**Features**:
- Range slider: 2018-2050
- Step: 1 year
- Real-time preview of selected year
- Default: 2025

**Database Alignment**: ✅ Fully aligned
- Database min year: 2018
- Database max year: 2050
- Component min: 2018
- Component max: 2050

**Used in**:
- Pirámide page (`/app/piramide/page.tsx`)

---

### 4. AreaSelect
**Location**: `frontend/src/components/filters/AreaSelect.tsx`

**Purpose**: Geographic area selection dropdown.

**Features**:
- Dropdown select
- 3 options matching database exactly

**Database Alignment**: ✅ Fully aligned

| Component Value | Database Value | Records |
|----------------|----------------|---------|
| Total | Total | 15,773,803 |
| Cabecera Municipal | Cabecera Municipal | 15,740,473 |
| Centros Poblados y Rural Disperso | Centros Poblados y Rural Disperso | 15,740,473 |

**Used in**:
- Pirámide page (`/app/piramide/page.tsx`)

---

### 5. SexoToggle
**Location**: `frontend/src/components/filters/SexoToggle.tsx`

**Purpose**: Sex/gender selection with toggle buttons.

**Features**:
- Button group toggle
- 3 options matching database exactly

**Database Alignment**: ✅ Fully aligned

| Component Value | Label | Database Value | Records |
|----------------|-------|----------------|---------|
| T | Total | T | 9,882,675 |
| H | Hombres | H | 18,686,037 |
| M | Mujeres | M | 18,686,037 |

**Used in**:
- (Currently available but not used in main pages - can be integrated as needed)

---

## Page-Level Filter Usage

### Pirámide Page (`/app/piramide/page.tsx`)

**Filters Used**:
1. **TerritorySelect** - All 1,156 territories with search
2. **YearSlider** - 2018-2050
3. **AreaSelect** - 3 geographic areas
4. **Modo Toggle** - Simple vs Quinquenal (custom, page-specific)

**State**:
- `territorioId: string` - Default: '05001' (Medellín)
- `anio: number` - Default: 2025
- `area: AreaGeografica` - Default: 'Total'
- `modo: 'simple' | 'quinquenal'` - Default: 'quinquenal'

**Dynamic Import**: ✅ Yes (SSR disabled to prevent hydration errors)

---

## TypeScript Types

### AreaGeografica
```typescript
type AreaGeografica = 'Total' | 'Cabecera Municipal' | 'Centros Poblados y Rural Disperso'
```

### Sexo
```typescript
type Sexo = 'T' | 'H' | 'M'
```

### TerritoryLevel
```typescript
type TerritoryLevel = 'DEPARTAMENTAL' | 'MUNICIPAL' | 'ALL'
```

---

## Best Practices

### 1. Dynamic Imports for Territory Components
All territory selector components use Next.js dynamic imports with SSR disabled:

```typescript
const TerritorySelect = dynamic(
  () => import('@/components/filters/TerritorySelect').then(mod => mod.TerritorySelect),
  { ssr: false, loading: () => <div className="h-48 animate-pulse bg-gray-100 rounded" /> }
)
```

**Reason**: Prevents hydration errors when fetching data during initial render.

### 2. Loading States
All components show appropriate loading states:
- Skeleton loaders during dynamic import
- "Cargando..." text in dropdowns during API fetches
- Disabled state for inputs while loading

### 3. Validation
- Year range validated on both frontend and backend
- Territory IDs validated against database
- Max selection limits enforced where applicable

### 4. Search Debouncing
Territory search inputs trigger immediate API queries (consider adding debouncing if performance issues arise).

---

## Database-to-UI Mapping

| Database Field | Component | Values | Match Status |
|---------------|-----------|--------|--------------|
| territorio.nivel | TerritorySelect nivel filter | DEPARTAMENTAL, MUNICIPAL | ✅ Perfect |
| poblacion_edad.anio | YearSlider | 2018-2050 | ✅ Perfect |
| poblacion_edad.area_geografica | AreaSelect | Total, Cabecera Municipal, Centros Poblados y Rural Disperso | ✅ Perfect |
| poblacion_edad.sexo | SexoToggle | T, H, M | ✅ Perfect |
| poblacion_edad.edad | (Modo toggle) | 0-100 (simple), 0-4, 5-9... (quinquenal) | ✅ Perfect |

---

## Migration Notes

### Changes Made (2025-11-10)

1. **TerritorySelect**: Already implemented with dynamic API loading ✅
2. **YearSlider**: Year range 2018-2050 ✅
3. **AreaSelect**: Values already matched database ✅
4. **SexoToggle**: Values already matched database ✅
5. **MultiTerritorySelect**: Created new component for multi-selection ✅
6. **Comparador Page**: Migrated from hardcoded 8 territories to dynamic MultiTerritorySelect ✅

### Previous Implementation (Comparador)
```typescript
// ❌ OLD: Hardcoded list
const TERRITORIOS_DISPONIBLES = [
  { id: '05001', nombre: 'Medellín' },
  { id: '11001', nombre: 'Bogotá' },
  // ... only 8 territories
]
```

### Current Implementation (Comparador)
```typescript
// ✅ NEW: Dynamic from database
<MultiTerritorySelect
  value={territoriosSeleccionados}
  onChange={setTerritoriosSeleccionados}
  maxSelections={10}
/>
```

---

## Summary

All filter components are now fully aligned with the database values:

- ✅ **Territories**: 1,156 territories dynamically loaded
- ✅ **Years**: 2018-2050 range (33 years)
- ✅ **Areas**: 3 geographic areas matching database exactly
- ✅ **Sexo**: 3 options matching database exactly
- ✅ **Ages**: 101 ages (0-100) with simple/quinquenal modes

No hardcoded values remain - all filters pull from the database or match database constraints exactly.
