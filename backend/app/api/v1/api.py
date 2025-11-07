"""
API v1 router configuration.
"""
from fastapi import APIRouter
from .endpoints import population

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    population.router,
    prefix="/population",
    tags=["population"]
)
