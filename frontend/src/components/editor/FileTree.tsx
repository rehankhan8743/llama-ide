import React, { useState, useCallback } from 'react';
import { useFiles } from '@/hooks/useFiles';
import {
  FiFolder,
  FiFolderPlus,
  FiFile,
  FiFilePlus,
  FiRefreshCw,
  FiTrash2,
  FiEdit2,
  FiUpload
} from 'react-icons/fi';

interface TreeNodeProps {
  name: string;
  path: string;
  isDirectory?: boolean;
  level?: number;
  onNavigate: (path: string) => void;
  onFileSelect: (path: string) => void;
  onDelete: (path: string) => void;
  onRename: (oldPath: string, newPath: string) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({
  name,
  path,
  isDirectory = false,
  level = 0,
  onNavigate,
  onFileSelect,
  onDelete,
  onRename
}) => {
  const [isOpen, setIsOpen] = useState(level < 2); // Auto-expand first two levels
  const [isRenaming, setIsRenaming] = useState(false);
  const [newName, setNewName] = useState(name);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });

  const handleClick = () => {
    if (isDirectory) {
      setIsOpen(!isOpen);
    } else {
      onFileSelect(path);
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    setContextMenuPosition({ x: e.clientX, y: e.clientY });
    setShowContextMenu(true);
  };

  const handleRename = () => {
    if (newName && newName !== name) {
      const newPath = path.substring(0, path.lastIndexOf('/') + 1) + newName;
      onRename(path, newPath);
    }
    setIsRenaming(false);
  };

  const handleDelete = () => {
    onDelete(path);
    setShowContextMenu(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setIsRenaming(false);
      setNewName(name);
    }
  };

  return (
    <div>
      <div
        className={`flex items-center py-1 px-2 cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700 relative`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={handleClick}
        onContextMenu={handleContextMenu}
      >
        {isDirectory ? (
          <span className="mr-1">{isOpen ? '📂' : '📁'}</span>
        ) : (
          <span className="mr-1">📄</span>
        )}

        {isRenaming ? (
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onBlur={handleRename}
            onKeyDown={handleKeyDown}
            autoFocus
            className="flex-grow bg-transparent border-b border-gray-400 focus:outline-none"
          />
        ) : (
          <span className="text-sm truncate flex-grow">{name}</span>
        )}
      </div>

      {isOpen && isDirectory && (
        <div>
          {/* Children would be rendered here in a real implementation */}
        </div>
      )}

      {/* Context Menu */}
      {showContextMenu && (
        <div
          className="absolute z-10 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded shadow-lg py-1"
          style={{ left: contextMenuPosition.x, top: contextMenuPosition.y }}
        >
          {!isDirectory && (
            <button
              className="block w-full text-left px-4 py-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-sm"
              onClick={() => {
                setShowContextMenu(false);
                setIsRenaming(true);
              }}
            >
              Rename
            </button>
          )}
          <button
            className="block w-full text-left px-4 py-1 hover:bg-red-100 dark:hover:bg-red-900 text-red-600 dark:text-red-400 text-sm"
            onClick={handleDelete}
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

interface FileTreeProps {
  onFileSelect: (filepath: string) => void;
}

export const FileTree: React.FC<FileTreeProps> = ({ onFileSelect }) => {
  const {
    files,
    currentPath,
    loading,
    error,
    refreshFiles,
    navigateTo,
    readFileContent,
    deleteItem,
    createNewFolder,
    renameItem
  } = useFiles();

  const [showNewFileDialog, setShowNewFileDialog] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [isFolder, setIsFolder] = useState(false);

  const handleRefresh = () => {
    refreshFiles();
  };

  const handleCreateNew = async () => {
    if (!newFileName) return;

    const fullPath = currentPath === '/'
      ? newFileName
      : `${currentPath}/${newFileName}`;

    if (isFolder) {
      await createNewFolder(fullPath);
    } else {
      // Create empty file
      // In a real implementation, you'd need an API call to create an empty file
      // For now, we'll just create the folder
    }

    setNewFileName('');
    setShowNewFileDialog(false);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-2 border-b border-gray-200 dark:border-gray-700">
        <span className="font-semibold text-sm">Explorer</span>
        <div className="flex space-x-1">
          <button
            onClick={handleRefresh}
            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
            title="Refresh"
          >
            <FiRefreshCw size={16} />
          </button>
          <button
            onClick={() => { setIsFolder(true); setShowNewFileDialog(true); }}
            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
            title="New Folder"
          >
            <FiFolderPlus size={16} />
          </button>
        </div>
      </div>

      {/* File List */}
      <div className="flex-grow overflow-y-auto">
        {loading && <div className="p-2 text-sm text-gray-500">Loading...</div>}
        {error && <div className="p-2 text-sm text-red-500">{error}</div>}

        {!loading && !error && files.map((file) => (
          <TreeNode
            key={file.name}
            name={file.name}
            path={currentPath === '/' ? file.name : `${currentPath}/${file.name}`}
            isDirectory={file.is_dir}
            level={1}
            onNavigate={navigateTo}
            onFileSelect={onFileSelect}
            onDelete={deleteItem}
            onRename={renameItem}
          />
        ))}

        {files.length === 0 && !loading && (
          <div className="p-2 text-sm text-gray-500">No files in this folder</div>
        )}
      </div>

      {/* New File/Folder Dialog */}
      {showNewFileDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-4 rounded shadow-lg w-80">
            <h3 className="font-semibold mb-2">Create New {isFolder ? 'Folder' : 'File'}</h3>
            <input
              type="text"
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              placeholder="Name..."
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded mb-3 bg-white dark:bg-gray-700"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreateNew();
                if (e.key === 'Escape') setShowNewFileDialog(false);
              }}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowNewFileDialog(false)}
                className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateNew}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileTree;
