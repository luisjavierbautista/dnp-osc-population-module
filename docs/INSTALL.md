# Guía de Instalación Detallada

Esta guía proporciona instrucciones paso a paso para instalar y configurar el Módulo de Población del DNP.

## Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación con Docker](#instalación-con-docker)
3. [Instalación Manual](#instalación-manual)
4. [Carga de Datos](#carga-de-datos)
5. [Verificación](#verificación)
6. [Problemas Comunes](#problemas-comunes)

---

## Requisitos del Sistema

### Hardware Mínimo

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 10 GB libres

### Software Requerido

#### Opción 1: Con Docker
- Docker 20.10+
- Docker Compose 2.0+

#### Opción 2: Sin Docker
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- npm 9+

---

## Instalación con Docker

### 1. Clonar el Repositorio

```bash
git clone https://github.com/your-org/dnp-osc-population-module.git
cd dnp-osc-population-module
```

### 2. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

Configuración mínima requerida:

```env
POSTGRES_PASSWORD=tu_password_seguro
SECRET_KEY=tu_clave_secreta_minimo_32_caracteres
```

### 3. Levantar los Servicios

```bash
# Construir e iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. Verificar Servicios

```bash
# Verificar estado
docker-compose ps

# Deberías ver:
# - dnp_population_db (PostgreSQL)
# - dnp_population_backend (FastAPI)
# - dnp_population_frontend (Next.js)
```

### 5. Acceder a las Aplicaciones

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

---

## Instalación Manual

### 1. Instalar PostgreSQL

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql-14 postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS

```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Windows

Descargar desde: https://www.postgresql.org/download/windows/

### 2. Crear Base de Datos

```bash
# Conectar como postgres
sudo -u postgres psql

# Crear usuario y base de datos
CREATE USER population_user WITH PASSWORD 'tu_password';
CREATE DATABASE population_db OWNER population_user;
GRANT ALL PRIVILEGES ON DATABASE population_db TO population_user;
\q
```

### 3. Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno del Backend

```bash
# Desde la raíz del proyecto
cp .env.example .env
nano .env
```

Asegúrate de configurar:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=population_user
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=population_db
SECRET_KEY=genera_una_clave_segura_aqui
```

### 5. Inicializar Base de Datos

```bash
cd backend
source venv/bin/activate

# Crear tablas
python -c "from app.db.database import init_db; init_db()"
```

### 6. Iniciar Backend

```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 7. Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables
cp .env.local.example .env.local
nano .env.local
```

Contenido de `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 8. Iniciar Frontend

```bash
# Desarrollo
npm run dev

# Producción
npm run build
npm start
```

---

## Carga de Datos

### Preparar Archivos CSV

Coloca los archivos CSV del DANE en:

```
etl/data/raw/
├── dane_departamental.csv
└── dane_municipal.csv
```

### Ejecutar ETL

```bash
cd backend
source venv/bin/activate

# Cargar datos departamentales
python -m etl.scripts.etl_dane \
    ../etl/data/raw/dane_departamental.csv \
    departamental

# Cargar datos municipales
python -m etl.scripts.etl_dane \
    ../etl/data/raw/dane_municipal.csv \
    municipal
```

### Validar Carga

```bash
# Conectar a PostgreSQL
psql -U population_user -d population_db

# Verificar datos
SELECT COUNT(*) FROM territorio;
SELECT COUNT(*) FROM poblacion_edad;
SELECT COUNT(*) FROM poblacion_total;

\q
```

---

## Verificación

### 1. Verificar Backend

```bash
# Health check
curl http://localhost:8000/health

# Debería retornar:
# {"status":"healthy","version":"1.0.0"}

# Probar endpoint
curl "http://localhost:8000/api/v1/population/age?territorio_id=05001&anio=2025&area=Total&sexo=T"
```

### 2. Verificar Frontend

- Abrir http://localhost:3000 en el navegador
- Verificar que cargue la página de inicio
- Navegar a cada vista (Mapa, Pirámide, Comparador, Bono Demográfico)

### 3. Verificar Base de Datos

```bash
# Ver estadísticas
psql -U population_user -d population_db -c "
SELECT
    nivel,
    COUNT(DISTINCT territorio_id) as territorios,
    COUNT(DISTINCT anio) as anios
FROM territorio t
JOIN poblacion_total pt ON t.territorio_id = pt.territorio_id
GROUP BY nivel;
"
```

---

## Problemas Comunes

### Error: "Database connection failed"

**Solución**:
1. Verificar que PostgreSQL esté corriendo: `sudo systemctl status postgresql`
2. Verificar credenciales en `.env`
3. Verificar que el usuario tenga permisos: `GRANT ALL...`

### Error: "Port 8000 already in use"

**Solución**:
```bash
# Encontrar proceso usando el puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Error: "Module not found" en Backend

**Solución**:
```bash
# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt
```

### Error: "Cannot find module" en Frontend

**Solución**:
```bash
# Limpiar y reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Error: ETL falla al cargar datos

**Solución**:
1. Verificar formato del CSV (debe tener las columnas esperadas)
2. Verificar encoding (debe ser UTF-8)
3. Ver logs detallados: `python -m etl.scripts.etl_dane --verbose`

---

## Siguientes Pasos

Después de la instalación exitosa:

1. Revisar la [documentación de la API](http://localhost:8000/docs)
2. Explorar las vistas del frontend
3. Leer la guía de desarrollo en `docs/DEVELOPMENT.md`
4. Configurar backups automáticos

---

## Soporte

Si encuentras problemas no listados aquí:

1. Revisar logs: `docker-compose logs` o archivos en `logs/`
2. Consultar issues en GitHub
3. Contactar al equipo de desarrollo
