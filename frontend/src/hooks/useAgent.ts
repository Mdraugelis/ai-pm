import { useState, useEffect, useCallback } from 'react';
import type { AgentMode, ConversationHistory } from '../types/agent';
import { getConversation, clearConversation as clearConversationAPI } from '../api/agent';
import { notifications } from '@mantine/notifications';

interface UseAgentReturn {
  mode: AgentMode;
  setMode: (mode: AgentMode) => void;
  sessionId?: string;
  loadConversation: () => Promise<void>;
  clearConversation: () => Promise<void>;
}

export function useAgent(): UseAgentReturn {
  const [mode, setMode] = useState<AgentMode>('general');
  const [sessionId, setSessionId] = useState<string>();

  // Load initial conversation state
  const loadConversation = useCallback(async () => {
    try {
      const conversation: ConversationHistory = await getConversation();
      if (conversation.mode) {
        setMode(conversation.mode);
      }
      if (conversation.session_id) {
        setSessionId(conversation.session_id);
      }
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  }, []);

  // Clear conversation
  const clearConversation = useCallback(async () => {
    try {
      await clearConversationAPI();
      notifications.show({
        title: 'Conversation Cleared',
        message: 'Started a new conversation',
        color: 'green'
      });
      // Generate new session ID
      setSessionId(`session-${Date.now()}`);
    } catch (error) {
      console.error('Failed to clear conversation:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to clear conversation',
        color: 'red'
      });
    }
  }, []);

  // Load conversation on mount
  useEffect(() => {
    loadConversation();
  }, [loadConversation]);

  return {
    mode,
    setMode,
    sessionId,
    loadConversation,
    clearConversation
  };
}