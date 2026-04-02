import axios from 'axios';

const API_BASE_URL = '/api/git';

export interface GitStatus {
  branch: string;
  clean: boolean;
  status: string[];
  ahead: number;
  behind: number;
}

export interface GitCommit {
  hash: string;
  message: string;
  author: string;
  date: string;
  short_hash: string;
}

export interface GitBranch {
  name: string;
  current: boolean;
  remote?: string;
}

export interface GitRemote {
  name: string;
  url: string;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Get repository status
export const getGitStatus = async (): Promise<GitStatus> => {
  try {
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    console.error('Error getting git status:', error);
    throw error;
  }
};

// Initialize repository
export const initRepo = async (): Promise<any> => {
  try {
    const response = await api.post('/init');
    return response.data;
  } catch (error) {
    console.error('Error initializing repository:', error);
    throw error;
  }
};

// Stage a file
export const stageFile = async (filepath: string): Promise<any> => {
  try {
    const response = await api.post('/stage', { filepath });
    return response.data;
  } catch (error) {
    console.error(`Error staging file ${filepath}:`, error);
    throw error;
  }
};

// Unstage a file
export const unstageFile = async (filepath: string): Promise<any> => {
  try {
    const response = await api.post('/unstage', { filepath });
    return response.data;
  } catch (error) {
    console.error(`Error unstaging file ${filepath}:`, error);
    throw error;
  }
};

// Commit changes
export const commitChanges = async (message: string, author?: string): Promise<any> => {
  try {
    const response = await api.post('/commit', { message, author });
    return response.data;
  } catch (error) {
    console.error('Error committing changes:', error);
    throw error;
  }
};

// Get recent commits
export const getCommits = async (limit: number = 10): Promise<GitCommit[]> => {
  try {
    const response = await api.get('/commits', { params: { limit } });
    return response.data;
  } catch (error) {
    console.error('Error getting commits:', error);
    throw error;
  }
};

// Get branches
export const getBranches = async (): Promise<GitBranch[]> => {
  try {
    const response = await api.get('/branches');
    return response.data;
  } catch (error) {
    console.error('Error getting branches:', error);
    throw error;
  }
};

// Create a new branch
export const createBranch = async (name: string): Promise<any> => {
  try {
    const response = await api.post('/branches', { name });
    return response.data;
  } catch (error) {
    console.error(`Error creating branch ${name}:`, error);
    throw error;
  }
};

// Switch to a branch
export const switchBranch = async (name: string): Promise<any> => {
  try {
    const response = await api.post('/branches/switch', { name });
    return response.data;
  } catch (error) {
    console.error(`Error switching to branch ${name}:`, error);
    throw error;
  }
};

// Get remotes
export const getRemotes = async (): Promise<GitRemote[]> => {
  try {
    const response = await api.get('/remotes');
    return response.data;
  } catch (error) {
    console.error('Error getting remotes:', error);
    throw error;
  }
};

// Add a remote
export const addRemote = async (name: string, url: string): Promise<any> => {
  try {
    const response = await api.post('/remotes', { name, url });
    return response.data;
  } catch (error) {
    console.error(`Error adding remote ${name}:`, error);
    throw error;
  }
};

// Pull changes
export const pullChanges = async (remote: string = "origin", branch: string = ""): Promise<any> => {
  try {
    const response = await api.post('/pull', null, { params: { remote, branch } });
    return response.data;
  } catch (error) {
    console.error('Error pulling changes:', error);
    throw error;
  }
};

// Push changes
export const pushChanges = async (remote: string = "origin", branch: string = ""): Promise<any> => {
  try {
    const response = await api.post('/push', null, { params: { remote, branch } });
    return response.data;
  } catch (error) {
    console.error('Error pushing changes:', error);
    throw error;
  }
};

// Get diff for a file
export const getDiff = async (filepath: string, staged: boolean = false): Promise<string> => {
  try {
    const response = await api.get(`/diff/${filepath}`, { params: { staged } });
    return response.data.diff;
  } catch (error) {
    console.error(`Error getting diff for ${filepath}:`, error);
    throw error;
  }
};
