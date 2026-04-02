import axios from 'axios';

const API_BASE_URL = '/api/providers';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
}

export interface ProviderConfig {
  name: string;
  api_key: string;
  enabled: boolean;
  model: string;
  base_url?: string;
}

export interface ProviderModel {
  name: string;
  display_name?: string;
  description?: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  model: string;
  temperature: number;
  max_tokens: number;
}

export interface ChatResponse {
  message: {
    role: string;
    content: string;
  };
  finish_reason?: string;
  usage?: Record<string, any>;
}

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Get available providers
export const getProviders = async (): Promise<Record<string, ProviderConfig>> => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Error fetching providers:', error);
    throw error;
  }
};

// Get available provider types
export const getAvailableProviders = async (): Promise<Record<string, string>> => {
  try {
    const response = await api.get('/available');
    return response.data;
  } catch (error) {
    console.error('Error fetching available providers:', error);
    throw error;
  }
};

// Get models for a provider
export const getProviderModels = async (providerName: string): Promise<ProviderModel[]> => {
  // Return default models per provider
  const defaultModels: Record<string, ProviderModel[]> = {
    ollama: [
      { name: 'llama2', display_name: 'Llama 2' },
      { name: 'codellama', display_name: 'Code Llama' },
      { name: 'mistral', display_name: 'Mistral' },
      { name: 'mixtral', display_name: 'Mixtral' }
    ],
    openai: [
      { name: 'gpt-3.5-turbo', display_name: 'GPT-3.5 Turbo' },
      { name: 'gpt-4', display_name: 'GPT-4' },
      { name: 'gpt-4-turbo', display_name: 'GPT-4 Turbo' }
    ],
    anthropic: [
      { name: 'claude-2', display_name: 'Claude 2' },
      { name: 'claude-2.1', display_name: 'Claude 2.1' },
      { name: 'claude-3-opus', display_name: 'Claude 3 Opus' },
      { name: 'claude-3-sonnet', display_name: 'Claude 3 Sonnet' }
    ],
    google: [
      { name: 'gemini-pro', display_name: 'Gemini Pro' },
      { name: 'gemini-pro-vision', display_name: 'Gemini Pro Vision' }
    ],
    groq: [
      { name: 'mixtral-8x7b-32768', display_name: 'Mixtral 8x7B' },
      { name: 'llama2-70b-4096', display_name: 'Llama 2 70B' }
    ]
  };

  return defaultModels[providerName] || [];
};

// Chat completion with a specific provider
export const providerChatCompletion = async (
  providerName: string,
  request: ChatRequest
): Promise<ChatResponse> => {
  try {
    const response = await api.post(`/${providerName}/chat/completion`, request);
    return response.data;
  } catch (error) {
    console.error(`Error with ${providerName} chat:`, error);
    throw error;
  }
};

// Stream chat completion with a specific provider
export const providerChatStream = async (
  providerName: string,
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onError?: (error: Error) => void
): Promise<void> => {
  try {
    // For streaming, we use EventSource approach via SSE
    // Since axios doesn't natively support SSE, we'll use fetch
    const response = await fetch(`${API_BASE_URL}/${providerName}/chat/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          onChunk(line);
        }
      }
    }
  } catch (error) {
    if (onError && error instanceof Error) {
      onError(error);
    } else if (error instanceof Error) {
      onError?.(error);
    }
  }
};
