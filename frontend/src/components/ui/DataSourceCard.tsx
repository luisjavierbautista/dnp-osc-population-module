import React from 'react'

type DataSourceType =
  | 'population'      // Departmental projections: 2018-2050
  | 'indicators'      // Regional DANE indicators: 2018-2070
  | 'municipal'       // Municipal projections: 2018-2042
  | 'fertility'       // Fertility indicators: 2018-2070
  | 'mortality'       // Mortality indicators: 2018-2070
  | 'migration'       // Migration indicators: 2018-2070
  | 'growth'          // Growth indicators: 2018-2070
  | 'principal'       // Principal demographic indicators: 2018-2070

interface DataSourceCardProps {
  compact?: boolean
  className?: string
  dataType?: DataSourceType
}

interface DataSourceInfo {
  yearRange: string
  description: string
  level: string
}

/**
 * DataSourceCard - Displays DANE data source attribution in a card format
 * Can be added to individual panels for more prominent attribution
 *
 * Year coverage by data type:
 * - Population projections (departmental): 2018-2050
 * - DANE indicators (regional): 2018-2070
 * - Municipal data: 2018-2042
 * - Fertility/Mortality/Migration/Growth indicators: 2018-2070
 */
export const DataSourceCard: React.FC<DataSourceCardProps> = ({
  compact = false,
  className = '',
  dataType = 'population'
}) => {
  const dataSourceInfo: Record<DataSourceType, DataSourceInfo> = {
    population: {
      yearRange: '2018-2050',
      description: 'Proyecciones de Población',
      level: 'Nivel Departamental'
    },
    indicators: {
      yearRange: '2018-2070',
      description: 'Indicadores Demográficos',
      level: '23 Regiones DANE'
    },
    municipal: {
      yearRange: '2018-2042',
      description: 'Proyecciones de Población',
      level: 'Nivel Municipal'
    },
    fertility: {
      yearRange: '2018-2070',
      description: 'Indicadores de Fecundidad',
      level: '23 Regiones DANE'
    },
    mortality: {
      yearRange: '2018-2070',
      description: 'Indicadores de Mortalidad',
      level: '23 Regiones DANE'
    },
    migration: {
      yearRange: '2018-2070',
      description: 'Indicadores de Migración',
      level: '23 Regiones DANE'
    },
    growth: {
      yearRange: '2018-2070',
      description: 'Indicadores de Crecimiento',
      level: '23 Regiones DANE'
    },
    principal: {
      yearRange: '2018-2070',
      description: 'Indicadores Principales (TBN, TBM, TCN)',
      level: '23 Regiones DANE'
    }
  }

  const info = dataSourceInfo[dataType]

  if (compact) {
    return (
      <div className={`text-xs text-muted-foreground border-t pt-3 mt-4 ${className}`}>
        <div>
          <span className="font-medium">Fuente:</span> DANE - {info.description} {info.yearRange}
        </div>
        <div className="mt-1">
          {info.level} | Actualizado: Julio 2025
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-muted/30 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <div className="text-2xl">📊</div>
        <div>
          <h4 className="text-sm font-semibold text-foreground mb-1">Fuente de Datos</h4>
          <p className="text-sm text-muted-foreground">
            DANE - Departamento Administrativo Nacional de Estadística
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            {info.description} {info.yearRange}
          </p>
          <p className="text-xs text-muted-foreground">
            {info.level} | Actualizado: Julio 2025
          </p>
          <p className="text-xs text-muted-foreground">
            Dirección de Censos y Demografía (DCD)
          </p>
        </div>
      </div>
    </div>
  )
}

export default DataSourceCard
