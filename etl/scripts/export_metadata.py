#!/usr/bin/env python3
"""
Export metadata to CSV files:
1. Glossary terms (from frontend TypeScript data)
2. DANE Indicators metadata (schema documentation)

Usage:
    python export_metadata.py

Output files are saved to etl/exports/
"""

import csv
import os
import json
import re
from datetime import datetime

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_glossary():
    """
    Export glossary terms from the frontend TypeScript file to CSV.
    """
    # Path to the glossary TypeScript file
    glossary_ts_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..',
        'frontend', 'src', 'data', 'glossaryTerms.ts'
    )

    # Read the TypeScript file
    with open(glossary_ts_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the array content between GLOSSARY_TERMS: GlossaryTerm[] = [ and ];
    match = re.search(r'GLOSSARY_TERMS:\s*GlossaryTerm\[\]\s*=\s*\[(.*?)\];', content, re.DOTALL)
    if not match:
        print("Could not find GLOSSARY_TERMS array in file")
        return

    array_content = match.group(1)

    # Parse each term object manually
    terms = []

    # Split by '  {' to get individual objects (each term starts with indented brace)
    term_blocks = re.split(r'\n  \{', array_content)

    for block in term_blocks[1:]:  # Skip first empty split
        block = '{' + block  # Re-add the opening brace

        # Extract fields using regex
        term_data = {}

        # id
        id_match = re.search(r"id:\s*'([^']+)'", block)
        if id_match:
            term_data['id'] = id_match.group(1)

        # term
        term_match = re.search(r"term:\s*'([^']+)'", block)
        if term_match:
            term_data['term'] = term_match.group(1)

        # definition
        def_match = re.search(r"definition:\s*'([^']+)'", block)
        if def_match:
            term_data['definition'] = def_match.group(1)

        # category
        cat_match = re.search(r"category:\s*'([^']+)'", block)
        if cat_match:
            term_data['category'] = cat_match.group(1)

        # examples (array)
        examples_match = re.search(r"examples:\s*\[(.*?)\]", block, re.DOTALL)
        if examples_match:
            examples_content = examples_match.group(1)
            examples = re.findall(r"'([^']+)'", examples_content)
            term_data['examples'] = ' | '.join(examples)
        else:
            term_data['examples'] = ''

        # relatedTerms (array)
        related_match = re.search(r"relatedTerms:\s*\[(.*?)\]", block, re.DOTALL)
        if related_match:
            related_content = related_match.group(1)
            related = re.findall(r"'([^']+)'", related_content)
            term_data['related_terms'] = ', '.join(related)
        else:
            term_data['related_terms'] = ''

        if term_data.get('id'):
            terms.append(term_data)

    # Write to CSV
    output_path = os.path.join(OUTPUT_DIR, 'glosario_demografico.csv')

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'term', 'category', 'definition', 'examples', 'related_terms'])
        writer.writeheader()
        writer.writerows(terms)

    print(f"Glossary exported: {output_path}")
    print(f"  Total terms: {len(terms)}")

    # Also export category counts
    categories = {}
    for term in terms:
        cat = term.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print(f"  By category: {categories}")

    return terms


