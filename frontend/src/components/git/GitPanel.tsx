import React, { useState } from 'react';
import { useGit } from '@/hooks/useGit';
import GitStatusBar from '@/components/git/GitStatusBar';
import {
  FiGitBranch,
  FiPlus,
  FiRefreshCw,
  FiArrowUp,
  FiArrowDown
} from 'react-icons/fi';

const GitPanel: React.FC = () => {
  const {
    status,
    commits,
    branches,
    loading,
    error,
    refreshStatus,
    stage,
    unstage,
    commit,
    createNewBranch,
    switchToBranch
  } = useGit();

  const [commitMessage, setCommitMessage] = useState('');
  const [newBranchName, setNewBranchName] = useState('');
  const [showNewBranchInput, setShowNewBranchInput] = useState(false);

  const handleCommit = () => {
    if (commitMessage.trim()) {
      commit(commitMessage);
      setCommitMessage('');
    }
  };

  const handleCreateBranch = () => {
    if (newBranchName.trim()) {
      createNewBranch(newBranchName);
      setNewBranchName('');
      setShowNewBranchInput(false);
    }
  };

  if (error) {
    return (
      <div className="p-4 text-red-500">
        Error: {error}
      </div>
    );
  }

  if (!status) {
    return (
      <div className="p-4 text-center">
        Loading git status...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Status Bar */}
      <GitStatusBar />

      {/* Changes Section */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-medium">Changes</h3>
          <button
            onClick={refreshStatus}
            disabled={loading}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <FiRefreshCw className={loading ? 'animate-spin' : ''} size={16} />
          </button>
        </div>

        {status.clean ? (
          <div className="text-sm text-gray-500 text-center py-4">
            No changes to commit
          </div>
        ) : (
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {status.status.map((item, index) => {
              const statusChar = item[0];
              const filePath = item.substring(3);
              const isStaged = statusChar !== ' ' && statusChar !== '?';

              return (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center">
                    <span className="mr-2 w-4 text-center">
                      {statusChar === 'M' ? '📝' :
                       statusChar === 'A' ? '➕' :
                       statusChar === 'D' ? '➖' :
                       statusChar === '?' ? '🆕' : statusChar}
                    </span>
                    <span className="truncate max-w-[200px]">{filePath}</span>
                  </div>
                  <div className="flex space-x-1">
                    {isStaged ? (
                      <button
                        onClick={() => unstage(filePath)}
                        className="text-xs px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded"
                      >
                        Unstage
                      </button>
                    ) : (
                      <button
                        onClick={() => stage(filePath)}
                        className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded"
                      >
                        Stage
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Commit Section */}
      {!status.clean && (
        <div className="border-b border-gray-200 dark:border-gray-700 p-4">
          <h3 className="font-medium mb-2">Commit</h3>
          <div className="flex">
            <input
              type="text"
              value={commitMessage}
              onChange={(e) => setCommitMessage(e.target.value)}
              placeholder="Commit message"
              className="flex-grow p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-l bg-white dark:bg-gray-800"
            />
            <button
              onClick={handleCommit}
              disabled={!commitMessage.trim() || loading}
              className="px-4 py-2 bg-green-500 text-white rounded-r disabled:opacity-50"
            >
              Commit
            </button>
          </div>
        </div>
      )}

      {/* Branches Section */}
      <div className="border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-medium">Branches</h3>
          <button
            onClick={() => setShowNewBranchInput(!showNewBranchInput)}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <FiPlus size={16} />
          </button>
        </div>

        {showNewBranchInput && (
          <div className="flex mb-3">
            <input
              type="text"
              value={newBranchName}
              onChange={(e) => setNewBranchName(e.target.value)}
              placeholder="New branch name"
              className="flex-grow p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-l bg-white dark:bg-gray-800"
              onKeyDown={(e) => e.key === 'Enter' && handleCreateBranch()}
            />
            <button
              onClick={handleCreateBranch}
              className="px-3 py-2 bg-blue-500 text-white rounded-r"
            >
              Create
            </button>
          </div>
        )}

        <div className="space-y-1 max-h-40 overflow-y-auto">
          {branches.map((branch, index) => (
            <div
              key={index}
              className={`flex items-center p-2 rounded cursor-pointer ${
                branch.current
                  ? 'bg-blue-100 dark:bg-blue-900'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
              onClick={() => !branch.current && switchToBranch(branch.name)}
            >
              <FiGitBranch className="mr-2" />
              <span className="text-sm flex-grow truncate">
                {branch.name}
                {branch.remote && ` (${branch.remote})`}
              </span>
              {branch.current && (
                <span className="text-xs bg-blue-500 text-white px-2 py-1 rounded">
                  Current
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Commits */}
      <div className="flex-grow p-4">
        <h3 className="font-medium mb-3">Recent Commits</h3>
        <div className="space-y-3 max-h-60 overflow-y-auto">
          {commits.length === 0 ? (
            <div className="text-sm text-gray-500 text-center py-4">
              No commits yet
            </div>
          ) : (
            commits.map((commitItem, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-700 pb-3 last:border-0">
                <div className="flex justify-between">
                  <span className="font-mono text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                    {commitItem.short_hash}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(commitItem.date).toLocaleDateString()}
                  </span>
                </div>
                <div className="mt-1 text-sm">{commitItem.message}</div>
                <div className="text-xs text-gray-500 mt-1">{commitItem.author}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default GitPanel;
