import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/debug`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DebugSession {
  id: string;
  name: string;
  language: string;
  status: 'running' | 'paused' | 'stopped';
  breakpoints: number[];
  currentLine?: number;
  variables: Record<string, unknown>;
  callStack: string[];
}

export interface Breakpoint {
  id: string;
  file: string;
  line: number;
  condition?: string;
  enabled: boolean;
}

export const debugApi = {
  // Start a debug session
  start: async (filePath: string, language: string): Promise<DebugSession> => {
    const response = await api.post('/start', {
      file_path: filePath,
      language,
    });
    return response.data;
  },

  // Stop a debug session
  stop: async (sessionId: string): Promise<void> => {
    await api.post(`/stop/${sessionId}`);
  },

  // Pause execution
  pause: async (sessionId: string): Promise<void> => {
    await api.post(`/pause/${sessionId}`);
  },

  // Continue execution
  continue: async (sessionId: string): Promise<void> => {
    await api.post(`/continue/${sessionId}`);
  },

  // Step over
  stepOver: async (sessionId: string): Promise<void> => {
    await api.post(`/step-over/${sessionId}`);
  },

  // Step into
  stepInto: async (sessionId: string): Promise<void> => {
    await api.post(`/step-into/${sessionId}`);
  },

  // Step out
  stepOut: async (sessionId: string): Promise<void> => {
    await api.post(`/step-out/${sessionId}`);
  },

  // Add breakpoint
  addBreakpoint: async (
    sessionId: string,
    file: string,
    line: number,
    condition?: string
  ): Promise<Breakpoint> => {
    const response = await api.post(`/breakpoints/${sessionId}`, {
      file,
      line,
      condition,
    });
    return response.data;
  },

  // Remove breakpoint
  removeBreakpoint: async (
    sessionId: string,
    breakpointId: string
  ): Promise<void> => {
    await api.delete(`/breakpoints/${sessionId}/${breakpointId}`);
  },

  // Get all breakpoints
  getBreakpoints: async (sessionId: string): Promise<Breakpoint[]> => {
    const response = await api.get(`/breakpoints/${sessionId}`);
    return response.data;
  },

  // Get variables at current scope
  getVariables: async (sessionId: string): Promise<Record<string, unknown>> => {
    const response = await api.get(`/variables/${sessionId}`);
    return response.data;
  },

  // Evaluate expression
  evaluate: async (
    sessionId: string,
    expression: string
  ): Promise<unknown> => {
    const response = await api.post(`/evaluate/${sessionId}`, {
      expression,
    });
    return response.data;
  },

  // Get call stack
  getCallStack: async (sessionId: string): Promise<string[]> => {
    const response = await api.get(`/call-stack/${sessionId}`);
    return response.data;
  },

  // Get debug session status
  getStatus: async (sessionId: string): Promise<DebugSession> => {
    const response = await api.get(`/status/${sessionId}`);
    return response.data;
  },

  // Get all active debug sessions
  getSessions: async (): Promise<DebugSession[]> => {
    const response = await api.get('/sessions');
    return response.data;
  },
};
