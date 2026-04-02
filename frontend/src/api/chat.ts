import axios from 'axios';
import type { ChatMessage, ChatRequest, ChatResponse } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/chat`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  // Send a chat message
  send: async (request: ChatRequest): Promise<ChatResponse> => {
    const response = await api.post('/chat', request);
    return response.data;
  },

  // Send a chat message with streaming
  stream: async (
    request: ChatRequest,
    onMessage: (chunk: string) => void,
    onError?: (error: Error) => void
  ): Promise<void> => {
    try {
      const response = await fetch(`${API_URL}/api/chat/stream`, {
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
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);
              if (data.content) {
                onMessage(data.content);
              }
            } catch (e) {
              // Handle non-JSON lines (like SSE events)
              if (line.startsWith('data: ')) {
                const content = line.slice(6);
                if (content && content !== '[DONE]') {
                  onMessage(content);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
      throw error;
    }
  },

  // Get chat history
  getHistory: async (sessionId?: string): Promise<ChatMessage[]> => {
    const response = await api.get('/history', {
      params: { session_id: sessionId },
    });
    return response.data;
  },

  // Clear chat history
  clearHistory: async (sessionId?: string): Promise<void> => {
    await api.delete('/history', {
      params: { session_id: sessionId },
    });
  },

  // Get available models
  getModels: async (): Promise<string[]> => {
    const response = await api.get('/models');
    return response.data.models;
  },
};
