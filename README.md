# Módulo de Población - Observatorio del Sistema de Ciudades (DNP)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)

**Módulo de Población del Observatorio del Sistema de Ciudades del DNP (Colombia)**. Implementación completa de backend (FastAPI) y frontend (Next.js) para visualización y análisis de datos demográficos basados en proyecciones del DANE 2018-2050.

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Stack Tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API](#api)
- [ETL](#etl)
- [Frontend](#frontend)
- [Despliegue](#despliegue)
- [Desarrollo](#desarrollo)
- [Testing](#testing)
- [Contribución](#contribución)

---

## 🚀 Características

### Backend (FastAPI)
- ✅ **API REST** con documentación OpenAPI/Swagger
- ✅ **Modelos de datos** con SQLModel (ORM)
- ✅ **Base de datos** PostgreSQL 14+
- ✅ **ETL completo** para datos DANE (departamental y municipal)
- ✅ **Validaciones de integridad** (cierres por sexo, edad, área)
- ✅ **Cálculos demográficos**: crecimiento, bono demográfico, envejecimiento
- ✅ **Autenticación JWT** y CORS configurado
- ✅ **Rate limiting** (100 req/min)

### Frontend (Next.js)
- ✅ **Next.js 14** con TypeScript
- ✅ **TailwindCSS** para estilos
- ✅ **React Query** para gestión de estado servidor
- ✅ **Zustand** para estado global
- ✅ **Componentes UI** reutilizables
- ✅ **Filtros dinámicos** (año, área, sexo, territorio)
- ✅ **Visualizaciones**:
  - Mapa categorizado (choropleth)
  - Pirámide poblacional
  - Comparador de territorios
  - Bono demográfico

### Datos
- 📊 **Fuente**: DANE - Proyecciones de Población 2018-2050
- 📍 **Cobertura**: Departamental y Municipal
- 👥 **Desagregación**: Por edad (0-100+), sexo (H/M/T), área (Cabecera/CPRD/Total)
- 📅 **Período**: 2018-2050 (33 años)

---

## 🛠 Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.109+
- **Base de datos**: PostgreSQL 14+
- **ORM**: SQLModel
- **Servidor**: Uvicorn + Gunicorn
- **Seguridad**: JWT (python-jose), CORS
- **Data**: Pandas, NumPy
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Lenguaje**: TypeScript 5.3+
- **Estilos**: TailwindCSS 3.4+
- **Componentes**: Radix UI
- **Gráficas**: Recharts
- **Mapas**: React Leaflet
- **Estado**: Zustand + React Query
- **HTTP**: Axios

### DevOps
- **Contenedores**: Docker + Docker Compose
- **Proxy**: Nginx (opcional)
- **CI/CD**: GitHub Actions (opcional)

---

## 📐 Arquitectura

```
dnp-osc-population-module/
├── backend/                  # API FastAPI
│   ├── app/
│   │   ├── api/v1/          # Endpoints
│   │   ├── core/            # Config, security
│   │   ├── db/              # Database
│   │   ├── models/          # SQLModel models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # App entry
│   ├── tests/               # Unit tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                # Next.js app
│   ├── src/
│   │   ├── app/            # Pages (App Router)
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   ├── stores/         # Zustand stores
│   │   └── types/          # TypeScript types
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── etl/                     # ETL scripts
│   ├── scripts/
│   │   ├── etl_dane.py     # Main ETL
│   │   └── validators.py   # Data validators
│   └── data/               # Raw & processed data
│
├── docs/                    # Documentation
├── docker-compose.yml       # Multi-container setup
├── .env.example            # Environment template
└── README.md               # This file
```

---

## 💻 Instalación

### Requisitos Previos

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 14+
- **Docker** y **Docker Compose** (opcional pero recomendado)

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/your-org/dnp-osc-population-module.git
cd dnp-osc-population-module

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Editar .env con tus credenciales (opcional)
nano .env

# 4. Levantar todos los servicios
docker-compose up -d

# 5. Verificar que los servicios estén corriendo
docker-compose ps

# Acceder a:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Frontend: http://localhost:3000
```

### Opción 2: Instalación Local

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp ../.env.example ../.env
nano ../.env

# Crear base de datos PostgreSQL
createdb population_db

# Ejecutar migraciones (si aplica)
# alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.local.example .env.local
nano .env.local

# Iniciar servidor de desarrollo
npm run dev
```

---

## ⚙️ Configuración

### Variables de Entorno

Edita el archivo `.env`:

```bash
# Application
PROJECT_NAME="Módulo de Población - DNP"
DEBUG=false

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=population_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=population_db
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-secret-key-min-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Frontend (`.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🎯 Uso

### 1. Cargar Datos con ETL

Antes de usar la API, debes cargar los datos del DANE:

```bash
# Activar entorno virtual del backend
cd backend
source venv/bin/activate

# Ejecutar ETL para datos departamentales
python -m etl.scripts.etl_dane \
    ../etl/data/raw/dane_departamental.csv \
    departamental

# Ejecutar ETL para datos municipales
python -m etl.scripts.etl_dane \
    ../etl/data/raw/dane_municipal.csv \
    municipal
```

**Nota**: Los archivos CSV deben seguir el formato especificado en la documentación técnica.

### 2. Acceder a la API

Una vez cargados los datos:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Ejemplos de consultas:

```bash
# Población por edad (Medellín, 2025)
curl "http://localhost:8000/api/v1/population/age?territorio_id=05001&anio=2025&area=Total&sexo=T"

# Distribución urbano-rural (Antioquia, 2025)
curl "http://localhost:8000/api/v1/population/urban_rural?territorio_id=05&anio=2025"

# Pirámide poblacional
curl "http://localhost:8000/api/v1/population/pyramid?territorio_id=05001&anio=2025&modo=simple"
```

### 3. Usar el Frontend

Navega a http://localhost:3000 y explora:

- **Mapa**: Visualización territorial de variables demográficas
- **Pirámide**: Estructura poblacional por edad y sexo
- **Comparador**: Compara múltiples territorios
- **Bono Demográfico**: Análisis de transición demográfica

---

## 📡 API

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/population/age` | Población por edad |
| `GET` | `/api/v1/population/urban_rural` | Distribución urbano-rural |
| `GET` | `/api/v1/population/growth` | Crecimiento poblacional |
| `GET` | `/api/v1/population/pyramid` | Datos para pirámide |
| `POST` | `/api/v1/population/compare` | Comparar territorios |
| `GET` | `/api/v1/population/indicators` | Indicadores demográficos |

### Ejemplo de Response

```json
{
  "territorioId": "05001",
  "anio": 2025,
  "area": "Total",
  "sexo": "T",
  "edadBins": [
    {"edad": 0, "poblacion": 26398},
    {"edad": 1, "poblacion": 27823},
    ...
  ]
}
```

Ver documentación completa en `/docs`.

---

## 🔄 ETL

### Proceso de Carga

El ETL realiza:

1. **Limpieza**: Normalización de strings, conversión numérica, padding de códigos
2. **Transformación**: Unpivot a formato largo (tidy data)
3. **Validación**: Cierres por sexo (±0.5%), edad (±0.5%), área (±1%)
4. **Carga**: Inserción en PostgreSQL con índices optimizados

### Validaciones

```python
# Ejecutar validaciones manualmente
from etl.scripts.validators import validate_dataframe
import pandas as pd

df = pd.read_csv('processed_data.csv')
results = validate_dataframe(df, print_report=True)
```

---

## 🎨 Frontend

### Estructura de Componentes

```typescript
// Usar el store global
import { usePopulationStore } from '@/stores/usePopulationStore'

function MyComponent() {
  const { filters, setAnio } = usePopulationStore()

  return (
    <YearSlider
      value={filters.anio}
      onChange={setAnio}
    />
  )
}
```

### Servicios API

```typescript
import { populationApi } from '@/services/api'

// Obtener pirámide
const pyramid = await populationApi.getPyramid({
  territorio_id: '05001',
  anio: 2025,
  modo: 'simple'
})
```

---

## 🚢 Despliegue

### Producción con Docker

```bash
# Build images
docker-compose build

# Deploy
docker-compose up -d

# Logs
docker-compose logs -f backend
```

### Variables de Producción

```bash
DEBUG=false
SECRET_KEY=<strong-random-key>
POSTGRES_PASSWORD=<secure-password>
BACKEND_CORS_ORIGINS=https://your-domain.com
```

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend

```bash
cd frontend
npm test
npm run type-check
```

---

## 📚 Documentación Adicional

- **Especificación Técnica**: `docs/especificacion_tecnica.md`
- **Modelo de Datos**: Ver comentarios en `backend/app/models/`
- **API Reference**: http://localhost:8000/docs

---

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto es parte del Observatorio del Sistema de Ciudades del DNP (Colombia).

---

## 📞 Contacto

- **Organización**: DNP Colombia
- **Proyecto**: Observatorio del Sistema de Ciudades
- **Fuente de Datos**: DANE - Proyecciones de Población 2018-2050

---

## 🙏 Agradecimientos

- DANE por las proyecciones de población
- DNP por el Observatorio del Sistema de Ciudades
- Comunidad open source de FastAPI y Next.js
