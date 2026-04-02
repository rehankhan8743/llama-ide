import React, { useState } from 'react';
import { usePlugins } from '@/hooks/usePlugins';
import {
  FiPackage,
  FiRefreshCw,
  FiPower,
  FiInfo
} from 'react-icons/fi';

const PluginManager: React.FC = () => {
  const {
    plugins,
    loading,
    error,
    refreshPlugins,
    enablePlugin,
    disablePlugin,
    reloadPlugin,
    getManifest
  } = usePlugins();

  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);
  const [pluginDetails, setPluginDetails] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);

  const handleViewDetails = async (pluginName: string) => {
    setSelectedPlugin(pluginName);
    try {
      const manifest = await getManifest(pluginName);
      setPluginDetails(manifest);
      setShowDetails(true);
    } catch (err) {
      console.error('Failed to load plugin details:', err);
    }
  };

  const handleAction = async (action: 'enable' | 'disable' | 'reload', pluginName: string) => {
    try {
      switch (action) {
        case 'enable':
          await enablePlugin(pluginName);
          break;
        case 'disable':
          await disablePlugin(pluginName);
          break;
        case 'reload':
          await reloadPlugin(pluginName);
          break;
      }
    } catch (err) {
      alert(`Failed to ${action} plugin`);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Plugin Manager</h2>
          <button
            onClick={refreshPlugins}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <FiRefreshCw className={loading ? 'animate-spin' : ''} size={18} />
          </button>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Extend functionality with plugins
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 text-red-500">
          Error: {error}
        </div>
      )}

      {/* Plugin List */}
      <div className="flex-grow overflow-y-auto p-4">
        {plugins.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            {loading ? 'Loading plugins...' : 'No plugins installed'}
          </div>
        ) : (
          <div className="space-y-3">
            {plugins.map((plugin) => (
              <div
                key={plugin.manifest?.name || plugin.name}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-start space-x-3">
                    <FiPackage className="mt-1 text-blue-500" size={20} />
                    <div>
                      <div className="font-medium">{plugin.manifest?.name || plugin.name}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {plugin.manifest?.description || plugin.description}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Version {plugin.manifest?.version || plugin.version}
                      </div>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleViewDetails(plugin.manifest?.name || plugin.name)}
                      className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      <FiInfo size={16} />
                    </button>

                    {plugin.enabled ? (
                      <button
                        onClick={() => handleAction('disable', plugin.manifest?.name || plugin.name)}
                        className="p-2 text-red-500 hover:text-red-700"
                      >
                        <FiPower size={16} />
                      </button>
                    ) : (
                      <button
                        onClick={() => handleAction('enable', plugin.manifest?.name || plugin.name)}
                        className="p-2 text-green-500 hover:text-green-700"
                      >
                        <FiPower size={16} />
                      </button>
                    )}
                  </div>
                </div>

                <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
                  <div className="flex items-center">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      plugin.enabled
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                      {plugin.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>

                  <button
                    onClick={() => handleAction('reload', plugin.manifest?.name || plugin.name)}
                    className="text-xs text-blue-500 hover:text-blue-700"
                  >
                    Reload
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Plugin Details Modal */}
      {showDetails && pluginDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Plugin Details</h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Name</div>
                <div className="text-sm">{pluginDetails.name}</div>
              </div>

              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Version</div>
                <div className="text-sm">{pluginDetails.version}</div>
              </div>

              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</div>
                <div className="text-sm">{pluginDetails.description}</div>
              </div>

              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Author</div>
                <div className="text-sm">{pluginDetails.author}</div>
              </div>

              {pluginDetails.keywords && pluginDetails.keywords.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Keywords</div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {pluginDetails.keywords.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {pluginDetails.homepage && (
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300">Homepage</div>
                  <a
                    href={pluginDetails.homepage}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-500 hover:text-blue-700"
                  >
                    {pluginDetails.homepage}
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PluginManager;
