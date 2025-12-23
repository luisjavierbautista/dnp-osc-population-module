-- ============================================================================
-- DNP Population Module - Database Schema
-- PostgreSQL Database: poblacion_db
-- Generated from SQLModel definitions
-- ============================================================================

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE nivel_territorial AS ENUM ('DEPARTAMENTAL', 'MUNICIPAL');
CREATE TYPE area_geografica AS ENUM ('Cabecera Municipal', 'Centros Poblados y Rural Disperso', 'Total');
CREATE TYPE sexo AS ENUM ('H', 'M', 'T');

-- ============================================================================
-- 1. TERRITORY TABLES
-- ============================================================================

CREATE TABLE territorio (
    territorio_id VARCHAR(5) PRIMARY KEY,
    nivel nivel_territorial NOT NULL,
    dp VARCHAR(2) NOT NULL,
    mpio VARCHAR(3),
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    transicion_demografica VARCHAR(50)
);

COMMENT ON TABLE territorio IS 'Geographic territories (departments and municipalities)';
COMMENT ON COLUMN territorio.territorio_id IS 'DANE code: 2 digits = department, 5 digits = municipality';
COMMENT ON COLUMN territorio.nivel IS 'Territory level: DEPARTAMENTAL, MUNICIPAL';
COMMENT ON COLUMN territorio.dp IS 'Department code (2 digits)';
COMMENT ON COLUMN territorio.mpio IS 'Municipality code (3 digits, only for municipal level)';
COMMENT ON COLUMN territorio.categoria IS 'Category: ciudad_intermedia, aglomeracion, etc.';
COMMENT ON COLUMN territorio.transicion_demografica IS 'Demographic transition level: alto, medio, bajo';

-- ============================================================================
-- 2. POPULATION TABLES
-- ============================================================================

CREATE TABLE poblacion_edad (
    territorio_id VARCHAR(5) NOT NULL,
    anio INTEGER NOT NULL,
    area_geografica VARCHAR(50) NOT NULL,
    sexo VARCHAR(1) NOT NULL,
    edad INTEGER NOT NULL,
    mayores_100 BOOLEAN DEFAULT FALSE,
    poblacion NUMERIC NOT NULL,

    PRIMARY KEY (territorio_id, anio, area_geografica, sexo, edad),
    FOREIGN KEY (territorio_id) REFERENCES territorio(territorio_id)
);

CREATE INDEX ix_poblacion_edad_lookup
    ON poblacion_edad(territorio_id, anio, area_geografica, sexo, edad);
CREATE INDEX ix_poblacion_edad_territorio_anio
    ON poblacion_edad(territorio_id, anio);

COMMENT ON TABLE poblacion_edad IS 'Population by age, sex, and geographic area (2018-2050)';
COMMENT ON COLUMN poblacion_edad.area_geografica IS 'Total, Cabecera Municipal, or Centros Poblados y Rural Disperso';
COMMENT ON COLUMN poblacion_edad.sexo IS 'H=Male, M=Female, T=Total';
COMMENT ON COLUMN poblacion_edad.edad IS 'Age 0-100';
COMMENT ON COLUMN poblacion_edad.mayores_100 IS 'True if represents 100+ age group';

-- ----------------------------------------------------------------------------

CREATE TABLE poblacion_total (
    territorio_id VARCHAR(5) NOT NULL,
    anio INTEGER NOT NULL,
    area_geografica VARCHAR(50) NOT NULL,
    pob_total NUMERIC NOT NULL,
    pob_hombres NUMERIC NOT NULL,
    pob_mujeres NUMERIC NOT NULL,
    pct_urbana NUMERIC(5,4),
    pct_rural NUMERIC(5,4),

    PRIMARY KEY (territorio_id, anio, area_geografica),
    FOREIGN KEY (territorio_id) REFERENCES territorio(territorio_id)
);

CREATE INDEX ix_poblacion_total_lookup
    ON poblacion_total(territorio_id, anio, area_geografica);

COMMENT ON TABLE poblacion_total IS 'Aggregated population totals by territory, year, and area';
COMMENT ON COLUMN poblacion_total.pct_urbana IS 'Urban percentage (only when area_geografica=Total)';
COMMENT ON COLUMN poblacion_total.pct_rural IS 'Rural percentage (only when area_geografica=Total)';

-- ============================================================================
-- 3. DANE DIMENSION TABLES
-- ============================================================================

