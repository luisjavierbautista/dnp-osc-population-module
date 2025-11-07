"""
Schemas Pydantic para requests y responses de la API de población.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from ..models.poblacion import AreaGeografica, Sexo


# =============================================================================
# Request Schemas
# =============================================================================

class PopulationAgeRequest(BaseModel):
    """Request para obtener población por edad."""
    territorio_id: List[str] = Field(..., description="Códigos de territorios")
    anio: Optional[int] = Field(None, ge=2018, le=2050, description="Año específico")
    anio_from: Optional[int] = Field(None, ge=2018, le=2050, description="Año inicial (rango)")
    anio_to: Optional[int] = Field(None, ge=2018, le=2050, description="Año final (rango)")
    area: AreaGeografica = Field(AreaGeografica.TOTAL, description="Área geográfica")
    sexo: Sexo = Field(Sexo.TOTAL, description="Sexo")
    quinquenios: bool = Field(False, description="Agrupar por quinquenios")

    @validator('anio_to')
    def validate_anio_range(cls, v, values):
        if v is not None and values.get('anio_from') is not None:
            if v < values['anio_from']:
                raise ValueError('anio_to debe ser mayor o igual a anio_from')
        return v


class PopulationCompareRequest(BaseModel):
    """Request para comparar territorios."""
    territorios: List[str] = Field(..., min_items=2, max_items=10, description="Códigos de territorios a comparar")
    anio: int = Field(..., ge=2018, le=2050, description="Año de comparación")
    area: AreaGeografica = Field(AreaGeografica.TOTAL, description="Área geográfica")
    metricas: List[str] = Field(
        default=["poblacion_total", "pct_urbana", "envejecimiento"],
        description="Métricas a incluir en la comparación"
    )


# =============================================================================
# Response Schemas
# =============================================================================

class EdadBin(BaseModel):
    """Bin de edad con población."""
    edad: int = Field(..., description="Edad o inicio del quinquenio")
    edad_fin: Optional[int] = Field(None, description="Fin del quinquenio (solo si quinquenios=true)")
    poblacion: Decimal = Field(..., description="Población en este bin")

    class Config:
        json_schema_extra = {
            "example": {
                "edad": 25,
                "poblacion": 45230
            }
        }


class PopulationAgeResponse(BaseModel):
    """Response para población por edad."""
    territorio_id: str
    anio: int
    area: str
    sexo: str
    edad_bins: List[EdadBin] = Field(..., alias="edadBins")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "territorioId": "05001",
                "anio": 2025,
                "area": "Total",
                "sexo": "T",
                "edadBins": [
                    {"edad": 0, "poblacion": 26398},
                    {"edad": 1, "poblacion": 27823}
                ]
            }
        }


class UrbanRuralResponse(BaseModel):
    """Response para distribución urbano-rural."""
    territorio_id: str = Field(..., alias="territorioId")
    anio: int
    urbana: Decimal
    rural: Decimal
    pct_urbana: Decimal = Field(..., alias="pctUrbana")
    pct_rural: Decimal = Field(..., alias="pctRural")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "territorioId": "05",
                "anio": 2025,
                "urbana": 5976371,
                "rural": 431778,
                "pctUrbana": 0.93,
                "pctRural": 0.07
            }
        }


class GrowthResponse(BaseModel):
    """Response para crecimiento poblacional."""
    territorio_id: str = Field(..., alias="territorioId")
    periodo: str
    t0: int
    t1: int
    p_t0: Decimal = Field(..., alias="pT0")
    p_t1: Decimal = Field(..., alias="pT1")
    cagr: Decimal
    variacion_total: Optional[Decimal] = Field(None, alias="variacionTotal")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "territorioId": "05001",
                "periodo": "desde_2020",
                "t0": 2020,
                "t1": 2025,
                "pT0": 2427133,
                "pT1": 2490000,
                "cagr": 0.0043
            }
        }


class PyramidSeries(BaseModel):
    """Serie de datos para pirámide poblacional."""
    edad: int
    hombres: Decimal
    mujeres: Decimal


class PyramidResponse(BaseModel):
    """Response para pirámide poblacional."""
    territorio_id: str = Field(..., alias="territorioId")
    anio: int
    area: str
    modo: str
    series: List[PyramidSeries]

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "territorioId": "05001",
                "anio": 2025,
                "area": "Total",
                "modo": "simple",
                "series": [
                    {"edad": 0, "hombres": 13500, "mujeres": 12898},
                    {"edad": 1, "hombres": 14200, "mujeres": 13623}
                ]
            }
        }


class CompareMetrics(BaseModel):
    """Métricas de un territorio para comparación."""
    territorio_id: str = Field(..., alias="territorioId")
    nombre: str
    poblacion_total: Optional[Decimal] = Field(None, alias="poblacionTotal")
    pct_urbana: Optional[Decimal] = Field(None, alias="pctUrbana")
    envejecimiento: Optional[Decimal] = None
    dependencia: Optional[Decimal] = None
    cagr: Optional[Decimal] = None

    class Config:
        populate_by_name = True


class CompareResponse(BaseModel):
    """Response para comparación de territorios."""
    anio: int
    area: str
    territorios: List[CompareMetrics]

    class Config:
        json_schema_extra = {
            "example": {
                "anio": 2025,
                "area": "Total",
                "territorios": [
                    {
                        "territorioId": "05001",
                        "nombre": "Medellín",
                        "poblacionTotal": 2500000,
                        "pctUrbana": 0.98,
                        "envejecimiento": 0.45
                    }
                ]
            }
        }


# =============================================================================
# Error Response
# =============================================================================

class ErrorDetail(BaseModel):
    """Detalle de error adicional."""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Response de error estándar."""
    code: str = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    detail: Optional[dict] = Field(None, description="Detalles adicionales del error")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "INVALID_PARAM",
                "message": "Año fuera de rango",
                "detail": {"min": 2018, "max": 2050}
            }
        }
