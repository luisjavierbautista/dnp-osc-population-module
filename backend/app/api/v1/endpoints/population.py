"""
Endpoints de la API de población.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ....db.database import get_session
from ....services import PopulationService
from ....schemas.population import (
    PopulationAgeRequest,
    PopulationAgeResponse,
    UrbanRuralResponse,
    GrowthResponse,
    PyramidResponse,
    PopulationCompareRequest,
    CompareResponse,
    ErrorResponse,
)

router = APIRouter()


@router.get(
    "/age",
    response_model=List[PopulationAgeResponse],
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Obtener población por edad",
    description="""
    Retorna la distribución de población por edad para uno o más territorios.

    **Parámetros:**
    - `territorio_id`: Códigos DANE de territorios (se puede repetir)
    - `anio`: Año específico (2018-2050)
    - `anio_from`, `anio_to`: Rango de años (alternativa a anio)
    - `area`: Área geográfica (Total, Cabecera Municipal, Centros Poblados y Rural Disperso)
    - `sexo`: H (hombres), M (mujeres), T (total)
    - `quinquenios`: Agrupar por quinquenios (5 años)

    **Ejemplo:**
    ```
    GET /api/v1/population/age?territorio_id=05001&anio=2025&area=Total&sexo=T
    ```
    """
)
def get_population_age(
    territorio_id: List[str] = Query(..., description="Códigos de territorios"),
    anio: Optional[int] = Query(None, ge=2018, le=2050, description="Año específico"),
    anio_from: Optional[int] = Query(None, ge=2018, le=2050, description="Año inicial"),
    anio_to: Optional[int] = Query(None, ge=2018, le=2050, description="Año final"),
    area: str = Query("Total", description="Área geográfica"),
    sexo: str = Query("T", regex="^[HMT]$", description="Sexo (H/M/T)"),
    quinquenios: bool = Query(False, description="Agrupar por quinquenios"),
    session: Session = Depends(get_session)
):
    """Obtener población por edad."""
    # Validaciones
    if anio is None and anio_from is None and anio_to is None:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAM",
                "message": "Debe especificar anio o rango (anio_from/anio_to)"
            }
        )

    if anio_from is not None and anio_to is not None and anio_to < anio_from:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAM",
                "message": "anio_to debe ser mayor o igual a anio_from"
            }
        )

    # Ejecutar consulta
    service = PopulationService(session)
    results = service.get_population_by_age(
        territorio_ids=territorio_id,
        anio=anio,
        anio_from=anio_from,
        anio_to=anio_to,
        area=area,
        sexo=sexo,
        quinquenios=quinquenios
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No se encontraron datos para los parámetros especificados"
            }
        )

    return results


@router.get(
    "/urban_rural",
    response_model=UrbanRuralResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Distribución urbano-rural",
    description="""
    Retorna la distribución de población entre áreas urbanas y rurales.

    **Parámetros:**
    - `territorio_id`: Código DANE del territorio
    - `anio`: Año de consulta (2018-2050)

    **Ejemplo:**
    ```
    GET /api/v1/population/urban_rural?territorio_id=05&anio=2025
    ```
    """
)
def get_urban_rural(
    territorio_id: str = Query(..., description="Código del territorio"),
    anio: int = Query(..., ge=2018, le=2050, description="Año"),
    session: Session = Depends(get_session)
):
    """Obtener distribución urbano-rural."""
    service = PopulationService(session)
    result = service.get_urban_rural_distribution(territorio_id, anio)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": f"No se encontraron datos para territorio {territorio_id} en año {anio}"
            }
        )

    return result


@router.get(
    "/growth",
    response_model=GrowthResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Crecimiento poblacional",
    description="""
    Calcula métricas de crecimiento poblacional por período.

    **Períodos disponibles:**
    - `hasta_2019`: Desde 2018 hasta 2019
    - `desde_2020`: Desde 2020 hasta 2050

    **Métricas calculadas:**
    - CAGR: Tasa de crecimiento anual compuesta
    - Variación total: Cambio porcentual entre t0 y t1

    **Ejemplo:**
    ```
    GET /api/v1/population/growth?territorio_id=05001&periodo=desde_2020
    ```
    """
)
def get_growth(
    territorio_id: str = Query(..., description="Código del territorio"),
    periodo: str = Query(..., regex="^(hasta_2019|desde_2020)$", description="Período"),
    area: str = Query("Total", description="Área geográfica"),
    session: Session = Depends(get_session)
):
    """Obtener crecimiento poblacional."""
    service = PopulationService(session)
    result = service.calculate_growth(territorio_id, periodo, area)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": f"No se encontraron datos para calcular crecimiento"
            }
        )

    return result


@router.get(
    "/pyramid",
    response_model=PyramidResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Pirámide poblacional",
    description="""
    Retorna datos para generar pirámide poblacional (distribución por edad y sexo).

    **Parámetros:**
    - `territorio_id`: Código DANE del territorio
    - `anio`: Año de consulta
    - `area`: Área geográfica
    - `modo`: 'simple' (edad por edad) o 'quinquenal' (grupos de 5 años)

    **Ejemplo:**
    ```
    GET /api/v1/population/pyramid?territorio_id=05001&anio=2025&modo=simple
    ```
    """
)
def get_pyramid(
    territorio_id: str = Query(..., description="Código del territorio"),
    anio: int = Query(..., ge=2018, le=2050, description="Año"),
    area: str = Query("Total", description="Área geográfica"),
    modo: str = Query("simple", regex="^(simple|quinquenal)$", description="Modo de agrupación"),
    session: Session = Depends(get_session)
):
    """Obtener datos para pirámide poblacional."""
    service = PopulationService(session)
    result = service.get_pyramid_data(territorio_id, anio, area, modo)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": f"No se encontraron datos para pirámide"
            }
        )

    return result


@router.post(
    "/compare",
    response_model=CompareResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    },
    summary="Comparar territorios",
    description="""
    Compara múltiples territorios en un año específico.

    **Métricas disponibles:**
    - `poblacion_total`: Población total
    - `pct_urbana`: Porcentaje urbano
    - `envejecimiento`: Índice de envejecimiento (65+ / 0-14)
    - `dependencia`: Índice de dependencia ((0-14 + 65+) / 15-64)
    - `cagr`: Tasa de crecimiento anual compuesta (desde 2020)

    **Ejemplo:**
    ```json
    POST /api/v1/population/compare
    {
      "territorios": ["05001", "11001"],
      "anio": 2025,
      "area": "Total",
      "metricas": ["poblacion_total", "pct_urbana", "envejecimiento"]
    }
    ```
    """
)
def compare_territories(
    request: PopulationCompareRequest,
    session: Session = Depends(get_session)
):
    """Comparar territorios."""
    # Validaciones
    if len(request.territorios) < 2:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAM",
                "message": "Debe especificar al menos 2 territorios para comparar"
            }
        )

    if len(request.territorios) > 10:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAM",
                "message": "Máximo 10 territorios por comparación"
            }
        )

    # Ejecutar comparación
    service = PopulationService(session)
    results = service.compare_territories(
        territorio_ids=request.territorios,
        anio=request.anio,
        area=request.area,
        metricas=request.metricas
    )

    if not results:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No se encontraron datos para los territorios especificados"
            }
        )

    return {
        "anio": request.anio,
        "area": request.area,
        "territorios": results
    }


@router.get(
    "/indicators",
    summary="Indicadores demográficos",
    description="""
    Calcula indicadores demográficos para un territorio y año.

    **Indicadores:**
    - Población infantil (0-14)
    - Población activa (15-64)
    - Población mayor (65+)
    - Índice de dependencia
    - Índice de envejecimiento

    **Ejemplo:**
    ```
    GET /api/v1/population/indicators?territorio_id=05001&anio=2025
    ```
    """
)
def get_indicators(
    territorio_id: str = Query(..., description="Código del territorio"),
    anio: int = Query(..., ge=2018, le=2050, description="Año"),
    area: str = Query("Total", description="Área geográfica"),
    session: Session = Depends(get_session)
):
    """Obtener indicadores demográficos."""
    service = PopulationService(session)
    result = service.calculate_demographic_indicators(territorio_id, anio, area)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No se encontraron datos para calcular indicadores"
            }
        )

    return result


@router.get(
    "/time_series",
    summary="Serie de tiempo de población",
    description="""
    Retorna serie de tiempo de población total con crecimiento y delta.

    **Parámetros:**
    - `territorio_id`: Código DANE del territorio (departamento o municipio)
    - `anio_from`: Año inicial (default: 2018)
    - `anio_to`: Año final (default: 2050)
    - `area`: Área geográfica

    **Métricas por año:**
    - `poblacion`: Población total
    - `delta`: Cambio absoluto respecto al año anterior
    - `tasa_crecimiento`: Tasa de crecimiento porcentual

    **Ejemplo:**
    ```
    GET /api/v1/population/time_series?territorio_id=05&anio_from=2020&anio_to=2030
    ```
    """
)
def get_time_series(
    territorio_id: str = Query(..., description="Código del territorio"),
    anio_from: int = Query(2018, ge=2018, le=2050, description="Año inicial"),
    anio_to: int = Query(2050, ge=2018, le=2050, description="Año final"),
    area: str = Query("Total", description="Área geográfica"),
    session: Session = Depends(get_session)
):
    """Obtener serie de tiempo de población."""
    if anio_to < anio_from:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PARAM",
                "message": "anio_to debe ser mayor o igual a anio_from"
            }
        )

    service = PopulationService(session)
    result = service.get_population_time_series(territorio_id, anio_from, anio_to, area)

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": "No se encontraron datos para la serie de tiempo"
            }
        )

    return {
        "territorio_id": territorio_id,
        "anio_from": anio_from,
        "anio_to": anio_to,
        "area": area,
        "series": result
    }


@router.get(
    "/territories",
    summary="Listar territorios",
    description="""
    Retorna la lista de territorios disponibles.

    **Parámetros:**
    - `nivel`: Filtrar por nivel (DEPARTAMENTAL, MUNICIPAL)
    - `search`: Buscar por nombre o código
    - `limit`: Límite de resultados (default: 1000)

    **Ejemplo:**
    ```
    GET /api/v1/population/territories?nivel=MUNICIPAL&search=Bogotá
    ```
    """
)
def get_territories(
    nivel: Optional[str] = Query(None, description="Nivel territorial"),
    search: Optional[str] = Query(None, description="Buscar por nombre o código"),
    limit: int = Query(1000, le=2000, description="Límite de resultados"),
    session: Session = Depends(get_session)
):
    """Obtener lista de territorios."""
    service = PopulationService(session)
    results = service.get_territories(nivel=nivel, search=search, limit=limit)

    return results