def export_indicators_metadata():
    """
    Export DANE indicators metadata (schema documentation) to CSV.
    This describes what indicators are available and their structure.
    """

    # Define indicator metadata based on the models
    indicators_metadata = [
        # Fertility Indicators
        {
            'table_name': 'dane_fertility_indicators',
            'indicator_category': 'Fecundidad',
            'indicator_name': 'TGF (Tasa Global de Fecundidad)',
            'indicator_code': 'tgf',
            'description': 'Número promedio de hijos que tendría una mujer durante su vida reproductiva (15-49 años)',
            'unit': 'Hijos por mujer',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-Fec-EstNal-Reg-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'TGF = 2.1 es el nivel de reemplazo poblacional'
        },
        {
            'table_name': 'dane_fertility_indicators',
            'indicator_category': 'Fecundidad',
            'indicator_name': 'Tasas de Fecundidad por Edad',
            'indicator_code': 'age_rates',
            'description': 'Tasas específicas de fecundidad por cada año de edad (10-49 años)',
            'unit': 'Tasa (nacimientos/mujeres)',
            'data_type': 'JSON (dict edad->tasa)',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-Fec-EstNal-Reg-2018-2070_VP.xlsx',
            'age_disaggregation': 'Sí (edades 10-49)',
            'sex_disaggregation': 'No (solo mujeres)',
            'notes': 'Incluye edades individuales de 10 a 49 años'
        },

        # Migration Indicators
        {
            'table_name': 'dane_migration_indicators',
            'indicator_category': 'Migración',
            'indicator_name': 'Saldo Neto Migratorio Internacional',
            'indicator_code': 'age_values (Internacional)',
            'description': 'Balance entre inmigración y emigración internacional por edad',
            'unit': 'Personas',
            'data_type': 'JSON (dict edad->valor)',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-Mig-EstSexNal-Reg-2018-2070_VP.xlsx',
            'age_disaggregation': 'Sí (edades 0-100)',
            'sex_disaggregation': 'Sí (Hombres/Mujeres)',
            'notes': 'Valores positivos = más inmigración, negativos = más emigración'
        },
        {
            'table_name': 'dane_migration_indicators',
            'indicator_category': 'Migración',
            'indicator_name': 'Saldo Neto Migratorio Interno',
            'indicator_code': 'age_values (Interna)',
            'description': 'Balance de migración interna (entre regiones) por edad',
            'unit': 'Personas',
            'data_type': 'JSON (dict edad->valor)',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-Mig-EstSexNal-Reg-2018-2070_VP.xlsx',
            'age_disaggregation': 'Sí (edades 0-100)',
            'sex_disaggregation': 'Sí (Hombres/Mujeres)',
            'notes': 'Migración dentro del país entre regiones'
        },

        # Mortality Indicators
        {
            'table_name': 'dane_mortality_indicators',
            'indicator_category': 'Mortalidad',
            'indicator_name': 'Probabilidad de Muerte por Edad (qx)',
            'indicator_code': 'age_mortality_rates',
            'description': 'Probabilidad de morir entre la edad x y x+1 años',
            'unit': 'Probabilidad (0-1)',
            'data_type': 'JSON (dict edad->tasa)',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-Mor-EstSexNal-Reg-2018-2070_VP.xlsx',
            'age_disaggregation': 'Sí (edades 0-100)',
            'sex_disaggregation': 'Sí (Hombres/Mujeres)',
            'notes': 'Base para tablas de vida y cálculo de esperanza de vida'
        },

        # Principal Indicators
        {
            'table_name': 'dane_principal_indicators',
            'indicator_category': 'Indicadores Principales',
            'indicator_name': 'Esperanza de Vida al Nacer - Hombres',
            'indicator_code': 'life_exp_male',
            'description': 'Años promedio de vida esperados al nacer para hombres',
            'unit': 'Años',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-camDemNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'Sí (solo hombres)',
            'notes': 'Indicador clave de desarrollo humano'
        },
        {
            'table_name': 'dane_principal_indicators',
            'indicator_category': 'Indicadores Principales',
            'indicator_name': 'Esperanza de Vida al Nacer - Mujeres',
            'indicator_code': 'life_exp_female',
            'description': 'Años promedio de vida esperados al nacer para mujeres',
            'unit': 'Años',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-camDemNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'Sí (solo mujeres)',
            'notes': 'Generalmente mayor que la de hombres'
        },
        {
            'table_name': 'dane_principal_indicators',
            'indicator_category': 'Indicadores Principales',
            'indicator_name': 'Esperanza de Vida al Nacer - Total',
            'indicator_code': 'life_exp_total',
            'description': 'Años promedio de vida esperados al nacer para la población total',
            'unit': 'Años',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-camDemNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No (ambos sexos)',
            'notes': 'Promedio ponderado de ambos sexos'
        },
        {
            'table_name': 'dane_principal_indicators',
            'indicator_category': 'Indicadores Principales',
            'indicator_name': 'Tasa de Mortalidad Infantil',
            'indicator_code': 'infant_mortality_rate',
            'description': 'Defunciones de menores de 1 año por cada 1,000 nacidos vivos',
            'unit': 'Por 1,000 nacidos vivos',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-camDemNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'Indicador clave de salud pública'
        },

        # Growth Indicators
        {
            'table_name': 'dane_growth_indicators',
            'indicator_category': 'Crecimiento Poblacional',
            'indicator_name': 'Población Total',
            'indicator_code': 'total_population',
            'description': 'Población total proyectada para el año',
            'unit': 'Personas',
            'data_type': 'Integer',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-crecPobNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'Proyección basada en Censo 2018'
        },
        {
            'table_name': 'dane_growth_indicators',
            'indicator_category': 'Crecimiento Poblacional',
            'indicator_name': 'Tasa de Crecimiento Poblacional',
            'indicator_code': 'growth_rate',
            'description': 'Variación porcentual de la población respecto al año anterior',
            'unit': 'Porcentaje (%)',
            'data_type': 'Decimal',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-crecPobNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'Incluye componentes vegetativo y migratorio'
        },
        {
            'table_name': 'dane_growth_indicators',
            'indicator_category': 'Crecimiento Poblacional',
            'indicator_name': 'Crecimiento Natural',
            'indicator_code': 'natural_increase',
            'description': 'Diferencia entre nacimientos y defunciones',
            'unit': 'Personas',
            'data_type': 'Integer',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-crecPobNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'Componente vegetativo del crecimiento'
        },
        {
            'table_name': 'dane_growth_indicators',
            'indicator_category': 'Crecimiento Poblacional',
            'indicator_name': 'Saldo Migratorio Neto',
            'indicator_code': 'net_migration',
            'description': 'Diferencia entre inmigrantes y emigrantes',
            'unit': 'Personas',
            'data_type': 'Integer',
            'temporal_coverage': '2018-2070',
            'geographic_level': 'Región DANE (23 regiones)',
            'source': 'DANE - DCD-PrinInd-crecPobNac-2018-2070_VP.xlsx',
            'age_disaggregation': 'No',
            'sex_disaggregation': 'No',
            'notes': 'Componente migratorio del crecimiento'
        },
    ]

    # Write to CSV
    output_path = os.path.join(OUTPUT_DIR, 'indicadores_dane_metadata.csv')

    fieldnames = [
        'table_name', 'indicator_category', 'indicator_name', 'indicator_code',
        'description', 'unit', 'data_type', 'temporal_coverage', 'geographic_level',
        'source', 'age_disaggregation', 'sex_disaggregation', 'notes'
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(indicators_metadata)

    print(f"\nIndicators metadata exported: {output_path}")
    print(f"  Total indicators: {len(indicators_metadata)}")

    # Category counts
    categories = {}
    for ind in indicators_metadata:
        cat = ind['indicator_category']
        categories[cat] = categories.get(cat, 0) + 1

    print(f"  By category: {categories}")

    return indicators_metadata


def export_dane_regions():
    """
    Export DANE regions reference data to CSV.
    """
    # Based on the documentation, these are the 23 DANE regions
    regions = [
        {'region_code': 'NAL', 'region_name': 'Total Nacional'},
        {'region_code': 'VDA', 'region_name': 'Valle de Aburrá'},
        {'region_code': 'ACB', 'region_name': 'Altiplano Cundiboyacense'},
        {'region_code': 'AQU', 'region_name': 'Antioquia y Urabá'},
        {'region_code': 'BOG', 'region_name': 'Bogotá D.C.'},
        {'region_code': 'CAL', 'region_name': 'Área Metropolitana de Cali'},
        {'region_code': 'BAR', 'region_name': 'Área Metropolitana de Barranquilla'},
        {'region_code': 'CAR', 'region_name': 'Caribe'},
        {'region_code': 'CEN', 'region_name': 'Centro'},
        {'region_code': 'ECA', 'region_name': 'Eje Cafetero'},
        {'region_code': 'LLA', 'region_name': 'Llanos Orientales'},
        {'region_code': 'NAR', 'region_name': 'Nariño'},
        {'region_code': 'ORI', 'region_name': 'Orinoquía'},
        {'region_code': 'PAC', 'region_name': 'Pacífico'},
        {'region_code': 'SAN', 'region_name': 'Santanderes'},
        {'region_code': 'SUR', 'region_name': 'Sur'},
        {'region_code': 'TOL', 'region_name': 'Tolima Grande'},
        {'region_code': 'VAL', 'region_name': 'Valle del Cauca'},
        {'region_code': 'AMA', 'region_name': 'Amazonía'},
        {'region_code': 'CHO', 'region_name': 'Chocó'},
        {'region_code': 'GUA', 'region_name': 'Guajira'},
        {'region_code': 'SAI', 'region_name': 'San Andrés y Providencia'},
        {'region_code': 'CES', 'region_name': 'Cesar'},
    ]

    output_path = os.path.join(OUTPUT_DIR, 'regiones_dane.csv')

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['region_code', 'region_name'])
        writer.writeheader()
        writer.writerows(regions)

    print(f"\nDANE regions exported: {output_path}")
    print(f"  Total regions: {len(regions)}")

    return regions


def main():
    """Main function to export all metadata."""
    print("=" * 60)
    print("METADATA EXPORT SCRIPT")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Export glossary
    print("\n1. Exporting Glossary Terms...")
    export_glossary()

    # Export indicators metadata
    print("\n2. Exporting DANE Indicators Metadata...")
    export_indicators_metadata()

    # Export DANE regions
    print("\n3. Exporting DANE Regions...")
    export_dane_regions()

    print("\n" + "=" * 60)
    print(f"All exports completed! Files saved to: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)


if __name__ == '__main__':
    main()
