# Quick Start Guide - Módulo de Población DNP

Esta guía te permitirá tener el proyecto corriendo en **menos de 5 minutos** usando Docker.

## 🚀 Inicio Rápido (Docker)

```bash
# 1. Clonar el repositorio
git clone <tu-repo-url>
cd dnp-osc-population-module

# 2. Configurar variables de entorno (opcional)
cp .env.example .env
# Editar .env si deseas cambiar contraseñas

# 3. Levantar todos los servicios
docker-compose up -d

# 4. Ver logs
docker-compose logs -f

# Esperar ~30 segundos a que todos los servicios inicien
```

## ✅ Verificar Instalación

### Backend API

```bash
# Health check
curl http://localhost:8000/health

# Debería responder: {"status":"healthy","version":"1.0.0"}
```

Abre en tu navegador:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

### Frontend

Abre en tu navegador:
- **Frontend**: http://localhost:3000

### Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it dnp_population_db psql -U population_user -d population_db

# Ver tablas
\dt

# Salir
\q
```

## 📊 Cargar Datos

Antes de usar la API, necesitas cargar los datos del DANE:

```bash
# 1. Coloca tus archivos CSV en etl/data/raw/
# - dane_departamental.csv
# - dane_municipal.csv

# 2. Ejecuta el ETL
docker exec -it dnp_population_backend python -m etl.scripts.etl_dane \
    /etl/data/raw/dane_departamental.csv \
    departamental

docker exec -it dnp_population_backend python -m etl.scripts.etl_dane \
    /etl/data/raw/dane_municipal.csv \
    municipal
```

## 🎯 Ejemplos de Uso

### API REST

```bash
# Obtener población por edad (Medellín 2025)
curl "http://localhost:8000/api/v1/population/age?territorio_id=05001&anio=2025&area=Total&sexo=T"

# Distribución urbano-rural (Antioquia 2025)
curl "http://localhost:8000/api/v1/population/urban_rural?territorio_id=05&anio=2025"

# Pirámide poblacional
curl "http://localhost:8000/api/v1/population/pyramid?territorio_id=05001&anio=2025&modo=quinquenal"

# Comparar territorios (POST)
curl -X POST "http://localhost:8000/api/v1/population/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "territorios": ["05001", "11001"],
    "anio": 2025,
    "area": "Total",
    "metricas": ["poblacion_total", "pct_urbana", "envejecimiento"]
  }'
```

### Frontend

Navega a http://localhost:3000 y explora:

1. **Inicio**: Overview del módulo
2. **Pirámide**: Visualiza estructura poblacional por edad y sexo
3. **Comparador**: Compara múltiples territorios
4. **Bono Demográfico**: Analiza transición demográfica

## 🛑 Detener Servicios

```bash
# Detener sin borrar datos
docker-compose stop

# Reiniciar
docker-compose start

# Detener y borrar todo (incluyendo datos)
docker-compose down -v
```

## 📝 Códigos de Territorios

Algunos códigos útiles:

| Código | Territorio |
|--------|------------|
| `05` | Antioquia (Depto) |
| `11` | Cundinamarca (Depto) |
| `76` | Valle del Cauca (Depto) |
| `05001` | Medellín |
| `11001` | Bogotá |
| `76001` | Cali |
| `08001` | Barranquilla |
| `13001` | Cartagena |

## 🔧 Troubleshooting

### Puerto ocupado

Si el puerto 8000 o 3000 está en uso:

```bash
# Modificar docker-compose.yml
# Cambiar "8000:8000" por "8001:8000" (u otro puerto)
```

### Base de datos no inicia

```bash
# Ver logs
docker-compose logs db

# Reiniciar solo la base de datos
docker-compose restart db
```

### Backend no conecta a DB

```bash
# Verificar que DB esté corriendo
docker-compose ps

# Reiniciar backend
docker-compose restart backend
```

## 📚 Documentación Completa

Para más detalles, ver:

- **README.md**: Documentación completa
- **INSTALL.md**: Instalación paso a paso
- **CONTRIBUTING.md**: Guía de contribución
- **docs/**: Documentación adicional

## 💡 Próximos Pasos

1. Cargar tus datos DANE con el ETL
2. Explorar la API en http://localhost:8000/docs
3. Explorar las vistas del frontend
4. Revisar el código para entender la arquitectura
5. Comenzar a desarrollar nuevas funcionalidades

---

¡Todo listo! 🎉

Si tienes problemas, revisa la documentación completa o abre un issue en GitHub.
