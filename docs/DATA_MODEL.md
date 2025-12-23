# Modelo de Datos

## Descripción General

Este documento describe el modelo de datos actual utilizado en el Módulo de Población DNP. La base de datos es PostgreSQL y utiliza SQLModel (Pydantic + SQLAlchemy) como ORM.

## Base de Datos: `poblacion_db`

---

## 1. Tablas de Territorio

### 1.1 `territorio`

Tabla principal para territorios geográficos (departamentos y municipios).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `territorio_id` | VARCHAR(5) | SI | Código DANE (2 dígitos = depto, 5 dígitos = municipio) |
| `nivel` | ENUM | | Nivel: `DEPARTAMENTAL`, `MUNICIPAL` |
| `dp` | VARCHAR(2) | | Código del departamento |
| `mpio` | VARCHAR(3) | | Código del municipio (solo para nivel municipal) |
| `nombre` | VARCHAR | | Nombre del territorio |
| `categoria` | VARCHAR | | Categoría: `ciudad_intermedia`, `aglomeracion`, etc. |
| `transicion_demografica` | VARCHAR | | Nivel de transición demográfica: `alto`, `medio`, `bajo` |

**Ejemplos:**
- `05` - Antioquia (Departamental)
- `05001` - Medellín (Municipal)
- `11` - Bogotá D.C. (Departamental)

---

## 2. Tablas de Población

### 2.1 `poblacion_edad`

Población por edad, sexo y área geográfica. **Soporta desglose urbano/rural.**

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `territorio_id` | VARCHAR(5) | SI | FK a territorio |
| `anio` | INTEGER | SI | Año (2018-2050) |
| `area_geografica` | VARCHAR(50) | SI | `Total`, `Cabecera Municipal`, `Centros Poblados y Rural Disperso` |
| `sexo` | VARCHAR(1) | SI | `H` (hombre), `M` (mujer), `T` (total) |
| `edad` | INTEGER | SI | Edad (0-100) |
| `mayores_100` | BOOLEAN | | True si es grupo "100 años y más" |
| `poblacion` | NUMERIC | | Cantidad de población |

**Índices:**
- `ix_poblacion_edad_lookup` en (territorio_id, anio, area_geografica, sexo, edad)
- `ix_poblacion_edad_territorio_anio` en (territorio_id, anio)

### 2.2 `poblacion_total`

Población total agregada por territorio, año y área. **Soporta desglose urbano/rural.**

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `territorio_id` | VARCHAR(5) | SI | FK a territorio |
| `anio` | INTEGER | SI | Año (2018-2050) |
| `area_geografica` | VARCHAR(50) | SI | Área geográfica |
| `pob_total` | NUMERIC | | Población total |
| `pob_hombres` | NUMERIC | | Población de hombres |
| `pob_mujeres` | NUMERIC | | Población de mujeres |
| `pct_urbana` | NUMERIC(5,4) | | Porcentaje urbano (solo cuando area=Total) |
| `pct_rural` | NUMERIC(5,4) | | Porcentaje rural (solo cuando area=Total) |

---

## 3. Tablas de Indicadores DANE

### 3.1 `dane_regions`

Regiones poblacionales DANE (23 regiones).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `region_code` | VARCHAR(10) | SI | Código de región (ej: `NAL`, `VDA`, `ACB`) |
| `region_name` | VARCHAR(100) | | Nombre de la región |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.2 `dane_departments`

Departamentos de Colombia (33).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `dept_code` | VARCHAR(10) | SI | Código del departamento (ej: `05`, `11`, `76`) |
| `dept_name` | VARCHAR(100) | | Nombre del departamento |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.3 `dane_municipalities`

Municipios de Colombia (1.122).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `muni_code` | VARCHAR(10) | SI | Código del municipio |
| `muni_name` | VARCHAR(100) | | Nombre del municipio |
| `dept_code` | VARCHAR(10) | | FK a dane_departments |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.4 `dane_fertility_indicators`

Indicadores de fecundidad por región (2018-2070).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID auto-incremental |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `year` | INTEGER | | Año |
| `area_type` | VARCHAR(50) | | Tipo de área (opcional) |
| `tgf` | NUMERIC(10,6) | | Tasa Global de Fecundidad |
| `age_rates` | JSON | | Tasas por edad: `{"10": 0.000096, "15": 0.027, ...}` |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.5 `dane_migration_indicators`

Indicadores de migración por región, sexo y tipo (2018-2070).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID auto-incremental |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `year` | INTEGER | | Año |
| `area_type` | VARCHAR(50) | | Tipo de área (opcional) |
| `sex` | VARCHAR(20) | | `Hombres` o `Mujeres` |
| `migration_type` | VARCHAR(30) | | `Internacional` o `Interna` |
| `age_values` | JSON | | Migración neta por edad: `{"0": 123.45, "20": 5678.9, ...}` |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.6 `dane_mortality_indicators`

