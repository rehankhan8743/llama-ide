// Core types for the Llama IDE application

// Chat-related types
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

export interface ChatSession {
  id: string;
  name: string;
  messages: ChatMessage[];
  model: string;
  createdAt: Date;
  updatedAt: Date;
}

// Editor types
export interface FileNode {
  id: string;
  name: string;
  path: string;
  type: 'file' | 'directory';
  children?: FileNode[];
  isOpen?: boolean;
}

export interface EditorTab {
  id: string;
  name: string;
  path: string;
  content: string;
  isModified: boolean;
  isActive: boolean;
  language?: string;
}

// Provider types
export interface ModelProvider {
  id: string;
  name: string;
  enabled: boolean;
  apiKey?: string;
  baseUrl?: string;
  models: string[];
}

// Settings types
export interface AppSettings {
  theme: 'dark' | 'light';
  defaultModel: string;
  ollamaHost: string;
  temperature: number;
  maxTokens: number;
  autoSave: boolean;
  wordWrap: boolean;
  fontSize: number;
}

// Plugin types
export interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  author: string;
  enabled: boolean;
  installed: boolean;
  path?: string;
}

// Git types
export interface GitStatus {
  branch: string;
  ahead: number;
  behind: number;
  modified: string[];
  staged: string[];
  untracked: string[];
  conflicted: string[];
}

// Session types - aligned with backend API
export interface Session {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

// Dashboard types
export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  position: { x: number; y: number; w: number; h: number };
  config?: Record<string, unknown>;
}

// Terminal types
export interface TerminalLine {
  id: string;
  type: 'input' | 'output' | 'error';
  content: string;
  timestamp: Date;
}

// Code Intelligence types
export interface CodeSuggestion {
  label: string;
  detail?: string;
  documentation?: string;
  insertText?: string;
  kind: 'function' | 'variable' | 'class' | 'snippet' | 'keyword';
}

export interface CodeError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}
