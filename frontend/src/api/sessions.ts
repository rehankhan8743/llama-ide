import axios from 'axios';

const API_BASE_URL = '/api/sessions';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export interface EditorFileState {
  filepath: string;
  content: string;
  cursor_position?: { line: number; column: number };
  scroll_position?: { top: number; left: number };
  language: string;
}

export interface SessionState {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  chat_history: ChatMessage[];
  editor_files: EditorFileState[];
  active_filepath?: string;
  settings: Record<string, any>;
  git_branch?: string;
}

export interface SessionSummary {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface CreateSessionRequest {
  name: string;
  template_session_id?: string;
}

export interface UpdateSessionRequest {
  name?: string;
  chat_history?: ChatMessage[];
  editor_files?: EditorFileState[];
  active_filepath?: string;
  settings?: Record<string, any>;
  git_branch?: string;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Create a new session
export const createSession = async (request: CreateSessionRequest): Promise<SessionState> => {
  try {
    const response = await api.post('/', request);
    return response.data;
  } catch (error) {
    console.error('Error creating session:', error);
    throw error;
  }
};

// Get a session by ID
export const getSession = async (sessionId: string): Promise<SessionState> => {
  try {
    const response = await api.get(`/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error(`Error getting session ${sessionId}:`, error);
    throw error;
  }
};

// Update a session
export const updateSession = async (sessionId: string, request: UpdateSessionRequest): Promise<SessionState> => {
  try {
    const response = await api.put(`/${sessionId}`, request);
    return response.data;
  } catch (error) {
    console.error(`Error updating session ${sessionId}:`, error);
    throw error;
  }
};

// Delete a session
export const deleteSession = async (sessionId: string): Promise<any> => {
  try {
    const response = await api.delete(`/${sessionId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting session ${sessionId}:`, error);
    throw error;
  }
};

// List all sessions
export const listSessions = async (): Promise<SessionSummary[]> => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Error listing sessions:', error);
    throw error;
  }
};

// Clone a session
export const cloneSession = async (sessionId: string, name: string): Promise<SessionState> => {
  try {
    const response = await api.post(`/${sessionId}/clone`, { name });
    return response.data;
  } catch (error) {
    console.error(`Error cloning session ${sessionId}:`, error);
    throw error;
  }
};

// Export session data
export const exportSession = async (sessionId: string): Promise<SessionState> => {
  try {
    const response = await api.post(`/${sessionId}/export`);
    return response.data;
  } catch (error) {
    console.error(`Error exporting session ${sessionId}:`, error);
    throw error;
  }
};

// Import session data
export const importSession = async (sessionData: SessionState): Promise<any> => {
  try {
    const response = await api.post('/import', sessionData);
    return response.data;
  } catch (error) {
    console.error('Error importing session:', error);
    throw error;
  }
};

// API object for useSession hook
export const sessionsApi = {
  create: createSession,
  get: getSession,
  update: updateSession,
  delete: deleteSession,
  getAll: listSessions,
  clone: cloneSession,
  export: exportSession,
  import: importSession,
};
