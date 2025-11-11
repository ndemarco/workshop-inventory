import React from 'react'
import { PageHeader, Button } from '../../components/UI'

export default function ItemHeader({ item, onEdit }) {
  return (
    <PageHeader
      title={item ? `📦 ${item.name}` : '📦 Item'}
      subtitle={item?.category}
      action={
        <Button variant="primary" onClick={() => onEdit?.(item?.id)}>
          ✏️ Edit Item
        </Button>
      }
    />
  )
}
