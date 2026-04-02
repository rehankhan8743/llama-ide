import React, { useState } from 'react';
import { useDebugger } from '@/hooks/useDebugger';
import {
  FiBug,
  FiPlay,
  FiRefreshCw,
  FiX
} from 'react-icons/fi';

interface DebugPanelProps {
  filepath: string;
  breakpoints?: Array<{ line: number; column: number }>;
  onSetBreakpoint?: (line: number) => void;
  onClearBreakpoint?: (line: number) => void;
}

const DebugPanel: React.FC<DebugPanelProps> = ({
  filepath,
  breakpoints = [],
  onSetBreakpoint,
  onClearBreakpoint
}) => {
  const {
    debugResult,
    testResult,
    loading,
    error,
    debugFile,
    runAllTests
  } = useDebugger();

  const [activeTab, setActiveTab] = useState<'debug' | 'test'>('debug');
  const [testPattern, setTestPattern] = useState('test_*.py');

  const handleDebug = () => {
    debugFile({ filepath, breakpoints });
  };

  const handleRunTests = () => {
    runAllTests({ test_pattern: testPattern });
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-2 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'debug'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
            onClick={() => setActiveTab('debug')}
          >
            Debug
          </button>
          <button
            className={`px-3 py-1 text-sm rounded ${
              activeTab === 'test'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700'
            }`}
            onClick={() => setActiveTab('test')}
          >
            Tests
          </button>
        </div>
        <button
          onClick={activeTab === 'debug' ? handleDebug : handleRunTests}
          disabled={loading}
          className="p-1 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          {loading ? (
            <FiRefreshCw className="animate-spin" size={18} />
          ) : (
            <FiPlay size={18} />
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-grow overflow-y-auto">
        {error && (
          <div className="p-3 text-red-500 text-sm">
            Error: {error}
          </div>
        )}

        {activeTab === 'debug' && (
          <div className="p-2">
            <div className="mb-3">
              <h3 className="font-medium mb-2">Breakpoints</h3>
              {breakpoints.length === 0 ? (
                <div className="text-gray-500 text-sm">No breakpoints set</div>
              ) : (
                <div className="space-y-1">
                  {breakpoints.map((bp, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-1 bg-gray-100 dark:bg-gray-800 rounded"
                    >
                      <span className="text-sm">Line {bp.line + 1}</span>
                      <button
                        onClick={() => onClearBreakpoint && onClearBreakpoint(bp.line)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <FiX size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {debugResult && (
              <div>
                <h3 className="font-medium mb-2">Output</h3>
                <div className="text-xs font-mono bg-black text-green-400 p-2 rounded whitespace-pre-wrap">
                  {debugResult.stdout}
                  {debugResult.stderr && (
                    <div className="text-red-400 mt-2">{debugResult.stderr}</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'test' && (
          <div className="p-2">
            <div className="mb-3">
              <label className="block text-sm font-medium mb-1">Test Pattern</label>
              <input
                type="text"
                value={testPattern}
                onChange={(e) => setTestPattern(e.target.value)}
                className="w-full p-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800"
              />
            </div>

            {testResult && (
              <div>
                <h3 className="font-medium mb-2">Results</h3>
                <div className={`p-2 rounded mb-2 ${
                  testResult.passed ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'
                }`}>
                  <span className={testResult.passed ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}>
                    {testResult.passed ? 'All tests passed!' : 'Some tests failed'}
                  </span>
                </div>
                <div className="text-xs font-mono bg-black text-green-400 p-2 rounded whitespace-pre-wrap">
                  {testResult.stdout}
                  {testResult.stderr && (
                    <div className="text-red-400 mt-2">{testResult.stderr}</div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DebugPanel;
