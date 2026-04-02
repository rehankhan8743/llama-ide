import { X } from 'lucide-react';
import type { EditorTab } from '../../types';

interface TabBarProps {
  tabs: EditorTab[];
  activeTabId: string | null;
  onTabClick: (tabId: string) => void;
  onTabClose: (tabId: string) => void;
}

export function TabBar({ tabs, activeTabId, onTabClick, onTabClose }: TabBarProps) {
  const handleClose = (e: React.MouseEvent, tabId: string) => {
    e.stopPropagation();
    onTabClose(tabId);
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const iconMap: Record<string, string> = {
      'ts': '🔷',
      'tsx': '⚛️',
      'js': '🟨',
      'jsx': '⚛️',
      'py': '🐍',
      'rs': '🦀',
      'go': '🐹',
      'java': '☕',
      'cpp': '⚙️',
      'c': '⚙️',
      'h': '📄',
      'hpp': '⚙️',
      'html': '🌐',
      'css': '🎨',
      'scss': '🎨',
      'json': '📋',
      'md': '📝',
      'mdx': '📝',
      'sql': '🗄️',
      'yaml': '⚙️',
      'yml': '⚙️',
      'toml': '⚙️',
      'sh': '💻',
      'bash': '💻',
      'dockerfile': '🐳',
      'vue': '💚',
      'svelte': '🧡',
      'py': '🐍',
      'rb': '💎',
      'php': '🐘',
      'swift': '🦉',
      'kt': '🟣',
    };
    return iconMap[ext || ''] || '📄';
  };

  if (tabs.length === 0) {
    return (
      <div className="flex items-center justify-center h-10 bg-[#2d2d2d] border-b border-[#333] text-gray-500 text-sm">
        No open files
      </div>
    );
  }

  return (
    <div className="flex h-10 bg-[#2d2d2d] border-b border-[#333] overflow-x-auto scrollbar-hide">
      {tabs.map((tab) => (
        <div
          key={tab.id}
          onClick={() => onTabClick(tab.id)}
          className={`group flex items-center gap-2 px-3 py-2 min-w-[120px] max-w-[200px] cursor-pointer border-r border-[#333] transition-colors ${
            activeTabId === tab.id
              ? 'bg-[#1e1e1e] text-white'
              : 'bg-[#2d2d2d] text-gray-400 hover:bg-[#3c3c3c]'
          }`}
        >
          <span className="text-sm">{getFileIcon(tab.name)}</span>
          <span className={`text-sm truncate flex-1 ${tab.isModified ? 'italic' : ''}`}>
            {tab.name}
            {tab.isModified && <span className="ml-1 text-blue-400">●</span>}
          </span>
          <button
            onClick={(e) => handleClose(e, tab.id)}
            className={`p-0.5 rounded hover:bg-[#505050] opacity-0 group-hover:opacity-100 transition-opacity ${
              activeTabId === tab.id ? 'opacity-100' : ''
            }`}
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
}
