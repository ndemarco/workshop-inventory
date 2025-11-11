import React from 'react'
import { Card, Badge, Input } from '../../components/UI'

export default function ItemMeta({ item, pendingTags, onAddTag, onRemoveTag }) {
  return (
    <Card>
      <h3 className="font-semibold mb-3">Tags & Details</h3>
      <div className="space-y-3 text-sm">
        {item?.category && (
          <div>
            <span className="text-gray-600 block text-xs font-medium mb-1">Category</span>
            <Badge variant="primary">{item.category}</Badge>
          </div>
        )}

        {item?.item_type && (
          <div>
            <span className="text-gray-600 block text-xs font-medium mb-1">Type</span>
            <p className="font-medium text-gray-900">{item.item_type}</p>
          </div>
        )}

        <div>
          <div className="flex flex-wrap gap-2 mb-2">
            {pendingTags.map((tag, i) => (
              <Badge key={i} variant="gray" onClick={() => onRemoveTag(tag)}>
                {tag} ×
              </Badge>
            ))}
          </div>

          <Input placeholder="Add tag..." onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault()
              onAddTag?.(e.target.value)
              e.target.value = ''
            }
          }} />
        </div>
      </div>
    </Card>
  )
}