CREATE TABLE dane_regions (
    region_code VARCHAR(10) PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_dane_regions_name ON dane_regions(region_name);

COMMENT ON TABLE dane_regions IS 'DANE population regions (23 regions)';
COMMENT ON COLUMN dane_regions.region_code IS 'Region code: NAL, VDA, ACB, etc.';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_departments (
    dept_code VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_dane_departments_name ON dane_departments(dept_name);

COMMENT ON TABLE dane_departments IS 'Colombian departments (33)';
COMMENT ON COLUMN dane_departments.dept_code IS 'Department DANE code: 05, 11, 76, etc.';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_municipalities (
    muni_code VARCHAR(10) PRIMARY KEY,
    muni_name VARCHAR(100) NOT NULL,
    dept_code VARCHAR(10) NOT NULL,
    region_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (dept_code) REFERENCES dane_departments(dept_code),
    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_municipalities_name ON dane_municipalities(muni_name);
CREATE INDEX ix_dane_municipalities_dept ON dane_municipalities(dept_code);
CREATE INDEX ix_dane_municipalities_region ON dane_municipalities(region_code);

COMMENT ON TABLE dane_municipalities IS 'Colombian municipalities (1,103 municipalities + 20 non-municipalized areas)';

-- ============================================================================
-- 4. DANE INDICATOR TABLES
-- ============================================================================

CREATE TABLE dane_fertility_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    tgf NUMERIC(10,6) NOT NULL,
    age_rates JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_fertility_region ON dane_fertility_indicators(region_code);
CREATE INDEX ix_dane_fertility_year ON dane_fertility_indicators(year);
CREATE INDEX ix_dane_fertility_region_year ON dane_fertility_indicators(region_code, year);

COMMENT ON TABLE dane_fertility_indicators IS 'Fertility indicators by region (2018-2070)';
COMMENT ON COLUMN dane_fertility_indicators.tgf IS 'Total Fertility Rate (TGF)';
COMMENT ON COLUMN dane_fertility_indicators.age_rates IS 'Age-specific fertility rates JSON: {"10": 0.000096, "15": 0.027, ...}';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_migration_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    sex VARCHAR(20) NOT NULL,
    migration_type VARCHAR(30) NOT NULL,
    age_values JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_migration_region ON dane_migration_indicators(region_code);
CREATE INDEX ix_dane_migration_year ON dane_migration_indicators(year);
CREATE INDEX ix_dane_migration_sex ON dane_migration_indicators(sex);
CREATE INDEX ix_dane_migration_type ON dane_migration_indicators(migration_type);

COMMENT ON TABLE dane_migration_indicators IS 'Migration indicators by region, sex, and type (2018-2070)';
COMMENT ON COLUMN dane_migration_indicators.sex IS 'Hombres or Mujeres';
COMMENT ON COLUMN dane_migration_indicators.migration_type IS 'Internacional or Interna';
COMMENT ON COLUMN dane_migration_indicators.age_values IS 'Net migration by age JSON: {"0": 123.45, "20": 5678.9, ...}';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_mortality_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    sex VARCHAR(20) NOT NULL,
    age_mortality_rates JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_mortality_region ON dane_mortality_indicators(region_code);
CREATE INDEX ix_dane_mortality_year ON dane_mortality_indicators(year);
CREATE INDEX ix_dane_mortality_sex ON dane_mortality_indicators(sex);

COMMENT ON TABLE dane_mortality_indicators IS 'Mortality indicators by region and sex (2018-2070)';
COMMENT ON COLUMN dane_mortality_indicators.sex IS 'Hombres or Mujeres';
COMMENT ON COLUMN dane_mortality_indicators.age_mortality_rates IS 'Probability of death (qx) by age JSON: {"0": 0.012, "1": 0.001, ...}';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_principal_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    life_exp_male NUMERIC(6,2),
    life_exp_female NUMERIC(6,2),
    life_exp_total NUMERIC(6,2),
    infant_mortality_rate NUMERIC(10,6),
    other_indicators JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_principal_region ON dane_principal_indicators(region_code);
CREATE INDEX ix_dane_principal_year ON dane_principal_indicators(year);

COMMENT ON TABLE dane_principal_indicators IS 'Principal demographic indicators by region (2018-2070)';
COMMENT ON COLUMN dane_principal_indicators.life_exp_male IS 'Life expectancy at birth - Male';
COMMENT ON COLUMN dane_principal_indicators.life_exp_female IS 'Life expectancy at birth - Female';
COMMENT ON COLUMN dane_principal_indicators.life_exp_total IS 'Life expectancy at birth - Total';
COMMENT ON COLUMN dane_principal_indicators.other_indicators IS 'Additional indicators JSON: {"tasa_bruta_natalidad": 15.67, ...}';

-- ----------------------------------------------------------------------------

CREATE TABLE dane_growth_indicators (
    id SERIAL PRIMARY KEY,
    region_code VARCHAR(10) NOT NULL,
    year INTEGER NOT NULL,
    area_type VARCHAR(50),
    total_population INTEGER,
    growth_rate NUMERIC(10,6),
    natural_increase INTEGER,
    net_migration INTEGER,
    other_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (region_code) REFERENCES dane_regions(region_code)
);

CREATE INDEX ix_dane_growth_region ON dane_growth_indicators(region_code);
CREATE INDEX ix_dane_growth_year ON dane_growth_indicators(year);

COMMENT ON TABLE dane_growth_indicators IS 'Population growth indicators by region (2018-2070)';
COMMENT ON COLUMN dane_growth_indicators.natural_increase IS 'Natural increase (births - deaths)';
COMMENT ON COLUMN dane_growth_indicators.net_migration IS 'Net migration balance';

-- ============================================================================
-- 5. CHAT TABLES (AI Assistant)
-- ============================================================================

CREATE TABLE chat (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE chat IS 'Chat sessions for AI assistant';

-- ----------------------------------------------------------------------------

CREATE TABLE chat_message (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
);

CREATE INDEX ix_chat_message_chat_id ON chat_message(chat_id);

COMMENT ON TABLE chat_message IS 'Individual chat messages';
COMMENT ON COLUMN chat_message.role IS 'user or assistant';
COMMENT ON COLUMN chat_message.metadata IS 'Additional metadata: SQL query, visualization config, etc.';

-- ============================================================================
-- SAMPLE DATA (Reference Only - Not for Production)
-- ============================================================================

-- Sample DANE Regions
-- INSERT INTO dane_regions (region_code, region_name) VALUES
--     ('NAL', 'Total Nacional'),
--     ('VDA', 'Valle de Aburrá'),
--     ('ACB', 'Altiplano Cundiboyacense'),
--     ('BOG', 'Bogotá D.C.');

-- Sample Territories (Departments and Municipalities only - no national level)
-- INSERT INTO territorio (territorio_id, nivel, dp, mpio, nombre) VALUES
--     ('05', 'DEPARTAMENTAL', '05', NULL, 'Antioquia'),
--     ('11', 'DEPARTAMENTAL', '11', NULL, 'Bogotá D.C.'),
--     ('05001', 'MUNICIPAL', '05', '001', 'Medellín');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
