/**
 * Glossary of Demographic Terms
 * Comprehensive list of demographic and population analysis concepts
 */

export interface GlossaryTerm {
  id: string;
  term: string;
  definition: string;
  category: 'indicator' | 'concept' | 'geographic' | 'data';
  examples?: string[];
  relatedTerms?: string[];
}

export const GLOSSARY_TERMS: GlossaryTerm[] = [
  // DEMOGRAPHIC INDICATORS
  {
    id: 'tasa-dependencia',
    term: 'Tasa de Dependencia (Índice de Dependencia)',
    definition: 'Relación entre la población dependiente (menores de 15 años y mayores de 65 años) y la población en edad de trabajar (15-64 años). Se expresa como el número de dependientes por cada 100 personas en edad productiva.',
    category: 'indicator',
    examples: [
      'Una tasa de 50 significa 50 dependientes por cada 100 trabajadores',
      'Valores menores a 60 indican oportunidad de bono demográfico',
      'Valores mayores a 70 indican alta carga de dependencia'
    ],
    relatedTerms: ['bono-demografico', 'poblacion-activa']
  },
  {
    id: 'indice-envejecimiento',
    term: 'Índice de Envejecimiento',
    definition: 'Relación entre la población mayor (65+ años) y la población infantil (0-14 años), multiplicado por 100. Indica el nivel de envejecimiento de la población.',
    category: 'indicator',
    examples: [
      'Valor de 100: igual número de niños y adultos mayores',
      'Menor a 100: población joven (más niños que adultos mayores)',
      'Mayor a 100: población envejecida (más adultos mayores que niños)'
    ],
    relatedTerms: ['transicion-demografica', 'poblacion-mayor']
  },
  {
    id: 'tgf',
    term: 'TGF (Tasa Global de Fecundidad)',
    definition: 'Número promedio de hijos que tendría una mujer durante su vida reproductiva (15-49 años) si se mantuvieran las tasas de fecundidad actuales. Es un indicador clave del cambio demográfico.',
    category: 'indicator',
    examples: [
      'TGF = 2.1 es el nivel de reemplazo poblacional',
      'TGF < 2.1 indica población que eventualmente decrecerá',
      'TGF > 3.0 indica alta fecundidad'
    ],
    relatedTerms: ['tasa-natalidad', 'cambio-demografico']
  },
  {
    id: 'esperanza-vida',
    term: 'Esperanza de Vida',
    definition: 'Número promedio de años que se espera que viva una persona desde su nacimiento, basado en las tasas de mortalidad actuales.',
    category: 'indicator',
    examples: [
      'Esperanza de vida al nacer en Colombia: ~77 años',
      'Varía por sexo: mujeres generalmente viven más que hombres',
      'Aumenta con el desarrollo socioeconómico'
    ],
    relatedTerms: ['tasa-mortalidad', 'tabla-vida']
  },
  {
    id: 'tasa-mortalidad',
    term: 'Tasa de Mortalidad',
    definition: 'Proporción de personas que fallecen en un período determinado. Puede ser específica por edad, sexo o causa de muerte.',
    category: 'indicator',
    examples: [
      'Tasa bruta de mortalidad: muertes por cada 1,000 habitantes',
      'Tasa de mortalidad infantil: muertes de menores de 1 año',
      'Tasas específicas por edad: probabilidad de muerte a cada edad (qx)'
    ],
    relatedTerms: ['esperanza-vida', 'tabla-mortalidad']
  },
  {
    id: 'tasa-natalidad',
    term: 'Tasa de Natalidad',
    definition: 'Número de nacimientos por cada 1,000 habitantes en un año determinado.',
    category: 'indicator',
    examples: [
      'Colombia 2025: aproximadamente 15-17 nacimientos por 1,000 habitantes',
      'Ha disminuido en las últimas décadas debido a la transición demográfica'
    ],
    relatedTerms: ['tgf', 'crecimiento-poblacional']
  },
  {
    id: 'tasa-migracion',
    term: 'Tasa de Migración',
    definition: 'Diferencia entre inmigración y emigración, expresada como el saldo migratorio neto por cada 1,000 habitantes.',
    category: 'indicator',
    examples: [
      'Migración neta positiva: más personas entran que salen',
      'Migración neta negativa: más personas salen que entran',
      'Afecta el crecimiento poblacional junto con natalidad y mortalidad'
    ],
    relatedTerms: ['crecimiento-poblacional']
  },
  {
    id: 'crecimiento-poblacional',
    term: 'Tasa de Crecimiento Poblacional',
    definition: 'Variación porcentual de la población en un período determinado. Resulta de la diferencia entre nacimientos, defunciones y migración neta.',
    category: 'indicator',
    examples: [
      'Colombia: aproximadamente 1.0% - 1.5% anual',
      'TCAA (Tasa de Crecimiento Anual Promedio): promedio geométrico del crecimiento'
    ],
    relatedTerms: ['tasa-natalidad', 'tasa-mortalidad', 'tasa-migracion']
  },
  {
    id: 'relacion-masculinidad',
    term: 'Relación de Masculinidad (Sex Ratio)',
    definition: 'Número de hombres por cada 100 mujeres en la población. Indica el equilibrio de género en la población.',
    category: 'indicator',
    examples: [
      'Valor de 100: igual número de hombres y mujeres',
      'Colombia: típicamente 95-98 (más mujeres que hombres)',
      'Al nacer suele ser ~105 (más nacimientos masculinos)'
    ],
    relatedTerms: []
  },

  // DEMOGRAPHIC CONCEPTS
  {
    id: 'bono-demografico',
    term: 'Bono Demográfico (Dividendo Demográfico)',
    definition: 'Período favorable en que la proporción de población en edad de trabajar (15-64 años) es mayor que la población dependiente, creando una ventana de oportunidad económica.',
    category: 'concept',
    examples: [
      'Ocurre cuando la tasa de dependencia es menor a 60',
      'Resultado de la transición demográfica: menor natalidad pero población aún joven',
      'Oportunidad para invertir en desarrollo económico y capital humano'
    ],
    relatedTerms: ['tasa-dependencia', 'transicion-demografica', 'poblacion-activa']
  },
  {
    id: 'transicion-demografica',
    term: 'Transición Demográfica',
    definition: 'Proceso de cambio de una población de altas tasas de natalidad y mortalidad a bajas tasas de ambas, pasando por etapas intermedias de crecimiento poblacional.',
    category: 'concept',
    examples: [
      'Etapa 1: Alta natalidad y mortalidad (crecimiento lento)',
      'Etapa 2: Baja mortalidad pero alta natalidad (crecimiento rápido)',
      'Etapa 3: Baja mortalidad y natalidad (crecimiento lento)',
      'Colombia está en etapa avanzada de transición'
    ],
    relatedTerms: ['bono-demografico', 'indice-envejecimiento']
  },
  {
    id: 'piramide-poblacional',
    term: 'Pirámide Poblacional',
    definition: 'Representación gráfica de la distribución de la población por edad y sexo, mostrando hombres a la izquierda y mujeres a la derecha.',
    category: 'concept',
    examples: [
      'Pirámide expansiva: base ancha (población joven)',
      'Pirámide constrictiva: base estrecha (población envejecida)',
      'Pirámide estacionaria: lados rectos (población estable)'
    ],
    relatedTerms: ['estructura-edad']
  },
  {
    id: 'poblacion-juvenil',
    term: 'Población Juvenil (Menor)',
    definition: 'Población menor de 15 años. También llamada población infantil o en edad no productiva.',
    category: 'concept',
    examples: [
      'Incluye edades 0-14 años',
      'Parte de la población dependiente',
      'Requiere inversión en educación y salud'
    ],
    relatedTerms: ['tasa-dependencia', 'estructura-edad']
  },
  {
    id: 'poblacion-activa',
    term: 'Población Activa (Productiva)',
    definition: 'Población entre 15 y 64 años, considerada en edad de trabajar. Es la base del dividendo demográfico.',
    category: 'concept',
    examples: [
      'Incluye edades 15-64 años',
      'Población potencialmente económicamente activa',
      'Sostiene a la población dependiente'
    ],
    relatedTerms: ['bono-demografico', 'tasa-dependencia']
  },
  {
    id: 'poblacion-mayor',
    term: 'Población Mayor (Adulta Mayor)',
    definition: 'Población de 65 años o más. Considerada población dependiente que requiere atención en salud y pensiones.',
    category: 'concept',
    examples: [
      'Incluye edades 65+ años',
      'Población en retiro',
      'Su proporción aumenta con el envejecimiento poblacional'
    ],
    relatedTerms: ['indice-envejecimiento', 'tasa-dependencia']
  },
  {
    id: 'estructura-edad',
    term: 'Estructura por Edad',
    definition: 'Distribución de la población según grupos de edad. Muestra la composición etaria de la población.',
    category: 'concept',
    examples: [
      'Tres grandes grupos: 0-14, 15-64, 65+',
      'Grupos quinquenales: 0-4, 5-9, 10-14, etc.',
      'Se visualiza mediante pirámides poblacionales'
    ],
    relatedTerms: ['piramide-poblacional']
  },
  {
    id: 'tabla-vida',
    term: 'Tabla de Vida (Life Table)',
    definition: 'Herramienta estadística que muestra la probabilidad de supervivencia a cada edad, basada en las tasas de mortalidad observadas.',
    category: 'concept',
    examples: [
      'Muestra esperanza de vida a cada edad',
      'Incluye probabilidad de muerte (qx) por edad',
      'Base para cálculos actuariales y de seguros'
    ],
    relatedTerms: ['esperanza-vida', 'tasa-mortalidad']
  },
  {
    id: 'tabla-mortalidad',
    term: 'Tabla de Mortalidad',
    definition: 'Similar a la tabla de vida, muestra las tasas de mortalidad específicas por edad y permite calcular indicadores de supervivencia.',
    category: 'concept',
    examples: [
      'qx: probabilidad de morir entre edad x y x+1',
      'lx: número de sobrevivientes a edad x',
      'ex: esperanza de vida a edad x'
    ],
    relatedTerms: ['tabla-vida', 'esperanza-vida']
  },

  // GEOGRAPHIC CONCEPTS
  {
    id: 'divipola',
    term: 'DIVIPOLA (División Político-Administrativa)',
    definition: 'Código de División Político-Administrativa de Colombia del DANE. Identifica de manera única cada departamento (2 dígitos) y municipio (5 dígitos).',
    category: 'geographic',
    examples: [
      '05: Departamento de Antioquia',
      '05001: Municipio de Medellín',
      '11001: Bogotá D.C.',
      '76001: Cali'
    ],
    relatedTerms: ['territorio']
  },
  {
    id: 'regiones-dane',
    term: 'Regiones Poblacionales DANE',
    definition: '23 regiones definidas por el DANE para realizar proyecciones de población, agrupando territorios con características demográficas similares.',
    category: 'geographic',
    examples: [
      'VDA: Valle de Aburrá',
      'AQU: Antioquia y Urabá',
      'ACB: Altiplano Cundiboyacense',
      'Permiten análisis regional más allá de divisiones político-administrativas'
    ],
    relatedTerms: ['divipola']
  },
  {
    id: 'area-geografica',
    term: 'Área Geográfica',
    definition: 'Clasificación del territorio según su ubicación: Cabecera Municipal (urbano), Centros Poblados y Rural Disperso (rural), o Total.',
    category: 'geographic',
    examples: [
      'Cabecera Municipal: zona urbana del municipio',
      'Centros Poblados y Rural Disperso: zona rural',
      'Total: suma de urbano y rural',
      'Colombia es ~75-80% urbana'
    ],
    relatedTerms: ['urbano-rural']
  },
  {
    id: 'urbano-rural',
    term: 'Distribución Urbano-Rural',
    definition: 'Porcentaje de la población que vive en zonas urbanas (cabeceras municipales) versus zonas rurales (centros poblados y rural disperso).',
    category: 'geographic',
    examples: [
      'Tendencia global: urbanización creciente',
      'Colombia: aproximadamente 77% urbana, 23% rural',
      'Varía significativamente entre departamentos'
    ],
    relatedTerms: ['area-geografica']
  },
  {
    id: 'territorio',
    term: 'Territorio',
    definition: 'Unidad geográfica de análisis. Puede ser un departamento (nivel departamental) o un municipio (nivel municipal).',
    category: 'geographic',
    examples: [
      '33 departamentos en Colombia',
      '1,123 municipios aproximadamente',
      'Nivel departamental: 2 dígitos DIVIPOLA',
      'Nivel municipal: 5 dígitos DIVIPOLA'
    ],
    relatedTerms: ['divipola']
  },

  // DATA SOURCES
  {
    id: 'dane',
    term: 'DANE (Departamento Administrativo Nacional de Estadística)',
    definition: 'Entidad responsable de la producción y difusión de información estadística oficial de Colombia, incluyendo censos y proyecciones de población.',
    category: 'data',
    examples: [
      'Realiza el Censo Nacional de Población cada 10-15 años',
      'Publica proyecciones de población 2018-2050',
      'Dirección de Censos y Demografía (DCD)'
    ],
    relatedTerms: ['proyecciones-poblacion']
  },
  {
    id: 'proyecciones-poblacion',
    term: 'Proyecciones de Población',
    definition: 'Estimaciones del tamaño y estructura de la población futura basadas en tendencias de natalidad, mortalidad y migración.',
    category: 'data',
    examples: [
      'DANE: proyecciones 2018-2050 (departamental)',
      'DANE: proyecciones 2018-2042 (municipal)',
      'Basadas en Censo 2018',
      'Actualizadas en julio 2025'
    ],
    relatedTerms: ['dane']
  },
  {
    id: 'censo',
    term: 'Censo de Población',
    definition: 'Recuento completo de la población de un país en un momento determinado, recopilando información demográfica, social y económica.',
    category: 'data',
    examples: [
      'Último censo en Colombia: 2018',
      'Censo anterior: 2005',
      'Base para las proyecciones de población',
      'Permite actualizar estadísticas demográficas'
    ],
    relatedTerms: ['dane', 'proyecciones-poblacion']
  },
  {
    id: 'grupos-edad-quinquenales',
    term: 'Grupos de Edad Quinquenales',
    definition: 'Agrupación de la población en intervalos de 5 años (0-4, 5-9, 10-14, etc.) utilizada comúnmente en análisis demográfico.',
    category: 'data',
    examples: [
      '0-4 años: primera infancia',
      '15-19 años: juventud',
      '60-64 años: pre-adulto mayor',
      'Facilita el análisis de tendencias'
    ],
    relatedTerms: ['estructura-edad']
  }
];

// Category labels
export const CATEGORY_LABELS = {
  indicator: 'Indicadores Demográficos',
  concept: 'Conceptos Demográficos',
  geographic: 'Geografía y Territorios',
  data: 'Fuentes de Datos'
};

// Helper functions
export const getTermsByCategory = (category: GlossaryTerm['category']) => {
  return GLOSSARY_TERMS.filter(term => term.category === category);
};

export const searchTerms = (query: string) => {
  const lowerQuery = query.toLowerCase();
  return GLOSSARY_TERMS.filter(term =>
    term.term.toLowerCase().includes(lowerQuery) ||
    term.definition.toLowerCase().includes(lowerQuery)
  );
};

export const getTermById = (id: string) => {
  return GLOSSARY_TERMS.find(term => term.id === id);
};
