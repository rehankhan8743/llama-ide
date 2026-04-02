import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/security`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SecurityScanResult {
  id: string;
  file: string;
  findings: SecurityFinding[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  scannedAt: Date;
}

export interface SecurityFinding {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  message: string;
  line?: number;
  column?: number;
  code?: string;
  recommendation?: string;
}

export interface VulnerabilityReport {
  dependencies: {
    name: string;
    version: string;
    vulnerabilities: {
      id: string;
      severity: string;
      description: string;
      fixedIn?: string;
    }[];
  }[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export const securityApi = {
  // Scan file for security issues
  scanFile: async (filePath: string): Promise<SecurityScanResult> => {
    const response = await api.post('/scan/file', {
      file_path: filePath,
    });
    return response.data;
  },

  // Scan project for security issues
  scanProject: async (projectPath?: string): Promise<SecurityScanResult[]> => {
    const response = await api.post('/scan/project', {
      project_path: projectPath,
    });
    return response.data;
  },

  // Check dependencies for vulnerabilities
  checkDependencies: async (
    manifestPath?: string
  ): Promise<VulnerabilityReport> => {
    const response = await api.post('/dependencies', {
      manifest_path: manifestPath,
    });
    return response.data;
  },

  // Get security scan history
  getScanHistory: async (): Promise<SecurityScanResult[]> => {
    const response = await api.get('/history');
    return response.data;
  },

  // Get specific scan result
  getScanResult: async (scanId: string): Promise<SecurityScanResult> => {
    const response = await api.get(`/scan/${scanId}`);
    return response.data;
  },

  // Get security policies
  getPolicies: async (): Promise<
    { id: string; name: string; enabled: boolean; rules: string[] }[]
  > => {
    const response = await api.get('/policies');
    return response.data;
  },

  // Update security policy
  updatePolicy: async (
    policyId: string,
    updates: { enabled?: boolean; rules?: string[] }
  ): Promise<void> => {
    await api.put(`/policies/${policyId}`, updates);
  },

  // Get secret scanning results
  getSecretFindings: async (): Promise<
    {
      id: string;
      file: string;
      line: number;
      type: string;
      secret: string;
    }[]
  > => {
    const response = await api.get('/secrets');
    return response.data;
  },

  // Ignore a finding
  ignoreFinding: async (
    findingId: string,
    reason: string
  ): Promise<void> => {
    await api.post(`/findings/${findingId}/ignore`, { reason });
  },

  // Get security dashboard data
  getDashboardData: async (): Promise<{
    totalScans: number;
    totalFindings: number;
    findingsBySeverity: Record<string, number>;
    recentFindings: SecurityFinding[];
    trends: { date: string; findings: number }[];
  }> => {
    const response = await api.get('/dashboard');
    return response.data;
  },
};
