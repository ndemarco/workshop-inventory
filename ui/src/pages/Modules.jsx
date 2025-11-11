import { useEffect, useState } from 'react'
import APIService from '../services/api'
import { Button, Card, PageHeader, Table, EmptyState, Modal, Input, Textarea, Alert } from '../components/UI'

export default function Modules({ onNavigate }) {
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [formError, setFormError] = useState(null)
  const [formData, setFormData] = useState({ name: '', description: '', location_description: '' })
  const [editing, setEditing] = useState(null)

  useEffect(() => {
    fetchModules()
  }, [])

  const fetchModules = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await APIService.getModules()
      if (!result.success) {
        throw new Error(result.error)
      }
      setModules(result.data.modules || [])
    } catch (error) {
      setError(error.message || 'Failed to fetch modules')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      setFormError(null)
      const result = editing 
        ? await APIService.updateModule(editing.id, formData)
        : await APIService.createModule(formData)
      
      if (!result.success) {
        throw new Error(result.error)
      }
      
      setModalOpen(false)
      setFormData({ name: '', description: '', location_description: '' })
      setEditing(null)
      await fetchModules()
    } catch (error) {
      setFormError(error.message || 'Failed to save module')
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this module? All levels and locations will be deleted.')) return
    try {
      setError(null)
      const result = await APIService.deleteModule(id)
      if (!result.success) {
        throw new Error(result.error)
      }
      await fetchModules()
    } catch (error) {
      setError(error.message || 'Failed to delete module')
    }
  }

  const columns = [
    { key: 'name', label: 'Name', render: (row) => <a href="#" className="text-primary-600 font-medium hover:underline">{row.name}</a> },
    { key: 'description', label: 'Description' },
    { key: 'location_description', label: 'Location' },
    {
      key: 'actions',
      label: 'Actions',
      render: (row) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setEditing(row)
              setFormData(row)
              setModalOpen(true)
            }}
          >
            Edit
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
        title="Modules"
        subtitle="Storage modules (cabinets, shelving units, etc.)"
        action={
          <Button
            variant="primary"
            onClick={() => {
              setEditing(null)
              setFormData({ name: '', description: '', location_description: '' })
              setModalOpen(true)
            }}
          >
            ➕ New Module
          </Button>
        }
      />

      {error && (
        <Alert type="error" title="Error" message={error} className="mb-4" />
      )}

      {loading ? (
        <Card className="text-center py-8">Loading modules...</Card>
      ) : modules.length === 0 ? (
        <EmptyState
          icon="📦"
          title="No modules yet"
          description="Create your first storage module to get started"
          action={
            <Button
              variant="primary"
              onClick={() => {
                setEditing(null)
                setFormData({ name: '', description: '', location_description: '' })
                setModalOpen(true)
              }}
            >
              Create Module
            </Button>
          }
        />
      ) : (
        <Table columns={columns} data={modules} loading={loading} />
      )}

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit Module' : 'New Module'}
        size="lg"
      >
        <form onSubmit={handleSave} className="space-y-4">
          <Input
            label="Module Name"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <Textarea
            label="Description"
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <Input
            label="Physical Location"
            placeholder="e.g., Room 1, Shelf 3"
            value={formData.location_description}
            onChange={(e) => setFormData({ ...formData, location_description: e.target.value })}
          />
          <div className="flex gap-3 justify-end pt-4">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              {editing ? 'Update' : 'Create'} Module
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
