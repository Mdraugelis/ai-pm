import React, { useEffect } from 'react';
import { Stack, Paper, Title, Text, Alert, Group } from '@mantine/core';
import { IconInfoCircle, IconBrain } from '@tabler/icons-react';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ThinkingIndicator } from './ThinkingIndicator';
import { useAgentStream } from '../hooks/useAgentStream';
import { clearConversation as clearConversationAPI } from '../api/agent';
import { notifications } from '@mantine/notifications';

interface ChatInterfaceProps {
  mode: string;
}

export function ChatInterface({ mode }: ChatInterfaceProps) {
  const { messages, isLoading, error, currentThinking, sendMessage, clearMessages } = useAgentStream();

  const handleClearConversation = async () => {
    try {
      await clearConversationAPI();
      clearMessages();
      notifications.show({
        title: 'Conversation Cleared',
        message: 'Started a new conversation',
        color: 'green'
      });
    } catch (err) {
      console.error('Failed to clear conversation:', err);
      notifications.show({
        title: 'Error',
        message: 'Failed to clear conversation',
        color: 'red'
      });
    }
  };

  // Show current thinking events while processing
  const showThinkingSection = currentThinking.length > 0 && isLoading;

  return (
    <Stack gap="md" h="100%">
      {/* Info banner */}
      <Alert
        icon={<IconInfoCircle />}
        title="How to Use"
        color="blue"
        variant="light"
        radius="md"
      >
        <Text size="sm">
          I'm your AI Product Manager assistant. I can help you with:
        </Text>
        <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
          <li><Text size="sm"><strong>AI Discovery:</strong> Generate comprehensive discovery forms for new AI initiatives</Text></li>
          <li><Text size="sm"><strong>Risk Assessment:</strong> Analyze and evaluate risks for AI programs</Text></li>
          <li><Text size="sm"><strong>POC Planning:</strong> Create proof-of-concept plans and roadmaps</Text></li>
          <li><Text size="sm"><strong>General Assistance:</strong> Answer questions about AI product management</Text></li>
        </ul>
        <Text size="sm" c="dimmed">
          Select a mode above to get specialized assistance, or use General mode for any questions.
        </Text>
      </Alert>

      {/* Current thinking section (shown during processing) */}
      {showThinkingSection && (
        <Paper p="md" radius="md" withBorder bg="blue.0">
          <Group gap="xs" mb="sm">
            <IconBrain size={20} color="var(--mantine-color-blue-6)" />
            <Title order={5} c="blue.7">Agent Reasoning</Title>
          </Group>
          <Stack gap="xs">
            {currentThinking.map((event, index) => (
              <ThinkingIndicator
                key={`current-${index}`}
                event={event}
                defaultExpanded={index === currentThinking.length - 1}
              />
            ))}
          </Stack>
        </Paper>
      )}

      {/* Error display */}
      {error && (
        <Alert
          icon={<IconInfoCircle />}
          title="Error"
          color="red"
          variant="filled"
          radius="md"
        >
          {error}
        </Alert>
      )}

      {/* Message list */}
      <Paper
        p={0}
        radius="md"
        withBorder
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
      >
        <MessageList
          messages={messages}
          isLoading={isLoading}
        />
      </Paper>

      {/* Message input */}
      <MessageInput
        onSendMessage={sendMessage}
        onClearConversation={handleClearConversation}
        disabled={isLoading}
        placeholder={
          isLoading
            ? 'AI is thinking...'
            : `Ask me about ${mode === 'ai_discovery' ? 'AI discovery forms' :
                mode === 'risk_assessment' ? 'risk analysis' :
                mode === 'poc_planning' ? 'POC planning' :
                'AI product management'}...`
        }
      />
    </Stack>
  );
}