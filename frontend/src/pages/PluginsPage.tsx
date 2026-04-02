import React, { useState } from 'react';
import PluginManager from '@/components/plugins/PluginManager';
import PluginMarketplace from '@/components/plugins/PluginMarketplace';

type TabType = 'installed' | 'marketplace';

const PluginsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('installed');

  return (
    <div className="h-full flex flex-col">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
        <div className="flex px-4">
          <button
            onClick={() => setActiveTab('installed')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'installed'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            Installed Plugins
          </button>
          <button
            onClick={() => setActiveTab('marketplace')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'marketplace'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            Marketplace
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-grow overflow-hidden">
        {activeTab === 'installed' ? (
          <PluginManager />
        ) : (
          <PluginMarketplace />
        )}
      </div>
    </div>
  );
};

export default PluginsPage;
