"""Data models for the population module."""
from .territorio import Territorio, NivelTerritorial
from .poblacion import (
    PoblacionEdad,
    PoblacionTotal,
    AreaGeografica,
    Sexo
)
from .chat import Chat, ChatMessage
from .dane_indicators import (
    DaneRegion,
    DaneDepartment,
    DaneMunicipality,
    DaneFertilityIndicator,
    DaneMigrationIndicator,
    DaneMortalityIndicator,
    DanePrincipalIndicator,
    DaneGrowthIndicator,
)

__all__ = [
    "Territorio",
    "NivelTerritorial",
    "PoblacionEdad",
    "PoblacionTotal",
    "AreaGeografica",
    "Sexo",
    "Chat",
    "ChatMessage",
    "DaneRegion",
    "DaneDepartment",
    "DaneMunicipality",
    "DaneFertilityIndicator",
    "DaneMigrationIndicator",
    "DaneMortalityIndicator",
    "DanePrincipalIndicator",
    "DaneGrowthIndicator",
]
