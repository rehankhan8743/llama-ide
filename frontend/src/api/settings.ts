import axios from 'axios';

const API_BASE_URL = '/api/settings';

export interface Settings {
  theme: string;
  default_model: string;
  ollama_host: string;
  temperature: number;
  max_tokens: number;
  auto_save: boolean;
  word_wrap: boolean;
  font_size: number;
}

export interface ProviderConfig {
  name: string;
  api_key: string;
  enabled: boolean;
  model: string;
}

export interface SettingsUpdate {
  theme?: string;
  default_model?: string;
  ollama_host?: string;
  temperature?: number;
  max_tokens?: number;
  auto_save?: boolean;
  word_wrap?: boolean;
  font_size?: number;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Get current settings
export const getSettings = async (): Promise<Settings> => {
  try {
    const response = await api.get('/config');
    return response.data;
  } catch (error) {
    console.error('Error fetching settings:', error);
    throw error;
  }
};

// Update settings
export const updateSettings = async (settings: SettingsUpdate): Promise<Settings> => {
  try {
    const response = await api.put('/config', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating settings:', error);
    throw error;
  }
};

// Get provider configurations
export const getProviders = async (): Promise<Record<string, ProviderConfig>> => {
  try {
    const response = await api.get('/providers');
    return response.data;
  } catch (error) {
    console.error('Error fetching providers:', error);
    throw error;
  }
};

// Update provider configuration
export const updateProvider = async (providerName: string, config: ProviderConfig): Promise<ProviderConfig> => {
  try {
    const response = await api.put(`/providers/${providerName}`, config);
    return response.data;
  } catch (error) {
    console.error(`Error updating provider ${providerName}:`, error);
    throw error;
  }
};

// Get available themes
export const getThemes = async (): Promise<string[]> => {
  try {
    const response = await api.get('/themes');
    return response.data;
  } catch (error) {
    console.error('Error fetching themes:', error);
    throw error;
  }
};

// Reset settings to defaults
export const resetSettings = async (): Promise<any> => {
  try {
    const response = await api.post('/reset');
    return response.data;
  } catch (error) {
    console.error('Error resetting settings:', error);
    throw error;
  }
};

// Export settings
export const exportSettings = async (): Promise<Settings> => {
  try {
    const response = await api.get('/export');
    return response.data;
  } catch (error) {
    console.error('Error exporting settings:', error);
    throw error;
  }
};

// Import settings
export const importSettings = async (settings: Settings): Promise<any> => {
  try {
    const response = await api.post('/import', settings);
    return response.data;
  } catch (error) {
    console.error('Error importing settings:', error);
    throw error;
  }
};
