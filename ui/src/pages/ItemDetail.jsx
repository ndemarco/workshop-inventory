import { useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import APIService from '../services/api'
import { Button, Card, PageHeader, Alert, Badge, Input } from '../components/UI'

export default function ItemDetail({ itemId, onNavigate }) {
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(false)
  const [pendingQuantity, setPendingQuantity] = useState(null)
  const [pendingTags, setPendingTags] = useState([])

  useEffect(() => {
    if (!itemId) {
      setLoading(false)
      return
    }
    const fetchItem = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await APIService.getItem(itemId)
        if (result.success) {
          setItem(result.data)
          setPendingQuantity(result.data.quantity)
          // Ensure tags are always array of strings without braces
          const normalizedTags = Array.isArray(result.data.tags)
            ? result.data.tags.map(t => t.replace(/^[\{\}"\s]+|[\{\}"\s]+$/g, ''))
            : []
          setPendingTags(normalizedTags)
        } else {
          setError(result.error)
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchItem()
  }, [itemId])

  const handleQuantityAdjust = (delta) => {
    setPendingQuantity(prev => Math.max(0, (prev ?? item?.quantity ?? 0) + delta))
  }

  const handleSave = async () => {
    if (!item) return
    setUpdating(true)
    setError(null)
    try {
      const cleanTags = pendingTags.map(t => t.trim()).filter(Boolean)
      const result = await APIService.updateItem(item.id, {
        ...item,
        quantity: pendingQuantity,
        tags: cleanTags
      })
      if (result.success) {
        setItem(result.data)
        setPendingQuantity(result.data.quantity)
        setPendingTags(Array.isArray(result.data.tags) ? result.data.tags : [])
      } else {
        setError(result.error)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(false)
    }
  }

  const handleAddTag = (tag) => {
    if (!tag.trim()) return
    setPendingTags(prev => Array.from(new Set([...prev, tag.trim()])))
  }

  const handleRemoveTag = (tag) => {
    setPendingTags(prev => prev.filter(t => t !== tag))
  }

  if (loading) return <Card className="text-center py-12">Loading...</Card>
  if (!item) return <Card className="text-center py-12">Item not found</Card>

  return (
    <div>
      <PageHeader
        title={`📦 ${item.name}`}
        action={
          <Button variant="primary" onClick={() => onNavigate('item-form', { itemId: item.id })}>
            ✏️ Edit Item
          </Button>
        }
      />
      {error && <Alert type="error" title="Error" message={error} />}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="text-lg font-semibold mb-4">Description</h2>
            <p className="text-gray-600 whitespace-pre-wrap">{item.description}</p>
          </Card>
          <Card>
            <h2 className="text-lg font-semibold mb-4">Storage Locations</h2>
            {item.locations && item.locations.length > 0 ? (
              <div className="space-y-2">
                {item.locations.map((loc) => (
                  <div key={loc.id} className="p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium text-gray-900">{loc.location?.location_name}</p>
                    <p className="text-sm text-gray-600">{loc.location?.full_address}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">No storage locations assigned</p>
            )}
          </Card>
          {item.notes && (
            <Card>
              <h2 className="text-lg font-semibold mb-4">Notes</h2>
              <p className="text-gray-600 whitespace-pre-wrap">{item.notes}</p>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <h3 className="font-semibold mb-4">Details</h3>
            <div className="space-y-4 text-sm">
              {item.category && (
                <div>
                  <span className="text-gray-600 block text-xs font-medium mb-1">Category</span>
                  <Badge variant="primary">{item.category}</Badge>
                </div>
              )}
              {item.item_type && (
                <div>
                  <span className="text-gray-600 block text-xs font-medium mb-1">Type</span>
                  <p className="font-medium text-gray-900">{item.item_type}</p>
                </div>
              )}
              <div>
                <span className="text-gray-600 block text-xs font-medium mb-2">Quantity</span>
                <div className="flex items-center gap-2 mb-2">
                  <Button variant="outline" size="sm" onClick={() => handleQuantityAdjust(-1)} disabled={updating || pendingQuantity <= 0}>−</Button>
                  <span className="font-medium text-gray-900 text-center flex-1 px-2 py-1 bg-gray-50 rounded">{pendingQuantity}</span>
                  <Button variant="outline" size="sm" onClick={() => handleQuantityAdjust(1)} disabled={updating}>+</Button>
                </div>
                <Button variant="primary" size="sm" onClick={handleSave} disabled={updating || (pendingQuantity === item.quantity && pendingTags.join(',') === (item.tags || []).join(','))} className="w-full">
                  {updating ? '💾 Saving...' : '💾 Save Quantity & Tags'}
                </Button>
                <p className="text-xs text-gray-500 mt-2">{item.unit}</p>
              </div>
            </div>
          </Card>

          <Card>
            <h3 className="font-semibold mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2 mb-2">
              {pendingTags.map((tag, i) => (
                <Badge key={i} variant="gray" onClick={() => handleRemoveTag(tag)}>
                  {tag} ×
                </Badge>
              ))}
            </div>
            <Input placeholder="Add tag..." onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleAddTag(e.target.value)
                e.target.value = ''
              }
            }}/>
          </Card>

          {item.qr_code && (
            <Card>
              <h3 className="font-semibold mb-4">QR Code</h3>
              <div className="flex flex-col items-center">
                <div className="bg-white p-4 rounded-lg border-2 border-gray-200 mb-4">
                  <QRCodeSVG value={`/item/${item.id}`} size={256} level="H" includeMargin={true}/>
                </div>
                <p className="text-xs text-gray-600 mb-4 text-center">
                  <span className="font-mono bg-gray-100 px-2 py-1 rounded block mb-2">{item.qr_code}</span>
                  Scan to view this item
                </p>
              </div>
              <Button variant="success" size="sm" onClick={() => {
                const url = APIService.getQRCodeUrl(item.id)
                const link = document.createElement('a')
                link.href = url
                link.download = `qr-code-${item.id}.png`
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
              }} className="w-full">⬇️ Download QR Code</Button>
            </Card>
          )}

          <Button variant="outline" onClick={() => onNavigate('items')} className="w-full">← Back to Items</Button>
        </div>
      </div>
    </div>
  )
}
