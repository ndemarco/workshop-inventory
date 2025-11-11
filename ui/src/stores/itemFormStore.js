import { create } from 'zustand'
import APIService from '../services/api'

const useItemFormStore = create((set, get) => ({
  // State
  currentItem: null,
  loadingItem: false,
  existing: {
    categories: [],
    itemTypes: [],
    units: []
  },
  loadingExisting: true,
  duplicates: [],
  showDuplicates: false,
  saving: false,
  saveError: null,
  regeneratingQR: false,

  // Form values
  formValues: {
    name: '',
    description: '',
    category: '',
    item_type: '',
    quantity: 0,
    unit: 'pieces',
    tags: '',
    notes: '',
  },

  // Actions
  setCurrentItem: (item) => set({ currentItem: item }),
  setLoadingItem: (loading) => set({ loadingItem: loading }),
  setExisting: (existing) => set({ existing }),
  setLoadingExisting: (loading) => set({ loadingExisting: loading }),
  setDuplicates: (duplicates) => set({ duplicates }),
  setShowDuplicates: (show) => set({ showDuplicates: show }),
  setSaving: (saving) => set({ saving }),
  setSaveError: (error) => set({ saveError: error }),
  setRegeneratingQR: (regenerating) => set({ regeneratingQR: regenerating }),
  setFormValues: (values) => set({ formValues: { ...get().formValues, ...values } }),
  resetFormValues: () => set({
    formValues: {
      name: '',
      description: '',
      category: '',
      item_type: '',
      quantity: 0,
      unit: 'pieces',
      tags: '',
      notes: '',
    }
  }),

  // Async actions
  fetchExistingValues: async () => {
    set({ loadingExisting: true })
    try {
      const result = await APIService.getExistingValues()
      if (result.success) {
        set({ existing: result.data, loadingExisting: false })
      } else {
        set({ loadingExisting: false })
      }
    } catch (err) {
      console.error('Failed to fetch existing values:', err)
      set({ loadingExisting: false })
    }
  },

  fetchItem: async (itemId) => {
    if (!itemId) {
      set({ loadingItem: false, currentItem: null })
      return
    }

    set({ loadingItem: true })
    try {
      const result = await APIService.getItem(itemId)
      if (result.success) {
        set({ currentItem: result.data, loadingItem: false })
        // Update form values
        const formValues = {
          name: result.data.name || '',
          description: result.data.description || '',
          category: result.data.category || '',
          item_type: result.data.item_type || '',
          quantity: result.data.quantity || 0,
          unit: result.data.unit || 'pieces',
          tags: Array.isArray(result.data.tags) ? result.data.tags.join(', ') : result.data.tags || '',
          notes: result.data.notes || '',
        }
        set({ formValues })
      } else {
        set({ loadingItem: false, currentItem: null })
      }
    } catch (err) {
      console.error('Failed to fetch item:', err)
      set({ loadingItem: false, currentItem: null })
    }
  },

  submitForm: async (itemId, formData, onSuccess) => {
    set({ saving: true, saveError: null })

    try {
      let result
      if (itemId) {
        result = await APIService.updateItem(itemId, formData)
      } else {
        result = await APIService.createItem(formData)
      }

      if (result.success) {
        onSuccess()
      } else {
        set({ saveError: result.error, saving: false })
      }
    } catch (error) {
      set({ saveError: error.message, saving: false })
    }
  },

  checkDuplicates: async () => {
    const { formValues } = get()
    if (!formValues.name || !formValues.description) {
      set({ saveError: 'Please fill in name and description first' })
      return
    }

    try {
      const result = await APIService.checkDuplicates({
        name: formValues.name,
        description: formValues.description,
        category: formValues.category,
        tags: formValues.tags,
        threshold: 0.70,
      })

      if (result.success && result.data.has_duplicates) {
        set({ duplicates: result.data.matches, showDuplicates: true })
      } else {
        set({ duplicates: [], showDuplicates: false })
      }
    } catch (error) {
      console.error('Failed to check duplicates:', error)
    }
  },

  extractSpecs: async () => {
    const { formValues, setFormValues } = get()
    if (!formValues.description) return

    try {
      const result = await APIService.extractSpecs(formValues.description, formValues.name)
      if (result.success && result.data.category && !formValues.category) {
        setFormValues({ category: result.data.category })
      }
    } catch (error) {
      console.error('Failed to extract specs:', error)
    }
  },

  regenerateQR: async (itemId) => {
    if (!itemId) return
    set({ regeneratingQR: true, saveError: null })
    try {
      const result = await APIService.generateQRCode(itemId)
      if (result.success) {
        // Refresh item data to show new QR code
        const itemResult = await APIService.getItem(itemId)
        if (itemResult.success) {
          set({ currentItem: itemResult.data })
        }
        alert(`QR code regenerated successfully!`)
      } else {
        set({ saveError: `Failed to regenerate QR code: ${result.error}` })
      }
    } catch (error) {
      set({ saveError: `Error regenerating QR code: ${error.message}` })
    } finally {
      set({ regeneratingQR: false })
    }
  },

  downloadQR: (itemId) => {
    const url = APIService.getQRCodeUrl(itemId)
    const link = document.createElement('a')
    link.href = url
    link.download = `qr-code-${itemId}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  },

  // Reset state
  reset: () => set({
    currentItem: null,
    loadingItem: false,
    existing: {
      categories: [],
      itemTypes: [],
      units: []
    },
    loadingExisting: true,
    duplicates: [],
    showDuplicates: false,
    saving: false,
    saveError: null,
    regeneratingQR: false,
    formValues: {
      name: '',
      description: '',
      category: '',
      item_type: '',
      quantity: 0,
      unit: 'pieces',
      tags: '',
      notes: '',
    }
  })
}))

export { useItemFormStore }