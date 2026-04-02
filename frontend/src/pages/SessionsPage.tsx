import { useState } from 'react';
import { Plus, Clock, Trash2, Edit2, FolderOpen } from 'lucide-react';
import { useSession } from '../hooks/useSession';
import type { Session } from '../types';

export function SessionsPage() {
  const { sessions, currentSession, createSession, loadSession, deleteSession, renameSession } = useSession();
  const [newSessionName, setNewSessionName] = useState('');
  const [editingSession, setEditingSession] = useState<string | null>(null);
  const [editName, setEditName] = useState('');

  const handleCreateSession = () => {
    if (newSessionName.trim()) {
      createSession(newSessionName.trim());
      setNewSessionName('');
    }
  };

  const handleRename = (sessionId: string) => {
    if (editName.trim()) {
      renameSession(sessionId, editName.trim());
      setEditingSession(null);
      setEditName('');
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  return (
    <div className="h-full flex flex-col p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Sessions</h1>
        <div className="flex gap-2">
          <input
            type="text"
            value={newSessionName}
            onChange={(e) => setNewSessionName(e.target.value)}
            placeholder="New session name..."
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500"
            onKeyDown={(e) => e.key === 'Enter' && handleCreateSession()}
          />
          <button
            onClick={handleCreateSession}
            disabled={!newSessionName.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sessions.map((session: Session) => (
          <div
            key={session.id}
            className={`p-4 rounded-lg border transition-all cursor-pointer ${
              currentSession?.id === session.id
                ? 'bg-blue-900/30 border-blue-500'
                : 'bg-gray-800 border-gray-700 hover:border-gray-600'
            }`}
            onClick={() => loadSession(session.id)}
          >
            <div className="flex items-start justify-between mb-3">
              {editingSession === session.id ? (
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onBlur={() => handleRename(session.id)}
                  onKeyDown={(e) => {
                    e.stopPropagation();
                    if (e.key === 'Enter') handleRename(session.id);
                    if (e.key === 'Escape') {
                      setEditingSession(null);
                      setEditName('');
                    }
                  }}
                  autoFocus
                  className="px-2 py-1 bg-gray-700 rounded text-sm"
                />
              ) : (
                <h3 className="font-semibold text-lg">{session.name}</h3>
              )}
              <div className="flex gap-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingSession(session.id);
                    setEditName(session.name);
                  }}
                  className="p-1 hover:bg-gray-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="p-1 hover:bg-red-900/50 text-red-400 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
              <span>Updated: {formatDate(new Date(session.updated_at))}</span>
            </div>

            {currentSession?.id === session.id && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <span className="text-xs text-blue-400 font-medium">Currently Active</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {sessions.length === 0 && (
        <div className="flex flex-col items-center justify-center flex-1 text-gray-500">
          <FolderOpen className="w-16 h-16 mb-4 opacity-50" />
          <p className="text-lg">No sessions yet</p>
          <p className="text-sm">Create a new session to get started</p>
        </div>
      )}
    </div>
  );
}

export default SessionsPage;
