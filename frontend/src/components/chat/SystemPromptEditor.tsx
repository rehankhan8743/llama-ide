import { useState } from 'react';
import { Save, RotateCcw, Sparkles } from 'lucide-react';

interface SystemPromptEditorProps {
  systemPrompt: string;
  onSave: (prompt: string) => void;
}

const DEFAULT_PROMPT = `You are a helpful AI assistant integrated into Llama IDE, a code editor. You can help with:
- Writing and reviewing code
- Explaining code concepts
- Debugging issues
- Answering questions about programming
- Providing code examples

Be concise, helpful, and provide code examples when relevant.`;

export function SystemPromptEditor({ systemPrompt, onSave }: SystemPromptEditorProps) {
  const [prompt, setPrompt] = useState(systemPrompt || DEFAULT_PROMPT);
  const [isDirty, setIsDirty] = useState(false);

  const handleSave = () => {
    onSave(prompt);
    setIsDirty(false);
  };

  const handleReset = () => {
    setPrompt(DEFAULT_PROMPT);
    setIsDirty(true);
  };

  const handleChange = (value: string) => {
    setPrompt(value);
    setIsDirty(true);
  };

  return (
    <div className="p-4 bg-[#1e1e1e] border-t border-[#333]">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-yellow-400" />
          <h3 className="font-semibold text-sm">System Prompt</h3>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#2d2d2d] hover:bg-[#3c3c3c] rounded transition-colors"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={!isDirty}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded transition-colors"
          >
            <Save className="w-3 h-3" />
            Save
          </button>
        </div>
      </div>

      <textarea
        value={prompt}
        onChange={(e) => handleChange(e.target.value)}
        className="w-full h-32 px-3 py-2 bg-[#252526] border border-[#3c3c3c] rounded text-sm font-mono resize-none focus:outline-none focus:border-blue-500 transition-colors"
        placeholder="Enter system prompt..."
      />

      <p className="mt-2 text-xs text-gray-500">
        This prompt defines how the AI assistant behaves. Changes take effect in new conversations.
      </p>
    </div>
  );
}
