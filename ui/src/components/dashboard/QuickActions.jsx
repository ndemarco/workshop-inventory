import { Card, Button } from '../UI'

export default function QuickActions({ onNavigate }) {
  return (
    <Card className="bg-white">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
      <div className="space-y-3">
        <Button
          onClick={() => onNavigate('item-form')}
          className="w-full btn btn-primary"
        >
          ➕ New Item
        </Button>
        <Button
          onClick={() => onNavigate('qr-scanner')}
          className="w-full btn btn-secondary"
        >
          📷 Scan QR
        </Button>
        <Button
          onClick={() => onNavigate('search')}
          className="w-full btn btn-outline"
        >
          🔍 Search
        </Button>
      </div>
    </Card>
  )
}