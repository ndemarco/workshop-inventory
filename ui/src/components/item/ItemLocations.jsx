import React from 'react'
import { Card } from '../UI'

export default function ItemLocations({ item }) {
  return (
    <Card>
      <h2 className="text-lg font-semibold mb-4">Storage Locations</h2>
      {item?.locations && item.locations.length > 0 ? (
        <div className="space-y-2">
          {item.locations.map((loc) => (
            <div key={loc.id} className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">{loc.location?.location_name}</p>
              <p className="text-sm text-gray-600">{loc.location?.full_address}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-600">No storage locations assigned</p>
      )}
    </Card>
  )
}