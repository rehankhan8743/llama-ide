import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/generation`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface CodeGenerationRequest {
  prompt: string;
  language: string;
  context?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface CodeGenerationResponse {
  code: string;
  language: string;
  explanation?: string;
}

export interface TestGenerationRequest {
  code: string;
  language: string;
  framework?: string;
}

export interface DocGenerationRequest {
  code: string;
  language: string;
  style?: 'jsdoc' | 'google' | 'numpy' | 'rst';
}

export const generationApi = {
  // Generate code from natural language
  generateCode: async (
    request: CodeGenerationRequest
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/code', request);
    return response.data;
  },

  // Generate code with streaming
  streamCode: async (
    request: CodeGenerationRequest,
    onChunk: (chunk: string) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    try {
      const response = await fetch(`${API_URL}/api/generation/code/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value, { stream: true });
        onChunk(text);
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
      throw error;
    }
  },

  // Generate unit tests
  generateTests: async (
    request: TestGenerationRequest
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/tests', request);
    return response.data;
  },

  // Generate documentation
  generateDocs: async (
    request: DocGenerationRequest
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/docs', request);
    return response.data;
  },

  // Refactor code
  refactor: async (
    code: string,
    instructions: string,
    language: string
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/refactor', {
      code,
      instructions,
      language,
    });
    return response.data;
  },

  // Complete code (autocomplete)
  complete: async (
    code: string,
    cursorPosition: number,
    language: string
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/complete', {
      code,
      cursor_position: cursorPosition,
      language,
    });
    return response.data;
  },

  // Explain code
  explain: async (code: string, language: string): Promise<string> => {
    const response = await api.post('/explain', {
      code,
      language,
    });
    return response.data.explanation;
  },

  // Fix code errors
  fix: async (
    code: string,
    error: string,
    language: string
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/fix', {
      code,
      error,
      language,
    });
    return response.data;
  },

  // Convert code to different language
  convert: async (
    code: string,
    fromLanguage: string,
    toLanguage: string
  ): Promise<CodeGenerationResponse> => {
    const response = await api.post('/convert', {
      code,
      from_language: fromLanguage,
      to_language: toLanguage,
    });
    return response.data;
  },
};
