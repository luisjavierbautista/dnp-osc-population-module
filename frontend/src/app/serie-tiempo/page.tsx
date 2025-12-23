'use client'

import { useState, useCallback } from 'react'
import { useQueries } from '@tanstack/react-query'
import dynamic from 'next/dynamic'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loading } from '@/components/ui/Loading'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { populationApi } from '@/services/api'
import { formatNumber } from '@/lib/utils'
import { DataSourceCard } from '@/components/ui/DataSourceCard'
import type { AreaGeografica } from '@/types/population'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

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

interface Territory {
  territorio_id: string
  nombre: string
  nivel: string
  dp?: string
  mpio?: string
}

export default function SerieTiempoPage() {
  const [territorioIds, setTerritorioIds] = useState<string[]>(['11']) // Bogotá by default
  const [territoriesMap, setTerritoriesMap] = useState<Record<string, Territory>>({})
  const [area, setArea] = useState<AreaGeografica>('Total')
  const [anioFrom, setAnioFrom] = useState(2018)
  const [anioTo, setAnioTo] = useState(2050)

  // Callback to store territory data when loaded
  const handleTerritoriesLoaded = useCallback((territories: Territory[]) => {
    const map: Record<string, Territory> = {}
    territories.forEach(t => {
      map[t.territorio_id] = t
    })
    setTerritoriesMap(prev => ({ ...prev, ...map }))
  }, [])

  // Fetch data for all selected territories in parallel
  const queries = useQueries({
    queries: territorioIds.map(territorioId => ({
      queryKey: ['time-series', territorioId, anioFrom, anioTo, area],
      queryFn: () => populationApi.getTimeSeries({
        territorio_id: territorioId,
        anio_from: anioFrom,
        anio_to: anioTo,
        area,
      }),
      enabled: territorioIds.length > 0,
    })),
  })

  const isLoading = queries.some(q => q.isLoading)
  const hasError = queries.some(q => q.error)

  // Combine data from all territories into a single dataset for the chart
  const combinedData = (() => {
    if (queries.length === 0 || queries.some(q => !q.data)) return []

    // Get all years from the first territory's data
    const firstData = queries[0].data
    if (!firstData?.series) return []

    return firstData.series.map((item, idx) => {
      const row: any = { anio: item.anio }

      queries.forEach((query, qIdx) => {
        const territorioId = territorioIds[qIdx]
        const seriesItem = query.data?.series?.[idx]
        if (seriesItem) {
          row[`poblacion_${territorioId}`] = seriesItem.poblacion
          row[`tasa_${territorioId}`] = seriesItem.tasa_crecimiento
          row[`delta_${territorioId}`] = seriesItem.delta
        }
      })

      return row
    })
  })()

  // Get territory names for the legend
  const getTerritoryName = (id: string) => {
    const territory = territoriesMap[id]
    if (territory) {
      // Format: "Nombre (Código)" or just "Nombre" for departments
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
          <h1 className="text-4xl font-bold mb-2">Serie de Tiempo Poblacional</h1>
          <p className="text-muted-foreground">
            Evolución de la población total con tasas de crecimiento y cambio absoluto
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
                maxSelections={8}
              />

              <AreaSelect value={area} onChange={setArea} />

              <div>
                <label className="block text-sm font-medium mb-2">Período</label>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1">Desde</label>
                    <select
                      value={anioFrom}
                      onChange={(e) => setAnioFrom(Number(e.target.value))}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    >
                      {Array.from({ length: 33 }, (_, i) => 2018 + i).map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-muted-foreground mb-1">Hasta</label>
                    <select
                      value={anioTo}
                      onChange={(e) => setAnioTo(Number(e.target.value))}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    >
                      {Array.from({ length: 33 }, (_, i) => 2018 + i).map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <DataSourceCard compact className="mt-4" />
            </CardContent>
          </Card>

          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {isLoading && <Loading size="lg" text="Cargando datos..." />}

            {hasError && (
              <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                Error al cargar los datos. Por favor intenta de nuevo.
              </div>
            )}

            {territorioIds.length === 0 && !isLoading && (
              <div className="p-8 text-center text-muted-foreground border rounded-lg">
                Selecciona al menos un territorio para ver las series de tiempo
              </div>
            )}

            {/* Population Time Series Chart */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>Evolución de la Población Total ({anioFrom}-{anioTo})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[400px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis
                          tickFormatter={(value) => {
                            if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
                            if (value >= 1000) return `${(value / 1000).toFixed(0)}K`
                            return value.toString()
                          }}
                        />
                        <Tooltip
                          formatter={(value: number) => formatNumber(value)}
                          labelFormatter={(label) => `Año ${label}`}
                        />
                        <Legend />
                        {territorioIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={`poblacion_${id}`}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            name={getTerritoryName(id)}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Growth Rate Chart */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>Tasa de Crecimiento Anual (%)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData.filter((_, i) => i > 0)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis
                          tickFormatter={(value) => `${value?.toFixed(2) || 0}%`}
                        />
                        <Tooltip
                          formatter={(value: number) => value ? `${value.toFixed(4)}%` : 'N/A'}
                          labelFormatter={(label) => `Año ${label}`}
                        />
                        <Legend />
                        {territorioIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={`tasa_${id}`}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            name={getTerritoryName(id)}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    Variación porcentual de la población respecto al año anterior.
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Delta (Absolute Change) Chart */}
            {combinedData.length > 0 && !isLoading && (
              <Card>
                <CardHeader>
                  <CardTitle>Cambio Absoluto de Población (Delta)</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={combinedData.filter((_, i) => i > 0)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="anio" />
                        <YAxis
                          tickFormatter={(value) => formatNumber(value)}
                        />
                        <Tooltip
                          formatter={(value: number) => value ? formatNumber(value) : 'N/A'}
                          labelFormatter={(label) => `Año ${label}`}
                        />
                        <Legend />
                        {territorioIds.map((id, idx) => (
                          <Line
                            key={id}
                            type="monotone"
                            dataKey={`delta_${id}`}
                            stroke={COLORS[idx % COLORS.length]}
                            strokeWidth={2}
                            name={getTerritoryName(id)}
                            dot={{ fill: COLORS[idx % COLORS.length], r: 2 }}
                            connectNulls
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-sm text-muted-foreground mt-4">
                    Diferencia absoluta en número de habitantes respecto al año anterior.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
