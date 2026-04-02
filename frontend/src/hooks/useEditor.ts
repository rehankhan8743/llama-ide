import { useState, useCallback } from 'react';
import type { EditorTab, FileNode } from '../types';

export function useEditor() {
  const [tabs, setTabs] = useState<EditorTab[]>([]);
  const [activeTabId, setActiveTabId] = useState<string | null>(null);
  const [openFiles, setOpenFiles] = useState<Set<string>>(new Set());

  const openFile = useCallback((file: FileNode) => {
    if (openFiles.has(file.path)) {
      setActiveTabId(file.path);
      return;
    }

    const newTab: EditorTab = {
      id: file.path,
      name: file.name,
      path: file.path,
      content: '', // Would fetch from backend
      isModified: false,
      isActive: true,
      language: file.name.split('.').pop(),
    };

    setTabs((prev) => {
      const updated = prev.map((t) => ({ ...t, isActive: false }));
      return [...updated, newTab];
    });
    setOpenFiles((prev) => new Set(prev).add(file.path));
    setActiveTabId(file.path);
  }, [openFiles]);

  const closeTab = useCallback((tabId: string) => {
    setTabs((prev) => {
      const index = prev.findIndex((t) => t.id === tabId);
      const newTabs = prev.filter((t) => t.id !== tabId);

      // Update active tab if needed
      if (activeTabId === tabId && newTabs.length > 0) {
        const newIndex = Math.min(index, newTabs.length - 1);
        newTabs[newIndex] = { ...newTabs[newIndex], isActive: true };
        setActiveTabId(newTabs[newIndex].id);
      } else if (newTabs.length === 0) {
        setActiveTabId(null);
      }

      return newTabs;
    });

    setOpenFiles((prev) => {
      const newSet = new Set(prev);
      newSet.delete(tabId);
      return newSet;
    });
  }, [activeTabId]);

  const setActiveTab = useCallback((tabId: string) => {
    setActiveTabId(tabId);
    setTabs((prev) =>
      prev.map((t) => ({
        ...t,
        isActive: t.id === tabId,
      }))
    );
  }, []);

  const updateTabContent = useCallback((tabId: string, content: string) => {
    setTabs((prev) =>
      prev.map((t) =>
        t.id === tabId
          ? { ...t, content, isModified: t.content !== content }
          : t
      )
    );
  }, []);

  const saveTab = useCallback((tabId: string) => {
    setTabs((prev) =>
      prev.map((t) =>
        t.id === tabId ? { ...t, isModified: false } : t
      )
    );
  }, []);

  const closeAllTabs = useCallback(() => {
    setTabs([]);
    setOpenFiles(new Set());
    setActiveTabId(null);
  }, []);

  const closeOtherTabs = useCallback((keepTabId: string) => {
    setTabs((prev) => {
      const keepTab = prev.find((t) => t.id === keepTabId);
      if (keepTab) {
        setOpenFiles(new Set([keepTabId]));
        setActiveTabId(keepTabId);
        return [{ ...keepTab, isActive: true }];
      }
      return prev;
    });
  }, []);

  const activeTab = tabs.find((t) => t.id === activeTabId) || null;

  return {
    tabs,
    activeTabId,
    activeTab,
    openFile,
    closeTab,
    setActiveTab,
    updateTabContent,
    saveTab,
    closeAllTabs,
    closeOtherTabs,
  };
}
