import { useState, useCallback } from 'react';
import {
  getDiagnostics,
  getCompletions,
  getDefinitions,
  getDocumentation,
  formatCode,
  CodeRequest,
  PositionRequest,
  Diagnostic,
  Completion,
  Definition,
  Documentation
} from '@/api/editor';

interface UseCodeIntelligenceReturn {
  diagnostics: Diagnostic[];
  completions: Completion[];
  definitions: Definition[];
  documentation: Documentation | null;
  loading: boolean;
  error: string | null;
  getDiagnosticsForCode: (request: CodeRequest) => Promise<void>;
  getCompletionsAtPosition: (request: PositionRequest) => Promise<void>;
  getDefinitionsAtPosition: (request: PositionRequest) => Promise<void>;
  getDocumentationAtPosition: (request: PositionRequest) => Promise<void>;
  formatCodeContent: (request: CodeRequest) => Promise<string>;
}

export const useCodeIntelligence = (): UseCodeIntelligenceReturn => {
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [completions, setCompletions] = useState<Completion[]>([]);
  const [definitions, setDefinitions] = useState<Definition[]>([]);
  const [documentation, setDocumentation] = useState<Documentation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: any) => {
    const message = err.response?.data?.detail || err.message || 'An error occurred';
    setError(message);
    console.error('Code intelligence error:', err);
  };

  const getDiagnosticsForCode = useCallback(async (request: CodeRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getDiagnostics(request);
      setDiagnostics(result.diagnostics);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getCompletionsAtPosition = useCallback(async (request: PositionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getCompletions(request);
      setCompletions(result.completions);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getDefinitionsAtPosition = useCallback(async (request: PositionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getDefinitions(request);
      setDefinitions(result.definitions);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getDocumentationAtPosition = useCallback(async (request: PositionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await getDocumentation(request);
      setDocumentation(result.documentation);
    } catch (err: any) {
      handleError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const formatCodeContent = useCallback(async (request: CodeRequest): Promise<string> => {
    setLoading(true);
    setError(null);
    try {
      const result = await formatCode(request);
      return result.formatted_content;
    } catch (err: any) {
      handleError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    diagnostics,
    completions,
    definitions,
    documentation,
    loading,
    error,
    getDiagnosticsForCode,
    getCompletionsAtPosition,
    getDefinitionsAtPosition,
    getDocumentationAtPosition,
    formatCodeContent
  };
};

export default useCodeIntelligence;
