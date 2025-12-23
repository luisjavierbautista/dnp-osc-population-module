/**
 * Tipos TypeScript para el módulo de población.
 */

export type AreaGeografica = 'Total' | 'Cabecera Municipal' | 'Centros Poblados y Rural Disperso'
export type Sexo = 'H' | 'M' | 'T'
export type NivelTerritorial = 'departamental' | 'municipal'

export interface Territorio {
  territorioId: string
  nivel: NivelTerritorial
  dp: string
  mpio?: string
  nombre: string
  categoria?: string
  transicionDemografica?: string
}

export interface EdadBin {
  edad: number
  edadFin?: number
  poblacion: number
}

export interface PopulationAgeResponse {
  territorioId: string
  anio: number
  area: string
  sexo: string
  edadBins: EdadBin[]
}

export interface UrbanRuralResponse {
  territorioId: string
  anio: number
  urbana: number
  rural: number
  pctUrbana: number
  pctRural: number
}

export interface GrowthResponse {
  territorioId: string
  periodo: string
  t0: number
  t1: number
  pT0: number
  pT1: number
  cagr: number
  variacionTotal?: number
}

export interface PyramidSeries {
  edad: number
  hombres: number
  mujeres: number
}

export interface PyramidResponse {
  territorioId: string
  anio: number
  area: string
  modo: 'simple' | 'quinquenal'
  series: PyramidSeries[]
}

export interface DemographicIndicators {
  territorio_id: string
  anio: number
  area: string
  poblacion_total: number
  poblacion_infantil: number
  poblacion_activa: number
  poblacion_mayor: number
  indice_dependencia: number | null
  indice_envejecimiento: number | null
}

export interface CompareMetrics {
  territorioId: string
  nombre: string
  poblacionTotal?: number
  pctUrbana?: number
  envejecimiento?: number
  dependencia?: number
  cagr?: number
}

export interface CompareResponse {
  anio: number
  area: string
  territorios: CompareMetrics[]
}

export interface PopulationFilters {
  territorioId: string[]
  anio: number
  area: AreaGeografica
  sexo: Sexo
}
