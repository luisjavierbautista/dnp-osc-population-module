"""
Script para cargar datos DEPARTAMENTALES de DANE.
IMPORTANTE: Los datos municipales deben cargarse con load_municipal_data.py (usa estrategia de chunks).
"""
import sys
from pathlib import Path
import pandas as pd
import logging
from typing import List, Tuple

# Agregar backend al path
# When running in Docker, backend is at /app
# When running locally, backend is at ../../../backend
backend_path = Path("/app") if Path("/app/app").exists() else Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

from sqlmodel import create_engine
from app.core.config import settings
from etl_dane import DANEDataProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_excel_files(data_dir: Path) -> List[Tuple[Path, str]]:
    """
    Obtiene archivos Excel DEPARTAMENTALES a procesar.

    NOTA: Los archivos municipales NO se procesan aquí.
    Usar load_municipal_data.py para datos municipales (carga por chunks).

    Returns:
        Lista de tuplas (ruta_archivo, nivel_territorial)
    """
    files = []

    # Archivos departamentales
    dept_dir = data_dir / "Departamental"
    if dept_dir.exists():
        for excel_file in sorted(dept_dir.glob("*.xlsx")):
            files.append((excel_file, "departamental"))
            logger.info(f"Encontrado departamental: {excel_file.name}")

    # IMPORTANTE: No procesamos archivos municipales aquí
    # Los municipales deben cargarse con load_municipal_data.py (estrategia de chunks)
    mun_dir = data_dir / "Municipal"
    if mun_dir.exists():
        mun_count = len(list(mun_dir.glob("*.xlsx")))
        if mun_count > 0:
            logger.info(f"\n{'='*80}")
            logger.info(f"NOTA: {mun_count} archivos municipales detectados pero NO serán procesados aquí")
            logger.info("Para cargar datos municipales, usar: load_municipal_data.py")
            logger.info(f"{'='*80}\n")

    return files


def convert_and_process_file(excel_path: Path, nivel: str, processor: DANEDataProcessor, csv_dir: Path):
    """
    Convierte un Excel a CSV y lo procesa.

    Args:
        excel_path: Ruta al archivo Excel
        nivel: Nivel territorial
        processor: Procesador de datos DANE
        csv_dir: Directorio para CSVs temporales
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"Procesando: {excel_path.name}")
    logger.info(f"Nivel: {nivel}")
    logger.info(f"Tamaño: {excel_path.stat().st_size / 1024 / 1024:.2f} MB")
    logger.info(f"{'='*80}\n")

    # Ruta del CSV temporal
    csv_path = csv_dir / f"{excel_path.stem}.csv"

    try:
        # Detectar formato del archivo
        excel_file = pd.ExcelFile(excel_path)
        logger.info(f"Hojas encontradas: {excel_file.sheet_names}")

        # Los archivos nuevos (2018+) tienen múltiples hojas y estructura diferente
        if len(excel_file.sheet_names) > 1:
            # Archivos PPED (2018+): usar hoja de datos (índice 2) y header en rows 7-8
            # Rows 7 y 8 forman multi-header, necesitamos aplanarlos
            sheet_name = 2  # PobDepartamentalxÁreaSexoEdad o PobMunicipalxÁreaSexoEdad
            logger.info(f"Formato PPED detectado - usando hoja índice {sheet_name}, multi-header rows 7-8")

            # Leer con multi-header
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=[7, 8], dtype=str)

            # Aplanar columnas multi-nivel de forma inteligente
            new_cols = []
            for cols in df.columns:
                # Filtrar valores válidos (sin Unnamed ni nan)
                valid_parts = [str(c).strip() for c in cols
                              if not str(c).startswith('Unnamed') and str(c) != 'nan']

                if len(valid_parts) == 0:
                    new_cols.append('')
                elif len(valid_parts) == 1:
                    new_cols.append(valid_parts[0])
                else:
                    # Si el segundo nivel ya contiene el primero (case-insensitive), usar solo el segundo
                    # Ej: ('HOMBRES', 'Hombres 0 años') -> 'Hombres 0 años'
                    if valid_parts[1].lower().startswith(valid_parts[0].lower()):
                        new_cols.append(valid_parts[1])
                    else:
                        new_cols.append(' '.join(valid_parts))

            df.columns = [col.strip() for col in new_cols]

        else:
            # Archivos DCD (antiguos): usar hoja 0 y header en row 11
            sheet_name = 0
            header_row = 11
            logger.info(f"Formato DCD detectado - usando hoja {sheet_name}, header row {header_row}")
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row, dtype=str)

        logger.info(f"Filas: {len(df):,}, Columnas: {len(df.columns)}")

        logger.info(f"Guardando CSV temporal en {csv_path}...")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info("CSV guardado exitosamente")

        # Procesar con el ETL
        logger.info("Iniciando proceso ETL...")
        processor.process_file(str(csv_path), nivel)
        logger.info(f"✓ Archivo procesado exitosamente: {excel_path.name}\n")

        # Limpiar CSV temporal
        csv_path.unlink()
        logger.info("CSV temporal eliminado")

        return True

    except Exception as e:
        logger.error(f"✗ Error procesando {excel_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Carga datos DEPARTAMENTALES."""
    logger.info("\n" + "="*80)
    logger.info("CARGANDO DATOS DEPARTAMENTALES DE POBLACIÓN DANE")
    logger.info("NOTA: Datos municipales se cargan con load_municipal_data.py")
    logger.info("="*80 + "\n")

    # Directorios
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_dir = script_dir.parent / "csv_temp"
    csv_dir.mkdir(exist_ok=True)

    # Verificar directorio de datos
    if not data_dir.exists():
        logger.error(f"Directorio de datos no encontrado: {data_dir}")
        sys.exit(1)

    # Obtener archivos
    files = get_excel_files(data_dir)
    logger.info(f"Total de archivos a procesar: {len(files)}\n")

    if not files:
        logger.error("No se encontraron archivos Excel para procesar")
        sys.exit(1)

    # Crear engine y procesador
    logger.info(f"Conectando a base de datos: {settings.POSTGRES_SERVER}...")
    engine = create_engine(settings.DATABASE_URL, echo=False)
    processor = DANEDataProcessor(engine)
    logger.info("Conexión establecida\n")

    # Procesar cada archivo
    processed = 0
    failed = 0

    for i, (excel_path, nivel) in enumerate(files, 1):
        logger.info(f"Archivo {i}/{len(files)}")

        success = convert_and_process_file(excel_path, nivel, processor, csv_dir)

        if success:
            processed += 1
        else:
            failed += 1

    # Resumen final
    logger.info("\n" + "="*80)
    logger.info("RESUMEN DE CARGA")
    logger.info("="*80)
    logger.info(f"Total archivos: {len(files)}")
    logger.info(f"Procesados exitosamente: {processed}")
    logger.info(f"Fallidos: {failed}")
    logger.info("="*80 + "\n")

    # Limpiar directorio temporal
    if csv_dir.exists():
        csv_dir.rmdir()

    if failed > 0:
        logger.error("Algunos archivos fallaron durante la carga")
        sys.exit(1)
    else:
        logger.info("✓ DATOS DEPARTAMENTALES CARGADOS EXITOSAMENTE")
        logger.info("\nPara cargar datos municipales, ejecutar:")
        logger.info("  python /etl/scripts/load_municipal_data.py")


if __name__ == '__main__':
    main()
