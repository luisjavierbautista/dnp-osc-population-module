'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MainLayout } from '@/components/layout/MainLayout'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Loading } from '@/components/ui/Loading'
import { YearSlider } from '@/components/filters/YearSlider'
import { AreaSelect } from '@/components/filters/AreaSelect'
import { populationApi } from '@/services/api'
import { formatNumber, formatPercentage, formatDecimal } from '@/lib/utils'
import type { AreaGeografica } from '@/types/population'

const TERRITORIOS_DISPONIBLES = [
  { id: '05001', nombre: 'Medellín' },
  { id: '11001', nombre: 'Bogotá' },
  { id: '76001', nombre: 'Cali' },
  { id: '08001', nombre: 'Barranquilla' },
  { id: '13001', nombre: 'Cartagena' },
  { id: '05', nombre: 'Antioquia (Depto)' },
  { id: '11', nombre: 'Cundinamarca (Depto)' },
  { id: '76', nombre: 'Valle del Cauca (Depto)' },
]

export default function ComparadorPage() {
  const [territoriosSeleccionados, setTerritoriosSeleccionados] = useState<string[]>([
    '05001',
    '11001',
  ])
  const [anio, setAnio] = useState(2025)
  const [area, setArea] = useState<AreaGeografica>('Total')

  const { data, isLoading, error } = useQuery({
    queryKey: ['compare', territoriosSeleccionados, anio, area],
    queryFn: () =>
      populationApi.compareTerritorios({
        territorios: territoriosSeleccionados,
        anio,
        area,
        metricas: ['poblacion_total', 'pct_urbana', 'envejecimiento', 'dependencia', 'cagr'],
      }),
    enabled: territoriosSeleccionados.length >= 2,
  })

  const toggleTerritorio = (id: string) => {
    if (territoriosSeleccionados.includes(id)) {
      setTerritoriosSeleccionados(territoriosSeleccionados.filter((t) => t !== id))
    } else {
      if (territoriosSeleccionados.length < 10) {
        setTerritoriosSeleccionados([...territoriosSeleccionados, id])
      }
    }
  }

  return (
    <MainLayout>
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Comparador de Territorios</h1>
          <p className="text-muted-foreground">
            Compara indicadores demográficos entre diferentes territorios
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filtros */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="text-lg">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <YearSlider value={anio} onChange={setAnio} />
              <AreaSelect value={area} onChange={setArea} />

              <div>
                <label className="block text-sm font-medium mb-2">
                  Territorios ({territoriosSeleccionados.length}/10)
                </label>
                <div className="space-y-2">
                  {TERRITORIOS_DISPONIBLES.map((territorio) => (
                    <label
                      key={territorio.id}
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={territoriosSeleccionados.includes(territorio.id)}
                        onChange={() => toggleTerritorio(territorio.id)}
                        className="rounded"
                      />
                      <span className="text-sm">{territorio.nombre}</span>
                    </label>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tabla de comparación */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Comparación - {anio}</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading && <Loading size="lg" text="Cargando datos..." />}

              {error && (
                <div className="p-4 bg-destructive/10 text-destructive rounded-md">
                  Error al cargar los datos. Por favor intenta de nuevo.
                </div>
              )}

              {territoriosSeleccionados.length < 2 && !isLoading && (
                <div className="p-8 text-center text-muted-foreground">
                  Selecciona al menos 2 territorios para comparar
                </div>
              )}

              {data && territoriosSeleccionados.length >= 2 && (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-semibold">Territorio</th>
                        <th className="text-right py-3 px-4 font-semibold">
                          Población Total
                        </th>
                        <th className="text-right py-3 px-4 font-semibold">
                          % Urbana
                        </th>
                        <th className="text-right py-3 px-4 font-semibold">
                          Envejecimiento
                        </th>
                        <th className="text-right py-3 px-4 font-semibold">
                          Dependencia
                        </th>
                        <th className="text-right py-3 px-4 font-semibold">
                          CAGR
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.territorios.map((territorio, idx) => (
                        <tr
                          key={territorio.territorioId}
                          className={idx % 2 === 0 ? 'bg-muted/50' : ''}
                        >
                          <td className="py-3 px-4 font-medium">
                            {territorio.nombre}
                          </td>
                          <td className="text-right py-3 px-4">
                            {formatNumber(territorio.poblacionTotal)}
                          </td>
                          <td className="text-right py-3 px-4">
                            {formatPercentage(territorio.pctUrbana)}
                          </td>
                          <td className="text-right py-3 px-4">
                            {formatDecimal(territorio.envejecimiento)}
                          </td>
                          <td className="text-right py-3 px-4">
                            {formatDecimal(territorio.dependencia)}
                          </td>
                          <td className="text-right py-3 px-4">
                            <span
                              className={
                                (territorio.cagr || 0) > 0
                                  ? 'text-green-600'
                                  : 'text-red-600'
                              }
                            >
                              {formatPercentage(territorio.cagr, 2)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  )
}
