# DNP Population Module - Quick Improvements Summary

## 📋 Consolidated Feedback from Luis Javier & Yurley

### 🌍 **GLOBAL (All Pages)**
- ✅ Add DANE source and date footer: "Fuente: DANE - Proyecciones 2018-2050, Actualizado: 30 Julio 2025"
- ✅ Change territory display format to: `DIVIPOLA - Name (Dept)` e.g., `05001 - Medellín (ANT)`
- ✅ Create global glossary modal (accessible from all pages)
- ✅ Add national-level calculations (currently only territorial)

---

### 📐 **PIRÁMIDE (Population Pyramid)**
- ✅ **Invert Y-axis** (ages bottom to top) ⭐ Both users
- ✅ **Change "Modo" to age grouping**: Simple (año a año) / Quinquenal (0-4, 5-9...) / Standard (0-14, 15-64, 65+) ⭐ Both users
- ✅ **Show percentages**: Toggle between absolute numbers and % of total population ⭐ Both users
- ⚠️ Align pyramid bars (left/right symmetry)
- ⚠️ Add comparison mode (side-by-side): vs territory / vs year / vs national

---

### 📊 **COMPARADOR → INDICADORES (Rename & Restructure)**
- ✅ **Rename module**: "Comparador" → "Indicadores" ⭐ Both users
- ✅ **Add DANE Demographic Indicators**: ⭐ Both users
  - Life tables (Tablas de vida)
  - Mortality rates (Tasas de mortalidad)
  - Fertility rates (Tasas de fecundidad)
  - Migration rates (Tasas de migración)
  - Life expectancy (Esperanza de vida)
- ✅ **Change to chart display** (replace table)
- ⚠️ Integrate DANE population regions (23 regions)
- ⚠️ Create separate **Regional View** module

---

### 💰 **BONO DEMOGRÁFICO**
- ⚠️ Rename "índice" → "tasa de dependencia"
- ⚠️ Change "población infantil" → "población juvenil" or "población menor"
- ⚠️ Show all years with quinquenal toggle (2020, 2025, 2030... vs all years)

---

## 🎯 **Priority Levels**

### 🔴 **CRITICAL** (Do First - 2-3 weeks)
1. Load DANE indicator data (Fertility, Mortality, Migration, Indicators)
2. Load DANE regions (23 population regions)
3. Calculate national aggregations
4. Add data source footer
5. Fix territory display format (DIVIPOLA - Name (Dept))
6. Pyramid: Invert Y-axis
7. Pyramid: Age grouping mode
8. Pyramid: Show percentages
9. Rename Comparador → Indicadores
10. Display DANE indicators with charts

### 🟡 **MEDIUM** (Do Second - 2-3 weeks)
11. Global glossary modal
12. Pyramid comparison (side-by-side)
13. Regional view module
14. Bono Demográfico terminology updates
15. Quinquenal time series toggle

### 🟢 **LOWER** (Nice to Have - 1-2 weeks)
16. Pyramid bar alignment fixes
17. Map regional view
18. Advanced visualizations

---

## 📊 **New Data Sources**

### Data Files Location
- **Regiones DANE**: `/home/luisjavier/Downloads/Regiones DANE.xlsx`
- **DANE Indicators**: `/home/luisjavier/Downloads/DANE Indicators/`
  - Fertility (Fecundidad)
  - Mortality (Mortalidad)
  - Migration (Migración)
  - Demographic Change Indicators
  - Population Growth Indicators

### Regions (23 DANE Population Regions)
VDA, AQU, SBC, BQR, BMG, BGR, ACB, CRI, SSS, GSV, EGS, ATN, ECF, AZN, VRC, NPA, APC, AMG, MTC, CCR, BMR, CLR

---

## 📅 **Timeline Estimate**
- **Phase 1** (Foundation & Data): 2-3 weeks
- **Phase 2** (Global Improvements): 1-2 weeks
- **Phase 3** (Pyramid Module): 1 week
- **Phase 4** (Indicators Module): 2 weeks
- **Phase 5** (Regional View): 1-2 weeks
- **Phase 6** (Bono Demográfico): 1 week

**Total**: 8-11 weeks for complete implementation

---

## 🚀 **Immediate Next Steps**

1. **Review** this plan and get approval
2. **Start Phase 1**: Create database schemas for new data
3. **Write ETL scripts** for DANE indicators and regions
4. **Quick wins**: Implement data source footer and territory formatting (can be done in parallel)
5. **Set up dev branch**: `feature/dane-improvements`

---

## ❓ **Validation Questions Answered**

1. **DANE Indicators Data**: ✅ Located at `/home/luisjavier/Downloads/DANE Indicators/`
2. **National Calculations**: ✅ Pre-calculate and store
3. **Regional Definition**: ✅ Defined in `/home/luisjavier/Downloads/Regiones DANE.xlsx` (23 regions)
4. **Quinquenal Toggle**: ✅ Per-module preference
5. **Pyramid Comparison**: ✅ Side-by-side
6. **Glossary Scope**: ✅ Global modal

---

**Full Details**: See `docs/IMPLEMENTATION_PLAN.md`
