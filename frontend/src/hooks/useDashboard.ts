import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '../api/dashboard';
import type { DashboardStats, RecentActivity } from '../api/dashboard';

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, activitiesData] = await Promise.all([
        dashboardApi.getStats(),
        dashboardApi.getRecentActivity(),
      ]);
      setStats(statsData);
      setActivities(activitiesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  const getWidgetData = useCallback(async (widgetId: string) => {
    try {
      return await dashboardApi.getWidgetData(widgetId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch widget data');
      throw err;
    }
  }, []);

  const addWidget = useCallback(async (config: Record<string, unknown>) => {
    try {
      const newWidget = await dashboardApi.addWidget(config);
      return newWidget;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add widget');
      throw err;
    }
  }, []);

  const removeWidget = useCallback(async (widgetId: string) => {
    try {
      await dashboardApi.removeWidget(widgetId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove widget');
    }
  }, []);

  const updateWidget = useCallback(
    async (widgetId: string, config: Record<string, unknown>) => {
      try {
        const updated = await dashboardApi.updateWidget(widgetId, config);
        return updated;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to update widget');
        throw err;
      }
    },
    []
  );

  return {
    stats,
    activities,
    loading,
    error,
    refresh: fetchDashboard,
    getWidgetData,
    addWidget,
    removeWidget,
    updateWidget,
  };
}