Indicadores de mortalidad por región y sexo (2018-2070).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID auto-incremental |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `year` | INTEGER | | Año |
| `area_type` | VARCHAR(50) | | Tipo de área (opcional) |
| `sex` | VARCHAR(20) | | `Hombres` o `Mujeres` |
| `age_mortality_rates` | JSON | | Probabilidad de muerte (qx) por edad: `{"0": 0.012, ...}` |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.7 `dane_principal_indicators`

Indicadores demográficos principales por región (2018-2070).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID auto-incremental |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `year` | INTEGER | | Año |
| `area_type` | VARCHAR(50) | | Tipo de área (opcional) |
| `life_exp_male` | NUMERIC(6,2) | | Esperanza de vida - Hombres |
| `life_exp_female` | NUMERIC(6,2) | | Esperanza de vida - Mujeres |
| `life_exp_total` | NUMERIC(6,2) | | Esperanza de vida - Total |
| `infant_mortality_rate` | NUMERIC(10,6) | | Tasa de mortalidad infantil |
| `other_indicators` | JSON | | Otros indicadores: `{"tasa_bruta_natalidad": 15.67, ...}` |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 3.8 `dane_growth_indicators`

Indicadores de crecimiento poblacional por región (2018-2070).

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID auto-incremental |
| `region_code` | VARCHAR(10) | | FK a dane_regions |
| `year` | INTEGER | | Año |
| `area_type` | VARCHAR(50) | | Tipo de área (opcional) |
| `total_population` | INTEGER | | Población total |
| `growth_rate` | NUMERIC(10,6) | | Tasa de crecimiento |
| `natural_increase` | INTEGER | | Crecimiento natural (nacimientos - defunciones) |
| `net_migration` | INTEGER | | Migración neta |
| `other_metrics` | JSON | | Otras métricas |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

---

## 4. Tablas de Chat (Asistente IA)

### 4.1 `chat`

Sesiones de chat para el asistente IA.

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID de la sesión |
| `title` | VARCHAR | | Título del chat |
| `created_at` | TIMESTAMP | | Fecha de creación |
| `updated_at` | TIMESTAMP | | Fecha de actualización |

### 4.2 `chat_message`

Mensajes individuales del chat.

| Columna | Tipo | PK | Descripción |
|---------|------|:--:|-------------|
| `id` | SERIAL | SI | ID del mensaje |
| `chat_id` | INTEGER | | FK a chat |
| `role` | VARCHAR | | `user` o `assistant` |
| `content` | TEXT | | Contenido del mensaje |
| `metadata` | JSON | | Metadatos adicionales (SQL, visualización, etc.) |
| `created_at` | TIMESTAMP | | Fecha de creación |

---

## 5. Enumeraciones

### 5.1 `AreaGeografica`
- `Cabecera Municipal` - Área urbana
- `Centros Poblados y Rural Disperso` - Área rural
- `Total` - Total (urbano + rural)

### 5.2 `Sexo`
- `H` - Hombre
- `M` - Mujer
- `T` - Total

### 5.3 `NivelTerritorial`
- `DEPARTAMENTAL` - Nivel departamental
- `MUNICIPAL` - Nivel municipal

---

## 6. Diagrama Entidad-Relación

