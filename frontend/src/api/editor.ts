import axios from 'axios';

const API_BASE_URL = '/api/editor';

export interface Diagnostic {
  severity: 'error' | 'warning' | 'info';
  message: string;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
  source?: string;
  code?: string;
}

export interface Completion {
  label: string;
  kind: string;
  detail?: string;
  documentation?: string;
}

export interface Definition {
  uri: string;
  range: {
    start: { line: number; character: number };
    end: { line: number; character: number };
  };
  name: string;
}

export interface Documentation {
  signature?: string;
  documentation?: string;
}

export interface CodeRequest {
  filepath: string;
  content: string;
}

export interface PositionRequest extends CodeRequest {
  line: number;
  character: number;
}

export interface DiagnosticsResponse {
  diagnostics: Diagnostic[];
}

export interface CompletionsResponse {
  completions: Completion[];
}

export interface DefinitionsResponse {
  definitions: Definition[];
}

export interface DocumentationResponse {
  documentation: Documentation | null;
}

export interface FormatResponse {
  formatted_content: string;
}

export interface DebugRequest {
  filepath: string;
  breakpoints?: Array<{ line: number; column: number }>;
}

export interface DebugResponse {
  stdout: string;
  stderr: string;
  returncode: number;
  error?: string;
}

export interface TestRequest {
  test_pattern?: string;
}

export interface TestResponse {
  stdout: string;
  stderr: string;
  returncode: number;
  passed: boolean;
  summary: Record<string, any>;
  error?: string;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const getDiagnostics = async (request: CodeRequest): Promise<DiagnosticsResponse> => {
  try {
    const response = await api.post('/diagnostics', request);
    return response.data;
  } catch (error) {
    console.error('Error getting diagnostics:', error);
    throw error;
  }
};

export const getCompletions = async (request: PositionRequest): Promise<CompletionsResponse> => {
  try {
    const response = await api.post('/completions', request);
    return response.data;
  } catch (error) {
    console.error('Error getting completions:', error);
    throw error;
  }
};

export const getDefinitions = async (request: PositionRequest): Promise<DefinitionsResponse> => {
  try {
    const response = await api.post('/definitions', request);
    return response.data;
  } catch (error) {
    console.error('Error getting definitions:', error);
    throw error;
  }
};

export const getDocumentation = async (request: PositionRequest): Promise<DocumentationResponse> => {
  try {
    const response = await api.post('/documentation', request);
    return response.data;
  } catch (error) {
    console.error('Error getting documentation:', error);
    throw error;
  }
};

export const formatCode = async (request: CodeRequest): Promise<FormatResponse> => {
  try {
    const response = await api.post('/format', request);
    return response.data;
  } catch (error) {
    console.error('Error formatting code:', error);
    throw error;
  }
};

export const debugCode = async (request: DebugRequest): Promise<DebugResponse> => {
  try {
    const response = await api.post('/debug', request);
    return response.data;
  } catch (error) {
    console.error('Error debugging code:', error);
    throw error;
  }
};

export const runTests = async (request: TestRequest = {}): Promise<TestResponse> => {
  try {
    const response = await api.post('/test', request);
    return response.data;
  } catch (error) {
    console.error('Error running tests:', error);
    throw error;
  }
};
