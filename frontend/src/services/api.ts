/**
 * Cliente API para el backend de población.
 */
import axios from 'axios'
import type {
  PopulationAgeResponse,
  UrbanRuralResponse,
  GrowthResponse,
  PyramidResponse,
  CompareResponse,
  DemographicIndicators,
} from '@/types/population'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para logging (desarrollo)
if (process.env.NODE_ENV === 'development') {
  api.interceptors.request.use((config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    return config
  })
}

export const populationApi = {
  /**
   * Obtiene población por edad.
   */
  getPopulationByAge: async (params: {
    territorio_id: string[]
    anio?: number
    anio_from?: number
    anio_to?: number
    area?: string
    sexo?: string
    quinquenios?: boolean
  }): Promise<PopulationAgeResponse[]> => {
    const response = await api.get('/population/age', { params })
    return response.data
  },

  /**
   * Obtiene distribución urbano-rural.
   */
  getUrbanRural: async (params: {
    territorio_id: string
    anio: number
  }): Promise<UrbanRuralResponse> => {
    const response = await api.get('/population/urban_rural', { params })
    return response.data
  },

  /**
   * Obtiene crecimiento poblacional.
   */
  getGrowth: async (params: {
    territorio_id: string
    periodo: 'hasta_2019' | 'desde_2020'
    area?: string
  }): Promise<GrowthResponse> => {
    const response = await api.get('/population/growth', { params })
    return response.data
  },

  /**
   * Obtiene datos para pirámide poblacional.
   */
  getPyramid: async (params: {
    territorio_id: string
    anio: number
    area?: string
    modo?: 'simple' | 'quinquenal'
  }): Promise<PyramidResponse> => {
    const response = await api.get('/population/pyramid', { params })
    return response.data
  },

  /**
   * Compara territorios.
   */
  compareTerritorios: async (data: {
    territorios: string[]
    anio: number
    area?: string
    metricas?: string[]
  }): Promise<CompareResponse> => {
    const response = await api.post('/population/compare', data)
    return response.data
  },

  /**
   * Obtiene indicadores demográficos.
   */
  getIndicators: async (params: {
    territorio_id: string
    anio: number
    area?: string
  }): Promise<DemographicIndicators> => {
    const response = await api.get('/population/indicators', { params })
    return response.data
  },
}

export default api
