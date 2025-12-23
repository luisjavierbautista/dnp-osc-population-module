"""
Convierte archivos Excel de DANE a formato CSV.
"""
import sys
from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_excel_to_csv(excel_path: str, csv_path: str, sheet_name: str = 0):
    """
    Convierte un archivo Excel a CSV.

    Args:
        excel_path: Ruta al archivo Excel
        csv_path: Ruta de salida para el CSV
        sheet_name: Nombre o índice de la hoja a convertir
    """
    logger.info(f"Convirtiendo {excel_path} a CSV...")

    try:
        # Leer Excel (headers start at row 11 in DANE files)
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=11, dtype=str)
        logger.info(f"Filas leídas: {len(df)}, Columnas: {len(df.columns)}")

        # Guardar como CSV
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"CSV guardado en: {csv_path}")

        return True
    except Exception as e:
        logger.error(f"Error al convertir {excel_path}: {e}")
        return False


def main():
    """Convierte todos los archivos Excel a CSV."""
    import argparse

    parser = argparse.ArgumentParser(description='Convertir Excel de DANE a CSV')
    parser.add_argument('excel_path', help='Ruta al archivo Excel')
    parser.add_argument('csv_path', help='Ruta de salida para CSV')
    parser.add_argument('--sheet', default=0, help='Nombre o índice de hoja (default: 0)')

    args = parser.parse_args()

    success = convert_excel_to_csv(args.excel_path, args.csv_path, args.sheet)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
