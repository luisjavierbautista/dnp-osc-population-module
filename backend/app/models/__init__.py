"""Data models for the population module."""
from .territorio import Territorio, NivelTerritorial
from .poblacion import (
    PoblacionEdad,
    PoblacionTotal,
    AreaGeografica,
    Sexo
)

__all__ = [
    "Territorio",
    "NivelTerritorial",
    "PoblacionEdad",
    "PoblacionTotal",
    "AreaGeografica",
    "Sexo",
]
