import { useState } from 'react'
import APIService from '../services/api'
import { Button, Card, PageHeader, Input, Badge, Alert } from '../components/UI'

export default function Search({ onNavigate }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    
    if (!searchTerm.trim()) {
      setError('Please enter a search term')
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const result = await APIService.searchItems(searchTerm)
      
      if (result.success) {
        setResults(result.data.results || [])
      } else {
        setError(result.error || 'Search failed')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setSearched(true)
    }
  }

  const handleClearSearch = () => {
    setSearchTerm('')
    setResults([])
    setError(null)
    setSearched(false)
  }

  return (
    <div>
      <PageHeader
        title="Search"
        subtitle="Find items quickly across your inventory"
      />

      <Card className="bg-white mb-8">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search by name, description, tags, or notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
              className="flex-1"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
              className="px-6"
            >
              {loading ? '🔍 Searching...' : '🔍 Search'}
            </Button>
            {searchTerm && (
              <Button
                type="button"
                variant="outline"
                onClick={handleClearSearch}
                className="px-6"
              >
                Clear
              </Button>
            )}
          </div>
        </form>
      </Card>

      {error && (
        <Alert type="error" title="Search error" message={error} />
      )}

      {/* Results */}
      {searched && (
        <div>
          {loading ? (
            <Card className="text-center py-12">
              <div className="text-gray-500">Searching...</div>
            </Card>
          ) : results.length === 0 ? (
            <Card className="text-center py-12">
              <div className="text-gray-500">
                No items found for "{searchTerm}"
              </div>
            </Card>
          ) : (
            <>
              <Card className="bg-white mb-4">
                <div className="text-sm text-gray-600">
                  Found <span className="font-bold text-gray-900">{results.length}</span> item(s)
                </div>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map(item => (
                  <Card
                    key={item.id}
                    className="bg-white hover:shadow-lg transition cursor-pointer"
                    onClick={() => onNavigate('item-detail', { itemId: item.id })}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-lg font-bold text-gray-900 flex-1">
                        {item.name}
                      </h3>
                      {item.category && (
                        <Badge variant="secondary" label={item.category} />
                      )}
                    </div>

                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                      {item.description}
                    </p>

                    <div className="grid grid-cols-2 gap-2 text-sm mb-4 pb-4 border-b">
                      <div>
                        <span className="text-gray-600">Quantity:</span>
                        <div className="font-semibold text-gray-900">
                          {item.quantity} {item.unit}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-600">Locations:</span>
                        <div className="font-semibold text-gray-900">
                          {item.locations?.length || 0}
                        </div>
                      </div>
                    </div>

                    {item.tags && (item.tags.length > 0) && (
                      <div className="mb-4 flex flex-wrap gap-1">
                        {(Array.isArray(item.tags) ? item.tags : item.tags.split(',')).slice(0, 3).map((tag, i) => (
                          <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            {typeof tag === 'string' ? tag.trim() : tag}
                          </span>
                        ))}
                        {(Array.isArray(item.tags) ? item.tags : item.tags.split(',')).length > 3 && (
                          <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                            +{(Array.isArray(item.tags) ? item.tags : item.tags.split(',')).length - 3} more
                          </span>
                        )}
                      </div>
                    )}

                    <Button
                      variant="primary"
                      size="sm"
                      className="w-full"
                    >
                      View Details
                    </Button>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
