import React from 'react'
import { Card, Button } from '../../components/UI'

export default function QuantityControls({ pendingQuantity, onAdjust, onSave, updating, unit, saveDisabled }) {
  return (
    <Card>
      <h3 className="font-semibold mb-2">Quantity</h3>
      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2 mb-2">
          <Button variant="outline" size="sm" onClick={() => onAdjust(-1)} disabled={updating || pendingQuantity <= 0}>−</Button>
          <span className="font-medium text-gray-900 text-center flex-1 px-2 py-1 bg-gray-50 rounded">{pendingQuantity}</span>
          <Button variant="outline" size="sm" onClick={() => onAdjust(1)} disabled={updating}>+</Button>
        </div>

        <Button variant="primary" size="sm" onClick={onSave} disabled={updating || saveDisabled} className="w-full">
          {updating ? '💾 Saving...' : '💾 Save Quantity & Tags'}
        </Button>

        {unit && <p className="text-xs text-gray-500 mt-2">{unit}</p>}
      </div>
    </Card>
  )
}
