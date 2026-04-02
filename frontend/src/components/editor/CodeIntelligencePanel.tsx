import React, { useState } from 'react';
import { useCodeIntelligence } from '@/hooks/useCodeIntelligence';
import {
  FiAlertCircle,
  FiInfo,
  FiBook,
  FiCode,
  FiX
} from 'react-icons/fi';

interface CodeIntelligencePanelProps {
  filepath: string;
  content: string;
  cursorPosition?: { line: number; column: number };
  onFormatCode?: (formatted: string) => void;
}

const CodeIntelligencePanel: React.FC<CodeIntelligencePanelProps> = ({
  filepath,
  content,
  cursorPosition,
  onFormatCode
}) => {
  const {
    diagnostics,
    documentation,
    loading,
    error,
    getDiagnosticsForCode,
    getDocumentationAtPosition,
    formatCodeContent
  } = useCodeIntelligence();

  const [activeTab, setActiveTab] = useState<'diagnostics' | 'documentation'>('diagnostics');

  // Load diagnostics when content changes
  React.useEffect(() => {
    if (content) {
      getDiagnosticsForCode({ filepath, content });
    }
  }, [content, filepath, getDiagnosticsForCode]);

  // Load documentation when cursor position changes
  React.useEffect(() => {
    if (cursorPosition && content) {
      getDocumentationAtPosition({
        filepath,
        content,
        line: cursorPosition.line,
        character: cursorPosition.column
      });
    }
  }, [cursorPosition, filepath, content, getDocumentationAtPosition]);

  const handleFormatCode = async () => {
    try {
      const formatted = await formatCodeContent({ filepath, content });
      if (onFormatCode) {
        onFormatCode(formatted);
      }
    } catch (err) {
      console.error('Failed to format code:', err);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error': return <FiAlertCircle className="text-red-500" />;
      case 'warning': return <FiAlertCircle className="text-yellow-500" />;
      case 'info': return <FiInfo className="text-blue-500" />;
      default: return <FiAlertCircle />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case 'error': return 'text-red-500';
      case 'warning': return 'text-yellow-500';
      case 'info': return 'text-blue-500';
      default: return '';
    }
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'diagnostics'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
            onClick={() => setActiveTab('diagnostics')}
          >
            Issues ({diagnostics.length})
          </button>
          <button
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'documentation'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
            onClick={() => setActiveTab('documentation')}
          >
            Docs
          </button>
        </div>
        <button
          onClick={handleFormatCode}
          disabled={loading}
          className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          <FiCode size={18} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-grow overflow-y-auto">
        {error && (
          <div className="p-3 text-red-500 text-sm">
            Error: {error}
          </div>
        )}

        {activeTab === 'diagnostics' && (
          <div className="p-2">
            {diagnostics.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                No issues found
              </div>
            ) : (
              <div className="space-y-2">
                {diagnostics.map((diag, index) => (
                  <div
                    key={index}
                    className="p-2 rounded border text-sm"
                  >
                    <div className="flex items-start">
                      <div className="mr-2 mt-1">
                        {getSeverityIcon(diag.severity)}
                      </div>
                      <div className="flex-grow">
                        <div className={getSeverityClass(diag.severity)}>
                          {diag.message}
                        </div>
                        {diag.source && (
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            {diag.source}
                            {diag.code && `: ${diag.code}`}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'documentation' && (
          <div className="p-2">
            {documentation ? (
              <div className="space-y-3">
                {documentation.signature && (
                  <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded">
                    <div className="font-mono text-sm">{documentation.signature}</div>
                  </div>
                )}
                {documentation.documentation && (
                  <div className="text-sm whitespace-pre-wrap">
                    {documentation.documentation}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                No documentation available
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeIntelligencePanel;
