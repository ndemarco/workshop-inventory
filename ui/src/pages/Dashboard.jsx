import { useEffect, useState } from 'react'
import APIService from '../services/api'
import { useAsync } from '../hooks/useAsync'
import { PageHeader, Card, Button, Alert } from '../components/UI'
import StatsCard from '../components/dashboard/StatsCard'
import RecentItems from '../components/dashboard/RecentItems'
import QuickActions from '../components/dashboard/QuickActions'

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
        <StatsCard
          title="Total Items"
          value={dashboardStats.items}
          loading={statsLoading}
          colorClass="text-primary-600"
          onClick={() => onNavigate('items')}
          linkText="View items →"
        />

        <StatsCard
          title="Storage Modules"
          value={dashboardStats.modules}
          loading={statsLoading}
          colorClass="text-secondary-600"
          onClick={() => onNavigate('modules')}
          linkText="View modules →"
        />

        <StatsCard
          title="Storage Levels"
          value={dashboardStats.levels}
          loading={statsLoading}
          colorClass="text-info-600"
        />

        <StatsCard
          title="Storage Locations"
          value={dashboardStats.locations}
          loading={statsLoading}
          colorClass="text-success-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecentItems
            items={recentItems}
            loading={itemsLoading}
            onNavigate={onNavigate}
          />
        </div>

        <div>
          <QuickActions onNavigate={onNavigate} />
        </div>
      </div>
    </div>
  )
}
