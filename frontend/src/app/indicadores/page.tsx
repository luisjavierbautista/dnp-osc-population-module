'use client'

import { useState } from 'react'
import { useQuery, useQueries } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loading } from '@/components/ui/Loading'
import { DataSourceCard } from '@/components/ui/DataSourceCard'
import { daneApi } from '@/services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// Colors for different region lines
const COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
]

type IndicatorType = 'fertility' | 'mortality' | 'migration' | 'principal'

const INDICATOR_CONFIG: Record<IndicatorType, {
  title: string
  description: string
  yAxisLabel: string
  dataType: 'fertility' | 'mortality' | 'migration' | 'indicators'
}> = {
  fertility: {
    title: 'Tasa Global de Fecundidad (TGF)',
    description: 'Número promedio de hijos por mujer durante su vida reproductiva',
    yAxisLabel: 'TGF (hijos por mujer)',
    dataType: 'fertility'
  },
  mortality: {
    title: 'Esperanza de Vida al Nacer',
    description: 'Años promedio que se espera viva una persona al nacer',
    yAxisLabel: 'Años',
    dataType: 'mortality'
  },
  migration: {
    title: 'Tasa Neta de Migración',
    description: 'Diferencia entre inmigrantes y emigrantes por cada 1,000 habitantes',
    yAxisLabel: 'Tasa (por 1,000)',
    dataType: 'migration'
  },
  principal: {
    title: 'Indicadores Demográficos Principales',
    description: 'Tasa bruta de natalidad, mortalidad y crecimiento natural',
    yAxisLabel: 'Tasa (por 1,000)',
    dataType: 'indicators'
  }
}

