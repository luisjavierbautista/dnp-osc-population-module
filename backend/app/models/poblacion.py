"""
Modelos de datos para población.
"""
from typing import Optional
from sqlmodel import SQLModel, Field, Column, String, Integer, Numeric, Boolean, Enum, Index
from decimal import Decimal
import enum


class AreaGeografica(str, enum.Enum):
    """Área geográfica."""
    CABECERA = "Cabecera Municipal"
    CPRD = "Centros Poblados y Rural Disperso"
    TOTAL = "Total"


class Sexo(str, enum.Enum):
    """Sexo."""
    HOMBRE = "H"
    MUJER = "M"
    TOTAL = "T"


class PoblacionEdad(SQLModel, table=True):
    """
    Tabla de población por edad, sexo y área geográfica.

    Attributes:
        territorio_id: FK a territorio
        anio: Año de la proyección (2018-2050)
        area_geografica: Área geográfica (Cabecera, CPRD, Total)
        sexo: Sexo (H, M, T)
        edad: Edad (0-100)
        mayores_100: True si corresponde al grupo "100 años y más"
        poblacion: Cantidad de población
    """
    __tablename__ = "poblacion_edad"
    __table_args__ = (
        Index('ix_poblacion_edad_lookup', 'territorio_id', 'anio', 'area_geografica', 'sexo', 'edad'),
        Index('ix_poblacion_edad_territorio_anio', 'territorio_id', 'anio'),
    )

    territorio_id: str = Field(
        sa_column=Column(String(5), primary_key=True, nullable=False),
        foreign_key="territorio.territorio_id",
        description="Código DANE del territorio"
    )
    anio: int = Field(
        sa_column=Column(Integer, primary_key=True, nullable=False),
        description="Año de la proyección"
    )
    area_geografica: AreaGeografica = Field(
        sa_column=Column(String(50), primary_key=True, nullable=False),
        description="Área geográfica"
    )
    sexo: Sexo = Field(
        sa_column=Column(String(1), primary_key=True, nullable=False),
        description="Sexo"
    )
    edad: int = Field(
        sa_column=Column(Integer, primary_key=True, nullable=False),
        description="Edad (0-100)"
    )
    mayores_100: bool = Field(
        default=False,
        description="True si corresponde al grupo '100 años y más'"
    )
    poblacion: Decimal = Field(
        sa_column=Column(Numeric, nullable=False),
        description="Cantidad de población"
    )

    class Config:
        schema_extra = {
            "example": {
                "territorio_id": "05001",
                "anio": 2025,
                "area_geografica": "Total",
                "sexo": "H",
                "edad": 25,
                "mayores_100": False,
                "poblacion": 45230
            }
        }


class PoblacionTotal(SQLModel, table=True):
    """
    Tabla de población total agregada por territorio, año y área.

    Attributes:
        territorio_id: FK a territorio
        anio: Año de la proyección
        area_geografica: Área geográfica
        pob_total: Población total
        pob_hombres: Población de hombres
        pob_mujeres: Población de mujeres
        pct_urbana: Porcentaje urbano (solo si area_geografica=Total)
        pct_rural: Porcentaje rural (solo si area_geografica=Total)
    """
    __tablename__ = "poblacion_total"
    __table_args__ = (
        Index('ix_poblacion_total_lookup', 'territorio_id', 'anio', 'area_geografica'),
    )

    territorio_id: str = Field(
        sa_column=Column(String(5), primary_key=True, nullable=False),
        foreign_key="territorio.territorio_id",
        description="Código DANE del territorio"
    )
    anio: int = Field(
        sa_column=Column(Integer, primary_key=True, nullable=False),
        description="Año de la proyección"
    )
    area_geografica: AreaGeografica = Field(
        sa_column=Column(String(50), primary_key=True, nullable=False),
        description="Área geográfica"
    )
    pob_total: Decimal = Field(
        sa_column=Column(Numeric, nullable=False),
        description="Población total"
    )
    pob_hombres: Decimal = Field(
        sa_column=Column(Numeric, nullable=False),
        description="Población de hombres"
    )
    pob_mujeres: Decimal = Field(
        sa_column=Column(Numeric, nullable=False),
        description="Población de mujeres"
    )
    pct_urbana: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 4), nullable=True),
        description="Porcentaje urbano (solo si area_geografica=Total)"
    )
    pct_rural: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 4), nullable=True),
        description="Porcentaje rural (solo si area_geografica=Total)"
    )

    class Config:
        schema_extra = {
            "example": {
                "territorio_id": "05001",
                "anio": 2025,
                "area_geografica": "Total",
                "pob_total": 2500000,
                "pob_hombres": 1200000,
                "pob_mujeres": 1300000,
                "pct_urbana": 0.95,
                "pct_rural": 0.05
            }
        }
