import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/dashboard`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DashboardStats {
  totalSessions: number;
  totalMessages: number;
  totalFiles: number;
  activeTime: string;
  gitCommits: number;
  codeLines: number;
}

export interface RecentActivity {
  id: string;
  type: 'chat' | 'file' | 'git' | 'session';
  description: string;
  timestamp: Date;
}

export const dashboardApi = {
  // Get dashboard statistics
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/stats');
    return response.data;
  },

  // Get recent activity
  getRecentActivity: async (limit = 20): Promise<RecentActivity[]> => {
    const response = await api.get('/activity', {
      params: { limit },
    });
    return response.data;
  },

  // Get widget data
  getWidgetData: async (widgetId: string): Promise<unknown> => {
    const response = await api.get(`/widgets/${widgetId}/data`);
    return response.data;
  },

  // Add a new widget
  addWidget: async (config: Record<string, unknown>): Promise<unknown> => {
    const response = await api.post('/widgets', config);
    return response.data;
  },

  // Update a widget
  updateWidget: async (
    widgetId: string,
    config: Record<string, unknown>
  ): Promise<unknown> => {
    const response = await api.put(`/widgets/${widgetId}`, config);
    return response.data;
  },

  // Remove a widget
  removeWidget: async (widgetId: string): Promise<void> => {
    await api.delete(`/widgets/${widgetId}`);
  },

  // Reorder widgets
  reorderWidgets: async (widgetIds: string[]): Promise<void> => {
    await api.post('/widgets/reorder', { widget_ids: widgetIds });
  },
};
