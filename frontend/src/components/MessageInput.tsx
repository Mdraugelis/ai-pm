import React, { useState, KeyboardEvent } from 'react';
import { TextInput, ActionIcon, Group, Paper } from '@mantine/core';
import { IconSend, IconEraser } from '@tabler/icons-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onClearConversation: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSendMessage,
  onClearConversation,
  disabled,
  placeholder = 'Type your message...'
}: MessageInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper p="md" radius="md" withBorder>
      <Group gap="sm">
        <TextInput
          value={message}
          onChange={(e) => setMessage(e.currentTarget.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          style={{ flex: 1 }}
          size="md"
          rightSection={
            <ActionIcon
              onClick={handleSend}
              disabled={!message.trim() || disabled}
              color="blue"
              variant="filled"
              size="md"
            >
              <IconSend size={18} />
            </ActionIcon>
          }
        />

        <ActionIcon
          onClick={onClearConversation}
          disabled={disabled}
          color="red"
          variant="light"
          size="lg"
          title="Clear conversation"
        >
          <IconEraser size={20} />
        </ActionIcon>
      </Group>
    </Paper>
  );
}