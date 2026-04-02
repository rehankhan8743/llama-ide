import { useState, useEffect, useCallback } from 'react';
import {
  listFiles,
  readFile,
  saveFile,
  deleteFile,
  createFolder,
  renameFile,
  uploadFile,
  FileInfo,
  FileContent
} from '@/api/files';

interface UseFilesReturn {
  files: FileInfo[];
  currentPath: string;
  loading: boolean;
  error: string | null;
  expandedFolders: Set<string>;
  refreshFiles: () => Promise<void>;
  navigateTo: (path: string) => void;
  navigateUp: () => void;
  readFileContent: (filepath: string) => Promise<FileContent>;
  saveFileContent: (filepath: string, content: string) => Promise<void>;
  createNewFile: (filepath: string, content?: string) => Promise<void>;
  deleteItem: (filepath: string) => Promise<void>;
  createNewFolder: (folderPath: string) => Promise<void>;
  renameItem: (oldPath: string, newPath: string) => Promise<void>;
  uploadFileItem: (file: File, path: string, onProgress?: (progress: number) => void) => Promise<void>;
  toggleFolder: (path: string) => void;
  isExpanded: (path: string) => boolean;
  clearError: () => void;
}

export const useFiles = (): UseFilesReturn => {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['/']));

  const refreshFiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fileList = await listFiles(currentPath);
      setFiles(fileList);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load files';
      setError(errorMsg);
      console.error('Error refreshing files:', err);
    } finally {
      setLoading(false);
    }
  }, [currentPath]);

  const navigateTo = useCallback((path: string) => {
    setCurrentPath(path);
    // Auto-expand the folder we're navigating to
    setExpandedFolders(prev => new Set([...prev, path]));
  }, []);

  const navigateUp = useCallback(() => {
    if (currentPath === '/') return;
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
  }, [currentPath]);

  const toggleFolder = useCallback((path: string) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(path)) {
        newSet.delete(path);
      } else {
        newSet.add(path);
      }
      return newSet;
    });
  }, []);

  const isExpanded = useCallback((path: string) => {
    return expandedFolders.has(path);
  }, [expandedFolders]);

  const readFileContent = useCallback(async (filepath: string): Promise<FileContent> => {
    try {
      const content = await readFile(filepath);
      return content;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to read file';
      setError(errorMsg);
      throw err;
    }
  }, []);

  const saveFileContent = useCallback(async (filepath: string, content: string) => {
    try {
      await saveFile(filepath, content);
      await refreshFiles();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to save file';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const createNewFile = useCallback(async (filepath: string, content: string = '') => {
    try {
      await saveFile(filepath, content);
      await refreshFiles();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to create file';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const deleteItem = useCallback(async (filepath: string) => {
    try {
      await deleteFile(filepath);
      await refreshFiles();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to delete item';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const createNewFolder = useCallback(async (folderPath: string) => {
    try {
      await createFolder(folderPath);
      await refreshFiles();
      // Auto-expand the new folder's parent
      const parentPath = folderPath.split('/').slice(0, -1).join('/') || '/';
      setExpandedFolders(prev => new Set([...prev, parentPath]));
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to create folder';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const renameItem = useCallback(async (oldPath: string, newPath: string) => {
    try {
      await renameFile(oldPath, newPath);
      await refreshFiles();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to rename item';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const uploadFileItem = useCallback(async (
    file: File,
    path: string,
    onProgress?: (progress: number) => void
  ) => {
    try {
      // Simulate progress since axios doesn't support native upload progress in this simple setup
      if (onProgress) {
        onProgress(0);
        const interval = setInterval(() => {
          onProgress(Math.min(90, (Date.now() % 100)));
        }, 100);
        await uploadFile(file, path);
        clearInterval(interval);
        onProgress(100);
      } else {
        await uploadFile(file, path);
      }
      await refreshFiles();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to upload file';
      setError(errorMsg);
      throw err;
    }
  }, [refreshFiles]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load files when current path changes
  useEffect(() => {
    refreshFiles();
  }, [currentPath, refreshFiles]);

  return {
    files,
    currentPath,
    loading,
    error,
    expandedFolders,
    refreshFiles,
    navigateTo,
    navigateUp,
    readFileContent,
    saveFileContent,
    createNewFile,
    deleteItem,
    createNewFolder,
    renameItem,
    uploadFileItem,
    toggleFolder,
    isExpanded,
    clearError
  };
};

export default useFiles;
