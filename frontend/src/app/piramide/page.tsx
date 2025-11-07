'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'
import { YearSlider } from '@/components/filters/YearSlider'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { populationApi } from '@/services/api'
import type { AreaGeografica } from '@/types/population'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function PiramidePage() {
  const [territorioId, setTerritorioId] = useState('05001') // Medellín
  const [anio, setAnio] = useState(2025)
  const [area, setArea] = useState<AreaGeografica>('Total')
  const [modo, setModo] = useState<'simple' | 'quinquenal'>('quinquenal')

  const { data, isLoading, error } = useQuery({
    queryKey: ['pyramid', territorioId, anio, area, modo],
    queryFn: () => populationApi.getPyramid({
      territorio_id: territorioId,
      anio,
      area,
      modo,
    }),
  })

  // Preparar datos para la gráfica
  const chartData = data?.series.map((item) => ({
    edad: modo === 'quinquenal' ? `${item.edad}-${item.edad + 4}` : item.edad,
    Hombres: -item.hombres, // Negativos para mostrar a la izquierda
    Mujeres: item.mujeres,
  })) || []

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Pirámide Poblacional</h1>
          <p className="text-muted-foreground">
            Visualiza la estructura de población por edad y sexo
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filtros */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Territorio
                </label>
                <select
                  value={territorioId}
                  onChange={(e) => setTerritorioId(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="05001">Medellín</option>
                  <option value="11001">Bogotá</option>
                  <option value="76001">Cali</option>
                  <option value="05">Antioquia</option>
                  <option value="11">Cundinamarca</option>
                </select>
              </div>

              <YearSlider value={anio} onChange={setAnio} />

              <AreaSelect value={area} onChange={setArea} />

              <div>
                <label className="block text-sm font-medium mb-2">Modo</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setModo('simple')}
                    className={`flex-1 px-3 py-2 rounded-md text-sm ${
                      modo === 'simple'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary'
                    }`}
                  >
                    Simple
                  </button>
                  <button
                    onClick={() => setModo('quinquenal')}
                    className={`flex-1 px-3 py-2 rounded-md text-sm ${
                      modo === 'quinquenal'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary'
                    }`}
                  >
                    Quinquenal
                  </button>
                </div>
              </div>
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

              {data && (
                <div className="h-[600px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      layout="vertical"
                      margin={{ top: 20, right: 30, left: 80, bottom: 20 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        type="number"
                        tickFormatter={(value) => Math.abs(value).toLocaleString()}
                      />
                      <YAxis type="category" dataKey="edad" />
                      <Tooltip
                        formatter={(value: number) => Math.abs(value).toLocaleString()}
                      />
                      <Legend />
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

                  <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-semibold">Total Hombres</div>
                      <div className="text-2xl text-blue-600">
                        {data.series
                          .reduce((acc, curr) => acc + curr.hombres, 0)
                          .toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <div className="font-semibold">Total Mujeres</div>
                      <div className="text-2xl text-pink-600">
                        {data.series
                          .reduce((acc, curr) => acc + curr.mujeres, 0)
                          .toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
