import { useState, useEffect, useCallback } from 'react';
import { sessionsApi } from '../api/sessions';
import type { Session } from '../types';

export function useSession() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await sessionsApi.getAll();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();

    // Load current session from localStorage
    const saved = localStorage.getItem('llama-ide-current-session');
    if (saved) {
      try {
        const session = JSON.parse(saved);
        setCurrentSession(session);
      } catch {
        localStorage.removeItem('llama-ide-current-session');
      }
    }
  }, [fetchSessions]);

  const createSession = useCallback(async (name: string) => {
    setLoading(true);
    try {
      const newSession = await sessionsApi.create({ name });
      setSessions((prev) => [newSession, ...prev]);
      setCurrentSession(newSession);
      localStorage.setItem('llama-ide-current-session', JSON.stringify(newSession));
      return newSession;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSession = useCallback(async (id: string) => {
    setLoading(true);
    try {
      const session = await sessionsApi.get(id);
      setCurrentSession(session);
      localStorage.setItem('llama-ide-current-session', JSON.stringify(session));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session');
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteSession = useCallback(async (id: string) => {
    setLoading(true);
    try {
      await sessionsApi.delete(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));

      if (currentSession?.id === id) {
        setCurrentSession(null);
        localStorage.removeItem('llama-ide-current-session');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session');
    } finally {
      setLoading(false);
    }
  }, [currentSession]);

  const renameSession = useCallback(async (id: string, name: string) => {
    setLoading(true);
    try {
      const updated = await sessionsApi.update(id, { name });
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? updated : s))
      );

      if (currentSession?.id === id) {
        setCurrentSession(updated);
        localStorage.setItem('llama-ide-current-session', JSON.stringify(updated));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rename session');
    } finally {
      setLoading(false);
    }
  }, [currentSession]);

  const updateSessionActivity = useCallback(async (id: string) => {
    try {
      const updated = await sessionsApi.update(id, { lastActive: new Date() });
      setSessions((prev) =>
        prev.map((s) => (s.id === id ? updated : s))
      );
    } catch (err) {
      console.error('Failed to update session activity:', err);
    }
  }, []);

  return {
    sessions,
    currentSession,
    loading,
    error,
    createSession,
    loadSession,
    deleteSession,
    renameSession,
    updateSessionActivity,
    refresh: fetchSessions,
  };
}
