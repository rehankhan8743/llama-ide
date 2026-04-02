import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  SessionState,
  SessionSummary,
  createSession,
  getSession,
  updateSession,
  listSessions,
  cloneSession,
  deleteSession
} from '@/api/sessions';

interface SessionContextType {
  currentSession: SessionState | null;
  sessions: SessionSummary[];
  loading: boolean;
  error: string | null;
  createNewSession: (name: string) => Promise<SessionState>;
  loadSession: (sessionId: string) => Promise<void>;
  saveSession: () => Promise<void>;
  listAllSessions: () => Promise<void>;
  cloneCurrentSession: (name: string) => Promise<SessionState>;
  deleteSessionById: (sessionId: string) => Promise<void>;
  updateSessionName: (name: string) => Promise<void>;
  updateChatHistory: (chatHistory: any[]) => void;
  updateEditorFiles: (editorFiles: any[]) => void;
  updateActiveFile: (filepath: string) => void;
  updateSettings: (settings: Record<string, any>) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentSession, setCurrentSession] = useState<SessionState | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err.response?.data?.detail || err.message || 'An error occurred';
    setError(message);
    console.error('Session error:', err);
  };

  const createNewSession = async (name: string): Promise<SessionState> => {
    setLoading(true);
    setError(null);
    try {
      const session = await createSession({ name });
      setCurrentSession(session);
      await listAllSessions();
      return session;
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const loadSession = async (sessionId: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const session = await getSession(sessionId);
      setCurrentSession(session);
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const saveSession = async (): Promise<void> => {
    if (!currentSession) return;

    setLoading(true);
    setError(null);
    try {
      const updated = await updateSession(currentSession.id, {
        name: currentSession.name,
        chat_history: currentSession.chat_history,
        editor_files: currentSession.editor_files,
        active_filepath: currentSession.active_filepath,
        settings: currentSession.settings,
        git_branch: currentSession.git_branch
      });
      setCurrentSession(updated);
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const listAllSessions = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const sessionList = await listSessions();
      setSessions(sessionList);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const cloneCurrentSession = async (name: string): Promise<SessionState> => {
    if (!currentSession) throw new Error("No current session");

    setLoading(true);
    setError(null);
    try {
      const cloned = await cloneSession(currentSession.id, name);
      await listAllSessions();
      return cloned;
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteSessionById = async (sessionId: string): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await deleteSession(sessionId);
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
      }
      await listAllSessions();
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateSessionName = async (name: string): Promise<void> => {
    if (!currentSession) return;

    setCurrentSession(prev => prev ? { ...prev, name } : null);
    try {
      await updateSession(currentSession.id, { name });
      await listAllSessions();
    } catch (err: any) {
      handleError(err);
    }
  };

  const updateChatHistory = (chatHistory: any[]): void => {
    setCurrentSession(prev => prev ? { ...prev, chat_history: chatHistory } : null);
  };

  const updateEditorFiles = (editorFiles: any[]): void => {
    setCurrentSession(prev => prev ? { ...prev, editor_files: editorFiles } : null);
  };

  const updateActiveFile = (filepath: string): void => {
    setCurrentSession(prev => prev ? { ...prev, active_filepath: filepath } : null);
  };

  const updateSettings = (settings: Record<string, any>): void => {
    setCurrentSession(prev => prev ? { ...prev, settings } : null);
  };

  // Load sessions on mount
  useEffect(() => {
    listAllSessions();
  }, []);

  return (
    <SessionContext.Provider value={{
      currentSession,
      sessions,
      loading,
      error,
      createNewSession,
      loadSession,
      saveSession,
      listAllSessions,
      cloneCurrentSession,
      deleteSessionById,
      updateSessionName,
      updateChatHistory,
      updateEditorFiles,
      updateActiveFile,
      updateSettings
    }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = (): SessionContextType => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
