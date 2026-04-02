import React from 'react';
import { useSession } from '@/context/SessionContext';
import { FiFolder, FiSave, FiRefreshCw } from 'react-icons/fi';

const SessionStatusBar: React.FC = () => {
  const { currentSession, loading, saveSession, listAllSessions } = useSession();

  return (
    <div className="flex items-center px-3 py-1 text-xs bg-gray-100 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700">
      <div className="flex items-center mr-4">
        <FiFolder className="mr-1" />
        <span>{currentSession?.name || 'No session'}</span>
      </div>

      {currentSession && (
        <div className="flex items-center mr-4 text-gray-500 dark:text-gray-400">
          <span>Auto-save enabled</span>
        </div>
      )}

      <div className="flex space-x-2 ml-auto">
        {currentSession && (
          <button
            onClick={saveSession}
            disabled={loading}
            className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <FiSave size={14} />
          </button>
        )}
        <button
          onClick={listAllSessions}
          disabled={loading}
          className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          <FiRefreshCw className={loading ? 'animate-spin' : ''} size={14} />
        </button>
      </div>
    </div>
  );
};

export default SessionStatusBar;
