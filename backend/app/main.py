"""
FastAPI application for the DNP Population Module.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .db.database import init_db
from .api.v1.api import api_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    """
    logger.info("Iniciando aplicación...")
    # Inicializar base de datos
    init_db()
    logger.info("Base de datos inicializada")
    yield
    logger.info("Cerrando aplicación...")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    description="""
    **Módulo de Población del Observatorio del Sistema de Ciudades (DNP - Colombia)**

    Este módulo proporciona datos y análisis demográficos basados en proyecciones del DANE
    para el período 2018-2050, cubriendo niveles departamental y municipal.

    ## Características principales

    * 📊 **Datos demográficos**: Población por edad, sexo y área geográfica
    * 🗺️ **Distribución territorial**: Urbano/rural a nivel departamental y municipal
    * 📈 **Indicadores**: Crecimiento, envejecimiento, bono demográfico
    * 🔍 **Comparaciones**: Entre territorios y períodos temporales
    * 📉 **Pirámides poblacionales**: Visualizaciones por edad y sexo

    ## Fuente de datos

    Departamento Administrativo Nacional de Estadística (DANE) - Proyecciones de Población 2018-2050

    ## Versión

    API v1.0.0 - Fase 2025
    """,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Comprimir respuestas
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Incluir routers de la API
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    Endpoint raíz de la API.
    """
    return {
        "message": "Módulo de Población - DNP",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de health check para monitoreo.
    """
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
