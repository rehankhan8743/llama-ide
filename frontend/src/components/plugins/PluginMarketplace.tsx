import React, { useState } from 'react';
import {
  FiDownload,
  FiSearch,
  FiStar,
  FiUsers
} from 'react-icons/fi';

interface MarketplacePlugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  downloads: number;
  rating: number;
  tags: string[];
  installed: boolean;
}

const PluginMarketplace: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');

  // Mock marketplace plugins
  const marketplacePlugins: MarketplacePlugin[] = [
    {
      id: '1',
      name: 'Python Debugger',
      description: 'Advanced debugging tools for Python development',
      version: '2.1.0',
      author: 'DevTools Inc',
      downloads: 15420,
      rating: 4.8,
      tags: ['debugging', 'python'],
      installed: false
    },
    {
      id: '2',
      name: 'Theme Pack Pro',
      description: 'Professional themes for enhanced coding experience',
      version: '1.3.2',
      author: 'Design Studio',
      downloads: 8920,
      rating: 4.6,
      tags: ['theme', 'customization'],
      installed: true
    },
    {
      id: '3',
      name: 'Git Integration Plus',
      description: 'Enhanced Git features with visual commit graphs',
      version: '3.0.1',
      author: 'VCS Team',
      downloads: 22150,
      rating: 4.9,
      tags: ['git', 'version-control'],
      installed: false
    }
  ];

  const filteredPlugins = marketplacePlugins.filter(plugin => {
    const matchesSearch = plugin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         plugin.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = category === 'all' || plugin.tags.includes(category);
    return matchesSearch && matchesCategory;
  });

  const handleInstall = (pluginId: string) => {
    console.log(`Installing plugin ${pluginId}`);
    alert(`Plugin installation started. This is a demo - actual installation would happen here.`);
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold">Plugin Marketplace</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Discover and install plugins to extend functionality
        </p>
      </div>

      {/* Search and Filters */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex space-x-2">
          <div className="relative flex-grow">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search plugins..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
            />
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
          >
            <option value="all">All Categories</option>
            <option value="debugging">Debugging</option>
            <option value="theme">Themes</option>
            <option value="git">Git</option>
            <option value="language">Languages</option>
          </select>
        </div>
      </div>

      {/* Plugin Grid */}
      <div className="flex-grow overflow-y-auto p-4">
        {filteredPlugins.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No plugins found matching your search
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredPlugins.map((plugin) => (
              <div
                key={plugin.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{plugin.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {plugin.description}
                    </p>
                  </div>
                  <div className="flex items-center bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-2 py-1 rounded text-xs">
                    <FiStar className="mr-1" size={12} />
                    {plugin.rating}
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {plugin.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="mt-3 flex justify-between items-center text-xs text-gray-500 dark:text-gray-400">
                  <div className="flex items-center">
                    <FiUsers className="mr-1" size={14} />
                    {plugin.downloads.toLocaleString()}
                  </div>
                  <div>v{plugin.version} by {plugin.author}</div>
                </div>

                <div className="mt-4 flex space-x-2">
                  {plugin.installed ? (
                    <button
                      disabled
                      className="flex-grow py-2 px-3 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-sm"
                    >
                      Installed
                    </button>
                  ) : (
                    <button
                      onClick={() => handleInstall(plugin.id)}
                      className="flex-grow py-2 px-3 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm flex items-center justify-center"
                    >
                      <FiDownload className="mr-2" size={14} />
                      Install
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PluginMarketplace;
