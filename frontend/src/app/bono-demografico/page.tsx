'use client'

import { useState, useCallback } from 'react'
import { useQueries } from '@tanstack/react-query'
import dynamic from 'next/dynamic'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loading } from '@/components/ui/Loading'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { populationApi } from '@/services/api'
import { DataSourceCard } from '@/components/ui/DataSourceCard'
import type { AreaGeografica } from '@/types/population'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// Import MultiTerritorySelect dynamically to avoid hydration errors
const MultiTerritorySelect = dynamic(
  () => import('@/components/filters/MultiTerritorySelect').then(mod => mod.MultiTerritorySelect),
  { ssr: false, loading: () => <div className="h-64 animate-pulse bg-gray-100 rounded" /> }
)

// Colors for different territory lines
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

// Years for historical data
const YEARS = [2018, 2020, 2025, 2030, 2035, 2040, 2045, 2050]

interface Territory {
  territorio_id: string
  nombre: string
  nivel: string
  dp?: string
  mpio?: string
}

export default function BonoDemograficoPage() {
  const [territorioIds, setTerritorioIds] = useState<string[]>(['11']) // Bogotá by default
  const [territoriesMap, setTerritoriesMap] = useState<Record<string, Territory>>({})
  const [area, setArea] = useState<AreaGeografica>('Total')

  // Callback to store territory data when loaded
  const handleTerritoriesLoaded = useCallback((territories: Territory[]) => {
    const map: Record<string, Territory> = {}
    territories.forEach(t => {
      map[t.territorio_id] = t
    })
    setTerritoriesMap(prev => ({ ...prev, ...map }))
  }, [])

  // Fetch historical data for all selected territories
  const queries = useQueries({
    queries: territorioIds.map(territorioId => ({
      queryKey: ['indicators-historical', territorioId, area],
      queryFn: async () => {
        const results = await Promise.all(
          YEARS.map(year =>
            populationApi.getIndicators({
              territorio_id: territorioId,
              anio: year,
              area,
            })
          )
        )
        return {
          territorioId,
          data: results.map((data, idx) => ({
            anio: YEARS[idx],
            dependencia: data.indice_dependencia,
            envejecimiento: data.indice_envejecimiento,
            pctInfantil: (data.poblacion_infantil / data.poblacion_total) * 100,
            pctActiva: (data.poblacion_activa / data.poblacion_total) * 100,
            pctMayor: (data.poblacion_mayor / data.poblacion_total) * 100,
          }))
        }
      },
      enabled: territorioIds.length > 0,
    })),
  })

  const isLoading = queries.some(q => q.isLoading)
  const hasError = queries.some(q => q.error)

  // Combine data from all territories for charts
  const combinedData = (() => {
    if (queries.length === 0 || queries.some(q => !q.data)) return []

    return YEARS.map((year, yearIdx) => {
      const row: any = { anio: year }

      queries.forEach((query, qIdx) => {
        const territorioId = territorioIds[qIdx]
        const yearData = query.data?.data?.[yearIdx]
        if (yearData) {
          row[`dependencia_${territorioId}`] = yearData.dependencia
          row[`pctInfantil_${territorioId}`] = yearData.pctInfantil
          row[`pctActiva_${territorioId}`] = yearData.pctActiva
          row[`pctMayor_${territorioId}`] = yearData.pctMayor
        }
      })

      return row
    })
  })()

  // Get territory names for the legend
  const getTerritoryName = (id: string) => {
    const territory = territoriesMap[id]
    if (territory) {
      if (territory.nivel === 'DEPARTAMENTAL') {
        return territory.nombre
      }
      return `${territory.nombre} (${territory.dp})`
    }
    return `Territorio ${id}`
  }

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Bono Demogr&#225;fico</h1>
          <p className="text-muted-foreground">
            An&#225;lisis de la transici&#243;n demogr&#225;fica y ventana de oportunidad
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filtros */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <MultiTerritorySelect
                value={territorioIds}
                onChange={setTerritorioIds}
                onTerritoriesLoaded={handleTerritoriesLoaded}
                maxSelections={6}
              />

              <AreaSelect value={area} onChange={setArea} />

              <div className="pt-4 border-t">
                <h4 className="text-sm font-medium mb-2">Sobre el Bono Demogr&#225;fico</h4>
                <p className="text-xs text-muted-foreground">
                  El bono demogr&#225;fico es el per&#237;odo donde la poblaci&#243;n en edad de trabajar (15-64 a&#241;os)
                  es significativamente mayor que la poblaci&#243;n dependiente (menores de 15 y mayores de 64).
                </p>
              </div>

              <DataSourceCard compact className="mt-4" />
            </CardContent>
          </Card>

          {/* Charts */}
          <div className="lg:col-span-3 space-y-6">
            {isLoading && <Loading size="lg" text="Cargando datos..." />}

            {hasError && (
              <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                Error al cargar los datos. Por favor intenta de nuevo.
              </div>
            )}

            {territorioIds.length === 0 && !isLoading && (
              <div className="p-8 text-center text-muted-foreground border rounded-lg">
                Selecciona al menos un territorio para ver los indicadores
              </div>
            )}

            {/* Population Distribution by Age Groups */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>Poblaci&#243;n Activa (15-64 a&#241;os) por Territorio</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis
                          domain={[50, 80]}
                          tickFormatter={(value) => `${value}%`}
                        />
                        <Tooltip formatter={(value: number) => `${value?.toFixed(2) || 0}%`} />
                        <Legend />
                        {territorioIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={`pctActiva_${id}`}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            name={`${getTerritoryName(id)} - Activa`}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 3 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    El bono demogr&#225;fico ocurre cuando la poblaci&#243;n activa (15-64 a&#241;os) representa
                    el mayor porcentaje del total.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Dependency Index Comparison */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>&#205;ndice de Dependencia por Territorio (2018-2050)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis />
                        <Tooltip formatter={(value: number) => value?.toFixed(2) || 'N/A'} />
                        <Legend />
                        {territorioIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={`dependencia_${id}`}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            name={getTerritoryName(id)}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 3 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    Dependientes (0-14 y 65+) por cada 100 personas en edad productiva (15-64).
                    Valores menores indican una ventana de oportunidad demogr&#225;fica.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Age Groups Distribution - Only for single territory */}
            {combinedData.length > 0 && !isLoading && territorioIds.length === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle>Distribuci&#243;n por Grupos de Edad - {getTerritoryName(territorioIds[0])}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis
                          domain={[0, 100]}
                          tickFormatter={(value) => `${value}%`}
                        />
                        <Tooltip formatter={(value: number) => `${value?.toFixed(2) || 0}%`} />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey={`pctInfantil_${territorioIds[0]}`}
                          stroke="#f59e0b"
                          strokeWidth={2}
                          name="0-14 a&#241;os (Infantil)"
                          dot={{ fill: '#f59e0b' }}
                        />
                        <Line
                          type="monotone"
                          dataKey={`pctActiva_${territorioIds[0]}`}
                          stroke="#10b981"
                          strokeWidth={2}
                          name="15-64 a&#241;os (Activa)"
                          dot={{ fill: '#10b981' }}
                        />
                        <Line
                          type="monotone"
                          dataKey={`pctMayor_${territorioIds[0]}`}
                          stroke="#6366f1"
                          strokeWidth={2}
                          name="65+ a&#241;os (Mayor)"
                          dot={{ fill: '#6366f1' }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    Distribuci&#243;n de los tres grupos de edad como porcentaje del total.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Comparison hint for multiple territories */}
            {combinedData.length > 0 && !isLoading && territorioIds.length > 1 && (
              <div className="p-4 bg-muted/50 rounded-lg text-sm text-muted-foreground">
                <strong>Tip:</strong> Selecciona un solo territorio para ver la distribuci&#243;n detallada
                de los tres grupos de edad (0-14, 15-64, 65+).
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
