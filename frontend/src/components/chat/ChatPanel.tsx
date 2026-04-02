import { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Trash2, Copy, Download } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { MessageList } from './MessageList';
import { ModelControls } from './ModelControls';
import type { ChatMessage } from '../../types';

export function ChatPanel() {
  const { messages, isLoading, sendMessage, clearMessages, currentModel } = useChat();
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const message = input.trim();
    setInput('');
    setIsStreaming(true);

    try {
      await sendMessage(message);
    } finally {
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCopyConversation = () => {
    const text = messages
      .map((m: ChatMessage) => `${m.role.toUpperCase()}: ${m.content}`)
      .join('\n\n');
    navigator.clipboard.writeText(text);
  };

  const handleExportConversation = () => {
    const data = {
      messages,
      model: currentModel,
      timestamp: new Date().toISOString()
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex flex-col bg-[#1e1e1e]">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#252526] border-b border-[#333]">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <span className="font-semibold">Chat</span>
          <span className="text-xs text-gray-500 ml-2">({currentModel})</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopyConversation}
            className="p-2 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white transition-colors"
            title="Copy conversation"
          >
            <Copy className="w-4 h-4" />
          </button>
          <button
            onClick={handleExportConversation}
            className="p-2 hover:bg-[#3c3c3c] rounded text-gray-400 hover:text-white transition-colors"
            title="Export conversation"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={clearMessages}
            className="p-2 hover:bg-red-900/50 text-gray-400 hover:text-red-400 rounded transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden">
        <MessageList messages={messages} isStreaming={isStreaming} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[#333]">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Shift+Enter for new line)"
              className="w-full px-4 py-3 bg-[#2d2d2d] border border-[#3c3c3c] rounded-lg resize-none outline-none focus:border-blue-500 transition-colors text-sm min-h-[52px] max-h-[200px]"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </form>
        <div className="mt-2">
          <ModelControls />
        </div>
      </div>
    </div>
  );
}
