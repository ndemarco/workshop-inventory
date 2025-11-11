import { create } from 'zustand'
import APIService from '../services/api'

const useDashboardStore = create((set, get) => ({
  // State
  recentItems: [],
  itemsLoading: true,
  stats: null,
  statsError: null,
  statsLoading: true,
  dashboardStats: {
    items: 0,
    modules: 0,
    locations: 0,
    levels: 0,
  },

  // Actions
  setRecentItems: (items) => set({ recentItems: items }),
  setItemsLoading: (loading) => set({ itemsLoading: loading }),
  setStats: (stats) => set({ stats }),
  setStatsError: (error) => set({ statsError: error }),
  setStatsLoading: (loading) => set({ statsLoading: loading }),
  setDashboardStats: (stats) => set({ dashboardStats: stats }),

  // Async actions
  fetchDashboardData: async () => {
    set({ itemsLoading: true, statsLoading: true, statsError: null })

    try {
      // Fetch recent items and stats in parallel
      const [recentItemsResult, statsResult] = await Promise.all([
        APIService.getRecentItems(5),
        APIService.getStats()
      ])

      // Handle recent items
      if (recentItemsResult.success) {
        set({ recentItems: recentItemsResult.data.items || [], itemsLoading: false })
      } else {
        set({ recentItems: [], itemsLoading: false })
      }

      // Handle stats
      if (statsResult.success) {
        set({
          stats: statsResult.data,
          dashboardStats: statsResult.data,
          statsLoading: false
        })
      } else {
        set({
          statsError: statsResult.error,
          stats: {
            items: 0,
            modules: 0,
            locations: 0,
            levels: 0,
          },
          dashboardStats: {
            items: 0,
            modules: 0,
            locations: 0,
            levels: 0,
          },
          statsLoading: false
        })
      }
    } catch (error) {
      set({
        recentItems: [],
        statsError: error.message || 'Failed to load dashboard data',
        stats: {
          items: 0,
          modules: 0,
          locations: 0,
          levels: 0,
        },
        dashboardStats: {
          items: 0,
          modules: 0,
          locations: 0,
          levels: 0,
        },
        itemsLoading: false,
        statsLoading: false
      })
    }
  },

  // Reset state
  reset: () => set({
    recentItems: [],
    itemsLoading: true,
    stats: null,
    statsError: null,
    statsLoading: true,
    dashboardStats: {
      items: 0,
      modules: 0,
      locations: 0,
      levels: 0,
    }
  })
}))

export { useDashboardStore }