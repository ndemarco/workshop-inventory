/**
 * Centralized API service for all backend communication
 * Built with axios, featuring interceptors and proper error handling
 * Uses relative URLs for seamless cross-environment deployment
 */

import axios from 'axios'

const API_BASE = '/api'
const DEFAULT_TIMEOUT = 30000 // 30 seconds

const axiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: DEFAULT_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken')
    if (token) config.headers.Authorization = `Bearer ${token}`

    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.baseURL}${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.status} ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => Promise.reject(error)
)

// ===================== Helper =====================
function normalizeItemTags(item) {
  if (!item || !item.tags) return item

  let tags = item.tags

  // If it's already an array, keep it
  if (Array.isArray(tags)) {
    item.tags = tags.map(t => String(t).trim())
    return item
  }

  // If it's a string, remove line breaks, curly braces, quotes, then split by comma or space
  if (typeof tags === 'string') {
    tags = tags
      .replace(/[\{\}"]/g, '')       // remove { } and "
      .split(/\s*,\s*|\n+/)          // split by comma or line break
      .map(t => t.trim())             // trim whitespace
      .filter(t => t.length > 0)     // remove empty strings
  }

  item.tags = tags
  return item
}

function normalizeResponseData(data) {
  if (Array.isArray(data)) return data.map(normalizeItemTags)
  if (data && data.id) return normalizeItemTags(data)
  return data
}

// ===================== Service =====================

class APIService {
  static async request(endpoint, options = {}) {
    try {
      const response = await axiosInstance({
        url: endpoint,
        method: 'GET',
        ...options,
      })

      const data = normalizeResponseData(response.data)
      return { success: true, data, status: response.status }
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Request failed',
        status: error.status,
      }
    }
  }

  static get(endpoint, config = {}) {
    return axiosInstance.get(endpoint, config)
  }



  static post(endpoint, data = {}, config = {}) {
    return axiosInstance.post(endpoint, data, config)
  }

  static put(endpoint, data = {}, config = {}) {
    // Ensure tags are always sent as array
    const payload = { ...data }
    if (payload.tags && !Array.isArray(payload.tags)) {
      if (typeof payload.tags === 'string') {
        try {
          payload.tags = JSON.parse(payload.tags)
        } catch {
          payload.tags = payload.tags.split(',').map(t => t.trim())
        }
      } else {
        payload.tags = []
      }
    }
    return axiosInstance.put(endpoint, payload, config)
  }

  static delete(endpoint, config = {}) {
    return axiosInstance.delete(endpoint, config)
  }

  // ===================== ITEMS =====================
  static async getItems(filters = {}) {
    return this.request('/items', { params: filters })
  }

  static async getItem(itemId) {
    return this.request(`/items/${itemId}`)
  }

  static async getRecentItems(count = 5) {
    return this.request(`/recent-items`, { params: { count } })
  }

  static async getStats() {
    return this.request('/stats')
  }

  static async createItem(itemData) {
    return this.request('/items', { method: 'post', data: itemData })
  }

  static async updateItem(itemId, itemData) {
    return this.request(`/items/${itemId}`, { method: 'put', data: itemData })
  }

  static async deleteItem(itemId) {
    return this.request(`/items/${itemId}`, { method: 'delete' })
  }

  // ===================== LOCATIONS =====================
  static async getLocations(filters = {}) {
    return this.request('/locations', { params: filters })
  }

  static async getLocation(locationId) {
    return this.request(`/locations/${locationId}`)
  }

  static async updateLocation(locationId, locationData) {
    return this.request(`/locations/${locationId}`, { method: 'put', data: locationData })
  }

  static async deleteLocation(locationId) {
    return this.request(`/locations/${locationId}`, { method: 'delete' })
  }

  static async getLocationItems(locationId) {
    return this.request(`/locations/${locationId}/items`)
  }

  // ===================== MODULES =====================
  static async getModules() {
    return this.request('/modules')
  }

  static async getModule(moduleId) {
    return this.request(`/modules/${moduleId}`)
  }

  static async createModule(moduleData) {
    return this.request('/modules', { method: 'post', data: moduleData })
  }

  static async updateModule(moduleId, moduleData) {
    return this.request(`/modules/${moduleId}`, { method: 'put', data: moduleData })
  }

  static async deleteModule(moduleId) {
    return this.request(`/modules/${moduleId}`, { method: 'delete' })
  }

  // ===================== LEVELS =====================
  static async getLevelsInModule(moduleId) {
    return this.request(`/modules/${moduleId}/levels`)
  }

  static async getLevel(moduleId, levelId) {
    return this.request(`/modules/${moduleId}/levels/${levelId}`)
  }

  static async createLevel(moduleId, levelData) {
    return this.request(`/modules/${moduleId}/levels`, { method: 'post', data: levelData })
  }

  static async updateLevel(moduleId, levelId, levelData) {
    return this.request(`/modules/${moduleId}/levels/${levelId}`, { method: 'put', data: levelData })
  }

  static async deleteLevel(moduleId, levelId) {
    return this.request(`/modules/${moduleId}/levels/${levelId}`, { method: 'delete' })
  }

  // ===================== SEARCH =====================
  static async searchItems(query, limit = 50) {
    return this.request('/search', { params: { q: query, limit } })
  }

  static async advancedSearch(filters) {
    return this.request('/search/advanced', { method: 'post', data: filters })
  }

  // ===================== QR CODES =====================
  static async generateQRCode(itemId) {
    return this.request(`/items/${itemId}/qr/generate`, { method: 'post' })
  }

  static getQRCodeUrl(itemId) {
    return `${API_BASE}/items/${itemId}/qr/download`
  }

  static async scanQRCode(qrCode) {
    return this.request(`/items/qr/scan/${encodeURIComponent(qrCode)}`)
  }
}

export default APIService
