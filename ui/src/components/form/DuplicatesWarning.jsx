import React from 'react'
import { Alert } from '../UI'

export default function DuplicatesWarning({ showDuplicates, duplicates }) {
  if (!showDuplicates || !duplicates.length) return null

  return (
    <Alert
      type="warning"
      title="Potential Duplicates Found"
      message={`${duplicates.length} similar item(s) already exist. Please review before saving.`}
    >
      <div className="mt-3 space-y-2">
        {duplicates.map(dup => (
          <div key={dup.id} className="text-sm text-gray-700 p-2 bg-yellow-50 rounded">
            <div className="font-medium">{dup.name}</div>
            <div className="text-xs">{dup.description}</div>
          </div>
        ))}
      </div>
    </Alert>
  )
}