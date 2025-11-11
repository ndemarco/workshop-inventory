import { useState, useEffect } from 'react'
import APIService from '../services/api'
import { useForm } from '../hooks/useAsync'
import { Button, Card, PageHeader, Input, Textarea, Select, Badge, Alert } from '../components/UI'

export default function ItemForm({ itemId, onNavigate }) {
  const [duplicates, setDuplicates] = useState([])
  const [showDuplicates, setShowDuplicates] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState(null)
  const [regeneratingQR, setRegeneratingQR] = useState(false)
  const [currentItem, setCurrentItem] = useState(null)
  const [loadingItem, setLoadingItem] = useState(!!itemId)
  const [existing, setExisting] = useState({
    categories: [],
    itemTypes: [],
    units: []
  })
  const [loadingExisting, setLoadingExisting] = useState(true)

  // Fetch existing values (categories, types, units)
  useEffect(() => {
    const fetchExisting = async () => {
      setLoadingExisting(true)
      try {
        const result = await APIService.getExistingValues()
        if (result.success) {
          setExisting(result.data)
        }
      } catch (err) {
        console.error('Failed to fetch existing values:', err)
      } finally {
        setLoadingExisting(false)
      }
    }

    fetchExisting()
  }, [])

  // Fetch item to edit (only if itemId provided)
  useEffect(() => {
    if (!itemId) {
      setLoadingItem(false)
      return
    }

    const fetchItem = async () => {
      setLoadingItem(true)
      try {
        const result = await APIService.getItem(itemId)
        if (result.success) {
          setCurrentItem(result.data)
        }
      } catch (err) {
        console.error('Failed to fetch item:', err)
      } finally {
        setLoadingItem(false)
      }
    }

    fetchItem()
  }, [itemId])

  const initialValues = {
    name: currentItem?.name || '',
    description: currentItem?.description || '',
    category: currentItem?.category || '',
    item_type: currentItem?.item_type || '',
    quantity: currentItem?.quantity || 0,
    unit: currentItem?.unit || 'pieces',
    tags: Array.isArray(currentItem?.tags) ? currentItem.tags.join(', ') : currentItem?.tags || '',
    notes: currentItem?.notes || '',
  }

  const { values, handleChange, handleSubmit: handleFormSubmit, reset, setValues } = useForm(initialValues, onSubmit)

  // Update form values when currentItem changes
  useEffect(() => {
    if (currentItem) {
      setValues(initialValues)
    }
  }, [currentItem])

  async function onSubmit(formData) {
    setSaving(true)
    setSaveError(null)

    try {
      let result
      if (itemId) {
        result = await APIService.updateItem(itemId, formData)
      } else {
        result = await APIService.createItem(formData)
      }

      if (result.success) {
        onNavigate('items')
      } else {
        setSaveError(result.error)
      }
    } catch (error) {
      setSaveError(error.message)
    } finally {
      setSaving(false)
    }
  }

  const checkDuplicates = async () => {
    if (!values.name || !values.description) {
      setSaveError('Please fill in name and description first')
      return
    }

    try {
      const result = await APIService.checkDuplicates({
        name: values.name,
        description: values.description,
        category: values.category,
        tags: values.tags,
        threshold: 0.70,
      })

      if (result.success && result.data.has_duplicates) {
        setDuplicates(result.data.matches)
        setShowDuplicates(true)
      } else {
        setShowDuplicates(false)
        setDuplicates([])
      }
    } catch (error) {
      console.error('Failed to check duplicates:', error)
    }
  }

  const handleExtractSpecs = async () => {
    if (!values.description) return

    try {
      const result = await APIService.extractSpecs(values.description, values.name)
      if (result.success && result.data.category && !values.category) {
        // Auto-populate category if found
        handleChange({ target: { name: 'category', value: result.data.category } })
      }
    } catch (error) {
      console.error('Failed to extract specs:', error)
    }
  }

  const handleRegenerateQR = async () => {
    if (!itemId) return
    setRegeneratingQR(true)
    try {
      const result = await APIService.generateQRCode(itemId)
      if (result.success) {
        // Refresh item data to show new QR code
        const itemResult = await APIService.getItem(itemId)
        if (itemResult.success) {
          setCurrentItem(itemResult.data)
        }
        alert(`QR code regenerated successfully!`)
      } else {
        setSaveError(`Failed to regenerate QR code: ${result.error}`)
      }
    } catch (error) {
      setSaveError(`Error regenerating QR code: ${error.message}`)
    } finally {
      setRegeneratingQR(false)
    }
  }

  const handleDownloadQR = (itemId) => {
    const url = APIService.getQRCodeUrl(itemId)
    const link = document.createElement('a')
    link.href = url
    link.download = `qr-code-${itemId}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const isLoading = loadingItem || loadingExisting

  return (
    <div>
      <PageHeader
        title={itemId ? 'Edit Item' : 'New Item'}
        subtitle={itemId ? 'Update item details' : 'Add a new item to inventory'}
      />

      {saveError && (
        <Alert type="error" title="Save error" message={saveError} />
      )}

      <Card className="bg-white max-w-2xl">
        <form onSubmit={handleFormSubmit} className="space-y-6">
          {/* Name & Description */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Item Name *
            </label>
            <Input
              name="name"
              value={values.name}
              onChange={handleChange}
              placeholder="e.g., M6 x 50mm Stainless Steel Bolt"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Description *
            </label>
            <Textarea
              name="description"
              value={values.description}
              onChange={handleChange}
              placeholder="Detailed description of the item"
              rows={4}
              required
            />
            <div className="mt-2 flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleExtractSpecs}
              >
                🔍 Extract Specs
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={checkDuplicates}
              >
                ⚠️ Check Duplicates
              </Button>
            </div>
          </div>

          {/* Category & Type */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Category
              </label>
              <Select
                name="category"
                value={values.category}
                onChange={handleChange}
                options={existing?.categories || []}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Item Type
              </label>
              <Select
                name="item_type"
                value={values.item_type}
                onChange={handleChange}
                options={existing?.itemTypes || []}
              />
            </div>
          </div>

          {/* Quantity & Unit */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Quantity
              </label>
              <Input
                type="number"
                name="quantity"
                value={values.quantity}
                onChange={handleChange}
                min="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Unit
              </label>
              <Select
                name="unit"
                value={values.unit}
                onChange={handleChange}
                options={existing?.units || ['pieces', 'meters', 'kg', 'liters']}
              />
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Tags (comma-separated)
            </label>
            <Textarea
              name="tags"
              value={values.tags}
              onChange={handleChange}
              placeholder="e.g., fastener, metal, stainless-steel"
              rows={2}
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Notes
            </label>
            <Textarea
              name="notes"
              value={values.notes}
              onChange={handleChange}
              placeholder="Additional notes or comments"
              rows={3}
            />
          </div>

          {/* QR Code Management */}
          {itemId && currentItem?.qr_code && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 sm:p-6">
              <h3 className="text-sm sm:text-base font-bold text-gray-900 mb-3">QR Code Management</h3>
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4 mb-4">
                <div className="text-xs sm:text-sm text-gray-700">
                  QR Code: <span className="font-mono font-bold text-blue-600">{currentItem.qr_code}</span>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2">
                <Button
                  type="button"
                  variant="success"
                  size="sm"
                  onClick={() => handleDownloadQR(itemId)}
                  className="flex-1"
                >
                  ⬇️ Download QR Code
                </Button>
                <Button
                  type="button"
                  variant="warning"
                  size="sm"
                  onClick={handleRegenerateQR}
                  disabled={regeneratingQR}
                  className="flex-1"
                >
                  {regeneratingQR ? '⏳ Regenerating...' : '🔄 Regenerate QR Code'}
                </Button>
              </div>
            </div>
          )}

          {/* Duplicates Warning */}
          {showDuplicates && duplicates.length > 0 && (
            <Alert 
              type="warning" 
              title="Potential Duplicates Found"
              message={`${duplicates.length} similar item(s) already exist. Please review before saving.`}
            >
              <div className="mt-3 space-y-2">
                {duplicates.map(dup => (
                  <div key={dup.id} className="text-sm text-gray-700 p-2 bg-yellow-50 rounded">
                    <div className="font-medium">{dup.name}</div>
                    <div className="text-xs">{dup.description}</div>
                  </div>
                ))}
              </div>
            </Alert>
          )}

          {/* Submit Buttons */}
          <div className="flex gap-3 pt-6 border-t">
            <Button
              type="submit"
              variant="primary"
              disabled={saving || isLoading}
              className="flex-1"
            >
              {saving ? 'Saving...' : itemId ? 'Update Item' : 'Create Item'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => onNavigate('items')}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}
