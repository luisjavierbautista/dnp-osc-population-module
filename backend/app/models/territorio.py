"""
Modelo de datos para territorios (departamentos y municipios).
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String, Enum
import enum


class NivelTerritorial(str, enum.Enum):
    """Nivel territorial."""
    DEPARTAMENTAL = "departamental"
    MUNICIPAL = "municipal"


class Territorio(SQLModel, table=True):
    """
    Tabla de territorios (departamentos y municipios).

    Attributes:
        territorio_id: Código DANE (2 dígitos para depto, 5 para municipio)
        nivel: Nivel territorial (departamental o municipal)
        dp: Código del departamento (2 dígitos)
        mpio: Código del municipio (3 dígitos, nullable)
        nombre: Nombre del territorio
        categoria: Categoría del territorio (opcional)
        transicion_demografica: Nivel de transición demográfica (opcional)
    """
    __tablename__ = "territorio"

    territorio_id: str = Field(
        sa_column=Column(String(5), primary_key=True),
        description="Código DANE del territorio"
    )
    nivel: NivelTerritorial = Field(
        description="Nivel territorial"
    )
    dp: str = Field(
        sa_column=Column(String(2), nullable=False),
        description="Código DANE del departamento"
    )
    mpio: Optional[str] = Field(
        default=None,
        sa_column=Column(String(3), nullable=True),
        description="Código DANE del municipio (solo para nivel municipal)"
    )
    nombre: str = Field(
        description="Nombre del territorio"
    )
    categoria: Optional[str] = Field(
        default=None,
        description="Categoría del territorio (ciudad_intermedia, aglomeracion, etc.)"
    )
    transicion_demografica: Optional[str] = Field(
        default=None,
        description="Nivel de transición demográfica (alto/medio/bajo)"
    )

    class Config:
        schema_extra = {
            "example": {
                "territorio_id": "05001",
                "nivel": "municipal",
                "dp": "05",
                "mpio": "001",
                "nombre": "Medellín",
                "categoria": "aglomeracion",
                "transicion_demografica": "alto"
            }
        }
