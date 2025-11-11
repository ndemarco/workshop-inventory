import { useEffect, useState } from 'react'
import axios from 'axios'
import { Button, Card, PageHeader, Table, EmptyState, Modal, Input, Select } from '../components/UI'

export default function Levels({ moduleId, onNavigate }) {
  const [levels, setLevels] = useState([])
  const [module, setModule] = useState(null)
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [formData, setFormData] = useState({ level_number: 1, name: '', rows: 1, columns: 1, description: '' })
  const [editing, setEditing] = useState(null)

  useEffect(() => {
    if (moduleId) {
      fetchData()
    }
  }, [moduleId])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [modRes, levRes] = await Promise.all([
        axios.get(`/api/modules/${moduleId}`),
        axios.get(`/api/modules/${moduleId}/levels`),
      ])
      setModule(modRes.data)
      setLevels(levRes.data.levels || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      if (editing) {
        await axios.post(`/api/levels/${editing.id}`, formData)
      } else {
        await axios.post(`/api/modules/${moduleId}/levels`, formData)
      }
      setModalOpen(false)
      setFormData({ level_number: 1, name: '', rows: 1, columns: 1, description: '' })
      setEditing(null)
      fetchData()
    } catch (error) {
      console.error('Failed to save level:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this level? All locations in this level will be deleted.')) return
    try {
      await axios.post(`/api/levels/${id}/delete`)
      fetchData()
    } catch (error) {
      console.error('Failed to delete level:', error)
    }
  }

  const columns = [
    { key: 'level_number', label: 'Level #' },
    { key: 'name', label: 'Name' },
    { key: 'rows', label: 'Rows' },
    { key: 'columns', label: 'Columns' },
    { key: 'location_count', label: 'Locations' },
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
        title={`Levels in ${module?.name || 'Module'}`}
        action={
          <Button
            variant="primary"
            onClick={() => {
              setEditing(null)
              setFormData({ level_number: 1, name: '', rows: 1, columns: 1, description: '' })
              setModalOpen(true)
            }}
          >
            ➕ New Level
          </Button>
        }
      />

      {loading ? (
        <Card className="text-center py-8">Loading levels...</Card>
      ) : levels.length === 0 ? (
        <EmptyState
          icon="📊"
          title="No levels yet"
          description="Create your first level to organize storage"
          action={
            <Button
              variant="primary"
              onClick={() => {
                setEditing(null)
                setFormData({ level_number: 1, name: '', rows: 1, columns: 1, description: '' })
                setModalOpen(true)
              }}
            >
              Create Level
            </Button>
          }
        />
      ) : (
        <Table columns={columns} data={levels} loading={loading} />
      )}

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit Level' : 'New Level'}
        size="lg"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Level Number"
            type="number"
            required
            min={1}
            value={formData.level_number}
            onChange={(e) => setFormData({ ...formData, level_number: parseInt(e.target.value) })}
          />
          <Input
            label="Name (optional)"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Rows"
              type="number"
              required
              min={1}
              value={formData.rows}
              onChange={(e) => setFormData({ ...formData, rows: parseInt(e.target.value) })}
            />
            <Input
              label="Columns"
              type="number"
              required
              min={1}
              value={formData.columns}
              onChange={(e) => setFormData({ ...formData, columns: parseInt(e.target.value) })}
            />
          </div>
          <div className="flex gap-3 justify-end pt-4">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editing ? 'Update' : 'Create'} Level
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
