'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import dynamic from 'next/dynamic'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Loading } from '@/components/ui/Loading'
import { YearSlider } from '@/components/filters/YearSlider'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { populationApi } from '@/services/api'
import { DataSourceCard } from '@/components/ui/DataSourceCard'
import type { AreaGeografica } from '@/types/population'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// Import TerritorySelect dynamically with SSR disabled to avoid hydration errors
const TerritorySelect = dynamic(
  () => import('@/components/filters/TerritorySelect').then(mod => mod.TerritorySelect),
  { ssr: false, loading: () => <div className="h-48 animate-pulse bg-gray-100 rounded" /> }
)

// Mini Pyramid Component for comparison view
function MiniPyramid({
  territorioId,
  anio,
  area,
  modo,
  displayMode,
  title
}: {
  territorioId: string
  anio: number
  area: AreaGeografica
  modo: 'simple' | 'quinquenal' | 'grupos'
  displayMode: 'absolute' | 'percentage'
  title: string
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['pyramid', territorioId, anio, area, modo],
    queryFn: () => populationApi.getPyramid({
      territorio_id: territorioId,
      anio,
      area,
      modo: modo === 'grupos' ? 'simple' : modo,
    }),
  })

  const chartData = (() => {
    if (!data?.series) return []

    const totalPopulation = data.series.reduce(
      (sum, item) => sum + parseFloat(String(item.hombres)) + parseFloat(String(item.mujeres)),
      0
    )

    let processedData: any[] = []

    if (modo === 'grupos') {
      const groups = [
        { label: '0-14', min: 0, max: 14 },
        { label: '15-64', min: 15, max: 64 },
        { label: '65+', min: 65, max: 150 }
      ]
      processedData = groups.map(group => {
        const filtered = data.series.filter(
          item => item.edad >= group.min && item.edad <= group.max
        )
        const hombres = filtered.reduce((sum, item) => sum + parseFloat(String(item.hombres)), 0)
        const mujeres = filtered.reduce((sum, item) => sum + parseFloat(String(item.mujeres)), 0)
        return { edad: group.label, Hombres: -hombres, Mujeres: mujeres }
      })
    } else {
      processedData = data.series.map((item) => ({
        edad: modo === 'quinquenal' ? `${item.edad}-${item.edad + 4}` : item.edad,
        Hombres: -parseFloat(String(item.hombres)),
        Mujeres: parseFloat(String(item.mujeres)),
      }))
    }

    if (displayMode === 'percentage' && totalPopulation > 0) {
      return processedData.map(item => ({
        edad: item.edad,
        Hombres: -(Math.abs(item.Hombres) / totalPopulation) * 100,
        Mujeres: (item.Mujeres / totalPopulation) * 100,
      }))
    }

    return processedData
  })()

  if (isLoading) {
    return (
      <div className="h-[300px] flex items-center justify-center">
        <Loading size="sm" text="Cargando..." />
      </div>
    )
  }

  if (!data) {
    return (
      <div className="h-[300px] flex items-center justify-center text-muted-foreground">
        Sin datos disponibles
      </div>
    )
  }

  const maxValue = Math.max(...chartData.map(d => Math.max(Math.abs(d.Hombres), d.Mujeres)))
  const axisMax = displayMode === 'percentage'
    ? Math.ceil(maxValue)
    : Math.ceil(maxValue / 10000) * 10000

  return (
    <div className="border rounded-lg p-3">
      <h4 className="text-sm font-medium mb-2 text-center">{title}</h4>
      <div className="h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
            barCategoryGap={1}
            barGap={-5}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              domain={[-axisMax, axisMax]}
              tickFormatter={(value) => {
                const absValue = Math.abs(value)
                if (displayMode === 'percentage') return `${absValue.toFixed(0)}%`
                return absValue >= 1000000 ? `${(absValue/1000000).toFixed(1)}M` : `${(absValue/1000).toFixed(0)}K`
              }}
              tick={{ fontSize: 9 }}
            />
            <YAxis
              type="category"
              dataKey="edad"
              width={35}
              tick={{ fontSize: 8 }}
              reversed
            />
            <Tooltip
              formatter={(value: number) => {
                const absValue = Math.abs(value)
                return displayMode === 'percentage' ? `${absValue.toFixed(2)}%` : absValue.toLocaleString('es-CO')
              }}
            />
            <Bar dataKey="Hombres" fill="#3b82f6" name="Hombres" />
            <Bar dataKey="Mujeres" fill="#ec4899" name="Mujeres" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function PiramidePage() {
  const [activeTab, setActiveTab] = useState<'single' | 'compare'>('single')
  const [territorioId, setTerritorioId] = useState('11') // Bogotá
  const [anio, setAnio] = useState(2025)
  const [area, setArea] = useState<AreaGeografica>('Total')
  const [modo, setModo] = useState<'simple' | 'quinquenal' | 'grupos'>('quinquenal')
  const [displayMode, setDisplayMode] = useState<'absolute' | 'percentage'>('absolute')

  // Comparison state
  const [compareMode, setCompareMode] = useState<'territories' | 'years'>('territories')
  const [compareTerritorios, setCompareTerritorios] = useState<string[]>(['11', '05'])
  const [compareAnios, setCompareAnios] = useState<number[]>([2025, 2035])

  const { data, isLoading, error } = useQuery({
    queryKey: ['pyramid', territorioId, anio, area, modo],
    queryFn: () => populationApi.getPyramid({
      territorio_id: territorioId,
      anio,
      area,
      modo: modo === 'grupos' ? 'simple' : modo, // Use simple mode for grupos, aggregate on frontend
    }),
  })

  // Fetch urban/rural distribution
  const { data: urbanRuralData } = useQuery({
    queryKey: ['urban-rural', territorioId, anio],
    queryFn: () => populationApi.getUrbanRural({
      territorio_id: territorioId,
      anio,
    }),
    enabled: !!territorioId, // Fetch for any selected territory
  })

  // Preparar datos para la gráfica
  const chartData = (() => {
    if (!data?.series) return []

    // Calculate total population for percentage mode
    const totalPopulation = data.series.reduce(
      (sum, item) => sum + Number(item.hombres) + Number(item.mujeres),
      0
    )

    let processedData: any[] = []

    // For standard groups mode, aggregate data
    if (modo === 'grupos') {
      const groups = [
        { label: '0-14 (Juvenil)', min: 0, max: 14 },
        { label: '15-64 (Activa)', min: 15, max: 64 },
        { label: '65+ (Mayor)', min: 65, max: 150 }
      ]

      processedData = groups.map(group => {
        const filtered = data.series.filter(
          item => item.edad >= group.min && item.edad <= group.max
        )
        const hombres = filtered.reduce((sum, item) => sum + Number(item.hombres), 0)
        const mujeres = filtered.reduce((sum, item) => sum + Number(item.mujeres), 0)

        return {
          edad: group.label,
          Hombres: -hombres,
          Mujeres: mujeres,
        }
      })
    } else {
      // For simple and quinquenal modes
      processedData = data.series.map((item) => ({
        edad: modo === 'quinquenal' ? `${item.edad}-${item.edad + 4}` : item.edad,
        Hombres: -Number(item.hombres),
        Mujeres: Number(item.mujeres),
      }))
    }

    // Convert to percentages if needed (always percentage of total population)
    if (displayMode === 'percentage' && totalPopulation > 0) {
      return processedData.map(item => ({
        edad: item.edad,
        // Hombres is already negative, so use abs value, calculate %, then negate again
        Hombres: -(Math.abs(item.Hombres) / totalPopulation) * 100,
        Mujeres: (item.Mujeres / totalPopulation) * 100,
      }))
    }

    return processedData
  })()

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Pirámide Poblacional</h1>
          <p className="text-muted-foreground">
            Visualiza la estructura de población por edad y sexo
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'single'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary/80'
            }`}
          >
            Pirámide Individual
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === 'compare'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary hover:bg-secondary/80'
            }`}
          >
            Comparar Pirámides
          </button>
        </div>

        {activeTab === 'single' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filtros */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <TerritorySelect
                value={territorioId}
                onChange={setTerritorioId}
              />

              <YearSlider value={anio} onChange={setAnio} />

              <AreaSelect value={area} onChange={setArea} />

              <div>
                <label className="block text-sm font-medium mb-2">Agrupación de Edad</label>
                <div className="space-y-2">
                  <button
                    onClick={() => setModo('simple')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left ${
                      modo === 'simple'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Años simples</div>
                    <div className="text-xs opacity-80">0, 1, 2, ..., 100</div>
                  </button>
                  <button
                    onClick={() => setModo('quinquenal')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left ${
                      modo === 'quinquenal'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Quinquenal</div>
                    <div className="text-xs opacity-80">0-4, 5-9, 10-14, ...</div>
                  </button>
                  <button
                    onClick={() => setModo('grupos')}
                    className={`w-full px-3 py-2 rounded-md text-sm text-left ${
                      modo === 'grupos'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    <div className="font-medium">Grupos estándar</div>
                    <div className="text-xs opacity-80">0-14, 15-64, 65+</div>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Mostrar como</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setDisplayMode('absolute')}
                    className={`flex-1 px-3 py-2 rounded-md text-sm ${
                      displayMode === 'absolute'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    Números
                  </button>
                  <button
                    onClick={() => setDisplayMode('percentage')}
                    className={`flex-1 px-3 py-2 rounded-md text-sm ${
                      displayMode === 'percentage'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary hover:bg-secondary/80'
                    }`}
                  >
                    Porcentaje
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {displayMode === 'percentage'
                    ? 'Porcentaje del total de población'
                    : 'Población absoluta'}
                </p>
              </div>

              <DataSourceCard compact className="mt-4" />
            </CardContent>
          </Card>

          {/* Gráfica */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>
                Pirámide Poblacional - {anio}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading && <Loading size="lg" text="Cargando datos..." />}

              {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                  Error al cargar los datos. Por favor intenta de nuevo.
                </div>
              )}

              {data && (() => {
                // Calculate max value for symmetric axis
                const maxValue = Math.max(
                  ...chartData.map(d => Math.max(Math.abs(d.Hombres), d.Mujeres))
                )

                // For percentage mode, use calculated max; for absolute, round to nearest 10k
                let axisMax
                if (displayMode === 'percentage') {
                  axisMax = Math.ceil(maxValue)
                } else {
                  axisMax = Math.ceil(maxValue / 10000) * 10000
                }

                // Calculate dynamic barGap based on available height and number of categories
                // Use a continuous formula: barGap = -(chartHeight / categories) * (0.772 / (1 + 0.012 * categories))
                const chartHeight = 600
                const categories = chartData.length
                const approximateBarHeight = chartHeight / categories
                // Continuous multiplier that decreases as categories increase
                const multiplier = 0.772 / (1 + 0.012 * categories)
                const dynamicBarGap = -Math.round(approximateBarHeight * multiplier)

                // Calculate total population from chart data
                const totalPopulation = chartData.reduce(
                  (sum, d) => sum + Math.abs(d.Hombres) + d.Mujeres, 0
                )

                return (
                  <>
                    <div className="h-[600px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={chartData}
                          layout="vertical"
                          margin={{ top: 40, right: 30, left: 30, bottom: 20 }}
                          barCategoryGap={1}
                          barGap={dynamicBarGap}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis
                            type="number"
                            domain={[-axisMax, axisMax]}
                            ticks={[-axisMax, 0, axisMax]}
                            tickFormatter={(value) => {
                              const absValue = Math.abs(value)
                              if (displayMode === 'percentage') {
                                return `${absValue.toFixed(1)}%`
                              }
                              return absValue.toLocaleString('es-CO')
                            }}
                            tick={{ fontSize: 12 }}
                            height={50}
                          />
                          <YAxis
                            type="category"
                            dataKey="edad"
                            width={70}
                            tick={{ fontSize: 11 }}
                            reversed  // Invert axis: youngest (0) at bottom, oldest (100) at top
                          />
                          <Tooltip
                            formatter={(value: number) => {
                              const absValue = Math.abs(value)
                              if (displayMode === 'percentage') {
                                return `${absValue.toFixed(2)}%`
                              }
                              return absValue.toLocaleString('es-CO')
                            }}
                            labelStyle={{ fontWeight: 'bold' }}
                          />
                          <Legend
                            verticalAlign="top"
                            wrapperStyle={{ paddingBottom: '20px' }}
                          />
                          <Bar
                            dataKey="Hombres"
                            fill="#3b82f6"
                            name="Hombres"
                          />
                          <Bar
                            dataKey="Mujeres"
                            fill="#ec4899"
                            name="Mujeres"
                          />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {/* Population Summary */}
                    <div className="mt-6 pt-4 border-t">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                        <div>
                          <p className="text-sm text-muted-foreground">Población Total</p>
                          <p className="text-xl font-bold">{totalPopulation.toLocaleString('es-CO')}</p>
                        </div>
                        {urbanRuralData && (
                          <>
                            <div>
                              <p className="text-sm text-muted-foreground">% Urbano</p>
                              <p className="text-xl font-bold text-blue-600">
                                {(urbanRuralData.pctUrbana * 100).toFixed(1)}%
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-muted-foreground">% Rural</p>
                              <p className="text-xl font-bold text-green-600">
                                {(urbanRuralData.pctRural * 100).toFixed(1)}%
                              </p>
                            </div>
                          </>
                        )}
                        {!urbanRuralData && (
                          <div className="col-span-2">
                            <p className="text-xs text-muted-foreground italic">
                              Cargando distribución urbano/rural...
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )
              })()}
            </CardContent>
          </Card>
        </div>
        )}

        {/* Comparison Tab */}
        {activeTab === 'compare' && (
          <div className="space-y-6">
            {/* Comparison Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Configuración de Comparación</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Compare Mode */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Comparar por</label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setCompareMode('territories')}
                        className={`flex-1 px-3 py-2 rounded-md text-sm ${
                          compareMode === 'territories'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary hover:bg-secondary/80'
                        }`}
                      >
                        Territorios
                      </button>
                      <button
                        onClick={() => setCompareMode('years')}
                        className={`flex-1 px-3 py-2 rounded-md text-sm ${
                          compareMode === 'years'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary hover:bg-secondary/80'
                        }`}
                      >
                        Años
                      </button>
                    </div>
                  </div>

                  {/* Display Mode */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Mostrar como</label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setDisplayMode('absolute')}
                        className={`flex-1 px-3 py-2 rounded-md text-sm ${
                          displayMode === 'absolute'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary hover:bg-secondary/80'
                        }`}
                      >
                        Números
                      </button>
                      <button
                        onClick={() => setDisplayMode('percentage')}
                        className={`flex-1 px-3 py-2 rounded-md text-sm ${
                          displayMode === 'percentage'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-secondary hover:bg-secondary/80'
                        }`}
                      >
                        Porcentaje
                      </button>
                    </div>
                  </div>

                  {/* Age Grouping */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Agrupación</label>
                    <select
                      value={modo}
                      onChange={(e) => setModo(e.target.value as 'simple' | 'quinquenal' | 'grupos')}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    >
                      <option value="quinquenal">Quinquenal</option>
                      <option value="grupos">Grupos estándar</option>
                      <option value="simple">Años simples</option>
                    </select>
                  </div>

                  {/* Area */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Área</label>
                    <select
                      value={area}
                      onChange={(e) => setArea(e.target.value as AreaGeografica)}
                      className="w-full px-3 py-2 border rounded-md text-sm"
                    >
                      <option value="Total">Total</option>
                      <option value="Cabecera Municipal">Cabecera Municipal</option>
                      <option value="Centros Poblados y Rural Disperso">Rural</option>
                    </select>
                  </div>
                </div>

                {/* Comparison Selections */}
                <div className="pt-4 border-t">
                  {compareMode === 'territories' ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium">Año fijo:</label>
                        <select
                          value={anio}
                          onChange={(e) => setAnio(Number(e.target.value))}
                          className="px-3 py-1 border rounded-md text-sm"
                        >
                          {Array.from({ length: 33 }, (_, i) => 2018 + i).map(y => (
                            <option key={y} value={y}>{y}</option>
                          ))}
                        </select>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[0, 1, 2, 3].map(idx => (
                          <div key={idx}>
                            <label className="block text-xs text-muted-foreground mb-1">
                              Territorio {idx + 1}
                            </label>
                            <TerritorySelect
                              value={compareTerritorios[idx] || ''}
                              onChange={(val) => {
                                const newTerrs = [...compareTerritorios]
                                newTerrs[idx] = val
                                setCompareTerritorios(newTerrs.filter(t => t))
                              }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <label className="text-sm font-medium">Territorio fijo:</label>
                        <div className="w-64">
                          <TerritorySelect
                            value={territorioId}
                            onChange={setTerritorioId}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[0, 1, 2, 3].map(idx => (
                          <div key={idx}>
                            <label className="block text-xs text-muted-foreground mb-1">
                              Año {idx + 1}
                            </label>
                            <select
                              value={compareAnios[idx] || ''}
                              onChange={(e) => {
                                const newAnios = [...compareAnios]
                                newAnios[idx] = Number(e.target.value)
                                setCompareAnios(newAnios.filter(a => a))
                              }}
                              className="w-full px-3 py-2 border rounded-md text-sm"
                            >
                              <option value="">Seleccionar...</option>
                              {Array.from({ length: 33 }, (_, i) => 2018 + i).map(y => (
                                <option key={y} value={y}>{y}</option>
                              ))}
                            </select>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Comparison Grid */}
            <Card>
              <CardHeader>
                <CardTitle>
                  Comparación de Pirámides - {compareMode === 'territories' ? `Año ${anio}` : 'Múltiples Años'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {compareMode === 'territories' ? (
                    compareTerritorios.slice(0, 4).map((terrId, idx) => (
                      <MiniPyramid
                        key={`${terrId}-${anio}-${idx}`}
                        territorioId={terrId}
                        anio={anio}
                        area={area}
                        modo={modo}
                        displayMode={displayMode}
                        title={`Territorio ${terrId} - ${anio}`}
                      />
                    ))
                  ) : (
                    compareAnios.slice(0, 4).map((compAnio, idx) => (
                      <MiniPyramid
                        key={`${territorioId}-${compAnio}-${idx}`}
                        territorioId={territorioId}
                        anio={compAnio}
                        area={area}
                        modo={modo}
                        displayMode={displayMode}
                        title={`Territorio ${territorioId} - ${compAnio}`}
                      />
                    ))
                  )}
                </div>
                {((compareMode === 'territories' && compareTerritorios.length < 2) ||
                  (compareMode === 'years' && compareAnios.length < 2)) && (
                  <p className="text-center text-muted-foreground mt-4">
                    Selecciona al menos 2 {compareMode === 'territories' ? 'territorios' : 'años'} para comparar
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </MainLayout>
  )
}
