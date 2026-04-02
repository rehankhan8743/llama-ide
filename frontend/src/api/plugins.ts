import axios from 'axios';

const API_BASE_URL = '/api/plugins';

export interface PluginManifest {
  name: string;
  version: string;
  description: string;
  author: string;
  homepage?: string;
  keywords: string[];
  hooks: string[];
  routes: string[];
  dependencies: string[];
}

export interface PluginInfo {
  manifest: PluginManifest;
  enabled: boolean;
  loaded: boolean;
}

export interface PluginListResponse {
  plugins: PluginInfo[];
}

export interface PluginActionRequest {
  action: 'enable' | 'disable' | 'reload';
  plugin_name: string;
}

export interface HookResponse {
  hook_name: string;
  results: any[];
}

export interface PluginRoute {
  plugin: string;
  path: string;
  method: string;
  handler: string;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// List all plugins
export const listPlugins = async (): Promise<PluginListResponse> => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Error listing plugins:', error);
    throw error;
  }
};

// Perform plugin action (enable, disable, reload)
export const pluginAction = async (request: PluginActionRequest): Promise<{ status: string; plugin: string }> => {
  try {
    const response = await api.post('/actions', request);
    return response.data;
  } catch (error) {
    console.error(`Error performing plugin action ${request.action}:`, error);
    throw error;
  }
};

// Enable a plugin
export const enablePlugin = async (pluginName: string): Promise<{ status: string; plugin: string }> => {
  return pluginAction({ action: 'enable', plugin_name: pluginName });
};

// Disable a plugin
export const disablePlugin = async (pluginName: string): Promise<{ status: string; plugin: string }> => {
  return pluginAction({ action: 'disable', plugin_name: pluginName });
};

// Reload a plugin
export const reloadPlugin = async (pluginName: string): Promise<{ status: string; plugin: string }> => {
  return pluginAction({ action: 'reload', plugin_name: pluginName });
};

// Get plugin manifest
export const getPluginManifest = async (pluginName: string): Promise<PluginManifest> => {
  try {
    const response = await api.get(`/manifest/${pluginName}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching manifest for ${pluginName}:`, error);
    throw error;
  }
};

// Invoke a plugin hook
export const invokeHook = async (hookName: string, params?: Record<string, any>): Promise<HookResponse> => {
  try {
    const response = await api.post(`/hooks/${hookName}`, { params: params || {} });
    return response.data;
  } catch (error) {
    console.error(`Error invoking hook ${hookName}:`, error);
    throw error;
  }
};

// Get all plugin routes
export const getPluginRoutes = async (): Promise<{ routes: PluginRoute[] }> => {
  try {
    const response = await api.get('/routes');
    return response.data;
  } catch (error) {
    console.error('Error fetching plugin routes:', error);
    throw error;
  }
};
