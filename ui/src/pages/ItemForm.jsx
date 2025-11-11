import { useEffect } from 'react'
import { Button, Card, PageHeader, Alert } from '../components/UI'
import ItemFormFields from '../components/form/ItemFormFields'
import QRCodeSection from '../components/item/QRCodeSection'
import DuplicatesWarning from '../components/form/DuplicatesWarning'
import { useItemFormStore } from '../stores/itemFormStore'

export default function ItemForm({ itemId, onNavigate }) {
  const {
    currentItem,
    loadingItem,
    existing,
    loadingExisting,
    duplicates,
    showDuplicates,
    saving,
    saveError,
    regeneratingQR,
    formValues,
    fetchExistingValues,
    fetchItem,
    submitForm,
    checkDuplicates,
    extractSpecs,
    regenerateQR,
    downloadQR,
    setFormValues
  } = useItemFormStore()

  // Fetch existing values on mount
  useEffect(() => {
    fetchExistingValues()
  }, [fetchExistingValues])

  // Fetch item to edit (only if itemId provided)
  useEffect(() => {
    fetchItem(itemId)
  }, [itemId, fetchItem])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormValues({ [name]: value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    await submitForm(itemId, formValues, () => onNavigate('items'))
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
        <form onSubmit={handleSubmit} className="space-y-6">
          <ItemFormFields
            formValues={formValues}
            onChange={handleChange}
            onExtractSpecs={extractSpecs}
            onCheckDuplicates={checkDuplicates}
            existing={existing}
          />

          {/* QR Code Management */}
          {itemId && (
            <QRCodeSection
              item={currentItem}
              mode="edit"
              regeneratingQR={regeneratingQR}
              onDownloadQR={() => downloadQR(itemId)}
              onRegenerateQR={() => regenerateQR(itemId)}
            />
          )}

          {/* Duplicates Warning */}
          <DuplicatesWarning showDuplicates={showDuplicates} duplicates={duplicates} />

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
