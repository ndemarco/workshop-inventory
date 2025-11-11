import { useEffect } from 'react'
import { Button, Card, Alert } from '../components/UI'
import ItemHeader from '../components/item/ItemHeader'
import QuantityControls from '../components/item/QuantityControls'
import ItemMeta from '../components/item/ItemMeta'
import QRCodeSection from '../components/item/QRCodeSection'
import ItemLocations from '../components/item/ItemLocations'
import ItemNotes from '../components/item/ItemNotes'
import { useItemDetailStore } from '../stores/itemDetailStore'

export default function ItemDetail({ itemId, onNavigate }) {
  const {
    item,
    loading,
    error,
    updating,
    pendingQuantity,
    pendingTags,
    fetchItem,
    updateItem,
    adjustQuantity,
    addTag,
    removeTag,
    isSaveDisabled
  } = useItemDetailStore()

  useEffect(() => {
    fetchItem(itemId)
  }, [itemId, fetchItem])

  if (loading) return <Card className="text-center py-12">Loading...</Card>
  if (!item) return <Card className="text-center py-12">Item not found</Card>

  return (
    <div>
      <ItemHeader item={item} onEdit={(id) => onNavigate('item-form', { itemId: id })} />
      {error && <Alert type="error" title="Error" message={error} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="text-lg font-semibold mb-4">Description</h2>
            <p className="text-gray-600 whitespace-pre-wrap">{item.description}</p>
          </Card>

          <ItemLocations item={item} />

          <ItemNotes item={item} />
        </div>

        <div className="space-y-6">
          <ItemMeta item={item} pendingTags={pendingTags} onAddTag={addTag} onRemoveTag={removeTag} />

          <QuantityControls
            pendingQuantity={pendingQuantity}
            onAdjust={adjustQuantity}
            onSave={updateItem}
            updating={updating}
            unit={item.unit}
            saveDisabled={isSaveDisabled()}
          />

          <QRCodeSection
            item={item}
            mode="view"
            onDownloadQR={() => {
              const url = APIService.getQRCodeUrl(item.id)
              const link = document.createElement('a')
              link.href = url
              link.download = `qr-code-${item.id}.png`
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
            }}
          />

          <Button variant="outline" onClick={() => onNavigate('items')} className="w-full">← Back to Items</Button>
        </div>
      </div>
    </div>
  )
}
