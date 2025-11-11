import React from 'react'
import { Card } from '../UI'

export default function ItemNotes({ item }) {
  if (!item?.notes) return null

  return (
    <Card>
      <h2 className="text-lg font-semibold mb-4">Notes</h2>
      <p className="text-gray-600 whitespace-pre-wrap">{item.notes}</p>
    </Card>
  )
}