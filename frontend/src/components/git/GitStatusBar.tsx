import React from 'react';
import { useGit } from '@/hooks/useGit';
import {
  FiGitBranch,
  FiArrowUp,
  FiArrowDown,
  FiRefreshCw
} from 'react-icons/fi';

const GitStatusBar: React.FC = () => {
  const { status, loading, refreshStatus } = useGit();

  if (!status) {
    return (
      <div className="flex items-center px-3 py-1 text-xs text-gray-500">
        <span>Loading git status...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center px-3 py-1 text-xs bg-gray-100 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700">
      <div className="flex items-center mr-4">
        <FiGitBranch className="mr-1" />
        <span>{status.branch || 'No branch'}</span>
      </div>

      {!status.clean && (
        <div className="flex items-center mr-4 text-yellow-600 dark:text-yellow-400">
          <span>{status.status.length} changes</span>
        </div>
      )}

      {status.ahead > 0 && (
        <div className="flex items-center mr-4 text-green-600 dark:text-green-400">
          <FiArrowUp className="mr-1" />
          <span>{status.ahead}</span>
        </div>
      )}

      {status.behind > 0 && (
        <div className="flex items-center mr-4 text-blue-600 dark:text-blue-400">
          <FiArrowDown className="mr-1" />
          <span>{status.behind}</span>
        </div>
      )}

      <button
        onClick={refreshStatus}
        disabled={loading}
        className="ml-auto p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
      >
        <FiRefreshCw className={loading ? 'animate-spin' : ''} size={14} />
      </button>
    </div>
  );
};

export default GitStatusBar;
