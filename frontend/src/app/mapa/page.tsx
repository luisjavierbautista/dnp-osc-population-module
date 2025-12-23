'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { useQuery } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { YearSlider } from '@/components/filters/YearSlider'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { Loading } from '@/components/ui/Loading'
import { populationApi } from '@/services/api'
import { DataSourceCard } from '@/components/ui/DataSourceCard'
import type { AreaGeografica } from '@/types/population'

// Import PopulationMap dynamically to avoid SSR issues with Leaflet
const PopulationMap = dynamic(
  () => import('@/components/map/PopulationMap').then(mod => mod.PopulationMap),
  { ssr: false, loading: () => <div className="h-[600px] animate-pulse bg-gray-100 rounded-lg" /> }
)

type TerritoryLevel = 'DEPARTAMENTAL' | 'MUNICIPAL'

export default function MapaPage() {
  const [nivel, setNivel] = useState<TerritoryLevel>('DEPARTAMENTAL')
  const [anio, setAnio] = useState(2025)
  const [area, setArea] = useState<AreaGeografica>('Total')
  const [variable, setVariable] = useState<string>('poblacion_total')

  const variables = [
    { value: 'poblacion_total', label: 'Población Total' },
    { value: 'pct_urbana', label: '% Población Urbana' },
    { value: 'pct_rural', label: '% Población Rural' },
    { value: 'envejecimiento', label: 'Índice de Envejecimiento' },
    { value: 'dependencia', label: 'Índice de Dependencia' },
  ]

  // Fetch GeoJSON data
  const { data: geojsonData, isLoading } = useQuery({
    queryKey: ['map-geojson', nivel, anio, area, variable],
    queryFn: () => populationApi.getMapGeoJSON({
      nivel,
      anio,
      area,
      variable,
    }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Mapa Categorizado</h1>
          <p className="text-muted-foreground">
            Visualización territorial de variables demográficas
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filtros */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Nivel territorial */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Nivel Territorial
                </label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setNivel('DEPARTAMENTAL')}
                    className={`flex-1 px-3 py-2 text-sm rounded-md transition-colors ${
                      nivel === 'DEPARTAMENTAL'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted hover:bg-muted/80'
                    }`}
                  >
                    Departamentos
                  </button>
                  <button
                    onClick={() => setNivel('MUNICIPAL')}
                    className={`flex-1 px-3 py-2 text-sm rounded-md transition-colors ${
                      nivel === 'MUNICIPAL'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted hover:bg-muted/80'
                    }`}
                  >
                    Municipios
                  </button>
                </div>
              </div>

              <YearSlider value={anio} onChange={setAnio} />

              <AreaSelect value={area} onChange={setArea} />

              <div>
                <label htmlFor="variable-select" className="block text-sm font-medium mb-2">
                  Variable
                </label>
                <select
                  id="variable-select"
                  value={variable}
                  onChange={(e) => setVariable(e.target.value)}
                  className="w-full px-3 py-2 border border-input bg-background rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  {variables.map((v) => (
                    <option key={v.value} value={v.value}>
                      {v.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-4 border-t">
                <h4 className="text-sm font-medium mb-2">Información</h4>
                <p className="text-xs text-muted-foreground">
                  Los datos geográficos provienen del servidor GIS del DNP.
                  Haz clic en un territorio para ver más detalles.
                </p>
              </div>

              <DataSourceCard compact className="mt-4" />
            </CardContent>
          </Card>

          {/* Mapa */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>
                {variables.find(v => v.value === variable)?.label} - {anio}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="h-[600px] flex items-center justify-center">
                  <Loading size="lg" text="Cargando mapa..." />
                </div>
              ) : (
                <div className="h-[600px]">
                  <PopulationMap
                    geojsonData={geojsonData}
                    variable={variable}
                  />
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
