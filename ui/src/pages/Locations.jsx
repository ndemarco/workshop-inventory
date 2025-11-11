import { useEffect, useState } from 'react'
import APIService from '../services/api'
import { Button, Card, PageHeader, Table, EmptyState, Modal, Input, Select, Alert } from '../components/UI'

export default function Locations({ onNavigate }) {
  const [locations, setLocations] = useState([])
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterModule, setFilterModule] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [formData, setFormData] = useState({ module_id: '', level_number: '', row: '', column: '', color: '#FFFFFF' })
  const [editing, setEditing] = useState(null)

  useEffect(() => {
    fetchData()
  }, [filterModule])

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [locResult, modResult] = await Promise.all([
        APIService.getLocations(filterModule ? { module_id: filterModule } : {}),
        APIService.getModules()
      ])

      if (!locResult.success) throw new Error(locResult.error)
      if (!modResult.success) throw new Error(modResult.error)

      setLocations(locResult.data.locations || [])
      setModules(modResult.data.modules || [])
    } catch (error) {
      setError(error.message || 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this location? This cannot be undone.')) return
    
    try {
      const result = await APIService.deleteLocation(id)
      if (!result.success) {
        throw new Error(result.error)
      }
      await fetchData()
    } catch (error) {
      setError(error.message || 'Failed to delete location')
    }
  }

  const columns = [
    { key: 'full_address', label: 'Address', render: (row) => <span className="font-medium">{row.full_address || `${row.row}${row.column}`}</span> },
    {
      key: 'color',
      label: 'Color',
      render: (row) => (
        <div className="flex items-center gap-2">
          <div
            className="w-6 h-6 rounded border border-gray-300"
            style={{ backgroundColor: row.color || '#FFFFFF' }}
          />
          <span className="text-sm font-mono">{row.color}</span>
        </div>
      ),
    },
    { key: 'location_type', label: 'Type' },
    { key: 'item_count', label: 'Items' },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="flex gap-2">
          <Button size="sm" variant="ghost">
            View
          </Button>
          <Button
            size="sm"
            variant="danger"
            onClick={() => handleDelete(row.id)}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Locations"
        subtitle="Storage locations and bins"
        action={
          <Button variant="primary">
            ➕ New Location
          </Button>
        }
      />

      {error && (
        <Alert type="error" title="Error" message={error} className="mb-4" />
      )}

      <div className="mb-6 flex gap-4">
        <Select
          label="Filter by Module"
          options={modules.map(m => ({ value: m.id, label: m.name }))}
          value={filterModule}
          onChange={(e) => setFilterModule(e.target.value)}
          className="w-64"
        />
      </div>

      {loading ? (
        <Card className="text-center py-8">Loading locations...</Card>
      ) : locations.length === 0 ? (
        <EmptyState
          icon="📍"
          title="No locations yet"
          description="Create your first storage location in a module"
          action={<Button variant="primary">Create Location</Button>}
        />
      ) : (
        <Table columns={columns} data={locations} loading={loading} />
      )}
    </div>
  )
}
