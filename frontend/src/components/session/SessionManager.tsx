import React, { useState } from 'react';
import { useSession } from '@/context/SessionContext';
import {
  FiFolderPlus,
  FiFolder,
  FiTrash2,
  FiCopy,
  FiSave,
  FiRefreshCw
} from 'react-icons/fi';

const SessionManager: React.FC = () => {
  const {
    sessions,
    currentSession,
    loading,
    createNewSession,
    loadSession,
    saveSession,
    listAllSessions,
    cloneCurrentSession,
    deleteSessionById
  } = useSession();

  const [newSessionName, setNewSessionName] = useState('');
  const [showNewSessionInput, setShowNewSessionInput] = useState(false);
  const [cloningSessionId, setCloningSessionId] = useState<string | null>(null);
  const [cloneName, setCloneName] = useState('');

  const handleCreateSession = async () => {
    if (newSessionName.trim()) {
      try {
        await createNewSession(newSessionName);
        setNewSessionName('');
        setShowNewSessionInput(false);
      } catch (err) {
        alert('Failed to create session');
      }
    }
  };

  const handleCloneSession = async (sessionId: string, sessionName: string) => {
    if (cloneName.trim()) {
      try {
        await cloneCurrentSession(cloneName);
        setCloningSessionId(null);
        setCloneName('');
      } catch (err) {
        alert('Failed to clone session');
      }
    } else {
      setCloningSessionId(sessionId);
      setCloneName(`${sessionName} (copy)`);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Sessions</h2>
          <div className="flex space-x-2">
            <button
              onClick={listAllSessions}
              disabled={loading}
              className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <FiRefreshCw className={loading ? 'animate-spin' : ''} size={18} />
            </button>
            <button
              onClick={() => setShowNewSessionInput(true)}
              className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              <FiFolderPlus size={18} />
            </button>
          </div>
        </div>

        {showNewSessionInput && (
          <div className="flex mb-4">
            <input
              type="text"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder="Session name"
              className="flex-grow p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-l bg-white dark:bg-gray-800"
              onKeyDown={(e) => e.key === 'Enter' && handleCreateSession()}
              autoFocus
            />
            <button
              onClick={handleCreateSession}
              className="px-3 py-2 bg-green-500 text-white rounded-r"
            >
              Create
            </button>
            <button
              onClick={() => {
                setShowNewSessionInput(false);
                setNewSessionName('');
              }}
              className="ml-2 px-3 py-2 bg-gray-500 text-white rounded"
            >
              Cancel
            </button>
          </div>
        )}

        {currentSession && (
          <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900 rounded">
            <div>
              <div className="font-medium">{currentSession.name}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Last saved: {formatDate(currentSession.updated_at)}
              </div>
            </div>
            <button
              onClick={saveSession}
              disabled={loading}
              className="p-2 text-blue-500 hover:text-blue-700 dark:hover:text-blue-300"
            >
              <FiSave size={18} />
            </button>
          </div>
        )}
      </div>

      {/* Session List */}
      <div className="flex-grow overflow-y-auto p-4">
        {sessions.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No sessions found
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 rounded border ${
                  currentSession?.id === session.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                    : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div
                    className="cursor-pointer flex-grow"
                    onClick={() => loadSession(session.id)}
                  >
                    <div className="font-medium">{session.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      Created: {formatDate(session.created_at)}
                    </div>
                  </div>

                  <div className="flex space-x-1">
                    <button
                      onClick={() => handleCloneSession(session.id, session.name)}
                      className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      <FiCopy size={16} />
                    </button>
                    <button
                      onClick={() => deleteSessionById(session.id)}
                      className="p-1 text-red-500 hover:text-red-700"
                    >
                      <FiTrash2 size={16} />
                    </button>
                  </div>
                </div>

                {cloningSessionId === session.id && (
                  <div className="mt-3 flex">
                    <input
                      type="text"
                      value={cloneName}
                      onChange={(e) => setCloneName(e.target.value)}
                      placeholder="Cloned session name"
                      className="flex-grow p-1 text-sm border border-gray-300 dark:border-gray-600 rounded-l bg-white dark:bg-gray-800"
                      onKeyDown={(e) => e.key === 'Enter' && handleCloneSession(session.id, session.name)}
                    />
                    <button
                      onClick={() => handleCloneSession(session.id, session.name)}
                      className="px-2 py-1 bg-green-500 text-white rounded-r text-sm"
                    >
                      Clone
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
        {sessions.length} session{sessions.length !== 1 ? 's' : ''} stored locally
      </div>
    </div>
  );
};

export default SessionManager;
