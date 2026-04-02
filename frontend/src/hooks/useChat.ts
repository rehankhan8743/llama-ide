import { useState, useEffect, useRef } from 'react';
import { ChatMessage, providerChatStream } from '@/api/providers';

interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  selectedProvider: string;
  setSelectedProvider: (provider: string) => void;
  sendMessage: (content: string, model?: string, temperature?: number) => void;
  clearConversation: () => void;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem('chat-messages');
    return saved ? JSON.parse(saved).map((msg: any) => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    })) : [];
  });

  const [isLoading, setIsLoading] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState('ollama');
  const abortControllerRef = useRef<AbortController | null>(null);
  const accumulatedContentRef = useRef('');

  // Persist messages to localStorage
  useEffect(() => {
    localStorage.setItem('chat-messages', JSON.stringify(messages));
  }, [messages]);

  const sendMessage = async (
    content: string,
    model: string = 'llama2',
    temperature: number = 0.7
  ) => {
    // Cancel any ongoing requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Add user message
    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    accumulatedContentRef.current = '';

    try {
      // Create new AbortController for this request
      abortControllerRef.current = new AbortController();

      // Create assistant message placeholder
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Stream the response from selected provider
      await providerChatStream(
        selectedProvider,
        {
          messages: [...messages, userMessage],
          model,
          temperature
        },
        (chunk) => {
          // Process SSE data
          if (chunk.startsWith('data: ')) {
            const data = chunk.slice(6);

            if (data === '[DONE]') {
              return;
            }

            try {
              const parsed = JSON.parse(data);

              if (parsed.error) {
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (lastIndex >= 0 && newMessages[lastIndex].role === 'assistant') {
                    newMessages[lastIndex] = {
                      ...newMessages[lastIndex],
                      content: `Error: ${parsed.error}`
                    };
                  }
                  return newMessages;
                });
                return;
              }

              if (parsed.content) {
                accumulatedContentRef.current += parsed.content;

                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastIndex = newMessages.length - 1;
                  if (lastIndex >= 0 && newMessages[lastIndex].role === 'assistant') {
                    newMessages[lastIndex] = {
                      ...newMessages[lastIndex],
                      content: accumulatedContentRef.current
                    };
                  }
                  return newMessages;
                });
              }
            } catch (e) {
              console.warn('Could not parse chunk:', chunk);
            }
          }
        },
        (error) => {
          if (error.name !== 'AbortError') {
            setMessages(prev => {
              const newMessages = [...prev];
              const lastIndex = newMessages.length - 1;
              if (lastIndex >= 0 && newMessages[lastIndex].role === 'assistant') {
                newMessages[lastIndex] = {
                  ...newMessages[lastIndex],
                  content: 'Sorry, something went wrong. Please try again.'
                };
              }
              return newMessages;
            });
          }
        }
      );
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        const errorMessage: ChatMessage = {
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const clearConversation = () => {
    setMessages([]);
    localStorage.removeItem('chat-messages');
  };

  return {
    messages,
    isLoading,
    selectedProvider,
    setSelectedProvider,
    sendMessage,
    clearConversation
  };
};

export default useChat;
