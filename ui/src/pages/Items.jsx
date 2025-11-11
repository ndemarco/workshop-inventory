import { useEffect, useState } from 'react'
import APIService from '../services/api'
import { useFilters } from '../hooks/useAsync'
import { Button, Card, PageHeader, Alert, Badge } from '../components/UI'

export default function Items({ onNavigate }) {
  const [items, setItems] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [generatingQR, setGeneratingQR] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showCategoryFilter, setShowCategoryFilter] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 9
  const { filters, setFilter, clearFilter, clearAllFilters, hasFilters } = useFilters({})

  const normalizeTags = (tags) => {
    if (!tags) return []
    return Array.isArray(tags)
      ? tags.map(t => t.replace(/^[\{\}"\s]+|[\{\}"\s]+$/g, '').trim()).filter(Boolean)
      : tags.split(',').map(t => t.replace(/^[\{\}"\s]+|[\{\}"\s]+$/g, '').trim()).filter(Boolean)
  }

  // Fetch items on mount and when filters change
  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true)
      setError(null)
      try {
        const result = await APIService.getItems(filters)
        if (result.success) {
          const normalizedItems = (result.data.items || []).map(item => ({
            ...item,
            tags: normalizeTags(item.tags)
          }))
          setItems(normalizedItems)
          setCategories(result.data.categories || [])
          setCurrentPage(1)
        } else {
          setError(result.error)
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchItems()
  }, [filters])

  const handleDelete = async (itemId, itemName) => {
    if (window.confirm(`Delete item "${itemName}"? This cannot be undone.`)) {
      const result = await APIService.deleteItem(itemId)
      if (result.success) {
        setItems(prev => prev.filter(item => item.id !== itemId))
      }
    }
  }

  const handleGenerateQR = async (itemId, itemName) => {
    setGeneratingQR(itemId)
    try {
      const result = await APIService.generateQRCode(itemId)
      if (result.success) {
        // Refresh items to get updated QR code
        const itemsResult = await APIService.getItems(filters)
        if (itemsResult.success) {
          const normalizedItems = (itemsResult.data.items || []).map(item => ({
            ...item,
            tags: normalizeTags(item.tags)
          }))
          setItems(normalizedItems)
          setCategories(itemsResult.data.categories || [])
        }
        alert(`QR code generated for "${itemName}"`)
      } else {
        alert(`Failed to generate QR code: ${result.error}`)
      }
    } catch (error) {
      alert(`Error generating QR code: ${error.message}`)
    } finally {
      setGeneratingQR(null)
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

  const handleCategoryFilter = (category) => {
    if (filters.category === category) {
      clearFilter('category')
    } else {
      setFilter('category', category)
    }
  }

  const filteredItems = items.filter(item => {
    const matchesCategory = !filters.category || item.category === filters.category
    const matchesSearch = !searchQuery || 
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.tags || []).some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  const totalPages = Math.ceil(filteredItems.length / itemsPerPage)
  const paginatedItems = filteredItems.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  useEffect(() => {
    setCurrentPage(1)
  }, [filters, searchQuery])

  return (
    <div>
      <PageHeader
        title="Items"
        subtitle={`Managing ${items.length} items`}
        action={
          <Button variant="primary" onClick={() => onNavigate('item-form')}>
            ➕ New Item
          </Button>
        }
      />

      {error && <Alert type="error" title="Error loading items" message={error} />}

      {/* Search & Filter Bar */}
      <Card className="bg-white border border-gray-200 mb-6 p-4 sm:p-6">
        <div className="mb-4 sm:mb-0">
          <div className="relative">
            <input
              type="text"
              placeholder="Search items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 sm:px-4 py-2 sm:py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-600 focus:border-transparent text-sm"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 text-lg"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {categories.length > 0 && (
          <div className="mt-4">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-3">
              <span className="text-xs sm:text-sm font-semibold text-gray-700 whitespace-nowrap">Categories:</span>
              {hasFilters && (
                <button
                  onClick={clearAllFilters}
                  className="text-xs text-gray-600 hover:text-primary-600 transition font-medium underline sm:ml-auto"
                >
                  Clear all
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => handleCategoryFilter(cat)}
                  className={`px-3 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-medium transition-all touch-manipulation ${
                    filters.category === cat
                      ? 'bg-primary-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 active:scale-95'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Items List */}
      {loading ? (
        <Card className="text-center py-16">
          <div className="text-gray-400 text-lg">
            <span className="inline-block animate-spin mr-2">⏳</span>
            Loading your items...
          </div>
        </Card>
      ) : filteredItems.length === 0 ? (
        <Card className="text-center py-16 border-dashed border-2 border-gray-300">
          <div className="text-gray-400 mb-6">
            <div className="text-5xl mb-2">📦</div>
            {searchQuery 
              ? `No items found matching "${searchQuery}"` 
              : hasFilters 
              ? 'No items match your filters' 
              : 'No items yet'}
          </div>
          {searchQuery && (
            <Button variant="outline" onClick={() => setSearchQuery('')} className="mr-2">
              Clear search
            </Button>
          )}
          {hasFilters && <Button variant="outline" onClick={clearAllFilters}>Clear filters</Button>}
          {!searchQuery && !hasFilters && (
            <Button variant="primary" onClick={() => onNavigate('item-form')}>
              ➕ Create your first item
            </Button>
          )}
        </Card>
      ) : (
        <div>
          <div className="text-xs sm:text-sm text-gray-600 mb-4">
            Found <span className="font-bold text-primary-600">{filteredItems.length}</span> item{filteredItems.length !== 1 ? 's' : ''}
            {searchQuery && <span> matching "{searchQuery}"</span>}
            {totalPages > 1 && <span> • Page {currentPage} of {totalPages}</span>}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {paginatedItems.map(item => (
              <Card key={item.id} className="bg-white hover:shadow-xl transition-all duration-300 border border-gray-200 hover:border-primary-300 flex flex-col p-4 sm:p-6">
                <div className="flex justify-between items-start mb-3 sm:mb-4 pb-3 border-b border-gray-100">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-1 break-words">{item.name}</h3>
                    {item.category && <Badge variant="primary" className="text-xs">{item.category}</Badge>}
                  </div>
                </div>
                {item.description && <p className="text-gray-600 text-xs sm:text-sm mb-3 sm:mb-4 line-clamp-2 flex-grow">{item.description}</p>}
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-3 sm:mb-4 p-2 sm:p-3 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="text-xs text-gray-600 font-medium mb-1">Quantity</div>
                    <div className="text-base sm:text-lg font-bold text-primary-600">{item.quantity}</div>
                    <div className="text-xs text-gray-500">{item.unit}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-600 font-medium mb-1">Locations</div>
                    <div className="text-base sm:text-lg font-bold text-success-600">{item.locations?.length || 0}</div>
                  </div>
                </div>
                {item.tags.length > 0 && (
                  <div className="mb-3 sm:mb-4 flex flex-wrap gap-1 sm:gap-2">
                    {item.tags.slice(0, 3).map((tag, i) => (
                      <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full font-medium border border-blue-200">{tag}</span>
                    ))}
                    {item.tags.length > 3 && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full font-medium">+{item.tags.length - 3}</span>
                    )}
                  </div>
                )}
                <div className="flex gap-1.5 sm:gap-2 pt-3 sm:pt-4 border-t border-gray-100 flex-wrap">
                  <Button variant="primary" size="sm" onClick={() => onNavigate('item-detail', { itemId: item.id })} className="flex-1 min-w-[50px] text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2">👁 View</Button>
                  <Button variant="secondary" size="sm" onClick={() => onNavigate('item-form', { itemId: item.id })} className="flex-1 min-w-[50px] text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2">✏️ Edit</Button>
                  {item.qr_code ? (
                    <Button variant="success" size="sm" onClick={() => handleDownloadQR(item.id)} className="text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2">⬇️</Button>
                  ) : (
                    <Button variant="outline" size="sm" onClick={() => handleGenerateQR(item.id, item.name)} disabled={generatingQR === item.id} className="text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2">{generatingQR === item.id ? '⏳' : '📱'}</Button>
                  )}
                  <Button variant="danger" size="sm" onClick={() => handleDelete(item.id, item.name)} className="text-xs sm:text-sm px-2 sm:px-3 py-1.5 sm:py-2">🗑</Button>
                </div>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-1 sm:gap-2 mt-8 pb-8 flex-wrap">
              <Button variant="outline" size="sm" onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))} disabled={currentPage === 1} className="px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm">← Prev</Button>
              <div className="flex gap-0.5 sm:gap-1">
                {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                  if (totalPages <= 5) return i + 1
                  if (currentPage <= 3) return i + 1
                  if (currentPage >= totalPages - 2) return totalPages - 4 + i
                  return currentPage - 2 + i
                }).map(page => (
                  <button key={page} onClick={() => setCurrentPage(page)} className={`w-8 h-8 sm:w-9 sm:h-9 rounded-lg font-medium text-xs sm:text-sm transition-all ${page === currentPage ? 'bg-primary-600 text-white shadow-md' : 'bg-gray-100 text-gray-700 hover:bg-gray-200 active:scale-95'}`}>{page}</button>
                ))}
              </div>
              <Button variant="outline" size="sm" onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages} className="px-2 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm">Next →</Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
