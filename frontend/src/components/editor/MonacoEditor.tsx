import { useEffect, useRef, useState } from 'react';
import Editor, { OnMount, loader } from '@monaco-editor/react';
import type { EditorTab } from '../../types';

interface MonacoEditorProps {
  tab: EditorTab;
  onChange: (content: string) => void;
  onSave: () => void;
}

export function MonacoEditor({ tab, onChange, onSave }: MonacoEditorProps) {
  const editorRef = useRef<any>(null);
  const [isReady, setIsReady] = useState(false);

  // Configure Monaco loader
  useEffect(() => {
    loader.config({
      paths: {
        vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs'
      }
    });
  }, []);

  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    setIsReady(true);

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      onSave();
    });

    // Configure TypeScript/JavaScript defaults
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.Latest,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.CommonJS,
      noEmit: true,
      esModuleInterop: true,
      jsx: monaco.languages.typescript.JsxEmit.React,
      reactNamespace: 'React',
      allowJs: true,
      typeRoots: ['node_modules/@types']
    });

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      fontFamily: 'JetBrains Mono, Fira Code, Consolas, monospace',
      fontLigatures: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      formatOnPaste: true,
      formatOnType: true,
      tabSize: 2,
      insertSpaces: true,
      wordWrap: 'on',
      smoothScrolling: true,
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      roundedSelection: true,
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      }
    });
  };

  const getLanguage = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase() || '';
    const langMap: Record<string, string> = {
      'ts': 'typescript',
      'tsx': 'typescript',
      'js': 'javascript',
      'jsx': 'javascript',
      'py': 'python',
      'rs': 'rust',
      'go': 'go',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'h': 'c',
      'hpp': 'cpp',
      'cs': 'csharp',
      'rb': 'ruby',
      'php': 'php',
      'swift': 'swift',
      'kt': 'kotlin',
      'scala': 'scala',
      'r': 'r',
      'm': 'objective-c',
      'mm': 'objective-c',
      'dart': 'dart',
      'lua': 'lua',
      'ex': 'elixir',
      'exs': 'elixir',
      'erl': 'erlang',
      'fs': 'fsharp',
      'fsx': 'fsharp',
      'ml': 'ocaml',
      'mli': 'ocaml',
      'hs': 'haskell',
      'lhs': 'haskell',
      'pl': 'perl',
      'pm': 'perl',
      't': 'perl',
      'html': 'html',
      'htm': 'html',
      'css': 'css',
      'scss': 'scss',
      'sass': 'scss',
      'less': 'less',
      'json': 'json',
      'xml': 'xml',
      'yaml': 'yaml',
      'yml': 'yaml',
      'toml': 'toml',
      'ini': 'ini',
      'cfg': 'ini',
      'conf': 'ini',
      'sh': 'shell',
      'bash': 'shell',
      'zsh': 'shell',
      'fish': 'shell',
      'ps1': 'powershell',
      'psm1': 'powershell',
      'psd1': 'powershell',
      'md': 'markdown',
      'mdx': 'markdown',
      'sql': 'sql',
      'graphql': 'graphql',
      'gql': 'graphql',
      'dockerfile': 'dockerfile',
      'makefile': 'makefile',
      'cmake': 'cmake',
      'vue': 'vue',
      'svelte': 'svelte',
      'astro': 'astro',
      'sol': 'solidity'
    };
    return langMap[ext] || 'plaintext';
  };

  const handleChange = (value: string | undefined) => {
    if (value !== undefined) {
      onChange(value);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      {/* Breadcrumb */}
      <div className="flex items-center px-4 py-2 bg-[#252526] border-b border-[#333] text-sm">
        <span className="text-gray-400">{tab.path}</span>
        {tab.isModified && (
          <span className="ml-2 text-blue-400">●</span>
        )}
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={getLanguage(tab.name)}
          value={tab.content}
          theme="vs-dark"
          onMount={handleMount}
          onChange={handleChange}
          options={{
            readOnly: false,
            domReadOnly: false
          }}
          loading={
            <div className="flex items-center justify-center h-full text-gray-400">
              Loading editor...
            </div>
          }
        />
      </div>

      {/* Status bar */}
      {isReady && (
        <div className="flex items-center justify-between px-4 py-1 bg-[#007acc] text-white text-xs">
          <div className="flex items-center gap-4">
            <span>{getLanguage(tab.name).toUpperCase()}</span>
            <span>UTF-8</span>
          </div>
          <div className="flex items-center gap-4">
            <span>Ln {tab.content.split('\n').length}, Col 1</span>
            <span>Spaces: 2</span>
          </div>
        </div>
      )}
    </div>
  );
}
