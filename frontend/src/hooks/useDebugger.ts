import { useState, useCallback } from 'react';
import {
  debugCode,
  runTests,
  DebugRequest,
  TestRequest,
  DebugResponse,
  TestResponse
} from '@/api/editor';

interface UseDebuggerReturn {
  debugResult: DebugResponse | null;
  testResult: TestResponse | null;
  loading: boolean;
  error: string | null;
  debugFile: (request: DebugRequest) => Promise<void>;
  runAllTests: (request?: TestRequest) => Promise<void>;
}

export const useDebugger = (): UseDebuggerReturn => {
  const [debugResult, setDebugResult] = useState<DebugResponse | null>(null);
  const [testResult, setTestResult] = useState<TestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err.response?.data?.detail || err.message || 'An error occurred';
    setError(message);
    console.error('Debugger error:', err);
  };

  const debugFile = useCallback(async (request: DebugRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await debugCode(request);
      setDebugResult(result);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const runAllTests = useCallback(async (request?: TestRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await runTests(request);
      setTestResult(result);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    debugResult,
    testResult,
    loading,
    error,
    debugFile,
    runAllTests
  };
};

export default useDebugger;
