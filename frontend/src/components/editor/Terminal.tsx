import { useEffect, useRef, useState } from 'react';
import { Send, Trash, Copy, Terminal as TerminalIcon } from 'lucide-react';
import type { TerminalLine } from '../../types';

interface TerminalProps {
  lines: TerminalLine[];
  onExecute: (command: string) => void;
  onClear: () => void;
}

export function Terminal({ lines, onExecute, onClear }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [lines]);

  // Focus input when clicking terminal
  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onExecute(input.trim());
      setHistory([...history, input.trim()]);
      setHistoryIndex(-1);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  const handleCopy = () => {
    const text = lines.map(line => line.content).join('\n');
    navigator.clipboard.writeText(text);
  };

  const getLineStyle = (type: TerminalLine['type']) => {
    switch (type) {
      case 'input':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-300';
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e] text-sm font-mono">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[#252526] border-b border-[#333]">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-4 h-4 text-gray-400" />
          <span className="text-gray-300">Terminal</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white transition-colors"
            title="Copy output"
          >
            <Copy className="w-4 h-4" />
          </button>
          <button
            onClick={onClear}
            className="p-1.5 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white transition-colors"
            title="Clear terminal"
          >
            <Trash className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Terminal output */}
      <div
        ref={terminalRef}
        onClick={handleTerminalClick}
        className="flex-1 overflow-y-auto p-4 space-y-1"
      >
        {lines.length === 0 && (
          <div className="text-gray-500 italic">
            Welcome to Llama IDE Terminal. Type a command to get started.
          </div>
        )}
        {lines.map((line) => (
          <div key={line.id} className={`${getLineStyle(line.type)} whitespace-pre-wrap break-all`}>
            {line.type === 'input' && (
              <span className="text-blue-400 mr-2">$</span>
            )}
            {line.content}
          </div>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex items-center gap-2 px-4 py-2 bg-[#252526] border-t border-[#333]">
        <span className="text-blue-400">$</span>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a command..."
          className="flex-1 bg-transparent text-white outline-none placeholder-gray-500"
          autoFocus
        />
        <button
          type="submit"
          disabled={!input.trim()}
          className="p-1.5 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
