import React, { useState, useEffect } from 'react';
import { getProviders, getProviderModels, ProviderConfig, ProviderModel } from '@/api/providers';

interface ModelControlsProps {
  onModelChange?: (model: string) => void;
  onTemperatureChange?: (temperature: number) => void;
  onProviderChange?: (provider: string) => void;
}

const ModelControls: React.FC<ModelControlsProps> = ({
  onModelChange,
  onTemperatureChange,
  onProviderChange
}) => {
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1000);
  const [selectedModel, setSelectedModel] = useState('llama2');
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const [providers, setProviders] = useState<Record<string, ProviderConfig>>({});
  const [models, setModels] = useState<ProviderModel[]>([]);
  const [loadingProviders, setLoadingProviders] = useState(true);
  const [loadingModels, setLoadingModels] = useState(true);

  // Fetch available providers
  useEffect(() => {
    const fetchProviders = async () => {
      try {
        const providerList = await getProviders();
        setProviders(providerList);

        // Set initial provider
        const enabledProviders = Object.entries(providerList)
          .filter(([_, config]) => config.enabled)
          .map(([name, _]) => name);

        if (enabledProviders.length > 0) {
          const initialProvider = enabledProviders[0];
          setSelectedProvider(initialProvider);
          if (onProviderChange) onProviderChange(initialProvider);

          // Set initial model for this provider
          const config = providerList[initialProvider];
          if (config.model) {
            setSelectedModel(config.model);
            if (onModelChange) onModelChange(config.model);
          }
        }
      } catch (error) {
        console.error('Failed to fetch providers:', error);
      } finally {
        setLoadingProviders(false);
      }
    };

    fetchProviders();
  }, [onModelChange, onProviderChange]);

  // Fetch models when provider changes
  useEffect(() => {
    const fetchModels = async () => {
      if (!selectedProvider) return;

      setLoadingModels(true);
      try {
        const modelList = await getProviderModels(selectedProvider);
        setModels(modelList);

        // Set first model as default if none selected
        if (modelList.length > 0 && !selectedModel) {
          setSelectedModel(modelList[0].name);
          if (onModelChange) onModelChange(modelList[0].name);
        }
      } catch (error) {
        console.error(`Failed to fetch models for ${selectedProvider}:`, error);
        setModels([]);
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, [selectedProvider, selectedModel, onModelChange]);

  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider);
    if (onProviderChange) onProviderChange(provider);

    // Reset model selection
    setSelectedModel('');
  };

  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    if (onModelChange) onModelChange(model);
  };

  const handleTemperatureChange = (temp: number) => {
    setTemperature(temp);
    if (onTemperatureChange) onTemperatureChange(temp);
  };

  return (
    <div className="mt-3 space-y-3">
      <div>
        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
          Provider
        </label>
        {loadingProviders ? (
          <div className="text-xs text-gray-500">Loading providers...</div>
        ) : (
          <select
            value={selectedProvider}
            onChange={(e) => handleProviderChange(e.target.value)}
            className="w-full p-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
          >
            {Object.entries(providers)
              .filter(([_, config]) => config.enabled)
              .map(([name, config]) => (
                <option key={name} value={name}>
                  {config.name || name}
                </option>
              ))}
          </select>
        )}
      </div>

      <div>
        <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
          Model
        </label>
        {loadingModels ? (
          <div className="text-xs text-gray-500">Loading models...</div>
        ) : (
          <select
            value={selectedModel}
            onChange={(e) => handleModelChange(e.target.value)}
            className="w-full p-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
          >
            {models.map(model => (
              <option key={model.name} value={model.name}>
                {model.display_name || model.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
            Temperature: {temperature}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => handleTemperatureChange(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
            Max Tokens: {maxTokens}
          </label>
          <input
            type="range"
            min="100"
            max="4000"
            step="100"
            value={maxTokens}
            onChange={(e) => setMaxTokens(parseInt(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
    </div>
  );
};

export default ModelControls;
