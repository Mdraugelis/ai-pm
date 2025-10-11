import React, { useEffect, useRef } from 'react';
import { Stack, Paper, Text, Group, Avatar, Badge, ScrollArea } from '@mantine/core';
import { IconUser, IconRobot } from '@tabler/icons-react';
import type { MessageTurn } from '../types/agent';
import { ThinkingIndicator } from './ThinkingIndicator';

interface MessageListProps {
  messages: MessageTurn[];
  isLoading?: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (messages.length === 0 && !isLoading) {
    return (
      <Paper
        p="xl"
        radius="md"
        style={{
          backgroundColor: 'var(--mantine-color-gray-0)',
          minHeight: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Stack align="center" gap="md">
          <IconRobot size={48} stroke={1.5} color="var(--mantine-color-gray-5)" />
          <Text size="lg" c="dimmed" ta="center">
            No messages yet. Start a conversation!
          </Text>
          <Text size="sm" c="dimmed" ta="center" maw={400}>
            I'm your AI Product Manager assistant. I can help with discovery forms,
            risk assessments, POC planning, and general product management tasks.
          </Text>
        </Stack>
      </Paper>
    );
  }

  return (
    <ScrollArea h="600px" type="auto" offsetScrollbars>
      <Stack gap="md" p="md">
        {messages.map((message, index) => (
          <div key={index}>
            {/* Show thinking indicators if present */}
            {message.thinking && message.thinking.length > 0 && (
              <Stack gap="xs" mb="sm">
                {message.thinking.map((event, eventIndex) => (
                  <ThinkingIndicator
                    key={`${index}-thinking-${eventIndex}`}
                    event={event}
                    defaultExpanded={eventIndex === message.thinking!.length - 1}
                  />
                ))}
              </Stack>
            )}

            {/* Message bubble */}
            <Group
              align="flex-start"
              gap="sm"
              style={{
                justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {message.role === 'assistant' && (
                <Avatar color="blue" radius="xl" size="md">
                  <IconRobot size={20} />
                </Avatar>
              )}

              <Paper
                p="md"
                radius="md"
                withBorder
                style={{
                  maxWidth: '70%',
                  backgroundColor: message.role === 'user'
                    ? 'var(--mantine-color-blue-0)'
                    : 'white',
                  borderColor: message.role === 'user'
                    ? 'var(--mantine-color-blue-3)'
                    : 'var(--mantine-color-gray-3)'
                }}
              >
                <Group justify="space-between" mb="xs">
                  <Badge
                    variant="light"
                    color={message.role === 'user' ? 'blue' : 'gray'}
                    size="sm"
                  >
                    {message.role === 'user' ? 'You' : 'AI Assistant'}
                  </Badge>
                  <Text size="xs" c="dimmed">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Text>
                </Group>

                <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </Text>
              </Paper>

              {message.role === 'user' && (
                <Avatar color="gray" radius="xl" size="md">
                  <IconUser size={20} />
                </Avatar>
              )}
            </Group>
          </div>
        ))}

        {isLoading && (
          <Group align="flex-start" gap="sm">
            <Avatar color="blue" radius="xl" size="md">
              <IconRobot size={20} />
            </Avatar>
            <Paper p="md" radius="md" withBorder>
              <Group gap="xs">
                <Text size="sm" c="dimmed">AI is thinking</Text>
                <div className="thinking-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </Group>
            </Paper>
          </Group>
        )}

        <div ref={scrollRef} />
      </Stack>
    </ScrollArea>
  );
}