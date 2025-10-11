import React from 'react';
import { AppShell, Container, Group, Title, Text, Badge, Grid, Paper, Stack, List, ScrollArea } from '@mantine/core';
import { IconBrain } from '@tabler/icons-react';
import { ModeSelector } from './components/ModeSelector';
import { ChatInterface } from './components/ChatInterface';
import { DualDocumentUpload } from './components/documents';
import { useAgent } from './hooks/useAgent';

function App() {
  const { mode, setMode, clearConversation } = useAgent();

  return (
    <AppShell
      header={{ height: 80 }}
      padding="md"
      styles={{
        header: {
          backgroundColor: 'var(--mantine-color-blue-6)',
          borderBottom: 'none'
        }
      }}
    >
      <AppShell.Header>
        <Container size="xl" h="100%">
          <Group h="100%" justify="space-between" align="center">
            <Group gap="md">
              <IconBrain size={36} color="white" stroke={1.5} />
              <div>
                <Title order={2} c="white" style={{ lineHeight: 1.2 }}>
                  AI Atlas
                </Title>
                <Text size="sm" c="blue.1">
                  AI Product Manager Agent
                </Text>
              </div>
              <Badge
                color="blue.8"
                variant="filled"
                size="lg"
                radius="sm"
              >
                BETA
              </Badge>
            </Group>

            <ModeSelector
              currentMode={mode}
              onModeChange={setMode}
            />
          </Group>
        </Container>
      </AppShell.Header>

      <AppShell.Main>
        <Container size="xl" py="md">
          <Grid gutter="md">
            {/* Main chat interface */}
            <Grid.Col span={{ base: 12, lg: 8 }}>
              <ChatInterface mode={mode} />
            </Grid.Col>

            {/* Side panel with documents and info */}
            <Grid.Col span={{ base: 12, lg: 4 }}>
              <Stack gap="md">
                {/* Document upload */}
                <DualDocumentUpload />

                {/* Agent info */}
                <Paper p="md" radius="md" withBorder>
                  <Group gap="xs" mb="sm">
                    <IconBrain size={20} />
                    <Text fw={500}>Agent Capabilities</Text>
                  </Group>

                  <Stack gap="xs">
                    <Text size="sm">
                      This AI agent uses advanced reasoning to help you with:
                    </Text>

                    <List size="sm" spacing="xs">
                      <List.Item>
                        <Text size="sm">
                          <strong>Multi-step reasoning</strong> - Breaks down complex tasks
                        </Text>
                      </List.Item>
                      <List.Item>
                        <Text size="sm">
                          <strong>Self-verification</strong> - Validates its own outputs
                        </Text>
                      </List.Item>
                      <List.Item>
                        <Text size="sm">
                          <strong>Policy compliance</strong> - Follows governance guidelines
                        </Text>
                      </List.Item>
                      <List.Item>
                        <Text size="sm">
                          <strong>Iterative improvement</strong> - Refines responses based on feedback
                        </Text>
                      </List.Item>
                    </List>

                    <Text size="xs" c="dimmed" mt="sm">
                      The agent shows its thinking process transparently, allowing you to
                      understand how it arrives at its conclusions.
                    </Text>
                  </Stack>
                </Paper>

                {/* Quick tips */}
                <Paper p="md" radius="md" withBorder bg="blue.0">
                  <Text fw={500} size="sm" mb="sm" c="blue.7">
                    💡 Quick Tips
                  </Text>
                  <Stack gap="xs">
                    <Text size="xs">
                      • Be specific in your requests for better results
                    </Text>
                    <Text size="xs">
                      • Upload relevant documents for context
                    </Text>
                    <Text size="xs">
                      • Check thinking indicators to understand the agent's process
                    </Text>
                    <Text size="xs">
                      • Use the appropriate mode for specialized assistance
                    </Text>
                  </Stack>
                </Paper>
              </Stack>
            </Grid.Col>
          </Grid>
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}

export default App;
