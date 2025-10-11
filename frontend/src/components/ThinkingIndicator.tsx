import React, { useState } from 'react';
import { Card, Group, Text, Badge, Collapse, ActionIcon, Progress, Stack, Code, Paper } from '@mantine/core';
import { IconChevronDown, IconChevronUp, IconBrain, IconTarget, IconRocket, IconCheck } from '@tabler/icons-react';
import type { ThinkingEvent } from '../types/agent';

interface ThinkingIndicatorProps {
  event: ThinkingEvent;
  defaultExpanded?: boolean;
}

const stepConfig = {
  gather: {
    icon: <IconBrain size={18} />,
    color: 'blue',
    label: 'Gathering Context',
    description: 'Collecting and analyzing relevant information'
  },
  plan: {
    icon: <IconTarget size={18} />,
    color: 'cyan',
    label: 'Planning',
    description: 'Creating execution strategy'
  },
  execute: {
    icon: <IconRocket size={18} />,
    color: 'green',
    label: 'Executing',
    description: 'Running actions and tools'
  },
  verify: {
    icon: <IconCheck size={18} />,
    color: 'orange',
    label: 'Verifying',
    description: 'Validating results and compliance'
  }
};

export function ThinkingIndicator({ event, defaultExpanded = false }: ThinkingIndicatorProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const config = stepConfig[event.step];

  return (
    <Card
      shadow="xs"
      padding="sm"
      radius="md"
      withBorder
      style={{
        borderLeft: `3px solid var(--mantine-color-${config.color}-6)`,
        backgroundColor: expanded ? 'var(--mantine-color-gray-0)' : 'transparent'
      }}
    >
      <Group justify="space-between" mb={expanded ? 'xs' : 0}>
        <Group gap="sm">
          <Badge
            leftSection={config.icon}
            color={config.color}
            variant="light"
            size="lg"
          >
            {config.label}
          </Badge>

          <Badge variant="outline" size="sm">
            Iteration {event.iteration}
          </Badge>

          {event.confidence !== undefined && (
            <Badge
              variant="dot"
              color={event.confidence > 0.8 ? 'green' : event.confidence > 0.6 ? 'yellow' : 'red'}
            >
              {Math.round(event.confidence * 100)}% confidence
            </Badge>
          )}
        </Group>

        <ActionIcon
          onClick={() => setExpanded(!expanded)}
          variant="subtle"
          color="gray"
          size="sm"
        >
          {expanded ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
        </ActionIcon>
      </Group>

      <Collapse in={expanded}>
        <Stack gap="sm" mt="sm">
          <Text size="sm" c="dimmed">
            {config.description}
          </Text>

          <Paper p="sm" radius="sm" bg="gray.1">
            <Text size="sm" fw={500} mb="xs">Reasoning:</Text>
            <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
              {event.reasoning}
            </Text>
          </Paper>

          {event.details && (
            <Paper p="sm" radius="sm" bg="gray.1">
              <Text size="sm" fw={500} mb="xs">Details:</Text>
              <Code block style={{ fontSize: '0.8rem' }}>
                {typeof event.details === 'string'
                  ? event.details
                  : JSON.stringify(event.details, null, 2)}
              </Code>
            </Paper>
          )}

          {event.confidence !== undefined && (
            <div>
              <Text size="xs" c="dimmed" mb={4}>Confidence Level</Text>
              <Progress
                value={event.confidence * 100}
                color={event.confidence > 0.8 ? 'green' : event.confidence > 0.6 ? 'yellow' : 'red'}
                size="sm"
                radius="xl"
                animate
              />
            </div>
          )}

          {event.timestamp && (
            <Text size="xs" c="dimmed" ta="right">
              {new Date(event.timestamp).toLocaleTimeString()}
            </Text>
          )}
        </Stack>
      </Collapse>
    </Card>
  );
}