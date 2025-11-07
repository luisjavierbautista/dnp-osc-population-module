"""
Servicio de cálculos demográficos y consultas de población.
"""
from typing import List, Optional, Dict, Tuple
from decimal import Decimal
from sqlmodel import Session, select, func, and_, or_
from ..models import PoblacionEdad, PoblacionTotal, Territorio, Sexo, AreaGeografica
import math


class PopulationService:
    """Servicio para consultas y cálculos de población."""

    def __init__(self, session: Session):
        """
        Inicializa el servicio.

        Args:
            session: Sesión de base de datos
        """
        self.session = session

    def get_population_by_age(
        self,
        territorio_ids: List[str],
        anio: Optional[int] = None,
        anio_from: Optional[int] = None,
        anio_to: Optional[int] = None,
        area: str = "Total",
        sexo: str = "T",
        quinquenios: bool = False
    ) -> List[Dict]:
        """
        Obtiene población por edad para territorio(s) y año(s).

        Args:
            territorio_ids: Lista de códigos de territorios
            anio: Año específico
            anio_from: Año inicial (rango)
            anio_to: Año final (rango)
            area: Área geográfica
            sexo: Sexo (H, M, T)
            quinquenios: Agrupar por quinquenios

        Returns:
            Lista de resultados por territorio y año
        """
        # Construir query
        stmt = select(PoblacionEdad).where(
            and_(
                PoblacionEdad.territorio_id.in_(territorio_ids),
                PoblacionEdad.area_geografica == area,
                PoblacionEdad.sexo == sexo
            )
        )

        # Filtro de año
        if anio is not None:
            stmt = stmt.where(PoblacionEdad.anio == anio)
        elif anio_from is not None and anio_to is not None:
            stmt = stmt.where(
                and_(
                    PoblacionEdad.anio >= anio_from,
                    PoblacionEdad.anio <= anio_to
                )
            )
        elif anio_from is not None:
            stmt = stmt.where(PoblacionEdad.anio >= anio_from)

        # Ejecutar query
        results = self.session.exec(stmt).all()

        # Agrupar resultados
        grouped = {}
        for row in results:
            key = (row.territorio_id, row.anio)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(row)

        # Formatear salida
        output = []
        for (terr_id, year), rows in grouped.items():
            if quinquenios:
                edad_bins = self._aggregate_quinquenios(rows)
            else:
                edad_bins = [
                    {
                        "edad": row.edad,
                        "poblacion": float(row.poblacion)
                    }
                    for row in sorted(rows, key=lambda x: x.edad)
                ]

            output.append({
                "territorioId": terr_id,
                "anio": year,
                "area": area,
                "sexo": sexo,
                "edadBins": edad_bins
            })

        return output

    def _aggregate_quinquenios(self, rows: List[PoblacionEdad]) -> List[Dict]:
        """
        Agrupa edades en quinquenios: [0-4], [5-9], ..., [95-99], [100+].

        Args:
            rows: Registros de población por edad

        Returns:
            Lista de bins quinquenales
        """
        quinquenios = {}

        for row in rows:
            if row.edad >= 100:
                key = 100
            else:
                key = (row.edad // 5) * 5

            if key not in quinquenios:
                quinquenios[key] = 0
            quinquenios[key] += float(row.poblacion)

        return [
            {
                "edad": edad_inicio,
                "edadFin": min(edad_inicio + 4, 100) if edad_inicio < 100 else None,
                "poblacion": poblacion
            }
            for edad_inicio, poblacion in sorted(quinquenios.items())
        ]

    def get_urban_rural_distribution(
        self,
        territorio_id: str,
        anio: int
    ) -> Optional[Dict]:
        """
        Calcula distribución urbano-rural para un territorio y año.

        Args:
            territorio_id: Código del territorio
            anio: Año

        Returns:
            Diccionario con población urbana y rural
        """
        # Obtener totales por área
        stmt = select(PoblacionTotal).where(
            and_(
                PoblacionTotal.territorio_id == territorio_id,
                PoblacionTotal.anio == anio
            )
        )
        results = self.session.exec(stmt).all()

        # Buscar por área
        urbana = None
        rural = None

        for row in results:
            if row.area_geografica == AreaGeografica.CABECERA.value:
                urbana = float(row.pob_total)
            elif row.area_geografica == AreaGeografica.CPRD.value:
                rural = float(row.pob_total)

        if urbana is None or rural is None:
            return None

        total = urbana + rural
        return {
            "territorioId": territorio_id,
            "anio": anio,
            "urbana": urbana,
            "rural": rural,
            "pctUrbana": round(urbana / total, 4) if total > 0 else 0,
            "pctRural": round(rural / total, 4) if total > 0 else 0
        }

    def calculate_growth(
        self,
        territorio_id: str,
        periodo: str,
        area: str = "Total"
    ) -> Optional[Dict]:
        """
        Calcula crecimiento poblacional por periodo.

        Periodos:
        - "hasta_2019": desde primer año disponible hasta 2019
        - "desde_2020": desde 2020 hasta último año disponible

        Args:
            territorio_id: Código del territorio
            periodo: Periodo de análisis
            area: Área geográfica

        Returns:
            Diccionario con métricas de crecimiento
        """
        # Definir años según periodo
        if periodo == "hasta_2019":
            t0, t1 = 2018, 2019
        elif periodo == "desde_2020":
            t0, t1 = 2020, 2050
        else:
            return None

        # Obtener población en t0 y t1
        stmt = select(PoblacionTotal).where(
            and_(
                PoblacionTotal.territorio_id == territorio_id,
                PoblacionTotal.area_geografica == area,
                or_(
                    PoblacionTotal.anio == t0,
                    PoblacionTotal.anio == t1
                )
            )
        )
        results = self.session.exec(stmt).all()

        pob_t0, pob_t1 = None, None
        for row in results:
            if row.anio == t0:
                pob_t0 = float(row.pob_total)
            elif row.anio == t1:
                pob_t1 = float(row.pob_total)

        if pob_t0 is None or pob_t1 is None or pob_t0 == 0:
            return None

        # Calcular CAGR
        years = t1 - t0
        cagr = (pob_t1 / pob_t0) ** (1 / years) - 1 if years > 0 else 0

        # Variación total
        variacion_total = (pob_t1 - pob_t0) / pob_t0

        return {
            "territorioId": territorio_id,
            "periodo": periodo,
            "t0": t0,
            "t1": t1,
            "pT0": pob_t0,
            "pT1": pob_t1,
            "cagr": round(cagr, 6),
            "variacionTotal": round(variacion_total, 4)
        }

    def get_pyramid_data(
        self,
        territorio_id: str,
        anio: int,
        area: str = "Total",
        modo: str = "simple"
    ) -> Optional[Dict]:
        """
        Obtiene datos para pirámide poblacional.

        Args:
            territorio_id: Código del territorio
            anio: Año
            area: Área geográfica
            modo: 'simple' o 'quinquenal'

        Returns:
            Diccionario con series de hombres y mujeres
        """
        # Obtener datos para H y M
        stmt = select(PoblacionEdad).where(
            and_(
                PoblacionEdad.territorio_id == territorio_id,
                PoblacionEdad.anio == anio,
                PoblacionEdad.area_geografica == area,
                PoblacionEdad.sexo.in_([Sexo.HOMBRE.value, Sexo.MUJER.value])
            )
        ).order_by(PoblacionEdad.edad)

        results = self.session.exec(stmt).all()

        # Separar por sexo
        hombres_data = {}
        mujeres_data = {}

        for row in results:
            edad = row.edad
            if row.sexo == Sexo.HOMBRE.value:
                hombres_data[edad] = float(row.poblacion)
            else:
                mujeres_data[edad] = float(row.poblacion)

        # Generar series
        if modo == "quinquenal":
            series = self._pyramid_quinquenios(hombres_data, mujeres_data)
        else:
            # Simple: edad por edad
            edades = sorted(set(hombres_data.keys()) | set(mujeres_data.keys()))
            series = [
                {
                    "edad": edad,
                    "hombres": hombres_data.get(edad, 0),
                    "mujeres": mujeres_data.get(edad, 0)
                }
                for edad in edades
            ]

        return {
            "territorioId": territorio_id,
            "anio": anio,
            "area": area,
            "modo": modo,
            "series": series
        }

    def _pyramid_quinquenios(
        self,
        hombres_data: Dict[int, float],
        mujeres_data: Dict[int, float]
    ) -> List[Dict]:
        """
        Agrupa datos de pirámide en quinquenios.

        Args:
            hombres_data: Población de hombres por edad
            mujeres_data: Población de mujeres por edad

        Returns:
            Lista de bins quinquenales
        """
        quinquenios_h = {}
        quinquenios_m = {}

        # Agrupar hombres
        for edad, pob in hombres_data.items():
            key = (edad // 5) * 5 if edad < 100 else 100
            quinquenios_h[key] = quinquenios_h.get(key, 0) + pob

        # Agrupar mujeres
        for edad, pob in mujeres_data.items():
            key = (edad // 5) * 5 if edad < 100 else 100
            quinquenios_m[key] = quinquenios_m.get(key, 0) + pob

        # Combinar
        edades = sorted(set(quinquenios_h.keys()) | set(quinquenios_m.keys()))
        return [
            {
                "edad": edad,
                "hombres": quinquenios_h.get(edad, 0),
                "mujeres": quinquenios_m.get(edad, 0)
            }
            for edad in edades
        ]

    def calculate_demographic_indicators(
        self,
        territorio_id: str,
        anio: int,
        area: str = "Total"
    ) -> Optional[Dict]:
        """
        Calcula indicadores demográficos (bono demográfico, envejecimiento).

        Grupos de edad:
        - 0-14: Infantil
        - 15-64: Activa
        - 65+: Mayor

        Indicadores:
        - dependencia = (0-14 + 65+) / (15-64)
        - envejecimiento = (65+) / (0-14)

        Args:
            territorio_id: Código del territorio
            anio: Año
            area: Área geográfica

        Returns:
            Diccionario con indicadores
        """
        # Obtener población por edad (sexo total)
        stmt = select(PoblacionEdad).where(
            and_(
                PoblacionEdad.territorio_id == territorio_id,
                PoblacionEdad.anio == anio,
                PoblacionEdad.area_geografica == area,
                PoblacionEdad.sexo == Sexo.TOTAL.value
            )
        )
        results = self.session.exec(stmt).all()

        # Agrupar por rangos
        infantil = 0  # 0-14
        activa = 0    # 15-64
        mayor = 0     # 65+

        for row in results:
            edad = row.edad
            pob = float(row.poblacion)

            if edad <= 14:
                infantil += pob
            elif edad <= 64:
                activa += pob
            else:
                mayor += pob

        # Calcular indicadores
        dependencia = (infantil + mayor) / activa if activa > 0 else None
        envejecimiento = mayor / infantil if infantil > 0 else None

        return {
            "territorioId": territorio_id,
            "anio": anio,
            "area": area,
            "infantil": infantil,
            "activa": activa,
            "mayor": mayor,
            "dependencia": round(dependencia, 4) if dependencia else None,
            "envejecimiento": round(envejecimiento, 4) if envejecimiento else None
        }

    def compare_territories(
        self,
        territorio_ids: List[str],
        anio: int,
        area: str = "Total",
        metricas: List[str] = None
    ) -> List[Dict]:
        """
        Compara múltiples territorios en un año.

        Args:
            territorio_ids: Lista de códigos de territorios
            anio: Año de comparación
            area: Área geográfica
            metricas: Lista de métricas a incluir

        Returns:
            Lista con métricas de cada territorio
        """
        if metricas is None:
            metricas = ["poblacion_total", "pct_urbana", "envejecimiento"]

        results = []

        for terr_id in territorio_ids:
            # Obtener territorio
            territorio = self.session.exec(
                select(Territorio).where(Territorio.territorio_id == terr_id)
            ).first()

            if not territorio:
                continue

            metrics = {
                "territorioId": terr_id,
                "nombre": territorio.nombre
            }

            # Población total
            if "poblacion_total" in metricas:
                pob_total = self.session.exec(
                    select(PoblacionTotal).where(
                        and_(
                            PoblacionTotal.territorio_id == terr_id,
                            PoblacionTotal.anio == anio,
                            PoblacionTotal.area_geografica == area
                        )
                    )
                ).first()

                metrics["poblacionTotal"] = float(pob_total.pob_total) if pob_total else None

            # Porcentaje urbano
            if "pct_urbana" in metricas:
                urban_rural = self.get_urban_rural_distribution(terr_id, anio)
                metrics["pctUrbana"] = urban_rural["pctUrbana"] if urban_rural else None

            # Envejecimiento
            if "envejecimiento" in metricas:
                indicators = self.calculate_demographic_indicators(terr_id, anio, area)
                metrics["envejecimiento"] = indicators["envejecimiento"] if indicators else None

            # Dependencia
            if "dependencia" in metricas:
                indicators = self.calculate_demographic_indicators(terr_id, anio, area)
                metrics["dependencia"] = indicators["dependencia"] if indicators else None

            # CAGR
            if "cagr" in metricas:
                growth = self.calculate_growth(terr_id, "desde_2020", area)
                metrics["cagr"] = growth["cagr"] if growth else None

            results.append(metrics)

        return results