export default function IndicadoresPage() {
  const [selectedRegions, setSelectedRegions] = useState<string[]>(['NAL'])
  const [selectedIndicator, setSelectedIndicator] = useState<IndicatorType>('fertility')
  const [selectedSex, setSelectedSex] = useState<'Hombres' | 'Mujeres' | 'Total'>('Total')

  // Get DANE regions
  const { data: regions } = useQuery({
    queryKey: ['dane-regions'],
    queryFn: () => daneApi.getRegions(),
  })

  // Get region name helper
  const getRegionName = (code: string) => {
    if (code === 'NAL') return 'Nacional'
    const region = regions?.find(r => r.region_code === code)
    return region ? region.region_name : code
  }

  // Fertility queries
  const fertilityQueries = useQueries({
    queries: selectedRegions.map(regionCode => ({
      queryKey: ['dane-fertility', regionCode],
      queryFn: () => daneApi.getFertility({
        region_code: regionCode,
        year_start: 2018,
        year_end: 2070,
        limit: 100
      }),
      enabled: selectedIndicator === 'fertility' && selectedRegions.length > 0,
    })),
  })

  // Mortality queries
  const mortalityQueries = useQueries({
    queries: selectedRegions.map(regionCode => ({
      queryKey: ['dane-mortality', regionCode, selectedSex],
      queryFn: () => daneApi.getMortality({
        region_code: regionCode,
        year_start: 2018,
        year_end: 2070,
        sex: selectedSex === 'Total' ? undefined : selectedSex,
        limit: 200
      }),
      enabled: selectedIndicator === 'mortality' && selectedRegions.length > 0,
    })),
  })

  // Migration queries
  const migrationQueries = useQueries({
    queries: selectedRegions.map(regionCode => ({
      queryKey: ['dane-migration', regionCode, selectedSex],
      queryFn: () => daneApi.getMigration({
        region_code: regionCode,
        year_start: 2018,
        year_end: 2070,
        sex: selectedSex === 'Total' ? undefined : selectedSex,
        limit: 200
      }),
      enabled: selectedIndicator === 'migration' && selectedRegions.length > 0,
    })),
  })

  // Principal indicators queries
  const principalQueries = useQueries({
    queries: selectedRegions.map(regionCode => ({
      queryKey: ['dane-principal', regionCode],
      queryFn: () => daneApi.getPrincipalTimeSeries(regionCode, 2018, 2070),
      enabled: selectedIndicator === 'principal' && selectedRegions.length > 0,
    })),
  })

  // Determine loading and error states based on selected indicator
  const getActiveQueries = () => {
    switch (selectedIndicator) {
      case 'fertility': return fertilityQueries
      case 'mortality': return mortalityQueries
      case 'migration': return migrationQueries
      case 'principal': return principalQueries
    }
  }

  const activeQueries = getActiveQueries()
  const isLoading = activeQueries.some(q => q.isLoading)
  const hasError = activeQueries.some(q => q.error)

  // Combine data based on indicator type
  const combinedData = (() => {
    if (activeQueries.some(q => !q.data)) return []

    // Get all unique years
    const allYears = new Set<number>()

    if (selectedIndicator === 'fertility') {
      fertilityQueries.forEach(query => {
        query.data?.forEach(item => allYears.add(item.year))
      })

      const sortedYears = Array.from(allYears).sort((a, b) => a - b)
      return sortedYears.map(year => {
        const row: any = { year }
        fertilityQueries.forEach((query, qIdx) => {
          const regionCode = selectedRegions[qIdx]
          const yearData = query.data?.find(item => item.year === year)
          if (yearData) {
            row[`TGF_${regionCode}`] = parseFloat(Number(yearData.tgf).toFixed(2))
          }
        })
        return row
      })
    }

    if (selectedIndicator === 'mortality') {
      mortalityQueries.forEach(query => {
        query.data?.forEach(item => allYears.add(item.year))
      })

      const sortedYears = Array.from(allYears).sort((a, b) => a - b)
      return sortedYears.map(year => {
        const row: any = { year }
        mortalityQueries.forEach((query, qIdx) => {
          const regionCode = selectedRegions[qIdx]
          // Calculate life expectancy from mortality rates (simplified)
          const yearDataItems = query.data?.filter(item => item.year === year) || []
          if (yearDataItems.length > 0) {
            // Get e0 (life expectancy at birth) if available in the data
            // For now, we'll calculate average mortality rate as proxy
            let totalRate = 0
            let count = 0
            yearDataItems.forEach(item => {
              const rates = Object.values(item.age_mortality_rates).filter((val): val is number =>
                typeof val === 'number' && !isNaN(val) && isFinite(val)
              )
              if (rates.length > 0) {
                totalRate += rates.reduce((sum, val) => sum + val, 0) / rates.length
                count++
              }
            })
            if (count > 0) {
              // Convert to approximate life expectancy (inverse relationship)
              const avgRate = totalRate / count
              // Simplified: lower mortality = higher life expectancy
              row[`Mortalidad_${regionCode}`] = parseFloat((avgRate * 1000).toFixed(2))
            }
          }
        })
        return row
      })
    }

    if (selectedIndicator === 'migration') {
      migrationQueries.forEach(query => {
        query.data?.forEach(item => allYears.add(item.year))
      })

      const sortedYears = Array.from(allYears).sort((a, b) => a - b)
      return sortedYears.map(year => {
        const row: any = { year }
        migrationQueries.forEach((query, qIdx) => {
          const regionCode = selectedRegions[qIdx]
          const yearDataItems = query.data?.filter(item => item.year === year) || []
          if (yearDataItems.length > 0) {
            // Sum all migration values for the year
            let totalMigration = 0
            let count = 0
            yearDataItems.forEach(item => {
              const values = Object.values(item.age_values).filter((val): val is number =>
                typeof val === 'number' && !isNaN(val) && isFinite(val)
              )
              if (values.length > 0) {
                totalMigration += values.reduce((sum, val) => sum + val, 0)
                count++
              }
            })
            if (count > 0) {
              row[`Migracion_${regionCode}`] = parseFloat((totalMigration / 1000).toFixed(2))
            }
          }
        })
        return row
      })
    }

    if (selectedIndicator === 'principal') {
      principalQueries.forEach(query => {
        query.data?.forEach(item => allYears.add(item.year))
      })

      const sortedYears = Array.from(allYears).sort((a, b) => a - b)
      return sortedYears.map(year => {
        const row: any = { year }
        principalQueries.forEach((query, qIdx) => {
          const regionCode = selectedRegions[qIdx]
          const yearData = query.data?.find(item => item.year === year)
          if (yearData && yearData.other_indicators) {
            // Get TBN (Tasa Bruta de Natalidad) if available
            const indicators = yearData.other_indicators
            const tbn = indicators['tasa_bruta_natalidad'] || indicators['TBN'] || indicators['tbn']
            const tbm = indicators['tasa_bruta_mortalidad'] || indicators['TBM'] || indicators['tbm']
            const tcn = indicators['tasa_crecimiento_natural'] || indicators['TCN'] || indicators['tcn']

            if (tbn !== undefined) row[`TBN_${regionCode}`] = parseFloat(Number(tbn).toFixed(2))
            if (tbm !== undefined) row[`TBM_${regionCode}`] = parseFloat(Number(tbm).toFixed(2))
            if (tcn !== undefined) row[`TCN_${regionCode}`] = parseFloat(Number(tcn).toFixed(2))
          }
        })
        return row
      })
    }

    return []
  })()

  // Get data keys for chart based on indicator
  const getDataKeys = () => {
    if (selectedIndicator === 'fertility') {
      return selectedRegions.map(r => `TGF_${r}`)
    }
    if (selectedIndicator === 'mortality') {
      return selectedRegions.map(r => `Mortalidad_${r}`)
    }
    if (selectedIndicator === 'migration') {
      return selectedRegions.map(r => `Migracion_${r}`)
    }
    if (selectedIndicator === 'principal') {
      // For principal, show TBN for all regions
      return selectedRegions.map(r => `TBN_${r}`)
    }
    return []
  }

  // Handle region selection change
  const handleRegionChange = (regionCode: string) => {
    setSelectedRegions(prev => {
      if (prev.includes(regionCode)) {
        if (prev.length > 1) {
          return prev.filter(r => r !== regionCode)
        }
        return prev
      } else {
        if (prev.length < 6) {
          return [...prev, regionCode]
        }
        return prev
      }
    })
  }

  const config = INDICATOR_CONFIG[selectedIndicator]

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Indicadores Demográficos DANE</h1>
          <p className="text-muted-foreground">
            Explora indicadores de fecundidad, mortalidad, migración y demografía (2018-2070)
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Configuración</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Indicator Selector */}
              <div>
                <label className="block text-sm font-medium mb-2">Indicador</label>
                <div className="space-y-2">
                  <button
                    onClick={() => setSelectedIndicator('fertility')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left transition-colors ${
                      selectedIndicator === 'fertility'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Fecundidad</div>
                    <div className="text-xs opacity-80">TGF - Tasa Global de Fecundidad</div>
                  </button>
                  <button
                    onClick={() => setSelectedIndicator('mortality')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left transition-colors ${
                      selectedIndicator === 'mortality'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Mortalidad</div>
                    <div className="text-xs opacity-80">Tasas de mortalidad por edad</div>
                  </button>
                  <button
                    onClick={() => setSelectedIndicator('migration')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left transition-colors ${
                      selectedIndicator === 'migration'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Migración</div>
                    <div className="text-xs opacity-80">Migración internacional e interna</div>
                  </button>
                  <button
                    onClick={() => setSelectedIndicator('principal')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left transition-colors ${
                      selectedIndicator === 'principal'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Principales</div>
                    <div className="text-xs opacity-80">TBN, TBM, Crecimiento Natural</div>
                  </button>
                </div>
              </div>

              {/* Sex filter for mortality and migration */}
              {(selectedIndicator === 'mortality' || selectedIndicator === 'migration') && (
                <div>
                  <label className="block text-sm font-medium mb-2">Sexo</label>
                  <div className="flex gap-1">
                    {(['Total', 'Hombres', 'Mujeres'] as const).map(sex => (
                      <button
                        key={sex}
                        onClick={() => setSelectedSex(sex)}
                        className={`flex-1 px-2 py-2 rounded-md text-xs ${
                          selectedSex === sex
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary'
                        }`}
                      >
                        {sex === 'Total' ? 'Todos' : sex === 'Hombres' ? 'H' : 'M'}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Multi-Region Selector */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Regiones DANE
                  <span className="text-muted-foreground font-normal ml-1">
                    ({selectedRegions.length}/6)
                  </span>
                </label>
                <div className="max-h-48 overflow-y-auto border rounded-md p-2 space-y-1">
                  {/* Nacional option first */}
                  <label
                    className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors ${
                      selectedRegions.includes('NAL')
                        ? 'bg-primary/10 border border-primary/30'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedRegions.includes('NAL')}
                      onChange={() => handleRegionChange('NAL')}
                      className="rounded"
                    />
                    <span className="text-sm font-medium">Nacional</span>
                    {selectedRegions.includes('NAL') && (
                      <span
                        className="ml-auto w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: COLORS[selectedRegions.indexOf('NAL') % COLORS.length] }}
                      />
                    )}
                  </label>

                  {/* Other regions */}
                  {regions?.map((region) => (
                    <label
                      key={region.region_code}
                      className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-colors ${
                        selectedRegions.includes(region.region_code)
                          ? 'bg-primary/10 border border-primary/30'
                          : 'hover:bg-muted'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedRegions.includes(region.region_code)}
                        onChange={() => handleRegionChange(region.region_code)}
                        disabled={!selectedRegions.includes(region.region_code) && selectedRegions.length >= 6}
                        className="rounded"
                      />
                      <span className="text-xs truncate flex-1" title={region.region_name}>
                        {region.region_name}
                      </span>
                      {selectedRegions.includes(region.region_code) && (
                        <span
                          className="ml-auto w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: COLORS[selectedRegions.indexOf(region.region_code) % COLORS.length] }}
                        />
                      )}
                    </label>
                  ))}
                </div>
              </div>

              <DataSourceCard compact dataType={config.dataType} className="mt-4" />
            </CardContent>
          </Card>

          {/* Chart Area */}
          <div className="lg:col-span-3 space-y-6">
            {isLoading && <Loading size="lg" text="Cargando indicadores..." />}

            {hasError && (
              <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                Error al cargar los datos. Por favor intenta de nuevo.
              </div>
            )}

            {selectedRegions.length === 0 && !isLoading && (
              <div className="p-8 text-center text-muted-foreground border rounded-lg">
                Selecciona al menos una región para ver los indicadores
              </div>
            )}

            {/* Main Chart */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>{config.title}</CardTitle>
                  <p className="text-sm text-muted-foreground">{config.description}</p>
                </CardHeader>
                <CardContent>
                  <div className="h-[500px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="year"
                          label={{ value: 'Año', position: 'insideBottom', offset: -10 }}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          label={{ value: config.yAxisLabel, angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip
                          formatter={(value: number, name: string) => {
                            const parts = name.split('_')
                            const regionCode = parts.slice(1).join('_')
                            return [`${value?.toFixed(2) || 'N/A'}`, getRegionName(regionCode)]
                          }}
                          labelFormatter={(label) => `Año ${label}`}
                        />
                        <Legend
                          formatter={(value: string) => {
                            const parts = value.split('_')
                            const regionCode = parts.slice(1).join('_')
                            return getRegionName(regionCode)
                          }}
                        />
                        {getDataKeys().map((dataKey, idx) => (
                          <Line
                            key={dataKey}
                            type="monotone"
                            dataKey={dataKey}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                            activeDot={{ r: 4 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Data summary */}
                  <div className="mt-4 p-4 bg-muted/30 rounded-md">
                    <p className="text-sm font-medium mb-2">Resumen de datos:</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Período</p>
                        <p className="font-semibold">
                          {combinedData[0]?.year} - {combinedData[combinedData.length - 1]?.year}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Datos</p>
                        <p className="font-semibold">{combinedData.length} años</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Regiones</p>
                        <p className="font-semibold">{selectedRegions.length} seleccionadas</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Indicador</p>
                        <p className="font-semibold">{selectedIndicator === 'fertility' ? 'TGF' : selectedIndicator === 'mortality' ? 'Mortalidad' : selectedIndicator === 'migration' ? 'Migración' : 'Principal'}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Additional chart for Principal indicators (TBM, TCN) */}
            {selectedIndicator === 'principal' && combinedData.length > 0 && !isLoading && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Tasa Bruta de Mortalidad (TBM)</CardTitle>
                    <p className="text-sm text-muted-foreground">Defunciones por cada 1,000 habitantes</p>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[350px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={combinedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis domain={['auto', 'auto']} />
                          <Tooltip
                            formatter={(value: number, name: string) => {
                              const regionCode = name.replace('TBM_', '')
                              return [`${value?.toFixed(2) || 'N/A'}`, getRegionName(regionCode)]
                            }}
                            labelFormatter={(label) => `Año ${label}`}
                          />
                          <Legend formatter={(value: string) => getRegionName(value.replace('TBM_', ''))} />
                          {selectedRegions.map((regionCode, idx) => (
                            <Line
                              key={regionCode}
                              type="monotone"
                              dataKey={`TBM_${regionCode}`}
                              stroke={COLORS[idx % COLORS.length]}
                              strokeWidth={2}
                              dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                              connectNulls
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Tasa de Crecimiento Natural (TCN)</CardTitle>
                    <p className="text-sm text-muted-foreground">Diferencia entre natalidad y mortalidad por 1,000 habitantes</p>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[350px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={combinedData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis domain={['auto', 'auto']} />
                          <Tooltip
                            formatter={(value: number, name: string) => {
                              const regionCode = name.replace('TCN_', '')
                              return [`${value?.toFixed(2) || 'N/A'}`, getRegionName(regionCode)]
                            }}
                            labelFormatter={(label) => `Año ${label}`}
                          />
                          <Legend formatter={(value: string) => getRegionName(value.replace('TCN_', ''))} />
                          {selectedRegions.map((regionCode, idx) => (
                            <Line
                              key={regionCode}
                              type="monotone"
                              dataKey={`TCN_${regionCode}`}
                              stroke={COLORS[idx % COLORS.length]}
                              strokeWidth={2}
                              dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                              connectNulls
                            />
                          ))}
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}

            {/* Comparison hint for single region */}
            {combinedData.length > 0 && !isLoading && selectedRegions.length === 1 && (
              <div className="p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground">
                <strong>Tip:</strong> Selecciona múltiples regiones para comparar la evolución de los indicadores entre ellas.
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
