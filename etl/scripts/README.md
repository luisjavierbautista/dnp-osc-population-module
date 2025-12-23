# ETL Scripts - Carga de Datos DANE

Este directorio contiene los scripts de ETL para cargar datos de población del DANE en la base de datos.

## 📋 Scripts Disponibles

### 1. `load_all_data.py` - Datos DEPARTAMENTALES

**Propósito**: Cargar SOLO datos departamentales (archivos pequeños).

**Uso**:
```bash
# Con Docker
docker compose exec backend python /etl/scripts/load_all_data.py

# Sin Docker
cd backend && python /etl/scripts/load_all_data.py
```

**Características**:
- ✅ Procesa archivos departamentales en memoria completa
- ✅ Rápido (~2 minutos)
- ✅ Archivos: DCD (1985-2004) y PPED (2018-2050)
- ❌ NO procesa archivos municipales (los detecta pero los omite con mensaje)

**Directorio de entrada**: `etl/data/Departamental/`

---

### 2. `load_municipal_data.py` - Datos MUNICIPALES

**Propósito**: Cargar SOLO datos municipales (archivos grandes) con estrategia de chunks.

**Uso**:
```bash
# Con Docker
docker compose exec backend python /etl/scripts/load_municipal_data.py

# Sin Docker
cd backend && python /etl/scripts/load_municipal_data.py
```

**Características**:
- ✅ Procesa archivos municipales en chunks de 1000 filas
- ✅ Optimizado para archivos grandes (39+ MB)
- ✅ Evita problemas de memoria (OOM)
- ✅ Muestra progreso detallado por chunk
- ⏱️ Tiempo de ejecución: ~30-60 minutos

**Directorio de entrada**: `etl/data/Municipal/`

**Archivos procesados**:
1. `DCD-area-sexo-edad-proypoblacion-Mun-1985-1994.xlsx` (~33,660 filas)
2. `DCD-area-sexo-edad-proypoblacion-Mun-1995-2004.xlsx`
3. `DCD-area-sexo-edad-proypoblacion-Mun-2005-2017_VP.xlsx`
4. `PPED-AreaSexoEdadMun-2018-2042_VP.xlsx`

---

### 3. `etl_dane.py` - Módulo ETL Core

Contiene la clase `DANEDataProcessor` con toda la lógica de transformación y carga.

**Métodos principales**:
- `process_file()`: Procesa archivo completo en memoria (departamental)
- `process_municipal_chunked()`: Procesa archivo municipal por chunks

---

## 🎯 Estrategia de Carga

### ¿Por qué dos scripts separados?

| Característica | Departamental | Municipal |
|----------------|---------------|-----------|
| **Tamaño archivos** | Pequeños (< 10 MB) | Grandes (39+ MB) |
| **Filas típicas** | ~500-1000 | ~30,000-35,000 |
| **Columnas edad** | 258 | 258 |
| **Registros finales** | ~1.5M total | ~30M+ total |
| **Estrategia** | Carga completa | Chunks de 1000 filas |
| **Tiempo carga** | ~2 minutos | ~30-60 minutos |
| **Uso memoria** | Normal | Alto (sin chunks) |

### Arquitectura de Chunks

```
Excel (33,660 filas × 258 edades)
    ↓
CSV Temporal
    ↓
Chunks de 1000 filas
    ↓ (para cada chunk)
Melt: 1000 → 258,000 registros
    ↓
Validación
    ↓
Batches de 50,000 para inserción
    ↓
PostgreSQL
```

**Ventajas del chunking**:
- ✅ Memoria estable (procesa 1000 filas a la vez)
- ✅ No crash por OOM (Out of Memory)
- ✅ Progreso visible y mensurable
- ✅ Puede procesar archivos de cualquier tamaño

---

## ⚠️ REGLAS IMPORTANTES

### ❌ NO HACER:

1. **NO usar `load_all_data.py` para datos municipales**
   - Causará problemas de memoria
   - El script ahora los detecta y omite automáticamente

2. **NO modificar el chunk size sin pruebas**
   - Valor actual: 1000 filas
   - Reducir → más lento
   - Aumentar → riesgo de OOM

3. **NO interrumpir la carga municipal**
   - Puede dejar datos parciales
   - Mejor: dejar que complete

