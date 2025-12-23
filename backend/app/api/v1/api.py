"""
API v1 router configuration.
"""
from fastapi import APIRouter
from .endpoints import population, map, chat, dane_indicators

api_router = APIRouter()

# Incluir routers de endpoints
api_router.include_router(
    population.router,
    prefix="/population",
    tags=["population"]
)

api_router.include_router(
    map.router,
    prefix="/map",
    tags=["map"]
)

api_router.include_router(
    chat.router,
    prefix="/chats",
    tags=["chats"]
)

api_router.include_router(
    dane_indicators.router,
    prefix="/dane",
    tags=["dane-indicators"]
)
