import { create } from 'zustand'
import APIService from '../services/api'

const useItemDetailStore = create((set, get) => ({
  // State
  item: null,
  loading: true,
  error: null,
  updating: false,
  pendingQuantity: null,
  pendingTags: [],

  // Actions
  setItem: (item) => set({ item }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setUpdating: (updating) => set({ updating }),
  setPendingQuantity: (quantity) => set({ pendingQuantity: quantity }),
  setPendingTags: (tags) => set({ pendingTags: tags }),

  // Async actions
  fetchItem: async (itemId) => {
    if (!itemId) {
      set({ loading: false, item: null })
      return
    }

    set({ loading: true, error: null })

    try {
      const result = await APIService.getItem(itemId)
      if (result.success) {
        set({
          item: result.data,
          pendingQuantity: result.data.quantity,
          // Ensure tags are always array of strings without braces
          pendingTags: Array.isArray(result.data.tags)
            ? result.data.tags.map(t => t.replace(/^[\{\}"\s]+|[\{\}"\s]+$/g, ''))
            : [],
          loading: false
        })
      } else {
        set({ error: result.error, loading: false, item: null })
      }
    } catch (err) {
      set({ error: err.message, loading: false, item: null })
    }
  },

  updateItem: async () => {
    const { item, pendingQuantity, pendingTags } = get()
    if (!item) return

    set({ updating: true, error: null })

    try {
      const cleanTags = pendingTags.map(t => t.trim()).filter(Boolean)
      const result = await APIService.updateItem(item.id, {
        ...item,
        quantity: pendingQuantity,
        tags: cleanTags
      })

      if (result.success) {
        set({
          item: result.data,
          pendingQuantity: result.data.quantity,
          pendingTags: Array.isArray(result.data.tags) ? result.data.tags : [],
          updating: false
        })
      } else {
        set({ error: result.error, updating: false })
      }
    } catch (err) {
      set({ error: err.message, updating: false })
    }
  },

  adjustQuantity: (delta) => {
    const { pendingQuantity, item } = get()
    const currentQuantity = pendingQuantity ?? item?.quantity ?? 0
    set({ pendingQuantity: Math.max(0, currentQuantity + delta) })
  },

  addTag: (tag) => {
    if (!tag.trim()) return
    const { pendingTags } = get()
    set({ pendingTags: Array.from(new Set([...pendingTags, tag.trim()])) })
  },

  removeTag: (tag) => {
    const { pendingTags } = get()
    set({ pendingTags: pendingTags.filter(t => t !== tag) })
  },

  // Computed properties
  isSaveDisabled: () => {
    const { item, pendingQuantity, pendingTags } = get()
    if (!item) return true
    return pendingQuantity === item.quantity &&
           pendingTags.join(',') === (item.tags || []).join(',')
  },

  // Reset state
  reset: () => set({
    item: null,
    loading: true,
    error: null,
    updating: false,
    pendingQuantity: null,
    pendingTags: []
  })
}))

export { useItemDetailStore }