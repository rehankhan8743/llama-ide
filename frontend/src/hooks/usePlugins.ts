import { useState, useEffect, useCallback } from 'react';
import {
  listPlugins,
  enablePlugin as apiEnablePlugin,
  disablePlugin as apiDisablePlugin,
  reloadPlugin as apiReloadPlugin,
  getPluginManifest,
  PluginInfo,
  PluginManifest
} from '@/api/plugins';

interface UsePluginsReturn {
  plugins: PluginInfo[];
  loading: boolean;
  error: string | null;
  refreshPlugins: () => Promise<void>;
  enablePlugin: (pluginName: string) => Promise<void>;
  disablePlugin: (pluginName: string) => Promise<void>;
  reloadPlugin: (pluginName: string) => Promise<void>;
  getManifest: (pluginName: string) => Promise<PluginManifest | null>;
}

export const usePlugins = (): UsePluginsReturn => {
  const [plugins, setPlugins] = useState<PluginInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = useCallback((err: any) => {
    const message = err.response?.data?.detail || err.message || 'An error occurred';
    setError(message);
    console.error('Plugins error:', err);
  }, []);

  const refreshPlugins = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await listPlugins();
      setPlugins(response.plugins);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  const enablePlugin = useCallback(async (pluginName: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiEnablePlugin(pluginName);
      await refreshPlugins();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [refreshPlugins, handleError]);

  const disablePlugin = useCallback(async (pluginName: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiDisablePlugin(pluginName);
      await refreshPlugins();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [refreshPlugins, handleError]);

  const reloadPlugin = useCallback(async (pluginName: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiReloadPlugin(pluginName);
      await refreshPlugins();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, [refreshPlugins, handleError]);

  const getManifest = useCallback(async (pluginName: string): Promise<PluginManifest | null> => {
    try {
      return await getPluginManifest(pluginName);
    } catch (err: any) {
      handleError(err);
      return null;
    }
  }, [handleError]);

  // Initial load
  useEffect(() => {
    refreshPlugins();
  }, [refreshPlugins]);

  return {
    plugins,
    loading,
    error,
    refreshPlugins,
    enablePlugin,
    disablePlugin,
    reloadPlugin,
    getManifest
  };
};

export default usePlugins;
