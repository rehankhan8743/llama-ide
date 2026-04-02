import React, { createContext, useContext, useState, useEffect } from 'react';
import { Settings, getSettings, updateSettings } from '@/api/settings';

interface SettingsContextType {
  settings: Settings;
  loading: boolean;
  error: string | null;
  updateSetting: (key: keyof Settings, value: any) => Promise<void>;
  refreshSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>({
    theme: 'dark',
    default_model: 'llama2',
    ollama_host: 'http://localhost:11434',
    temperature: 0.7,
    max_tokens: 1000,
    auto_save: true,
    word_wrap: true,
    font_size: 14
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const fetchedSettings = await getSettings();
      setSettings(fetchedSettings);
    } catch (err: any) {
      setError(err.message || 'Failed to load settings');
      console.error('Error loading settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key: keyof Settings, value: any) => {
    try {
      const updateData = { [key]: value };
      const updatedSettings = await updateSettings(updateData);
      setSettings(updatedSettings);
    } catch (err: any) {
      setError(err.message || 'Failed to update setting');
      console.error('Error updating setting:', err);
      throw err;
    }
  };

  useEffect(() => {
    refreshSettings();
  }, []);

  return (
    <SettingsContext.Provider value={{
      settings,
      loading,
      error,
      updateSetting,
      refreshSettings
    }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = (): SettingsContextType => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
