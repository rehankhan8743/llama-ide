import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/analytics`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UsageStats {
  totalRequests: number;
  totalTokens: number;
  averageResponseTime: number;
  requestsByDay: { date: string; count: number }[];
  tokensByProvider: { provider: string; tokens: number }[];
}

export interface PerformanceMetrics {
  averageLatency: number;
  p50Latency: number;
  p95Latency: number;
  p99Latency: number;
  errorRate: number;
  uptime: number;
}

export interface CodeMetrics {
  totalLinesWritten: number;
  totalLinesDeleted: number;
  filesModified: number;
  languagesUsed: { language: string; percentage: number }[];
}

export const analyticsApi = {
  // Get usage statistics
  getUsageStats: async (
    startDate?: Date,
    endDate?: Date
  ): Promise<UsageStats> => {
    const response = await api.get('/usage', {
      params: {
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
      },
    });
    return response.data;
  },

  // Get performance metrics
  getPerformanceMetrics: async (): Promise<PerformanceMetrics> => {
    const response = await api.get('/performance');
    return response.data;
  },

  // Get code metrics
  getCodeMetrics: async (
    startDate?: Date,
    endDate?: Date
  ): Promise<CodeMetrics> => {
    const response = await api.get('/code', {
      params: {
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
      },
    });
    return response.data;
  },

  // Get model usage breakdown
  getModelUsage: async (
    startDate?: Date,
    endDate?: Date
  ): Promise<{ model: string; requests: number; tokens: number }[]> => {
    const response = await api.get('/models', {
      params: {
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
      },
    });
    return response.data;
  },

  // Get session analytics
  getSessionAnalytics: async (sessionId: string): Promise<unknown> => {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  // Export analytics data
  exportData: async (
    format: 'csv' | 'json',
    startDate?: Date,
    endDate?: Date
  ): Promise<Blob> => {
    const response = await api.get('/export', {
      params: {
        format,
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
      },
      responseType: 'blob',
    });
    return response.data;
  },

  // Track event
  trackEvent: async (
    event: string,
    properties?: Record<string, unknown>
  ): Promise<void> => {
    await api.post('/track', {
      event,
      properties,
      timestamp: new Date().toISOString(),
    });
  },

  // Get real-time metrics
  getRealtimeMetrics: async (): Promise<{
    activeUsers: number;
    requestsPerMinute: number;
    averageLatency: number;
  }> => {
    const response = await api.get('/realtime');
    return response.data;
  },
};
