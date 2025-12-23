"""
ETL para cargar y procesar datos de población del DANE.

Este script procesa archivos CSV con proyecciones de población del DANE
(departamental y municipal) y los carga en la base de datos en formato normalizado.
"""
import re
import sys
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from decimal import Decimal
from sqlmodel import Session, create_engine, select
from sqlalchemy import text
import logging

# Agregar el directorio backend al path para importar modelos
# When running in Docker, backend is at /app
# When running locally, backend is at ../../../backend
backend_path = Path("/app") if Path("/app/app").exists() else Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

from app.models import Territorio, PoblacionEdad, PoblacionTotal, NivelTerritorial, AreaGeografica, Sexo
from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DANEDataProcessor:
    """Procesador de datos DANE."""

    # Patrones regex para parsear columnas de edad
    # Soporta dos formatos:
    # 1. Hombres_0, Mujeres_25, Total_100 y más, etc.
    # 2. Hombres 0 años, Mujeres 25 años, Total 100 años y más
    AGE_PATTERN = re.compile(r'^(Hombres|Mujeres|Total)[_\s]+(\d{1,3})(?:[\s_]+(?:años?))?([\s_]+y[\s_]+más)?$', re.IGNORECASE)

    def __init__(self, engine):
        """
        Inicializa el procesador.

        Args:
            engine: SQLAlchemy engine
        """
        self.engine = engine

    @staticmethod
    def parse_numeric(value: str) -> Optional[float]:
        """
        Convierte un string numérico a float, manejando separadores de miles.

        Args:
            value: Valor string a convertir

        Returns:
            Valor numérico o None si no se puede convertir
        """
        if pd.isna(value):
            return None
        try:
            # Remover puntos (separadores de miles) y comas
            cleaned = str(value).replace('.', '').replace(',', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def parse_age_column(column_name: str) -> Optional[Tuple[str, int, bool]]:
        """
        Parsea el nombre de una columna de edad.

        Args:
            column_name: Nombre de la columna (ej: "Hombres 25 años")

        Returns:
            Tupla (sexo, edad, mayores_100) o None si no coincide
        """
        match = DANEDataProcessor.AGE_PATTERN.match(column_name.strip())
        if not match:
            return None

        sexo_str = match.group(1)
        edad_str = match.group(2)
        es_mayor_100 = match.group(3) is not None

        sexo = {'Hombres': 'H', 'Mujeres': 'M', 'Total': 'T'}[sexo_str]
        edad = 100 if es_mayor_100 else int(edad_str)

        return sexo, edad, es_mayor_100

    def normalize_area(self, area: str) -> str:
        """
        Normaliza el nombre del área geográfica.

        Args:
            area: Nombre del área

        Returns:
            Nombre normalizado
        """
        # Handle non-string values (e.g., float NaN)
        if not isinstance(area, str):
            return str(area) if area is not None else ''

        area = area.strip()
        # Mapeo de variantes
        area_map = {
            'cabecera municipal': AreaGeografica.CABECERA.value,
            'cabecera': AreaGeografica.CABECERA.value,
            'centros poblados y rural disperso': AreaGeografica.CPRD.value,
            'cprd': AreaGeografica.CPRD.value,
            'rural': AreaGeografica.CPRD.value,
            'total': AreaGeografica.TOTAL.value,
        }
        return area_map.get(area.lower(), area)

    def load_departamental(self, csv_path: str) -> pd.DataFrame:
        """
        Carga y procesa datos departamentales.

        Args:
            csv_path: Ruta al archivo CSV departamental

        Returns:
            DataFrame en formato largo (tidy)
        """
        logger.info(f"Cargando datos departamentales desde {csv_path}")

        # Cargar CSV
        df = pd.read_csv(csv_path, dtype=str)
        logger.info(f"Filas cargadas: {len(df)}")

        # Normalizar strings (handle NaN values)
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Identificar columnas de edad
        age_cols = [col for col in df.columns if self.parse_age_column(col) is not None]
        logger.info(f"Columnas de edad encontradas: {len(age_cols)}")

        # Convertir columnas numéricas
        numeric_cols = ['Total', 'Hombres', 'Mujeres'] + age_cols
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(self.parse_numeric)

        # Padding de códigos
        df['DP'] = df['DP'].str.zfill(2)

        # Normalizar área geográfica
        if 'ÁREA GEOGRÁFICA' in df.columns:
            df['ÁREA GEOGRÁFICA'] = df['ÁREA GEOGRÁFICA'].apply(self.normalize_area)

        # Melt a formato largo
        id_vars = ['DP', 'DPNOM', 'AÑO', 'ÁREA GEOGRÁFICA']
        long_df = df.melt(
            id_vars=id_vars,
            value_vars=age_cols,
            var_name='edad_col',
            value_name='poblacion'
        )

        # Parsear edad, sexo y mayores_100
        parsed = long_df['edad_col'].apply(self.parse_age_column)
        long_df[['sexo', 'edad', 'mayores_100']] = pd.DataFrame(
            parsed.tolist(), index=long_df.index
        )

        # Renombrar columnas
        long_df = long_df.rename(columns={
            'DP': 'territorio_id',
            'DPNOM': 'nombre',
            'AÑO': 'anio',
            'ÁREA GEOGRÁFICA': 'area_geografica'
        })

        # Agregar nivel territorial
        long_df['nivel'] = NivelTerritorial.DEPARTAMENTAL.value
        long_df['dp'] = long_df['territorio_id']
        long_df['mpio'] = None

        # Limpiar filas sin población
        long_df = long_df[long_df['poblacion'].notna()].copy()

        logger.info(f"Filas procesadas en formato largo: {len(long_df)}")
        return long_df

    def load_municipal(self, csv_path: str) -> pd.DataFrame:
        """
        Carga y procesa datos municipales.

        Args:
            csv_path: Ruta al archivo CSV municipal

        Returns:
            DataFrame en formato largo (tidy)
        """
        logger.info(f"Cargando datos municipales desde {csv_path}")

        # Cargar CSV
        df = pd.read_csv(csv_path, dtype=str)
        logger.info(f"Filas cargadas: {len(df)}")

        # Normalizar strings (handle NaN values)
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Identificar columnas de edad
        age_cols = [col for col in df.columns if self.parse_age_column(col) is not None]
        logger.info(f"Columnas de edad encontradas: {len(age_cols)}")

        # Convertir columnas numéricas
        numeric_cols = ['Total', 'Hombres', 'Mujeres'] + age_cols
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].apply(self.parse_numeric)

        # Padding de códigos
        df['DP'] = df['DP'].str.zfill(2)
        df['MPIO'] = df['MPIO'].str.zfill(3)

        # Generar DPMP si no existe
        if 'DPMP' not in df.columns:
            df['DPMP'] = df['DP'] + df['MPIO']
        else:
            df['DPMP'] = df['DPMP'].str.zfill(5)

        # Normalizar área geográfica
        if 'ÁREA GEOGRÁFICA' in df.columns:
            df['ÁREA GEOGRÁFICA'] = df['ÁREA GEOGRÁFICA'].apply(self.normalize_area)

        # Melt a formato largo
        id_vars = ['DP', 'DPNOM', 'MPIO', 'MPNOM', 'DPMP', 'AÑO', 'ÁREA GEOGRÁFICA']
        # Filtrar id_vars que existen en el DataFrame
        id_vars = [col for col in id_vars if col in df.columns]

        long_df = df.melt(
            id_vars=id_vars,
            value_vars=age_cols,
            var_name='edad_col',
            value_name='poblacion'
        )

        # Parsear edad, sexo y mayores_100
        parsed = long_df['edad_col'].apply(self.parse_age_column)
        long_df[['sexo', 'edad', 'mayores_100']] = pd.DataFrame(
            parsed.tolist(), index=long_df.index
        )

        # Renombrar columnas
        # Note: DPMP in some files is the municipality NAME, MPIO is the full code
        rename_map = {
            'AÑO': 'anio',
            'ÁREA GEOGRÁFICA': 'area_geografica'
        }

        # Handle territorio_id: prefer MPIO (full code), fallback to DPMP
        if 'MPIO' in long_df.columns:
            rename_map['MPIO'] = 'territorio_id'
            # DPMP might be the name if MPIO exists
            if 'DPMP' in long_df.columns:
                rename_map['DPMP'] = 'nombre'
        elif 'DPMP' in long_df.columns:
            rename_map['DPMP'] = 'territorio_id'

        # Handle nombre: prefer MPNOM, fallback already handled above
        if 'MPNOM' in long_df.columns:
            rename_map['MPNOM'] = 'nombre'

        long_df = long_df.rename(columns=rename_map)

        # Agregar nivel territorial
        long_df['nivel'] = NivelTerritorial.MUNICIPAL.value

        # Extract codes from territorio_id or existing columns
        if 'DP' in long_df.columns:
            long_df['dp'] = long_df['DP']
        else:
            long_df['dp'] = long_df['territorio_id'].str[:2]

        # mpio should be the 3-digit municipality code
        long_df['mpio'] = long_df['territorio_id'].str[2:5]  # Extract last 3 digits

        # Limpiar filas sin población
        long_df = long_df[long_df['poblacion'].notna()].copy()

        logger.info(f"Filas procesadas en formato largo: {len(long_df)}")
        return long_df

    def load_municipal_chunked(self, csv_path: str, chunk_size: int = 1000):
        """
        Carga y procesa datos municipales en chunks para evitar problemas de memoria.

        Args:
            csv_path: Ruta al archivo CSV municipal
            chunk_size: Número de filas a procesar por vez

        Yields:
            DataFrames en formato largo (tidy), uno por chunk
        """
        logger.info(f"Cargando datos municipales en chunks de {chunk_size} filas desde {csv_path}")

        # Leer en chunks
        chunks_processed = 0
        total_rows_processed = 0

        for chunk_df in pd.read_csv(csv_path, dtype=str, chunksize=chunk_size):
            chunks_processed += 1
            logger.info(f"Procesando chunk {chunks_processed} ({len(chunk_df)} filas)...")

            # Normalizar strings (handle NaN values)
            for col in chunk_df.select_dtypes(include=['object']).columns:
                chunk_df[col] = chunk_df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)

            # Identificar columnas de edad
            age_cols = [col for col in chunk_df.columns if self.parse_age_column(col) is not None]

            # Convertir columnas numéricas
            numeric_cols = ['Total', 'Hombres', 'Mujeres'] + age_cols
            for col in numeric_cols:
                if col in chunk_df.columns:
                    chunk_df[col] = chunk_df[col].apply(self.parse_numeric)

            # Padding de códigos
            if 'DP' in chunk_df.columns:
                chunk_df['DP'] = chunk_df['DP'].str.zfill(2)
            if 'MPIO' in chunk_df.columns:
                chunk_df['MPIO'] = chunk_df['MPIO'].str.zfill(5)

            # Normalizar área geográfica
            if 'ÁREA GEOGRÁFICA' in chunk_df.columns:
                chunk_df['ÁREA GEOGRÁFICA'] = chunk_df['ÁREA GEOGRÁFICA'].apply(self.normalize_area)

            # Melt a formato largo
            id_vars = ['DP', 'DPNOM', 'MPIO', 'MPNOM', 'DPMP', 'AÑO', 'ÁREA GEOGRÁFICA']
            # Filtrar id_vars que existen en el DataFrame
            id_vars = [col for col in id_vars if col in chunk_df.columns]

            long_df = chunk_df.melt(
                id_vars=id_vars,
                value_vars=age_cols,
                var_name='edad_col',
                value_name='poblacion'
            )

            # Parsear edad, sexo y mayores_100
            parsed = long_df['edad_col'].apply(self.parse_age_column)
            long_df[['sexo', 'edad', 'mayores_100']] = pd.DataFrame(
                parsed.tolist(), index=long_df.index
            )

            # Renombrar columnas
            rename_map = {
                'AÑO': 'anio',
                'ÁREA GEOGRÁFICA': 'area_geografica'
            }

            # Detect which format: DANE changed column meanings between file versions!
            # Old format (1985-1994): DPMP=code, MPIO=name
            # New format (2005+): DPMP=name, MPIO=code
            # We detect by checking if MPIO looks like a code (5 digits) or name
            if 'MPIO' in long_df.columns and 'DPMP' in long_df.columns:
                # Sample first non-null MPIO value to detect format
                sample_mpio = long_df['MPIO'].dropna().iloc[0] if len(long_df['MPIO'].dropna()) > 0 else ''
                sample_dpmp = long_df['DPMP'].dropna().iloc[0] if len(long_df['DPMP'].dropna()) > 0 else ''

                # Check if MPIO is numeric (code) or text (name)
                if sample_mpio.isdigit() and len(sample_mpio) == 5:
                    # New format: MPIO is code, DPMP is name
                    rename_map['MPIO'] = 'territorio_id'
                    rename_map['DPMP'] = 'nombre'
                elif sample_dpmp.isdigit() and len(sample_dpmp) == 5:
                    # Old format: DPMP is code, MPIO is name
                    rename_map['DPMP'] = 'territorio_id'
                    rename_map['MPIO'] = 'nombre'
                else:
                    # Fallback: assume MPIO is code
                    rename_map['MPIO'] = 'territorio_id'
                    if 'DPMP' in long_df.columns:
                        rename_map['DPMP'] = 'nombre'
            elif 'MPIO' in long_df.columns:
                rename_map['MPIO'] = 'territorio_id'
            elif 'DPMP' in long_df.columns:
                rename_map['DPMP'] = 'territorio_id'

            # Handle nombre: prefer MPNOM if it exists
            if 'MPNOM' in long_df.columns:
                rename_map['MPNOM'] = 'nombre'

            long_df = long_df.rename(columns=rename_map)

            # Agregar nivel territorial
            long_df['nivel'] = NivelTerritorial.MUNICIPAL.value

            # Extract codes from territorio_id or existing columns
            if 'DP' in long_df.columns:
                long_df['dp'] = long_df['DP']
            else:
                long_df['dp'] = long_df['territorio_id'].str[:2]

            # mpio should be the 3-digit municipality code
            long_df['mpio'] = long_df['territorio_id'].str[2:5]  # Extract last 3 digits

            # Limpiar filas sin población
            long_df = long_df[long_df['poblacion'].notna()].copy()

            total_rows_processed += len(long_df)
            logger.info(f"Chunk {chunks_processed} procesado: {len(long_df)} filas en formato largo (Total acumulado: {total_rows_processed:,})")

            yield long_df

            # Force garbage collection to free memory
            del chunk_df
            del long_df
            import gc
            gc.collect()

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valida la integridad de los datos.

        Args:
            df: DataFrame con datos en formato largo

        Returns:
            DataFrame con flags de validación
        """
        logger.info("Validando integridad de datos...")

        df = df.copy()
        df['validation_errors'] = ''

        # Validar años (DANE data covers 1985-2050)
        invalid_years = ~df['anio'].astype(int).between(1985, 2050)
        if invalid_years.any():
            logger.warning(f"Años inválidos encontrados: {invalid_years.sum()} filas")
            df.loc[invalid_years, 'validation_errors'] += 'invalid_year;'

        # Validar edades
        invalid_ages = ~df['edad'].astype(int).between(0, 100)
        if invalid_ages.any():
            logger.warning(f"Edades inválidas encontradas: {invalid_ages.sum()} filas")
            df.loc[invalid_ages, 'validation_errors'] += 'invalid_age;'

        # TODO: Implementar validaciones de cierre por sexo, edad y área
        # (ver tarea siguiente)

        return df

    def insert_territorios(self, df: pd.DataFrame, session: Session):
        """
        Inserta territorios únicos en la base de datos.

        Args:
            df: DataFrame con datos procesados
            session: Sesión de base de datos
        """
        logger.info("Insertando territorios...")

        # Obtener territorios únicos
        territorios_df = df[['territorio_id', 'nivel', 'dp', 'mpio', 'nombre']].drop_duplicates()

        inserted = 0
        for _, row in territorios_df.iterrows():
            # Verificar si ya existe
            existing = session.exec(
                select(Territorio).where(Territorio.territorio_id == row['territorio_id'])
            ).first()

            if not existing:
                territorio = Territorio(
                    territorio_id=row['territorio_id'],
                    nivel=row['nivel'],
                    dp=row['dp'],
                    mpio=row['mpio'] if pd.notna(row['mpio']) else None,
                    nombre=row['nombre']
                )
                session.add(territorio)
                inserted += 1

        session.commit()
        logger.info(f"Territorios insertados: {inserted}")

    def insert_poblacion_edad(self, df: pd.DataFrame, session: Session, batch_size: int = 50000):
        """
        Inserta datos de población por edad en batches.

        Args:
            df: DataFrame con datos procesados
            session: Sesión de base de datos
            batch_size: Tamaño del batch (default: 50000)
        """
        logger.info(f"Insertando datos de población por edad en batches de {batch_size:,}...")

        total_rows = len(df)
        total_inserted = 0
        total_skipped = 0

        # Usar SQL con ON CONFLICT para manejar duplicados eficientemente
        insert_query = text("""
            INSERT INTO poblacion_edad (territorio_id, anio, area_geografica, sexo, edad, mayores_100, poblacion)
            VALUES (:territorio_id, :anio, :area_geografica, :sexo, :edad, :mayores_100, :poblacion)
            ON CONFLICT (territorio_id, anio, area_geografica, sexo, edad) DO UPDATE SET
                mayores_100 = EXCLUDED.mayores_100,
                poblacion = EXCLUDED.poblacion
        """)

        # Procesar en batches
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_records = []

            for _, row in batch_df.iterrows():
                batch_records.append({
                    'territorio_id': row['territorio_id'],
                    'anio': int(row['anio']),
                    'area_geografica': row['area_geografica'],
                    'sexo': row['sexo'],
                    'edad': int(row['edad']),
                    'mayores_100': bool(row['mayores_100']),
                    'poblacion': float(row['poblacion'])
                })

            # Insertar batch
            try:
                session.execute(insert_query, batch_records)
                session.commit()
                total_inserted += len(batch_records)
                logger.info(f"Progreso: {total_inserted:,}/{total_rows:,} registros insertados ({100*total_inserted/total_rows:.1f}%)")
            except Exception as e:
                logger.warning(f"Error en batch {i}-{i+batch_size}: {e}")
                session.rollback()
                total_skipped += len(batch_records)

        logger.info(f"Total registros procesados: {total_inserted:,} insertados, {total_skipped:,} omitidos")

    def calculate_poblacion_total(self, session: Session):
        """
        Calcula y almacena totales de población.

        Args:
            session: Sesión de base de datos
        """
        logger.info("Calculando totales de población...")

        # Esta es una versión simplificada
        # En producción, se haría con una query SQL más eficiente
        query = text("""
        INSERT INTO poblacion_total (territorio_id, anio, area_geografica, pob_total, pob_hombres, pob_mujeres)
        SELECT
            territorio_id,
            anio,
            area_geografica,
            SUM(CASE WHEN sexo = 'T' THEN poblacion ELSE 0 END) as pob_total,
            SUM(CASE WHEN sexo = 'H' THEN poblacion ELSE 0 END) as pob_hombres,
            SUM(CASE WHEN sexo = 'M' THEN poblacion ELSE 0 END) as pob_mujeres
        FROM poblacion_edad
        GROUP BY territorio_id, anio, area_geografica
        ON CONFLICT (territorio_id, anio, area_geografica) DO UPDATE SET
            pob_total = EXCLUDED.pob_total,
            pob_hombres = EXCLUDED.pob_hombres,
            pob_mujeres = EXCLUDED.pob_mujeres
        """)
        session.exec(query)
        session.commit()
        logger.info("Totales de población calculados")

    def process_file(self, csv_path: str, nivel: str):
        """
        Procesa un archivo completo y carga a BD.

        Args:
            csv_path: Ruta al archivo CSV
            nivel: 'departamental' o 'municipal'
        """
        # Cargar datos
        if nivel == 'departamental':
            df = self.load_departamental(csv_path)
        elif nivel == 'municipal':
            df = self.load_municipal(csv_path)
        else:
            raise ValueError(f"Nivel inválido: {nivel}")

        # Validar
        df = self.validate_data(df)

        # Insertar en BD
        with Session(self.engine) as session:
            self.insert_territorios(df, session)
            self.insert_poblacion_edad(df, session)
            self.calculate_poblacion_total(session)

        logger.info(f"Procesamiento completo de {csv_path}")

    def process_municipal_chunked(self, csv_path: str, chunk_size: int = 1000):
        """
        Procesa un archivo municipal en chunks para evitar problemas de memoria.

        Args:
            csv_path: Ruta al archivo CSV municipal
            chunk_size: Número de filas CSV a procesar por vez
        """
        logger.info(f"Procesando archivo municipal en chunks: {csv_path}")

        # Create database session
        with Session(self.engine) as session:
            # Track unique territorios across chunks
            territorios_inserted = set()

            # Process each chunk
            for chunk_df in self.load_municipal_chunked(csv_path, chunk_size=chunk_size):
                # Validar chunk
                chunk_df = self.validate_data(chunk_df)

                # Insert territorios (only new ones)
                territorios_df = chunk_df[['territorio_id', 'nivel', 'dp', 'mpio', 'nombre']].drop_duplicates()
                for _, row in territorios_df.iterrows():
                    if row['territorio_id'] not in territorios_inserted:
                        # Verificar si ya existe en BD
                        existing = session.exec(
                            select(Territorio).where(Territorio.territorio_id == row['territorio_id'])
                        ).first()

                        if not existing:
                            territorio = Territorio(
                                territorio_id=row['territorio_id'],
                                nivel=row['nivel'],
                                dp=row['dp'],
                                mpio=row['mpio'] if pd.notna(row['mpio']) else None,
                                nombre=row['nombre']
                            )
                            session.add(territorio)
                            territorios_inserted.add(row['territorio_id'])

                session.commit()

                # Insert población data for this chunk
                self.insert_poblacion_edad(chunk_df, session)

            # Calculate totals after all chunks are processed
            logger.info("Calculando totales de población para archivo municipal...")
            self.calculate_poblacion_total(session)

        logger.info(f"Procesamiento chunked completo de {csv_path}")


def main():
    """Función principal del ETL."""
    import argparse

    parser = argparse.ArgumentParser(description='ETL para datos DANE de población')
    parser.add_argument('csv_path', help='Ruta al archivo CSV')
    parser.add_argument('nivel', choices=['departamental', 'municipal'], help='Nivel territorial')
    parser.add_argument('--db-url', help='URL de base de datos (opcional)')

    args = parser.parse_args()

    # Crear engine
    db_url = args.db_url or settings.DATABASE_URL
    engine = create_engine(db_url, echo=False)

    # Procesar
    processor = DANEDataProcessor(engine)
    processor.process_file(args.csv_path, args.nivel)

    logger.info("ETL completado exitosamente")


if __name__ == '__main__':
    main()
