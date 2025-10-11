import React from 'react';
import { Select, Badge, Group, Text } from '@mantine/core';
import { IconRobot, IconShieldCheck, IconRocket, IconMessageDots } from '@tabler/icons-react';
import type { AgentMode } from '../types/agent';
import { setMode } from '../api/agent';
import { notifications } from '@mantine/notifications';

interface ModeSelectorProps {
  currentMode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
  disabled?: boolean;
}

const modeOptions = [
  {
    value: 'ai_discovery',
    label: 'AI Discovery Form',
    description: 'Generate AI initiative discovery forms',
    icon: <IconRobot size={20} />,
    color: 'blue'
  },
  {
    value: 'risk_assessment',
    label: 'Risk Assessment',
    description: 'Analyze and assess AI program risks',
    icon: <IconShieldCheck size={20} />,
    color: 'orange'
  },
  {
    value: 'poc_planning',
    label: 'POC Planning',
    description: 'Plan proof of concept initiatives',
    icon: <IconRocket size={20} />,
    color: 'green'
  },
  {
    value: 'general',
    label: 'General Assistance',
    description: 'General AI product management help',
    icon: <IconMessageDots size={20} />,
    color: 'gray'
  }
];

export function ModeSelector({ currentMode, onModeChange, disabled }: ModeSelectorProps) {
  const handleModeChange = async (value: string | null) => {
    if (!value) return;

    const mode = value as AgentMode;

    try {
      await setMode(mode);
      onModeChange(mode);

      const selectedOption = modeOptions.find(opt => opt.value === mode);
      notifications.show({
        title: 'Mode Changed',
        message: `Switched to ${selectedOption?.label} mode`,
        color: selectedOption?.color || 'blue'
      });
    } catch (error) {
      console.error('Failed to set mode:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to change agent mode',
        color: 'red'
      });
    }
  };

  const currentOption = modeOptions.find(opt => opt.value === currentMode);

  return (
    <Group gap="sm">
      <Select
        value={currentMode}
        onChange={handleModeChange}
        data={modeOptions.map(option => ({
          value: option.value,
          label: option.label
        }))}
        disabled={disabled}
        placeholder="Select agent mode"
        leftSection={currentOption?.icon}
        styles={{
          input: { minWidth: 200 }
        }}
      />

      <Badge
        color={currentOption?.color || 'blue'}
        variant="light"
        size="lg"
      >
        {currentOption?.label || 'Unknown Mode'}
      </Badge>

      {currentOption && (
        <Text size="sm" c="dimmed" style={{ maxWidth: 300 }}>
          {currentOption.description}
        </Text>
      )}
    </Group>
  );
}