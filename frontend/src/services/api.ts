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

// API URL from environment variable (set at build time)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

  /**
   * Obtiene lista de territorios.
   */
  getTerritories: async (params?: {
    nivel?: 'DEPARTAMENTAL' | 'MUNICIPAL'
    search?: string
    limit?: number
  }): Promise<Array<{
    territorio_id: string
    nombre: string
    nivel: string
    dp?: string
    mpio?: string
  }>> => {
    const response = await api.get('/population/territories', { params })
    return response.data
  },

  /**
   * Obtiene GeoJSON enriquecido con datos de población.
   */
  getMapGeoJSON: async (params: {
    nivel: 'DEPARTAMENTAL' | 'MUNICIPAL'
    anio: number
    area?: string
    variable?: string
  }): Promise<any> => {
    const response = await api.get('/map/geojson', { params })
    return response.data
  },

  /**
   * Obtiene serie de tiempo de población con crecimiento y delta.
   */
  getTimeSeries: async (params: {
    territorio_id: string
    anio_from?: number
    anio_to?: number
    area?: string
  }): Promise<{
    territorio_id: string
    anio_from: number
    anio_to: number
    area: string
    series: Array<{
      anio: number
      poblacion: number
      delta: number | null
      tasa_crecimiento: number | null
    }>
  }> => {
    const response = await api.get('/population/time_series', { params })
    return response.data
  },
}

// ============================================================================
// DANE INDICATORS API
// ============================================================================

export const daneApi = {
  /**
   * Get all DANE regions
   */
  getRegions: async (): Promise<Array<{
    region_code: string
    region_name: string
  }>> => {
    const response = await api.get('/dane/regions')
    return response.data
  },

  /**
   * Get DANE departments
   */
  getDepartments: async (): Promise<Array<{
    dept_code: string
    dept_name: string
  }>> => {
    const response = await api.get('/dane/departments')
    return response.data
  },

  /**
   * Get fertility indicators
   */
  getFertility: async (params?: {
    region_code?: string
    year_start?: number
    year_end?: number
    limit?: number
  }): Promise<Array<{
    region_code: string
    year: number
    tgf: number
    age_rates: Record<string, number>
  }>> => {
    const response = await api.get('/dane/fertility', { params })
    return response.data
  },

  /**
   * Get migration indicators
   */
  getMigration: async (params?: {
    region_code?: string
    year_start?: number
    year_end?: number
    sex?: 'Hombres' | 'Mujeres'
    migration_type?: 'Internacional' | 'Interna'
    limit?: number
  }): Promise<Array<{
    region_code: string
    year: number
    sex: string
    migration_type: string
    age_values: Record<string, number>
  }>> => {
    const response = await api.get('/dane/migration', { params })
    return response.data
  },

  /**
   * Get mortality indicators
   */
  getMortality: async (params?: {
    region_code?: string
    year_start?: number
    year_end?: number
    sex?: 'Hombres' | 'Mujeres'
    limit?: number
  }): Promise<Array<{
    region_code: string
    year: number
    sex: string
    age_mortality_rates: Record<string, number>
  }>> => {
    const response = await api.get('/dane/mortality', { params })
    return response.data
  },

  /**
   * Get principal demographic indicators
   */
  getPrincipal: async (params?: {
    region_code?: string
    year_start?: number
    year_end?: number
    limit?: number
  }): Promise<Array<{
    region_code: string
    year: number
    other_indicators: Record<string, number>
  }>> => {
    const response = await api.get('/dane/principal', { params })
    return response.data
  },

  /**
   * Get principal indicators time series for a region
   */
  getPrincipalTimeSeries: async (
    region_code: string,
    year_start: number = 2018,
    year_end: number = 2070
  ): Promise<Array<{
    region_code: string
    year: number
    other_indicators: Record<string, number>
  }>> => {
    const response = await api.get(`/dane/principal/${region_code}`, {
      params: { year_start, year_end }
    })
    return response.data
  },

  /**
   * Get data summary
   */
  getSummary: async (): Promise<{
    regions: number
    indicators: {
      fertility: number
      migration: number
      mortality: number
      principal: number
      total: number
    }
    years: {
      start: number
      end: number
      count: number
    }
    data_source: string
    last_updated: string
  }> => {
    const response = await api.get('/dane/summary')
    return response.data
  },
}

// ============================================================================
// CHAT API
// ============================================================================

export const chatApi = {
  /**
   * Get available LLM providers
   */
  getProviders: async (): Promise<{
    available: string[]
    default: string | null
  }> => {
    const response = await api.get('/chats/providers')
    return response.data
  },

  /**
   * Get all chats
   */
  getChats: async (): Promise<Array<{
    id: number
    title: string
    created_at: string
  }>> => {
    const response = await api.get('/chats/')
    return response.data
  },

  /**
   * Get messages for a chat
   */
  getMessages: async (chatId: number): Promise<Array<{
    id: number
    role: string
    content: string
    message_metadata?: any
    chat_id: number
    created_at: string
  }>> => {
    const response = await api.get(`/chats/${chatId}/messages`)
    return response.data
  },

  /**
   * Create a new chat
   */
  createChat: async (title: string = 'Nueva conversación'): Promise<{
    id: number
    title: string
    created_at: string
  }> => {
    const response = await api.post('/chats/', { title })
    return response.data
  },

  /**
   * Delete a chat
   */
  deleteChat: async (chatId: number): Promise<void> => {
    await api.delete(`/chats/${chatId}`)
  },

  /**
   * Send a query to the chat
   */
  sendQuery: async (params: {
    query: string
    chat_id: number
    provider?: string
  }): Promise<{
    response: string
    sql_query?: string
    visualization?: any
    data?: any
  }> => {
    const response = await api.post('/chats/query', params)
    return response.data
  },
}

export default api
