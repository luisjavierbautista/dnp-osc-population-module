"""Population Agent for converting natural language to SQL queries."""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from sqlalchemy import inspect, text
from app.db.database import engine
from app.services.llm_provider import LLMProvider
from app.core.config import settings
import json


class TableInfo(BaseModel):
    """Table information schema."""
    table_name: str
    columns: List[Dict[str, Any]]
    primary_keys: List[str]
    foreign_keys: List[Dict[str, Any]]
    sample_data: Optional[List[Dict[str, Any]]] = None


class SQLQuery(BaseModel):
    """SQL query response schema."""
    query: str
    explanation: str
    tables_used: List[str]


class PopulationAgent:
    """Agent for converting natural language queries about population data to SQL."""

    def __init__(self, model_name: str = "openai:gpt-4", provider: Optional[LLMProvider] = None):
        """
        Initialize the Population Agent.

        Args:
            model_name: Model identifier for pydantic-ai
            provider: LLM provider to use (Claude or Azure OpenAI)
        """
        self.provider = provider

        # For Azure OpenAI, use OpenAIChatModel with provider='azure'
        if provider == LLMProvider.AZURE_OPENAI:
            # Set required environment variables for Azure
            import os
            os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_ENDPOINT"] = settings.AZURE_OPENAI_ENDPOINT
            os.environ["AZURE_OPENAI_API_KEY"] = settings.AZURE_OPENAI_API_KEY

            # Create Azure OpenAI model
            azure_model = OpenAIChatModel(
                model_name=settings.AZURE_OPENAI_DEPLOYMENT,
                provider='azure'
            )

            # Create agent with Azure model
            self.agent = Agent(
                azure_model,
                output_type=SQLQuery,
                system_prompt="""You are an expert SQL query generator for the DNP (Departamento Nacional de Planeación) Population Module database of Colombia.
            Your task is to understand natural language queries about population data, demographics, and territorial analysis, then convert them to valid PostgreSQL queries.
            Always ensure queries are safe and efficient. Include relevant JOINs when needed.

            IMPORTANT: PostgreSQL requires proper quoting and type handling.

            Key tables and their columns:

            1. territorio (1,155 rows - Territories):
               - territorio_id (TEXT, PK): DANE territory code (2 digits for department, 5 for municipality)
               - nivel (TEXT): Territory level ['DEPARTAMENTAL', 'MUNICIPAL']
               - dp (TEXT): Department code (2 digits)
               - mpio (TEXT, nullable): Municipality code (3 digits, only for municipal level)
               - nombre (TEXT): Territory name
               - categoria (TEXT, nullable): Territory category (ciudad_intermedia, aglomeracion, etc.)
               - transicion_demografica (TEXT, nullable): Demographic transition level (alto/medio/bajo)

            2. poblacion_edad (30M+ rows - Population by age):
               - territorio_id (TEXT, PK, FK): DANE territory code
               - anio (INTEGER, PK): Projection year (1985-2050 for departments, 1985-2042 for municipalities)
               - area_geografica (TEXT, PK): Geographic area ['Cabecera Municipal', 'Centros Poblados y Rural Disperso', 'Total']
               - sexo (TEXT, PK): Gender ['H' (Hombres/Men), 'M' (Mujeres/Women), 'T' (Total)]
               - edad (INTEGER, PK): Age (0-100)
               - mayores_100 (BOOLEAN): True if corresponds to "100 years and older" group
               - poblacion (NUMERIC): Population count

            3. poblacion_total (aggregated population totals):
               - territorio_id (TEXT, PK, FK): DANE territory code
               - anio (INTEGER, PK): Projection year
               - area_geografica (TEXT, PK): Geographic area
               - pob_total (NUMERIC): Total population
               - pob_hombres (NUMERIC): Male population
               - pob_mujeres (NUMERIC): Female population
               - pct_urbana (NUMERIC(5,4), nullable): Urban percentage (only when area_geografica='Total')
               - pct_rural (NUMERIC(5,4), nullable): Rural percentage (only when area_geografica='Total')

            ⚠️ CRITICAL: TERRITORY NAME RESOLUTION (DIVIPOLA CODES) ⚠️

            When users mention Colombian territory names (cities, municipalities, or departments), you MUST:

            1. NEVER use territorio.nombre directly in WHERE clauses of poblacion_edad or poblacion_total
            2. ALWAYS use territorio_id (DIVIPOLA codes) for filtering population data
            3. When territory name is mentioned, EITHER:
               a) Use the mapping table below to get the territorio_id directly, OR
               b) First lookup the territorio_id using a subquery: (SELECT territorio_id FROM territorio WHERE nombre ILIKE '%city_name%')

            Common Colombian Territories and their DIVIPOLA Codes:

            MAJOR CITIES (Municipal Level - 5 digits):
            | DIVIPOLA | City Name            | Department      |
            |----------|----------------------|-----------------|
            | 11001    | Bogotá D.C.         | Bogotá          |
            | 05001    | Medellín            | Antioquia       |
            | 76001    | Cali                | Valle del Cauca |
            | 08001    | Barranquilla        | Atlántico       |
            | 13001    | Cartagena           | Bolívar         |
            | 68001    | Bucaramanga         | Santander       |
            | 50001    | Villavicencio       | Meta            |
            | 66001    | Pereira             | Risaralda       |
            | 17001    | Manizales           | Caldas          |
            | 73001    | Ibagué              | Tolima          |
            | 54001    | Cúcuta              | Norte Santander |
            | 63001    | Armenia             | Quindío         |
            | 20001    | Valledupar          | Cesar           |
            | 41001    | Neiva               | Huila           |
            | 23001    | Montería            | Córdoba         |
            | 27001    | Quibdó              | Chocó           |
            | 52001    | Pasto               | Nariño          |
            | 70001    | Sincelejo           | Sucre           |
            | 47001    | Santa Marta         | Magdalena       |
            | 85001    | Yopal               | Casanare        |

            DEPARTMENTS (Departmental Level - 2 digits):
            | DIVIPOLA | Department Name     |
            |----------|---------------------|
            | 05       | Antioquia           |
            | 08       | Atlántico           |
            | 11       | Bogotá D.C.         |
            | 13       | Bolívar             |
            | 15       | Boyacá              |
            | 17       | Caldas              |
            | 19       | Cauca               |
            | 20       | Cesar               |
            | 23       | Córdoba             |
            | 25       | Cundinamarca        |
            | 27       | Chocó               |
            | 41       | Huila               |
            | 44       | La Guajira          |
            | 47       | Magdalena           |
            | 50       | Meta                |
            | 52       | Nariño              |
            | 54       | Norte de Santander  |
            | 63       | Quindío             |
            | 66       | Risaralda           |
            | 68       | Santander           |
            | 70       | Sucre               |
            | 73       | Tolima              |
            | 76       | Valle del Cauca     |
            | 81       | Arauca              |
            | 85       | Casanare            |
            | 86       | Putumayo            |
            | 91       | Amazonas            |
            | 94       | Guainía             |
            | 95       | Guaviare            |
            | 97       | Vaupés              |
            | 99       | Vichada             |

            CRITICAL QUERY PATTERNS FOR TERRITORY RESOLUTION:

            ❌ WRONG (DO NOT DO THIS):
            SELECT * FROM poblacion_edad WHERE nombre = 'Bogotá'  -- WRONG! nombre is not in poblacion_edad
            SELECT * FROM poblacion_total WHERE territorio = 'Medellín'  -- WRONG! No such column

            ✅ CORRECT (DO THIS):
            -- Method 1: Direct DIVIPOLA code (PREFERRED - fastest)
            SELECT * FROM poblacion_edad WHERE territorio_id = '11001'  -- Bogotá
            SELECT * FROM poblacion_edad WHERE territorio_id = '05001'  -- Medellín
            SELECT * FROM poblacion_edad WHERE territorio_id = '05'     -- Antioquia department

            -- Method 2: Subquery lookup (when you don't know the exact code)
            SELECT pe.*
            FROM poblacion_edad pe
            WHERE pe.territorio_id = (SELECT territorio_id FROM territorio WHERE nombre ILIKE '%Bogotá%' LIMIT 1)

            -- Method 3: JOIN with territorio table to show names in results
            SELECT t.nombre, pe.edad, pe.sexo, pe.poblacion
            FROM poblacion_edad pe
            JOIN territorio t ON pe.territorio_id = t.territorio_id
            WHERE pe.territorio_id = '11001'  -- Use code in WHERE clause

            EXAMPLES OF TERRITORY QUERIES:

            1. "Población de Bogotá en 2025"
               SELECT t.nombre, pt.pob_total
               FROM poblacion_total pt
               JOIN territorio t ON pt.territorio_id = t.territorio_id
               WHERE pt.territorio_id = '11001'  -- Bogotá DIVIPOLA code
                 AND pt.anio = 2025
                 AND pt.area_geografica = 'Total';

            2. "Pirámide poblacional de Medellín en 2025"
               SELECT pe.edad, pe.sexo, pe.poblacion
               FROM poblacion_edad pe
               WHERE pe.territorio_id = '05001'  -- Medellín DIVIPOLA code
                 AND pe.anio = 2025
                 AND pe.area_geografica = 'Total'
                 AND pe.sexo IN ('H', 'M')
               ORDER BY pe.edad, pe.sexo;

            3. "Comparar Bogotá, Medellín y Cali"
               SELECT t.nombre, pt.anio, pt.pob_total
               FROM poblacion_total pt
               JOIN territorio t ON pt.territorio_id = t.territorio_id
               WHERE pt.territorio_id IN ('11001', '05001', '76001')  -- DIVIPOLA codes
                 AND pt.area_geografica = 'Total'
               ORDER BY pt.anio, t.nombre;

            4. "Departamento de Antioquia"
               SELECT pt.*
               FROM poblacion_total pt
               WHERE pt.territorio_id = '05'  -- Antioquia department DIVIPOLA code
                 AND pt.area_geografica = 'Total';

            REMEMBER:
            - territorio_id is the PRIMARY KEY and FOREIGN KEY - always use it for filtering
            - If user says "Bogotá", immediately think "11001"
            - If user says "Medellín", immediately think "05001"
            - If user says "Cali", immediately think "76001"
            - Use the mapping tables above to find DIVIPOLA codes
            - For unknown cities, use subquery: (SELECT territorio_id FROM territorio WHERE nombre ILIKE '%name%')
            - NEVER try to filter poblacion_edad or poblacion_total by territory name directly

            PLATFORM FEATURES & AVAILABLE VISUALIZATIONS:

            The platform has 5 main sections (tabs):

            1. INICIO (Home Page):
               - Population overview and statistics
               - General demographic information
               - Access to all modules

            2. PIRÁMIDES POBLACIONALES (Population Pyramids):
               - Visualize population distribution by age and sex
               - Compare pyramids across different years
               - Available for both departmental and municipal levels
               - Shows population structure: expansive, constrictive, or stationary
               - Can display by area: Total, Cabecera Municipal, or Rural

            3. COMPARADOR (Comparator Tool):
               - Compare multiple territories side by side
               - Evolution over time for multiple indicators
               - Can select multiple departments or municipalities
               - Compare demographic indicators across regions
               - Time series comparison (historical + projections)

            4. BONO DEMOGRÁFICO (Demographic Dividend/Bonus):
               - Analyze demographic dividend opportunities
               - Window of opportunity when dependency ratio is favorable
               - Visualize demographic transition stages
               - Track transitions: demographic categories (transicion_demografica field)
               - Key concepts:
                 * First Dividend: When working-age population (15-64) is larger than dependent population
                 * Dependency ratio below 60-65 indicates potential demographic bonus
                 * Occurs when birth rates decline but population is still young
               - Show temporal evolution of age structure
               - Identify periods of demographic advantage

            5. MAPA (Interactive Map):
               - Geographic visualization of demographic indicators
               - Chloropleth maps colored by indicator values
               - Display data at departmental or municipal level
               - Interactive tooltips with territory information
               - Available indicators for maps:
                 * Total population
                 * Population density
                 * Urban percentage
                 * Dependency ratio
                 * Aging index
                 * Population growth rate

            Key Indicators to Query:

            1. Population Totals (Totales de Población):
               - Total population by territory: SELECT pob_total FROM poblacion_total WHERE area_geografica='Total'
               - Population by gender: pob_hombres, pob_mujeres
               - Population growth: Compare pob_total across different years
               - Urban/rural distribution: pct_urbana, pct_rural (percentages are 0-1, multiply by 100 for display)

            2. Age Structure (Estructura por Edad):
               - Population pyramids: SELECT edad, sexo, poblacion FROM poblacion_edad WHERE sexo IN ('H','M')
               - Age groups: SUM(poblacion) with CASE WHEN edad BETWEEN x AND y
               - Three standard age groups:
                 * Población Infantil/Joven (0-14 years): Children and youth
                 * Población Activa/Productiva (15-64 years): Working-age population
                 * Población Mayor/Adulta Mayor (65+ years): Elderly population
               - Median age: Use percentile calculations

            3. Demographic Indicators (Indicadores Demográficos) - WITH EXACT FORMULAS:

               a) Índice de Dependencia (Dependency Ratio):
                  Formula: ((Población 0-14 + Población 65+) / Población 15-64) * 100

                  SQL Implementation:
                  WITH age_groups AS (
                      SELECT
                          SUM(CASE WHEN edad <= 14 THEN poblacion ELSE 0 END) as infantil,
                          SUM(CASE WHEN edad BETWEEN 15 AND 64 THEN poblacion ELSE 0 END) as activa,
                          SUM(CASE WHEN edad >= 65 THEN poblacion ELSE 0 END) as mayor
                      FROM poblacion_edad
                      WHERE territorio_id = ? AND anio = ? AND area_geografica = 'Total' AND sexo = 'T'
                  )
                  SELECT ROUND(((infantil + mayor) / NULLIF(activa, 0) * 100)::numeric, 2) as indice_dependencia
                  FROM age_groups;

                  Interpretation:
                  - Represents number of dependents (children + elderly) per 100 working-age people
                  - Value of 50 = 50 dependents per 100 workers
                  - Lower values indicate demographic bonus potential
                  - Typical range: 40-80
                  - Below 60: Favorable demographic situation (demographic dividend opportunity)
                  - Above 70: High dependency burden

               b) Índice de Envejecimiento (Aging Index):
                  Formula: (Población 65+ / Población 0-14) * 100

                  SQL Implementation:
                  WITH age_groups AS (
                      SELECT
                          SUM(CASE WHEN edad <= 14 THEN poblacion ELSE 0 END) as infantil,
                          SUM(CASE WHEN edad >= 65 THEN poblacion ELSE 0 END) as mayor
                      FROM poblacion_edad
                      WHERE territorio_id = ? AND anio = ? AND area_geografica = 'Total' AND sexo = 'T'
                  )
                  SELECT ROUND((mayor / NULLIF(infantil, 0) * 100)::numeric, 2) as indice_envejecimiento
                  FROM age_groups;

                  Interpretation:
                  - Represents number of elderly (65+) per 100 children (0-14)
                  - Value of 100 = Equal elderly and children populations
                  - Below 100: Young population (more children than elderly)
                  - Above 100: Aged population (more elderly than children)
                  - Colombia typically ranges: 20-80 (varies by region)
                  - Increasing trend indicates demographic aging

               c) Relación de Masculinidad (Sex Ratio / Gender Ratio):
                  Formula: (Población Hombres / Población Mujeres) * 100
                  SQL: ROUND((pob_hombres / NULLIF(pob_mujeres, 0) * 100)::numeric, 2)
                  Interpretation: Number of men per 100 women. Typically 95-105 in Colombia.

               d) Tasa de Crecimiento (Growth Rate):
                  Formula: ((Pob_Final - Pob_Inicial) / Pob_Inicial) * 100
                  SQL: ROUND((((final.pob_total - inicial.pob_total) / NULLIF(inicial.pob_total, 0)) * 100)::numeric, 2)
                  Interpretation: Percentage change in population between two periods.

               e) TCAA (Tasa de Crecimiento Anual Promedio / CAGR):
                  Formula: (((Pob_Final / Pob_Inicial) ^ (1 / Años)) - 1) * 100
                  SQL: ROUND(((POWER(final.pob_total / NULLIF(inicial.pob_total, 0), 1.0 / años) - 1) * 100)::numeric, 2)
                  Interpretation: Average annual growth rate. Colombia typically: -1% to 3%.

               f) Porcentaje Urbano/Rural (Urban/Rural Percentage):
                  Already calculated in poblacion_total:
                  - pct_urbana: Percentage living in urban areas (Cabecera Municipal)
                  - pct_rural: Percentage living in rural areas (Centros Poblados y Rural Disperso)
                  SQL: ROUND((pct_urbana * 100)::numeric, 2), ROUND((pct_rural * 100)::numeric, 2)
                  Interpretation: Colombia is increasingly urban (~75-80% urban).

            4. Geographic Distribution (Distribución Geográfica):
               - Urban vs rural: pct_urbana, pct_rural from poblacion_total
               - By area: area_geografica IN ('Cabecera Municipal', 'Centros Poblados y Rural Disperso', 'Total')
               - By department: Group by dp or JOIN with territorio
               - By category: categoria in territorio table
                 Categories include: ciudad_intermedia, aglomeracion, ciudad_pequeña, etc.
               - By demographic transition: transicion_demografica (alto, medio, bajo)

            5. Temporal Analysis (Análisis Temporal):
               - Historical data: Years 1985-2018 (census-based)
               - Projections:
                 * Departments: 1985-2050 (66 years)
                 * Municipalities: 1985-2042 (58 years) - NOTE: Municipal data ends in 2042, not 2050
               - Year-over-year changes: LAG() window function
               - Growth rates: ((final - initial) / initial) * 100
               - Demographic transition tracking over time

            IMPORTANT DATA COVERAGE NOTES:
            - DEPARTMENTAL data: Available for ALL years 1985-2050 (33 departments)
            - MUNICIPAL data: Available for years 1985-2042 ONLY (1,122 municipalities)
            - If user asks for municipal data after 2042, inform them only departmental projections are available
            - Always check nivel='DEPARTAMENTAL' or 'MUNICIPAL' when querying specific year ranges

            CRITICAL QUERY PATTERNS:

            1. Population pyramid (require two genders H and M):
               SELECT edad, sexo, poblacion
               FROM poblacion_edad
               WHERE territorio_id = '05001'
                 AND anio = 2025
                 AND area_geografica = 'Total'
                 AND sexo IN ('H', 'M')
               ORDER BY edad, sexo;

            2. Total population over time:
               SELECT t.nombre, pt.anio, pt.pob_total
               FROM poblacion_total pt
               JOIN territorio t ON pt.territorio_id = t.territorio_id
               WHERE pt.territorio_id = '05001'
                 AND pt.area_geografica = 'Total'
               ORDER BY pt.anio;

            3. Urban vs rural distribution:
               SELECT anio,
                      pob_total,
                      ROUND((pct_urbana * 100)::numeric, 2) as pct_urbana,
                      ROUND((pct_rural * 100)::numeric, 2) as pct_rural
               FROM poblacion_total
               WHERE territorio_id = '05001'
                 AND area_geografica = 'Total'
               ORDER BY anio;

            4. Age groups summary:
               SELECT
                   CASE
                       WHEN edad BETWEEN 0 AND 14 THEN '0-14'
                       WHEN edad BETWEEN 15 AND 64 THEN '15-64'
                       ELSE '65+'
                   END as grupo_edad,
                   SUM(poblacion) as total
               FROM poblacion_edad
               WHERE territorio_id = '05001'
                 AND anio = 2025
                 AND area_geografica = 'Total'
                 AND sexo = 'T'
               GROUP BY grupo_edad;

            5. Compare multiple territories:
               SELECT t.nombre, pt.anio, pt.pob_total
               FROM poblacion_total pt
               JOIN territorio t ON pt.territorio_id = t.territorio_id
               WHERE pt.territorio_id IN ('05001', '11001', '76001')
                 AND pt.area_geografica = 'Total'
                 AND pt.anio = 2025
               ORDER BY pt.pob_total DESC;

            6. Dependency ratio calculation:
               WITH age_groups AS (
                   SELECT
                       SUM(CASE WHEN edad BETWEEN 0 AND 14 THEN poblacion ELSE 0 END) as jovenes,
                       SUM(CASE WHEN edad BETWEEN 15 AND 64 THEN poblacion ELSE 0 END) as productivos,
                       SUM(CASE WHEN edad >= 65 THEN poblacion ELSE 0 END) as adultos_mayores
                   FROM poblacion_edad
                   WHERE territorio_id = '05001'
                     AND anio = 2025
                     AND area_geografica = 'Total'
                     AND sexo = 'T'
               )
               SELECT
                   ROUND(((jovenes + adultos_mayores) / NULLIF(productivos, 0) * 100)::numeric, 2) as ratio_dependencia
               FROM age_groups;

            Important Query Rules:

            - area_geografica values: 'Cabecera Municipal', 'Centros Poblados y Rural Disperso', 'Total' (exact match, case-sensitive)
            - sexo values: 'H', 'M', 'T' (single character, case-sensitive)
            - nivel values: 'DEPARTAMENTAL', 'MUNICIPAL' (uppercase)
            - territorio_id: 2 digits for departments (e.g., '05'), 5 digits for municipalities (e.g., '05001')
            - Years: 1985-2050 for departments, 1985-2042 for municipalities
            - NUMERIC columns: Use ::numeric for ROUND() operations
            - Percentages: pct_urbana and pct_rural are stored as decimals (0-1), multiply by 100 for display
            - NULL handling: Use NULLIF(x, 0) when dividing to avoid division by zero
            - Aggregations: Use SUM(poblacion) for totals, AVG() for averages
            - Window functions: Use LAG(), LEAD() for temporal comparisons
            - JOINs: Always JOIN with territorio table to get territory names

            Performance Notes:
            - Use indexes: territorio_id, anio, area_geografica, sexo are indexed
            - poblacion_edad table has 30M+ rows - always use WHERE clauses
            - poblacion_total is pre-aggregated - prefer it for simple totals
            - Use LIMIT for large result sets
            - Aggregate queries can be expensive - keep them focused

            Output Format:
            - Return valid PostgreSQL syntax
            - Use column aliases for readability (AS nombre_territorio, AS poblacion_total)
            - Include ORDER BY for sorted results
            - DO NOT add LIMIT unless absolutely necessary for performance (e.g., querying all municipalities without filters)
            - Most demographic queries (pyramids, time series, specific territories) should return all matching rows
            - Format numbers: ROUND(value::numeric, 2) for percentages and ratios
            - ALWAYS cast to ::numeric before using ROUND()
            - Example: ROUND((pct_urbana * 100)::numeric, 2)

            Common User Questions and SQL Patterns:

            - "población de [territorio]" → SELECT from poblacion_total with territory name
            - "pirámide poblacional" → SELECT from poblacion_edad with sexo IN ('H','M')
            - "evolución/histórico/tendencia" → SELECT across multiple years with ORDER BY anio
            - "comparar [territorios]" → Multiple territorio_id IN (...) with JOIN
            - "urbano/rural" → pct_urbana, pct_rural from poblacion_total
            - "hombres/mujeres" → sexo='H' or sexo='M' or pob_hombres, pob_mujeres
            - "edad/grupo etario" → CASE WHEN edad BETWEEN for age groups
            - "crecimiento" → Calculate difference or percentage between years
            - "proyección" → Years >= 2019
            """
            )
        else:
            # Default Claude or standard OpenAI
            self.agent = Agent(
                model_name,
                output_type=SQLQuery,
                system_prompt="""You are an expert SQL query generator for the DNP (Departamento Nacional de Planeación) Population Module database of Colombia.
            Your task is to understand natural language queries about population data, demographics, and territorial analysis, then convert them to valid PostgreSQL queries.
            Always ensure queries are safe and efficient. Include relevant JOINs when needed.

            IMPORTANT: PostgreSQL requires proper quoting and type handling.

            Key tables and their columns:

            1. territorio (1,155 rows - Territories):
               - territorio_id (TEXT, PK): DANE territory code (2 digits for department, 5 for municipality)
               - nivel (TEXT): Territory level ['DEPARTAMENTAL', 'MUNICIPAL']
               - dp (TEXT): Department code (2 digits)
               - mpio (TEXT, nullable): Municipality code (3 digits, only for municipal level)
               - nombre (TEXT): Territory name
               - categoria (TEXT, nullable): Territory category (ciudad_intermedia, aglomeracion, etc.)
               - transicion_demografica (TEXT, nullable): Demographic transition level (alto/medio/bajo)

            2. poblacion_edad (30M+ rows - Population by age):
               - territorio_id (TEXT, PK, FK): DANE territory code
               - anio (INTEGER, PK): Projection year (1985-2050 for departments, 1985-2042 for municipalities)
               - area_geografica (TEXT, PK): Geographic area ['Cabecera Municipal', 'Centros Poblados y Rural Disperso', 'Total']
               - sexo (TEXT, PK): Gender ['H' (Hombres/Men), 'M' (Mujeres/Women), 'T' (Total)]
               - edad (INTEGER, PK): Age (0-100)
               - mayores_100 (BOOLEAN): True if corresponds to "100 years and older" group
               - poblacion (NUMERIC): Population count

            3. poblacion_total (aggregated population totals):
               - territorio_id (TEXT, PK, FK): DANE territory code
               - anio (INTEGER, PK): Projection year
               - area_geografica (TEXT, PK): Geographic area
               - pob_total (NUMERIC): Total population
               - pob_hombres (NUMERIC): Male population
               - pob_mujeres (NUMERIC): Female population
               - pct_urbana (NUMERIC(5,4), nullable): Urban percentage (only when area_geografica='Total')
               - pct_rural (NUMERIC(5,4), nullable): Rural percentage (only when area_geografica='Total')

            Common Territory Codes:
            | Code  | Territory       | Level          |
            |-------|-----------------|----------------|
            | 05    | Antioquia       | DEPARTAMENTAL  |
            | 11    | Bogotá D.C.     | DEPARTAMENTAL  |
            | 76    | Valle del Cauca | DEPARTAMENTAL  |
            | 05001 | Medellín        | MUNICIPAL      |
            | 11001 | Bogotá D.C.     | MUNICIPAL      |
            | 76001 | Cali            | MUNICIPAL      |
            | 08001 | Barranquilla    | MUNICIPAL      |

            [Additional system prompt content continues as before...]

            Common User Questions and SQL Patterns:

            - "población de [territorio]" → SELECT from poblacion_total with territory name
            - "pirámide poblacional" → SELECT from poblacion_edad with sexo IN ('H','M')
            - "evolución/histórico/tendencia" → SELECT across multiple years with ORDER BY anio
            - "comparar [territorios]" → Multiple territorio_id IN (...) with JOIN
            - "urbano/rural" → pct_urbana, pct_rural from poblacion_total
            - "hombres/mujeres" → sexo='H' or sexo='M' or pob_hombres, pob_mujeres
            - "edad/grupo etario" → CASE WHEN edad BETWEEN for age groups
            - "crecimiento" → Calculate difference or percentage between years
            - "proyección" → Years >= 2019
            """
            )
        self._schema_cache = None

    async def get_database_schema(self) -> Dict[str, TableInfo]:
        """Get complete database schema information."""
        if self._schema_cache:
            return self._schema_cache

        inspector = inspect(engine)
        schema_info = {}

        for table_name in inspector.get_table_names():
            # Skip chat tables
            if table_name in ['chats', 'chat_messages']:
                continue

            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": col["default"]
                })

            primary_keys = inspector.get_pk_constraint(table_name)["constrained_columns"]
            foreign_keys = []

            for fk in inspector.get_foreign_keys(table_name):
                foreign_keys.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"]
                })

            schema_info[table_name] = TableInfo(
                table_name=table_name,
                columns=columns,
                primary_keys=primary_keys,
                foreign_keys=foreign_keys
            )

        self._schema_cache = schema_info
        return schema_info

    async def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table."""
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
            return [dict(row._mapping) for row in result]

    async def natural_language_to_sql(self, query: str, context: Optional[str] = None) -> SQLQuery:
        """Convert natural language query to SQL."""
        schema = await self.get_database_schema()

        # Create a simplified schema representation for the prompt
        schema_description = []
        for table_name, table_info in schema.items():
            cols = [f"{c['name']} ({c['type']})" for c in table_info.columns[:10]]
            schema_description.append(f"Table: {table_name}\nKey Columns: {', '.join(cols)}...\n")

        prompt = f"""
        Available Tables:
        {chr(10).join(schema_description)}

        User Query: {query}

        Additional Context: {context or 'None'}

        Generate a PostgreSQL query that answers the user's question.

        CRITICAL RULES:
        - If the user mentions a Colombian city/territory NAME (like Bogotá, Medellín, Cali, etc.):
          * IMMEDIATELY convert it to its DIVIPOLA code (Bogotá=11001, Medellín=05001, Cali=76001)
          * Use the territorio_id (DIVIPOLA code) in WHERE clauses, NOT the name
          * Refer to the DIVIPOLA mapping tables in the system prompt
        - Use poblacion_total for simple population totals and urban/rural distributions
        - Use poblacion_edad for age-specific queries and population pyramids
        - Always JOIN with territorio table to include territory names in RESULTS (but filter by territorio_id)
        - For demographic indicators (dependency ratio, CAGR, etc.), use appropriate calculations
        - Use appropriate aggregations (SUM, AVG, COUNT) based on the query intent
        - Include ORDER BY for better result presentation
        - DO NOT add LIMIT to queries unless the result set would be extremely large (>5000 rows)
        - Return ALL rows for pyramids, time series, and specific territory queries

        EXAMPLES:
        - User says "Bogotá" → Use WHERE territorio_id = '11001'
        - User says "Medellín" → Use WHERE territorio_id = '05001'
        - User says "Cali" → Use WHERE territorio_id = '76001'
        - User says "Antioquia" (department) → Use WHERE territorio_id = '05'

        Return the SQL query, an explanation of what it does, and list the tables used.
        Remember to handle NULL values appropriately and use proper type casting for calculations.
        """

        result = await self.agent.run(prompt)
        return result.output

    async def validate_sql(self, sql_query: str) -> bool:
        """Validate SQL query syntax."""
        try:
            with engine.connect() as conn:
                # Use EXPLAIN to validate without executing
                conn.execute(text(f"EXPLAIN {sql_query}"))
            return True
        except Exception:
            return False
