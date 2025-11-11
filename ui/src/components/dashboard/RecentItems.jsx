import { Card } from '../UI'

export default function RecentItems({ items, loading, onNavigate }) {
    console.log(items);
  return (
    <Card className="bg-white">
      <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Items</h2>
      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading recent items...</div>
      ) : items && items.length > 0 ? (
        <div className="space-y-3">
          {items.map(item => (
            <div
              key={item.id}
              onClick={() => onNavigate('item-detail', { itemId: item.id })}
              className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition"
            >
              <div className="font-medium text-gray-900">{item.name}</div>
              <div className="text-sm text-gray-600">{item.description}</div>
              {item.category && (
                <div className="text-xs text-gray-500 mt-1">Category: {item.category}</div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">No items found</div>
      )}
    </Card>
  )
}