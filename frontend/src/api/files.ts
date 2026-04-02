import axios from 'axios';

const API_BASE_URL = '/api/files';

export interface FileInfo {
  name: string;
  is_dir: boolean;
  size?: number;
  modified?: number;
}

export interface FileContent {
  name: string;
  content: string;
  language: string;
}

export interface ExecuteResult {
  stdout: string;
  stderr: string;
  returncode: number;
}

export interface GitStatus {
  branch: string;
  clean: boolean;
  status: string[];
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// List files in a directory
export const listFiles = async (path: string = '/'): Promise<FileInfo[]> => {
  try {
    const response = await api.get('/list', { params: { path } });
    return response.data;
  } catch (error) {
    console.error('Error listing files:', error);
    throw error;
  }
};

// Read a file
export const readFile = async (filepath: string): Promise<FileContent> => {
  try {
    const response = await api.get(`/read/${filepath}`);
    return response.data;
  } catch (error) {
    console.error(`Error reading file ${filepath}:`, error);
    throw error;
  }
};

// Save a file
export const saveFile = async (filepath: string, content: string): Promise<any> => {
  try {
    const response = await api.post('/save', content, {
      params: { filepath }
    });
    return response.data;
  } catch (error) {
    console.error(`Error saving file ${filepath}:`, error);
    throw error;
  }
};

// Delete a file or directory
export const deleteFile = async (filepath: string): Promise<any> => {
  try {
    const response = await api.delete(`/delete/${filepath}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting ${filepath}:`, error);
    throw error;
  }
};

// Create a new folder
export const createFolder = async (filepath: string): Promise<any> => {
  try {
    const response = await api.post('/create-folder', null, {
      params: { filepath }
    });
    return response.data;
  } catch (error) {
    console.error(`Error creating folder ${filepath}:`, error);
    throw error;
  }
};

// Rename a file or folder
export const renameFile = async (oldPath: string, newPath: string): Promise<any> => {
  try {
    const response = await api.post('/rename', null, {
      params: { old_path: oldPath, new_path: newPath }
    });
    return response.data;
  } catch (error) {
    console.error(`Error renaming ${oldPath} to ${newPath}:`, error);
    throw error;
  }
};

// Upload a file
export const uploadFile = async (file: File, path: string = '/'): Promise<any> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      params: { path },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
};

// Execute a shell command
export const executeCommand = async (command: string, cwd: string = '/'): Promise<ExecuteResult> => {
  try {
    const response = await api.post('/execute', { command }, {
      params: { cwd }
    });
    return response.data;
  } catch (error) {
    console.error(`Error executing command: ${command}`, error);
    throw error;
  }
};

// Get git status
export const getGitStatus = async (): Promise<GitStatus> => {
  try {
    const response = await api.get('/git/status');
    return response.data;
  } catch (error) {
    console.error('Error getting git status:', error);
    throw error;
  }
};
