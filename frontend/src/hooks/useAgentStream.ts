import { useState, useCallback, useRef } from 'react';
import type { MessageTurn, ThinkingEvent } from '../types/agent';
import { sendMessage } from '../api/agent';
import { notifications } from '@mantine/notifications';

interface UseAgentStreamReturn {
  messages: MessageTurn[];
  isLoading: boolean;
  error: string | null;
  currentThinking: ThinkingEvent[];
  sendMessage: (message: string) => void;
  clearMessages: () => void;
}

export function useAgentStream(): UseAgentStreamReturn {
  const [messages, setMessages] = useState<MessageTurn[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentThinking, setCurrentThinking] = useState<ThinkingEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const handleSendMessage = useCallback((message: string) => {
    // Clean up any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    // Reset state
    setIsLoading(true);
    setError(null);
    setCurrentThinking([]);

    // Add user message immediately
    const userMessage: MessageTurn = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);

    // Create EventSource connection
    try {
      const eventSource = sendMessage(message);
      eventSourceRef.current = eventSource;

      let assistantResponse = '';
      let thinkingEvents: ThinkingEvent[] = [];

      eventSource.onopen = () => {
        console.log('SSE connection opened');
      };

      // Handle named SSE events with addEventListener
      eventSource.addEventListener('thinking', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          const thinkingEvent: ThinkingEvent = {
            step: data.step,
            iteration: data.iteration,
            confidence: data.confidence,
            reasoning: data.reasoning,
            details: data.details,
            timestamp: new Date().toISOString()
          };
          thinkingEvents.push(thinkingEvent);
          setCurrentThinking([...thinkingEvents]);
        } catch (err) {
          console.error('Error parsing thinking event:', err);
        }
      });

      eventSource.addEventListener('iteration', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Iteration:', data.iteration);
        } catch (err) {
          console.error('Error parsing iteration event:', err);
        }
      });

      eventSource.addEventListener('response', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          assistantResponse = data.content;
        } catch (err) {
          console.error('Error parsing response event:', err);
        }
      });

      eventSource.addEventListener('complete', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          const assistantMessage: MessageTurn = {
            role: 'assistant',
            content: assistantResponse || 'I encountered an issue processing your request.',
            timestamp: new Date().toISOString(),
            thinking: thinkingEvents.length > 0 ? thinkingEvents : undefined
          };
          setMessages(prev => [...prev, assistantMessage]);
          setCurrentThinking([]);
          setIsLoading(false);

          // Close connection
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }
        } catch (err) {
          console.error('Error parsing complete event:', err);
        }
      });

      eventSource.addEventListener('error', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          setError(data.message || 'An error occurred');
          notifications.show({
            title: 'Error',
            message: data.message || 'Failed to process message',
            color: 'red'
          });
          setIsLoading(false);

          // Close connection
          if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
          }
        } catch (err) {
          console.error('Error parsing error event:', err);
        }
      });

      eventSource.onerror = (err) => {
        console.error('SSE error:', err);
        setError('Connection error. Please try again.');
        setIsLoading(false);

        // Add error message if no assistant response yet
        if (!assistantResponse) {
          const errorMessage: MessageTurn = {
            role: 'assistant',
            content: 'I encountered a connection error. Please try again.',
            timestamp: new Date().toISOString(),
            thinking: thinkingEvents.length > 0 ? thinkingEvents : undefined
          };
          setMessages(prev => [...prev, errorMessage]);
        }

        // Clean up
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
      };

    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
      setIsLoading(false);

      notifications.show({
        title: 'Error',
        message: 'Failed to send message',
        color: 'red'
      });
    }
  }, []);

  const clearMessages = useCallback(() => {
    // Close any active connections
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    setMessages([]);
    setCurrentThinking([]);
    setIsLoading(false);
    setError(null);
  }, []);

  // Cleanup on unmount
  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    currentThinking,
    sendMessage: handleSendMessage,
    clearMessages
  };
}