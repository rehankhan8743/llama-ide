import { useState, useEffect } from 'react';
import {
  getGitStatus,
  initRepo,
  stageFile,
  unstageFile,
  commitChanges,
  getCommits,
  getBranches,
  createBranch,
  switchBranch,
  getRemotes,
  addRemote,
  pullChanges,
  pushChanges,
  getDiff as getFileDiff,
  GitStatus,
  GitCommit,
  GitBranch,
  GitRemote
} from '@/api/git';

interface UseGitReturn {
  status: GitStatus | null;
  commits: GitCommit[];
  branches: GitBranch[];
  remotes: GitRemote[];
  loading: boolean;
  error: string | null;
  refreshStatus: () => Promise<void>;
  initializeRepo: () => Promise<void>;
  stage: (filepath: string) => Promise<void>;
  unstage: (filepath: string) => Promise<void>;
  commit: (message: string, author?: string) => Promise<void>;
  refreshCommits: () => Promise<void>;
  refreshBranches: () => Promise<void>;
  createNewBranch: (name: string) => Promise<void>;
  switchToBranch: (name: string) => Promise<void>;
  refreshRemotes: () => Promise<void>;
  addNewRemote: (name: string, url: string) => Promise<void>;
  pull: (remote?: string, branch?: string) => Promise<void>;
  push: (remote?: string, branch?: string) => Promise<void>;
  getDiff: (filepath: string, staged?: boolean) => Promise<string>;
}

export const useGit = (): UseGitReturn => {
  const [status, setStatus] = useState<GitStatus | null>(null);
  const [commits, setCommits] = useState<GitCommit[]>([]);
  const [branches, setBranches] = useState<GitBranch[]>([]);
  const [remotes, setRemotes] = useState<GitRemote[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err.response?.data?.detail || err.message || 'An error occurred';
    setError(message);
    console.error('Git error:', err);
  };

  const refreshStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const gitStatus = await getGitStatus();
      setStatus(gitStatus);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const initializeRepo = async () => {
    setLoading(true);
    setError(null);
    try {
      await initRepo();
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const stage = async (filepath: string) => {
    setLoading(true);
    setError(null);
    try {
      await stageFile(filepath);
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const unstage = async (filepath: string) => {
    setLoading(true);
    setError(null);
    try {
      await unstageFile(filepath);
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const commit = async (message: string, author?: string) => {
    setLoading(true);
    setError(null);
    try {
      await commitChanges(message, author);
      await refreshStatus();
      await refreshCommits();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const refreshCommits = async () => {
    setLoading(true);
    setError(null);
    try {
      const commitList = await getCommits(20);
      setCommits(commitList);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const refreshBranches = async () => {
    setLoading(true);
    setError(null);
    try {
      const branchList = await getBranches();
      setBranches(branchList);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const createNewBranch = async (name: string) => {
    setLoading(true);
    setError(null);
    try {
      await createBranch(name);
      await refreshBranches();
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const switchToBranch = async (name: string) => {
    setLoading(true);
    setError(null);
    try {
      await switchBranch(name);
      await refreshBranches();
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const refreshRemotes = async () => {
    setLoading(true);
    setError(null);
    try {
      const remoteList = await getRemotes();
      setRemotes(remoteList);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const addNewRemote = async (name: string, url: string) => {
    setLoading(true);
    setError(null);
    try {
      await addRemote(name, url);
      await refreshRemotes();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const pull = async (remote: string = 'origin', branch: string = '') => {
    setLoading(true);
    setError(null);
    try {
      await pullChanges(remote, branch);
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const push = async (remote: string = 'origin', branch: string = '') => {
    setLoading(true);
    setError(null);
    try {
      await pushChanges(remote, branch);
      await refreshStatus();
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  const getDiff = async (filepath: string, staged: boolean = false): Promise<string> => {
    try {
      return await getFileDiff(filepath, staged);
    } catch (err: any) {
      handleError(err);
      return '';
    }
  };

  // Initial load
  useEffect(() => {
    refreshStatus();
    refreshCommits();
    refreshBranches();
    refreshRemotes();
  }, []);

  return {
    status,
    commits,
    branches,
    remotes,
    loading,
    error,
    refreshStatus,
    initializeRepo,
    stage,
    unstage,
    commit,
    refreshCommits,
    refreshBranches,
    createNewBranch,
    switchToBranch,
    refreshRemotes,
    addNewRemote,
    pull,
    push,
    getDiff
  };
};

export default useGit;
