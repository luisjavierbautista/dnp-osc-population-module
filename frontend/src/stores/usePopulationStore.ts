/**
 * Store global de población con Zustand.
 */
import { create } from 'zustand'
import type { AreaGeografica, Sexo } from '@/types/population'

interface PopulationFilters {
  anio: number
  area: AreaGeografica
  sexo: Sexo
  territorios: string[]
}

interface PopulationStore {
  // Filters
  filters: PopulationFilters
  setAnio: (anio: number) => void
  setArea: (area: AreaGeografica) => void
  setSexo: (sexo: Sexo) => void
  setTerritorios: (territorios: string[]) => void
  addTerritorio: (territorio: string) => void
  removeTerritorio: (territorio: string) => void
  resetFilters: () => void
}

const DEFAULT_FILTERS: PopulationFilters = {
  anio: 2025,
  area: 'Total',
  sexo: 'T',
  territorios: [],
}

export const usePopulationStore = create<PopulationStore>((set) => ({
  filters: DEFAULT_FILTERS,

  setAnio: (anio) =>
    set((state) => ({
      filters: { ...state.filters, anio },
    })),

  setArea: (area) =>
    set((state) => ({
      filters: { ...state.filters, area },
    })),

  setSexo: (sexo) =>
    set((state) => ({
      filters: { ...state.filters, sexo },
    })),

  setTerritorios: (territorios) =>
    set((state) => ({
      filters: { ...state.filters, territorios },
    })),

  addTerritorio: (territorio) =>
    set((state) => ({
      filters: {
        ...state.filters,
        territorios: [...state.filters.territorios, territorio],
      },
    })),

  removeTerritorio: (territorio) =>
    set((state) => ({
      filters: {
        ...state.filters,
        territorios: state.filters.territorios.filter((t) => t !== territorio),
      },
    })),

  resetFilters: () =>
    set({
      filters: DEFAULT_FILTERS,
    }),
}))