```
┌─────────────────────────────────────────────────────────────────┐
│                      TABLAS DE TERRITORIO                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │   territorio    │                                            │
│  ├─────────────────┤                                            │
│  │ territorio_id PK│◄───────────────────────────────────┐       │
│  │ nivel          │                                     │       │
│  │ dp             │                                     │       │
│  │ mpio           │                                     │       │
│  │ nombre         │                                     │       │
│  └─────────────────┘                                     │       │
│                                                          │       │
├─────────────────────────────────────────────────────────│───────┤
│                     TABLAS DE POBLACIÓN                  │       │
├─────────────────────────────────────────────────────────│───────┤
│                                                          │       │
│  ┌─────────────────┐    ┌─────────────────┐            │       │
│  │ poblacion_edad  │    │ poblacion_total │            │       │
│  ├─────────────────┤    ├─────────────────┤            │       │
│  │ territorio_id FK│────│ territorio_id FK│────────────┘       │
│  │ anio           │    │ anio           │                      │
│  │ area_geografica│    │ area_geografica│                      │
│  │ sexo           │    │ pob_total      │                      │
│  │ edad           │    │ pob_hombres    │                      │
│  │ poblacion      │    │ pob_mujeres    │                      │
│  └─────────────────┘    │ pct_urbana     │                      │
│                         │ pct_rural      │                      │
│                         └─────────────────┘                      │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                  TABLAS DE INDICADORES DANE                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │  dane_regions   │◄────────────────────────────────────┐      │
│  ├─────────────────┤                                     │      │
│  │ region_code PK  │                                     │      │
│  │ region_name     │                                     │      │
│  └─────────────────┘                                     │      │
│          ▲                                               │      │
│          │                                               │      │
│  ┌───────┴─────────┐                                     │      │
│  │                 │                                     │      │
│  │  ┌─────────────────────┐  ┌─────────────────────┐    │      │
│  │  │dane_fertility_indic │  │dane_migration_indic │    │      │
│  │  ├─────────────────────┤  ├─────────────────────┤    │      │
│  │  │ region_code FK      │  │ region_code FK      │────┘      │
│  │  │ year               │  │ year               │             │
│  │  │ tgf                │  │ sex                │             │
│  │  │ age_rates (JSON)   │  │ migration_type     │             │
│  │  └─────────────────────┘  │ age_values (JSON)  │             │
│  │                           └─────────────────────┘             │
│  │                                                               │
│  │  ┌─────────────────────┐  ┌─────────────────────┐            │
│  │  │dane_mortality_indic │  │dane_principal_indic │            │
│  │  ├─────────────────────┤  ├─────────────────────┤            │
│  └──│ region_code FK      │  │ region_code FK      │            │
│     │ year               │  │ year               │             │
│     │ sex                │  │ life_exp_*         │             │
│     │ age_mortality(JSON)│  │ other_indicators   │             │
│     └─────────────────────┘  └─────────────────────┘             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Cobertura de Datos

| Tipo de Dato | Nivel Geográfico | Rango de Años | Urbano/Rural |
|--------------|------------------|---------------|:------------:|
| Población por edad | Municipal | 2018-2050 | SI |
| Totales de población | Municipal | 2018-2050 | SI |
| Fecundidad (TGF) | Región DANE (23) | 2018-2070 | NO |
| Migración | Región DANE (23) | 2018-2070 | NO |
| Mortalidad (qx) | Región DANE (23) | 2018-2070 | NO |
| Esperanza de vida | Región DANE (23) | 2018-2070 | NO |
| Indicadores crecimiento | Región DANE (23) | 2018-2070 | NO |

---

## 8. Mapeo de Indicadores - Nueva API

### Disponibles en Nueva API

| Indicador Actual | Código Nueva API | Descripción |
|------------------|------------------|-------------|
| Población total | CV-01-1c2018 | Población total del municipio |
| Población hombres | CV-01-15c2018 | Población hombres |
| Población mujeres | CV-01-16c2018 | Población mujeres |
| Tasa crecimiento | CV-01-17c2018 | Tasa de Crecimiento Poblacional |
| TGF | CV-01-18c2018 | Tasa Global de Fecundidad |
| Fecundidad por edad | CV-01-19c2018 | Tasas de Fecundidad por Edad |
| Migración internacional | CV-01-20c2018 | Saldo Neto Migratorio Internacional |
| Migración interna | CV-01-21c2018 | Saldo Neto Migratorio Interno |
| Probabilidad muerte (qx) | CV-01-22c2018 | Probabilidad de Muerte por Edad |
| Esperanza vida H | CV-01-23c2018 | Esperanza de Vida al Nacer - Hombres |
| Esperanza vida M | CV-01-24c2018 | Esperanza de Vida al Nacer - Mujeres |
| Esperanza vida Total | CV-01-25c2018 | Esperanza de Vida al Nacer - Total |
| Crecimiento natural | CV-01-262018 | Crecimiento Natural |
| Saldo migratorio neto | CV-01-272018 | Saldo Migratorio Neto |
| Bono demog. niños | CV-01-282018 | Bono demográfico niños y adolescentes |
| Bono demog. PET | CV-01-292018 | Bono demográfico población en edad de trabajar |
| Bono demog. mayores | CV-01-302018 | Bono demográfico adultos mayores |

### NO Disponibles en Nueva API (Faltantes)

| Indicador | Descripción | Notas |
|-----------|-------------|-------|
| Tasa Bruta Natalidad (TBN) | Nacimientos por cada 1.000 habitantes | Solicitar al desarrollador API |
| Tasa Bruta Mortalidad (TBM) | Defunciones por cada 1.000 habitantes | Solicitar al desarrollador API |
| Distribución Urbano/Rural | % urbano vs % rural | Puede derivarse si CV-01-1c2018 tiene desglose por área |

---

## 9. Indicadores que Requieren Desglose Urbano/Rural

Los siguientes indicadores actualmente soportan desglose por área geográfica (Cabecera Municipal / Centros Poblados y Rural Disperso / Total):

1. **CV-01-1c2018** - Población total del municipio
2. **CV-01-15c2018** - Población hombres
3. **CV-01-16c2018** - Población mujeres
4. **CV-01-17c2018** - Tasa de Crecimiento Poblacional
5. **CV-01-282018** - Bono demográfico niños y adolescentes
6. **CV-01-292018** - Bono demográfico población en edad de trabajar
7. **CV-01-302018** - Bono demográfico adultos mayores

---

*Última actualización: Diciembre 2024*
