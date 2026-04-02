import { useState, useEffect, useCallback } from 'react';
import { providersApi } from '../api/providers';
import type { ModelProvider } from '../types';

export function useProviders() {
  const [providers, setProviders] = useState<ModelProvider[]>([]);
  const [currentProvider, setCurrentProvider] = useState<ModelProvider | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProviders = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await providersApi.getAll();
      setProviders(data);

      // Set current provider to first enabled one or Ollama default
      const enabled = data.find((p: ModelProvider) => p.enabled);
      if (enabled) {
        setCurrentProvider(enabled);
      } else if (data.length > 0) {
        setCurrentProvider(data[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch providers');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  const updateProvider = useCallback(async (id: string, updates: Partial<ModelProvider>) => {
    try {
      const updated = await providersApi.update(id, updates);
      setProviders((prev) =>
        prev.map((p) => (p.id === id ? updated : p))
      );

      if (currentProvider?.id === id) {
        setCurrentProvider(updated);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update provider');
    }
  }, [currentProvider]);

  const setProviderEnabled = useCallback(async (id: string, enabled: boolean) => {
    await updateProvider(id, { enabled });

    // If enabling, make it current
    if (enabled) {
      const provider = providers.find((p) => p.id === id);
      if (provider) {
        setCurrentProvider(provider);
      }
    }
  }, [providers, updateProvider]);

  const selectProvider = useCallback((id: string) => {
    const provider = providers.find((p) => p.id === id);
    if (provider) {
      setCurrentProvider(provider);
    }
  }, [providers]);

  const selectModel = useCallback((providerId: string, model: string) => {
    updateProvider(providerId, { model });
  }, [updateProvider]);

  const testConnection = useCallback(async (id: string): Promise<boolean> => {
    try {
      return await providersApi.test(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection test failed');
      return false;
    }
  }, []);

  const getAvailableModels = useCallback(async (providerId: string): Promise<string[]> => {
    try {
      return await providersApi.getModels(providerId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch models');
      return [];
    }
  }, []);

  return {
    providers,
    currentProvider,
    loading,
    error,
    refresh: fetchProviders,
    updateProvider,
    setProviderEnabled,
    selectProvider,
    selectModel,
    testConnection,
    getAvailableModels,
  };
}
