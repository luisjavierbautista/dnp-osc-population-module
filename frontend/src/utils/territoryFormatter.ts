/**
 * Territory Formatter Utility
 * Formats territory display as: DIVIPOLA - Name (DEPT)
 * Example: 05001 - Medellín (ANT)
 */

// Department abbreviations mapping
export const DEPARTMENT_ABBREVIATIONS: Record<string, string> = {
  '05': 'ANT',     // Antioquia
  '08': 'ATL',     // Atlántico
  '11': 'BOG',     // Bogotá D.C.
  '13': 'BOL',     // Bolívar
  '15': 'BOY',     // Boyacá
  '17': 'CAL',     // Caldas
  '18': 'CAQ',     // Caquetá
  '19': 'CAU',     // Cauca
  '20': 'CES',     // Cesar
  '23': 'COR',     // Córdoba
  '25': 'CUN',     // Cundinamarca
  '27': 'CHO',     // Chocó
  '41': 'HUI',     // Huila
  '44': 'LAG',     // La Guajira
  '47': 'MAG',     // Magdalena
  '50': 'MET',     // Meta
  '52': 'NAR',     // Nariño
  '54': 'NSA',     // Norte de Santander
  '63': 'QUI',     // Quindío
  '66': 'RIS',     // Risaralda
  '68': 'SAN',     // Santander
  '70': 'SUC',     // Sucre
  '73': 'TOL',     // Tolima
  '76': 'VAC',     // Valle del Cauca
  '81': 'ARA',     // Arauca
  '85': 'CAS',     // Casanare
  '86': 'PUT',     // Putumayo
  '88': 'SAP',     // San Andrés y Providencia
  '91': 'AMA',     // Amazonas
  '94': 'GUA',     // Guainía
  '95': 'GUV',     // Guaviare
  '97': 'VAU',     // Vaupés
  '99': 'VIC',     // Vichada
};

// Department full names mapping
export const DEPARTMENT_NAMES: Record<string, string> = {
  '05': 'Antioquia',
  '08': 'Atlántico',
  '11': 'Bogotá D.C.',
  '13': 'Bolívar',
  '15': 'Boyacá',
  '17': 'Caldas',
  '18': 'Caquetá',
  '19': 'Cauca',
  '20': 'Cesar',
  '23': 'Córdoba',
  '25': 'Cundinamarca',
  '27': 'Chocó',
  '41': 'Huila',
  '44': 'La Guajira',
  '47': 'Magdalena',
  '50': 'Meta',
  '52': 'Nariño',
  '54': 'Norte de Santander',
  '63': 'Quindío',
  '66': 'Risaralda',
  '68': 'Santander',
  '70': 'Sucre',
  '73': 'Tolima',
  '76': 'Valle del Cauca',
  '81': 'Arauca',
  '85': 'Casanare',
  '86': 'Putumayo',
  '88': 'San Andrés y Providencia',
  '91': 'Amazonas',
  '94': 'Guainía',
  '95': 'Guaviare',
  '97': 'Vaupés',
  '99': 'Vichada',
};

export interface Territory {
  territorio_id: string;
  nombre: string;
  dp?: string;
  nivel?: string;
}

/**
 * Get department abbreviation from department code
 */
export const getDepartmentAbbreviation = (dpCode: string): string => {
  return DEPARTMENT_ABBREVIATIONS[dpCode] || dpCode;
};

/**
 * Get department full name from department code
 */
export const getDepartmentName = (dpCode: string): string => {
  return DEPARTMENT_NAMES[dpCode] || dpCode;
};

/**
 * Format territory for display
 * @param territory - Territory object
 * @returns Formatted string: "DIVIPOLA - Name (DEPT)"
 *
 * Examples:
 * - Municipality: "05001 - Medellín (ANT)"
 * - Department: "05 - Antioquia"
 * - Bogotá: "11001 - Bogotá D.C. (BOG)"
 */
export const formatTerritory = (territory: Territory): string => {
  const { territorio_id, nombre, dp, nivel } = territory;

  // For departments (2-digit codes), don't show abbreviation
  if (territorio_id.length === 2 || nivel === 'DEPARTAMENTAL') {
    return `${territorio_id} - ${nombre}`;
  }

  // For municipalities, show DIVIPOLA - Name (DEPT)
  const deptAbbr = dp ? getDepartmentAbbreviation(dp) : extractDepartmentCode(territorio_id);
  return `${territorio_id} - ${nombre} (${getDepartmentAbbreviation(deptAbbr)})`;
};

/**
 * Format territory for compact display (just name and abbreviation)
 * @param territory - Territory object
 * @returns Formatted string: "Name (DEPT)" or just "Name" for departments
 */
export const formatTerritoryCompact = (territory: Territory): string => {
  const { nombre, dp, territorio_id, nivel } = territory;

  // For departments, just show name
  if (territorio_id.length === 2 || nivel === 'DEPARTAMENTAL') {
    return nombre;
  }

  // For municipalities, show Name (DEPT)
  const deptCode = dp || extractDepartmentCode(territorio_id);
  const deptAbbr = getDepartmentAbbreviation(deptCode);
  return `${nombre} (${deptAbbr})`;
};

/**
 * Format territory for search/filter (lowercase, no accents)
 */
export const formatTerritoryForSearch = (territory: Territory): string => {
  const formatted = formatTerritory(territory);
  return formatted
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, ''); // Remove accents
};

/**
 * Extract department code from territory ID
 * @param territorioId - DIVIPOLA code (2 or 5 digits)
 * @returns Department code (2 digits)
 */
export const extractDepartmentCode = (territorioId: string): string => {
  if (territorioId.length >= 2) {
    return territorioId.substring(0, 2);
  }
  return territorioId;
};

/**
 * Check if territory is a department (2-digit code)
 */
export const isDepartment = (territorioId: string): boolean => {
  return territorioId.length === 2;
};

/**
 * Check if territory is a municipality (5-digit code)
 */
export const isMunicipality = (territorioId: string): boolean => {
  return territorioId.length === 5;
};
