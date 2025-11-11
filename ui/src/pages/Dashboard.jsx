import { useEffect, useState } from 'react'
import APIService from '../services/api'
import { useAsync } from '../hooks/useAsync'
import { PageHeader, Card, Button, Alert } from '../components/UI'

export default function Dashboard({ onNavigate }) {
  const [recentItems, setRecentItems] = useState([]);
  const [itemsLoading, setItemsLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    const fetchRecentItems = async () => {
      setItemsLoading(true);
      setStatsLoading(true);
      try {
        const result = await APIService.getRecentItems(5);
        const statsResult = await APIService.getStats();
        if (result.success) {
          setRecentItems(result.data);
        } else {
          setRecentItems([]);
        }

        if (statsResult.success) {  
          setStats(statsResult.data);
          setStatsLoading(false);
        } else {
          setStatsError(statsResult.error);
          setStats({
            items: 0,
            modules: 0,
            locations: 0,
            levels: 0,
          });
        }

      } catch {
        setRecentItems([]);
      } finally {
        setItemsLoading(false);
      }
    };

    fetchRecentItems();
  }, []);


  const [dashboardStats, setDashboardStats] = useState({
    items: 0,
    modules: 0,
    locations: 0,
    levels: 0,
  })

  useEffect(() => {
    if (stats) {
      setDashboardStats(stats)
    }
  }, [stats])

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Overview of your inventory" />

      {statsError && (
        <Alert type="error" title="Error loading stats" message={statsError} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-white">
          <div className="text-gray-600 text-sm font-medium mb-2">Total Items</div>
          <div className="text-3xl font-bold text-primary-600">
            {statsLoading ? '...' : dashboardStats.items}
          </div>
          <button 
            onClick={() => onNavigate('items')}
            className="text-primary-600 text-sm font-medium mt-4 hover:underline"
          >
            View items →
          </button>
        </Card>

        <Card className="bg-white">
          <div className="text-gray-600 text-sm font-medium mb-2">Storage Modules</div>
          <div className="text-3xl font-bold text-secondary-600">
            {statsLoading ? '...' : dashboardStats.modules}
          </div>
          <button 
            onClick={() => onNavigate('modules')}
            className="text-secondary-600 text-sm font-medium mt-4 hover:underline"
          >
            View modules →
          </button>
        </Card>

        <Card className="bg-white">
          <div className="text-gray-600 text-sm font-medium mb-2">Storage Levels</div>
          <div className="text-3xl font-bold text-info-600">
            {statsLoading ? '...' : dashboardStats.levels}
          </div>
        </Card>

        <Card className="bg-white">
          <div className="text-gray-600 text-sm font-medium mb-2">Storage Locations</div>
          <div className="text-3xl font-bold text-success-600">
            {statsLoading ? '...' : dashboardStats.locations}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card className="bg-white">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Items</h2>
            {itemsLoading ? (
              <div className="text-center py-8 text-gray-500">Loading recent items...</div>
            ) : recentItems && recentItems.length > 0 ? (
              <div className="space-y-3">
                {recentItems?.map(item => (
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
        </div>

        <div>
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
        </div>
      </div>
    </div>
  )
}
