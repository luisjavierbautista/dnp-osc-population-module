"""
Endpoints para datos de mapas.
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
import httpx

from ....db.database import get_session
from ....services import PopulationService

router = APIRouter()

# DNP GIS Server URLs
DNP_GIS_MUNICIPALITIES_URL = "https://gis.dnp.gov.co/server/rest/services/osc/territorios/MapServer/4/query?where=1%3D1&outFields=*&returnGeometry=true&f=geojson"
DNP_GIS_DEPARTMENTS_URL = "https://gis.dnp.gov.co/server/rest/services/osc/territorios/MapServer/2/query?where=1%3D1&outFields=*&returnGeometry=true&f=geojson"


@router.get(
    "/geojson",
    summary="GeoJSON con datos de población",
    description="""
    Retorna GeoJSON de territorios colombianos enriquecido con datos de población.

    **Parámetros:**
    - `nivel`: DEPARTAMENTAL o MUNICIPAL
    - `anio`: Año de consulta
    - `area`: Área geográfica
    - `variable`: Variable a mostrar (poblacion_total, pct_urbana, envejecimiento, dependencia)

    **Ejemplo:**
    ```
    GET /api/v1/map/geojson?nivel=DEPARTAMENTAL&anio=2020&area=Total&variable=poblacion_total
    ```
    """
)
async def get_map_geojson(
    nivel: str = Query("DEPARTAMENTAL", regex="^(DEPARTAMENTAL|MUNICIPAL)$", description="Nivel territorial"),
    anio: int = Query(..., ge=1985, le=2050, description="Año"),
    area: str = Query("Total", description="Área geográfica"),
    variable: str = Query("poblacion_total", description="Variable a visualizar"),
    session: Session = Depends(get_session)
):
    """Obtener GeoJSON enriquecido con datos de población."""
    service = PopulationService(session)

    # Select GeoJSON source
    geojson_url = DNP_GIS_DEPARTMENTS_URL if nivel == "DEPARTAMENTAL" else DNP_GIS_MUNICIPALITIES_URL

    # Fetch GeoJSON from DNP
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(geojson_url)
            response.raise_for_status()
            geojson = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching GeoJSON: {str(e)}")

    # Enrich features with population data
    from ....models.poblacion import PoblacionTotal, PoblacionEdad
    from sqlmodel import select, and_, func

    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})

        # Get territorio_id from properties
        # The CODIGO field from DNP GIS contains the DANE code
        territorio_id_raw = properties.get("CODIGO")

        if not territorio_id_raw:
            # Try other common fields as fallback
            territorio_id_raw = properties.get("DPTO_CCDGO") or properties.get("MPIO_CCDGO") or properties.get("codigo")

        # Initialize value
        value = None

        if territorio_id_raw:
            # Convert to string and handle both departmental and municipal codes
            territorio_id = str(territorio_id_raw)

            # For municipalities, CODIGO should be 5 digits (e.g., "05001")
            # For departments, CODIGO should be 2 digits (e.g., "05")
            # Skip regional codes like "R01", "R02", etc.
            if territorio_id.startswith('R'):
                # Regional grouping, skip enrichment
                properties["territorio_id"] = territorio_id
                properties["value"] = None
                properties["variable"] = variable
                properties["anio"] = anio
                continue

            # Ensure proper padding based on nivel
            if nivel == "DEPARTAMENTAL":
                # Departments are 2 digits
                territorio_id = territorio_id.zfill(2)
            else:
                # Municipalities are 5 digits
                territorio_id = territorio_id.zfill(5)

            # Get population data based on variable
            if variable == "poblacion_total":
                # Calculate total from poblacion_edad since poblacion_total table is empty
                stmt = select(func.sum(PoblacionEdad.poblacion)).where(
                    and_(
                        PoblacionEdad.territorio_id == territorio_id,
                        PoblacionEdad.anio == anio,
                        PoblacionEdad.area_geografica == area
                    )
                )
                total = session.exec(stmt).first()
                value = float(total) if total else None

            elif variable == "pct_urbana":
                urban_data = service.get_urban_rural_distribution(territorio_id, anio)
                value = urban_data.get("pctUrbana") if urban_data else None

            elif variable in ["envejecimiento", "dependencia"]:
                indicators = service.calculate_demographic_indicators(territorio_id, anio, area)
                if indicators:
                    value = indicators.get(f"indice_{variable}") if indicators else None

        # Add population data to properties
        properties["territorio_id"] = territorio_id
        properties["value"] = value
        properties["variable"] = variable
        properties["anio"] = anio

    return geojson