### ✅ SÍ HACER:

1. **Cargar departamentales primero**
   - Más rápido
   - Permite probar la aplicación pronto

2. **Monitorear logs durante carga municipal**
   ```bash
   docker compose logs -f backend | grep -E "Progreso|Chunk|Archivo"
   ```

3. **Verificar datos después de cada carga**
   ```sql
   SELECT COUNT(*) FROM poblacion_edad;
   SELECT nivel, COUNT(DISTINCT territorio_id) FROM territorio GROUP BY nivel;
   ```

---

## 📊 Estructura de Datos Esperada

### Archivos Excel

**Formato DCD (antiguos, pre-2018)**:
- Hoja 0 (única)
- Header en fila 11
- Columnas: DP, DPNOM/MPNOM, AÑO, ÁREA GEOGRÁFICA, [258 columnas de edad]

**Formato PPED (nuevos, 2018+)**:
- Múltiples hojas
- Hoja de datos en índice 2
- Multi-header en filas 7-8
- Columnas: Similar a DCD pero con estructura diferente

### Transformación ETL

```python
# Input (Wide format)
DP  | DPNOM      | AÑO  | ÁREA | 0   | 1   | 2   | ... | 100+
05  | Antioquia  | 2025 | Total| 1234| 1456| 1678| ... | 891

# Output (Long format) - después de melt()
territorio_id | anio | area  | sexo | edad | poblacion
05           | 2025 | Total | T    | 0    | 1234
05           | 2025 | Total | T    | 1    | 1456
05           | 2025 | Total | T    | 2    | 1678
...
```

---

## 🔍 Troubleshooting

### Error: "Memory Error" o proceso mata inesperadamente

**Causa**: Intentando procesar archivo municipal sin chunks

**Solución**: Usar `load_municipal_data.py`

### Error: "No such file or directory: etl/data/"

**Causa**: Archivos no están en la ubicación correcta

**Solución**:
```bash
# Verificar estructura
ls -la etl/data/Departamental/
ls -la etl/data/Municipal/
```

### Carga municipal muy lenta

**Normal**: El script municipal tarda 30-60 minutos

**Verificar progreso**:
```bash
# Ver últimas 20 líneas del log
docker compose logs backend --tail=20

# O si usas tee:
tail -f /tmp/load_municipal_fresh.log
```

### Datos parciales después de interrupción

**Solución**: Limpiar y recargar
```bash
# Limpiar datos municipales
docker compose exec db psql -U population_user -d population_db -c "
DELETE FROM poblacion_edad
WHERE territorio_id IN (
    SELECT territorio_id FROM territorio WHERE nivel = 'MUNICIPAL'
);
DELETE FROM territorio WHERE nivel = 'MUNICIPAL';
"

# Volver a cargar
docker compose exec backend python /etl/scripts/load_municipal_data.py
```

---

## 📝 Logs y Monitoreo

### Ver logs en tiempo real

```bash
# Docker
docker compose logs -f backend

# Archivo específico (si se usa tee)
tail -f /tmp/load_municipal_fresh.log
```

### Progreso esperado (Municipal)

```
Archivo 1/4: DCD-area-sexo-edad-proypoblacion-Mun-1985-1994.xlsx
├── Chunk 1/34: 258,000 registros ✓
├── Chunk 2/34: 258,000 registros ✓
├── Chunk 3/34: 258,000 registros ✓
...
└── Chunk 34/34: ~XXX,000 registros ✓

Archivo 2/4: ...
```

---

## 🚀 Mejoras Futuras

Posibles optimizaciones:

1. **Procesamiento paralelo de chunks** (requiere cambios en DB)
2. **Compresión de archivos intermedios** (CSV temp)
3. **Índices temporales deshabilitados** durante carga
4. **COPY en lugar de INSERT** para PostgreSQL
5. **Particionamiento de tabla poblacion_edad** por año o territorio

---

## 📚 Referencias

- Documentación DANE: https://www.dane.gov.co/
- PostgreSQL COPY: https://www.postgresql.org/docs/current/sql-copy.html
- Pandas chunking: https://pandas.pydata.org/docs/user_guide/io.html#iterating-through-files-chunk-by-chunk

---

**Última actualización**: 2025-11-10
**Mantenedor**: Equipo DNP - Módulo de Población
