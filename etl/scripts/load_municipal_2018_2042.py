"""
Script para cargar SOLO datos municipales 2018-2042 (no duplicar 1985-2017).
"""
import sys
from pathlib import Path
import pandas as pd
import logging

# Agregar backend al path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.append(str(backend_path))

from sqlmodel import create_engine
from app.core.config import settings
from etl_dane import DANEDataProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Carga SOLO datos municipales 2018-2042."""
    logger.info("\n" + "="*80)
    logger.info("CARGANDO DATOS MUNICIPALES 2018-2042")
    logger.info("="*80 + "\n")

    # Directorios
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data"
    csv_dir = script_dir.parent / "csv_temp"
    csv_dir.mkdir(exist_ok=True)

    # Archivo específico 2018-2042
    excel_path = data_dir / "Municipal" / "PPED-AreaSexoEdadMun-2018-2042_VP.xlsx"

    if not excel_path.exists():
        logger.error(f"Archivo no encontrado: {excel_path}")
        sys.exit(1)

    logger.info(f"Archivo a procesar: {excel_path.name}")
    logger.info(f"Tamaño: {excel_path.stat().st_size / 1024 / 1024:.2f} MB\n")

    # Crear engine y procesador
    logger.info(f"Conectando a base de datos: {settings.POSTGRES_SERVER}...")
    engine = create_engine(settings.DATABASE_URL, echo=False)
    processor = DANEDataProcessor(engine)
    logger.info("Conexión establecida\n")

    # Ruta del CSV temporal
    csv_path = csv_dir / f"{excel_path.stem}.csv"

    try:
        # Leer Excel con formato PPED (multi-header)
        logger.info("Leyendo archivo Excel...")
        excel_file = pd.ExcelFile(excel_path)
        logger.info(f"Hojas encontradas: {excel_file.sheet_names}")

        # Archivos PPED: hoja índice 2, multi-header en rows 7-8
        sheet_name = 2
        logger.info(f"Usando hoja índice {sheet_name}, multi-header rows 7-8")

        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=[7, 8], dtype=str)

        # Aplanar columnas multi-nivel
        new_cols = []
        for cols in df.columns:
            valid_parts = [str(c).strip() for c in cols
                          if not str(c).startswith('Unnamed') and str(c) != 'nan']

            if len(valid_parts) == 0:
                new_cols.append('')
            elif len(valid_parts) == 1:
                new_cols.append(valid_parts[0])
            else:
                if valid_parts[1].lower().startswith(valid_parts[0].lower()):
                    new_cols.append(valid_parts[1])
                else:
                    new_cols.append(' '.join(valid_parts))

        df.columns = [col.strip() for col in new_cols]

        logger.info(f"Filas: {len(df):,}, Columnas: {len(df.columns)}")

        # Guardar CSV temporal
        logger.info(f"Guardando CSV temporal en {csv_path}...")
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info("CSV guardado exitosamente")

        # Procesar con ETL chunked (para archivos grandes)
        chunk_size = 1000
        logger.info(f"Iniciando proceso ETL chunked (chunks de {chunk_size} filas)...")
        processor.process_municipal_chunked(str(csv_path), chunk_size=chunk_size)
        logger.info(f"✓ Archivo procesado exitosamente\n")

        # Limpiar CSV temporal
        csv_path.unlink()
        logger.info("CSV temporal eliminado")

        logger.info("\n" + "="*80)
        logger.info("✓ DATOS MUNICIPALES 2018-2042 CARGADOS EXITOSAMENTE")
        logger.info("="*80 + "\n")

    except Exception as e:
        logger.error(f"✗ Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Limpiar directorio temporal
        if csv_dir.exists() and not list(csv_dir.glob("*")):
            csv_dir.rmdir()


if __name__ == '__main__':
    main()
