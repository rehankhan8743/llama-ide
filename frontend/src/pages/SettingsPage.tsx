import React, { useState } from 'react';
import { useSettings } from '@/context/SettingsContext';
import { getThemes, resetSettings, exportSettings, importSettings } from '@/api/settings';

const SettingsPage: React.FC = () => {
  const { settings, updateSetting, refreshSettings } = useSettings();
  const [themes, setThemes] = useState<string[]>(['dark', 'light']);
  const [importData, setImportData] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Load themes on mount
  React.useEffect(() => {
    const fetchThemes = async () => {
      try {
        const themeList = await getThemes();
        setThemes(themeList);
      } catch (err) {
        console.error('Failed to fetch themes:', err);
      }
    };
    fetchThemes();
  }, []);

  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      try {
        await resetSettings();
        await refreshSettings();
        setSuccessMessage('Settings reset to defaults');
        setTimeout(() => setSuccessMessage(''), 3000);
      } catch (err: any) {
        setErrorMessage('Failed to reset settings: ' + err.message);
        setTimeout(() => setErrorMessage(''), 5000);
      }
    }
  };

  const handleExport = async () => {
    try {
      const data = await exportSettings();
      const dataStr = JSON.stringify(data, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

      const exportFileDefaultName = 'llama-ide-settings.json';

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    } catch (err: any) {
      setErrorMessage('Failed to export settings: ' + err.message);
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };

  const handleImport = async () => {
    try {
      const data = JSON.parse(importData);
      await importSettings(data);
      await refreshSettings();
      setSuccessMessage('Settings imported successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
      setImportData('');
    } catch (err: any) {
      setErrorMessage('Failed to import settings: ' + err.message);
      setTimeout(() => setErrorMessage(''), 5000);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Customize your llama-ide experience
        </p>
      </div>

      {successMessage && (
        <div className="mb-6 p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200 rounded">
          {successMessage}
        </div>
      )}

      {errorMessage && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded">
          {errorMessage}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Appearance Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Appearance</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Theme
              </label>
              <select
                value={settings.theme}
                onChange={(e) => updateSetting('theme', e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
              >
                {themes.map(theme => (
                  <option key={theme} value={theme}>
                    {theme.charAt(0).toUpperCase() + theme.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Font Size: {settings.font_size}px
              </label>
              <input
                type="range"
                min="10"
                max="24"
                value={settings.font_size}
                onChange={(e) => updateSetting('font_size', parseInt(e.target.value))}
                className="w-full"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="wordWrap"
                checked={settings.word_wrap}
                onChange={(e) => updateSetting('word_wrap', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="wordWrap" className="text-sm text-gray-700 dark:text-gray-300">
                Word Wrap
              </label>
            </div>
          </div>
        </div>

        {/* Editor Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Editor</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Ollama Host
              </label>
              <input
                type="text"
                value={settings.ollama_host}
                onChange={(e) => updateSetting('ollama_host', e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Default Model
              </label>
              <input
                type="text"
                value={settings.default_model}
                onChange={(e) => updateSetting('default_model', e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoSave"
                checked={settings.auto_save}
                onChange={(e) => updateSetting('auto_save', e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="autoSave" className="text-sm text-gray-700 dark:text-gray-300">
                Auto Save
              </label>
            </div>
          </div>
        </div>

        {/* AI Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">AI Settings</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Temperature: {settings.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => updateSetting('temperature', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Max Tokens: {settings.max_tokens}
              </label>
              <input
                type="range"
                min="100"
                max="4000"
                step="100"
                value={settings.max_tokens}
                onChange={(e) => updateSetting('max_tokens', parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Data Management */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Data Management</h2>

          <div className="space-y-4">
            <div className="flex space-x-2">
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Export Settings
              </button>
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Reset to Defaults
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Import Settings
              </label>
              <textarea
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                placeholder="Paste exported settings JSON here"
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 h-24"
              />
              <button
                onClick={handleImport}
                disabled={!importData}
                className="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
              >
                Import Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
