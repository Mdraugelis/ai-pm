import React, { useState, useEffect } from 'react';
import {
  Paper,
  Stack,
  Group,
  Text,
  Badge,
  Button,
  Table,
  TextInput,
  Select,
  ActionIcon,
  Modal,
  ScrollArea,
  Alert,
  Grid,
  Card,
  RingProgress,
  ThemeIcon,
  Loader,
  Center,
  Menu,
  Code,
  Divider
} from '@mantine/core';
import {
  IconBook,
  IconSearch,
  IconTrash,
  IconEye,
  IconFilter,
  IconRefresh,
  IconDownload,
  IconCheck,
  IconAlertCircle,
  IconFileText,
  IconX,
  IconDots
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { modals } from '@mantine/modals';
import {
  getBlueprints,
  getBlueprint,
  deleteBlueprint,
  getBlueprintStats,
  type BlueprintDocument
} from '../../api/agent';

// Blueprint subtype color mapping
const SUBTYPE_COLORS: Record<string, string> = {
  policy: 'red',
  guideline: 'blue',
  procedure: 'green',
  reference: 'yellow',
  example: 'violet'
};

// Blueprint subtype labels
const SUBTYPE_LABELS: Record<string, string> = {
  policy: 'Policy',
  guideline: 'Guideline',
  procedure: 'Procedure',
  reference: 'Reference',
  example: 'Example'
};

export function BlueprintLibrary() {
  const [blueprints, setBlueprints] = useState<BlueprintDocument[]>([]);
  const [filteredBlueprints, setFilteredBlueprints] = useState<BlueprintDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubtype, setSelectedSubtype] = useState<string | null>(null);
  const [selectedBlueprint, setSelectedBlueprint] = useState<BlueprintDocument | null>(null);
  const [detailsOpened, setDetailsOpened] = useState(false);
  const [stats, setStats] = useState<any>(null);

  // Load blueprints on mount
  useEffect(() => {
    loadBlueprints();
    loadStats();
  }, []);

  // Filter blueprints when search or filter changes
  useEffect(() => {
    filterBlueprints();
  }, [searchQuery, selectedSubtype, blueprints]);

  const loadBlueprints = async () => {
    try {
      setIsLoading(true);
      const docs = await getBlueprints(undefined, 'default', 100);
      setBlueprints(docs);
    } catch (error) {
      console.error('Failed to load blueprints:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load blueprint documents',
        color: 'red',
        icon: <IconX size={16} />
      });
    } finally {
      setIsLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await getBlueprintStats('default');
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const filterBlueprints = () => {
    let filtered = [...blueprints];

    // Filter by subtype
    if (selectedSubtype && selectedSubtype !== 'all') {
      filtered = filtered.filter(bp => bp.blueprint_subtype === selectedSubtype);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(bp =>
        bp.metadata.filename?.toLowerCase().includes(query) ||
        bp.blueprint_subtype?.toLowerCase().includes(query) ||
        bp.metadata.key_concepts?.some(concept => concept.toLowerCase().includes(query))
      );
    }

    setFilteredBlueprints(filtered);
  };

  const handleViewDetails = async (docId: string) => {
    try {
      const blueprint = await getBlueprint(docId);
      setSelectedBlueprint(blueprint);
      setDetailsOpened(true);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to load blueprint details',
        color: 'red'
      });
    }
  };

  const handleDelete = (docId: string, filename: string) => {
    modals.openConfirmModal({
      title: 'Delete Blueprint',
      children: (
        <Text size="sm">
          Are you sure you want to delete <strong>{filename}</strong>? This action cannot be undone.
          The agent will no longer have access to this knowledge.
        </Text>
      ),
      labels: { confirm: 'Delete', cancel: 'Cancel' },
      confirmProps: { color: 'red' },
      onConfirm: async () => {
        try {
          await deleteBlueprint(docId);
          setBlueprints(prev => prev.filter(bp => bp.id !== docId));
          await loadStats(); // Reload stats

          notifications.show({
            title: 'Blueprint Deleted',
            message: `${filename} has been removed from the knowledge base`,
            color: 'orange',
            icon: <IconCheck size={16} />
          });
        } catch (error) {
          notifications.show({
            title: 'Delete Failed',
            message: 'Failed to delete blueprint',
            color: 'red',
            icon: <IconX size={16} />
          });
        }
      }
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'yellow';
    return 'orange';
  };

  if (isLoading) {
    return (
      <Paper p="md" radius="md" withBorder>
        <Center h={400}>
          <Stack align="center" gap="md">
            <Loader size="lg" variant="dots" />
            <Text c="dimmed">Loading blueprint library...</Text>
          </Stack>
        </Center>
      </Paper>
    );
  }

  return (
    <Paper p="md" radius="md" withBorder>
      <Stack gap="md">
        {/* Header */}
        <Group justify="space-between">
          <Group gap="xs">
            <ThemeIcon color="violet" variant="light" size="lg">
              <IconBook size={20} />
            </ThemeIcon>
            <div>
              <Text size="lg" fw={600}>Blueprint Library</Text>
              <Text size="xs" c="dimmed">Strategic knowledge documents</Text>
            </div>
            <Badge color="violet" variant="filled">{blueprints.length}</Badge>
          </Group>

          <Button
            leftSection={<IconRefresh size={16} />}
            variant="light"
            size="sm"
            onClick={() => {
              loadBlueprints();
              loadStats();
            }}
          >
            Refresh
          </Button>
        </Group>

        {/* Statistics Cards */}
        {stats && stats.statistics && (
          <Grid>
            <Grid.Col span={3}>
              <Card padding="sm" radius="md" withBorder>
                <Stack gap="xs">
                  <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Total Blueprints</Text>
                  <Text size="xl" fw={700}>{stats.statistics.total_documents}</Text>
                </Stack>
              </Card>
            </Grid.Col>

            {stats.statistics.blueprint_breakdown && Object.entries(stats.statistics.blueprint_breakdown).map(([type, count]: [string, any]) => (
              <Grid.Col span={3} key={type}>
                <Card padding="sm" radius="md" withBorder>
                  <Stack gap="xs">
                    <Group gap="xs">
                      <Badge color={SUBTYPE_COLORS[type] || 'gray'} size="xs">
                        {SUBTYPE_LABELS[type] || type}
                      </Badge>
                    </Group>
                    <Text size="xl" fw={700}>{count}</Text>
                  </Stack>
                </Card>
              </Grid.Col>
            ))}
          </Grid>
        )}

        {/* Filters */}
        <Group>
          <TextInput
            placeholder="Search blueprints..."
            leftSection={<IconSearch size={16} />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.currentTarget.value)}
            style={{ flex: 1 }}
          />

          <Select
            placeholder="Filter by type"
            leftSection={<IconFilter size={16} />}
            data={[
              { value: 'all', label: 'All Types' },
              { value: 'policy', label: 'Policy' },
              { value: 'guideline', label: 'Guideline' },
              { value: 'procedure', label: 'Procedure' },
              { value: 'reference', label: 'Reference' },
              { value: 'example', label: 'Example' }
            ]}
            value={selectedSubtype}
            onChange={setSelectedSubtype}
            clearable
            style={{ width: 200 }}
          />
        </Group>

        {/* Blueprints Table */}
        {filteredBlueprints.length === 0 ? (
          <Alert icon={<IconAlertCircle size={16} />} color="gray" variant="light">
            <Text size="sm">
              {blueprints.length === 0
                ? 'No blueprints uploaded yet. Upload strategic documents to build the knowledge base.'
                : 'No blueprints match your filters.'}
            </Text>
          </Alert>
        ) : (
          <ScrollArea>
            <Table highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Document</Table.Th>
                  <Table.Th>Type</Table.Th>
                  <Table.Th>Confidence</Table.Th>
                  <Table.Th>Key Concepts</Table.Th>
                  <Table.Th>Uploaded</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {filteredBlueprints.map((blueprint) => (
                  <Table.Tr key={blueprint.id}>
                    <Table.Td>
                      <Group gap="xs">
                        <ThemeIcon color="violet" variant="light" size="sm">
                          <IconFileText size={14} />
                        </ThemeIcon>
                        <div>
                          <Text size="sm" fw={500}>
                            {blueprint.metadata.filename || 'Unnamed'}
                          </Text>
                          <Text size="xs" c="dimmed">
                            {(blueprint.content_length / 1024).toFixed(1)} KB
                          </Text>
                        </div>
                      </Group>
                    </Table.Td>

                    <Table.Td>
                      <Badge
                        color={SUBTYPE_COLORS[blueprint.blueprint_subtype] || 'gray'}
                        variant="light"
                      >
                        {SUBTYPE_LABELS[blueprint.blueprint_subtype] || blueprint.blueprint_subtype}
                      </Badge>
                    </Table.Td>

                    <Table.Td>
                      {blueprint.metadata.classification_confidence && (
                        <Group gap="xs">
                          <RingProgress
                            size={32}
                            thickness={4}
                            sections={[{
                              value: blueprint.metadata.classification_confidence * 100,
                              color: getConfidenceColor(blueprint.metadata.classification_confidence)
                            }]}
                          />
                          <Text size="sm">
                            {Math.round(blueprint.metadata.classification_confidence * 100)}%
                          </Text>
                        </Group>
                      )}
                    </Table.Td>

                    <Table.Td>
                      {blueprint.metadata.key_concepts && blueprint.metadata.key_concepts.length > 0 ? (
                        <Group gap={4}>
                          {blueprint.metadata.key_concepts.slice(0, 2).map((concept, idx) => (
                            <Badge key={idx} size="xs" variant="outline" color="violet">
                              {concept}
                            </Badge>
                          ))}
                          {blueprint.metadata.key_concepts.length > 2 && (
                            <Badge size="xs" variant="outline" color="gray">
                              +{blueprint.metadata.key_concepts.length - 2}
                            </Badge>
                          )}
                        </Group>
                      ) : (
                        <Text size="xs" c="dimmed">None</Text>
                      )}
                    </Table.Td>

                    <Table.Td>
                      <Text size="xs" c="dimmed">
                        {new Date(blueprint.created_at).toLocaleDateString()}
                      </Text>
                    </Table.Td>

                    <Table.Td>
                      <Group gap={4}>
                        <ActionIcon
                          variant="subtle"
                          color="violet"
                          onClick={() => handleViewDetails(blueprint.id)}
                          title="View details"
                        >
                          <IconEye size={16} />
                        </ActionIcon>

                        <ActionIcon
                          variant="subtle"
                          color="red"
                          onClick={() => handleDelete(blueprint.id, blueprint.metadata.filename || 'document')}
                          title="Delete"
                        >
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </ScrollArea>
        )}
      </Stack>

      {/* Details Modal */}
      <Modal
        opened={detailsOpened}
        onClose={() => setDetailsOpened(false)}
        title="Blueprint Details"
        size="xl"
      >
        {selectedBlueprint && (
          <Stack gap="md">
            {/* Header */}
            <Group justify="space-between">
              <div>
                <Text size="lg" fw={600}>{selectedBlueprint.metadata.filename}</Text>
                <Group gap="xs" mt="xs">
                  <Badge color={SUBTYPE_COLORS[selectedBlueprint.blueprint_subtype]}>
                    {SUBTYPE_LABELS[selectedBlueprint.blueprint_subtype]}
                  </Badge>
                  {selectedBlueprint.metadata.classification_confidence && (
                    <Badge color={getConfidenceColor(selectedBlueprint.metadata.classification_confidence)}>
                      {Math.round(selectedBlueprint.metadata.classification_confidence * 100)}% confidence
                    </Badge>
                  )}
                </Group>
              </div>
            </Group>

            <Divider />

            {/* Summary */}
            {selectedBlueprint.metadata.summary && (
              <div>
                <Text size="sm" fw={600} mb="xs">Summary</Text>
                <Text size="sm" c="dimmed">{selectedBlueprint.metadata.summary}</Text>
              </div>
            )}

            {/* Key Concepts */}
            {selectedBlueprint.metadata.key_concepts && selectedBlueprint.metadata.key_concepts.length > 0 && (
              <div>
                <Text size="sm" fw={600} mb="xs">Key Concepts</Text>
                <Group gap="xs">
                  {selectedBlueprint.metadata.key_concepts.map((concept, idx) => (
                    <Badge key={idx} variant="light" color="violet">
                      {concept}
                    </Badge>
                  ))}
                </Group>
              </div>
            )}

            {/* Classification Reasoning */}
            {selectedBlueprint.metadata.classification_reasoning && (
              <div>
                <Text size="sm" fw={600} mb="xs">Classification Reasoning</Text>
                <Alert icon={<IconAlertCircle size={16} />} color="violet" variant="light">
                  <Text size="sm">{selectedBlueprint.metadata.classification_reasoning}</Text>
                </Alert>
              </div>
            )}

            {/* Metadata */}
            <div>
              <Text size="sm" fw={600} mb="xs">Metadata</Text>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Document ID:</Text>
                  <Code>{selectedBlueprint.id}</Code>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Size:</Text>
                  <Text size="sm">{(selectedBlueprint.content_length / 1024).toFixed(2)} KB</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Uploaded:</Text>
                  <Text size="sm">{new Date(selectedBlueprint.created_at).toLocaleString()}</Text>
                </Group>
                <Group justify="space-between">
                  <Text size="sm" c="dimmed">Lifecycle:</Text>
                  <Badge size="sm">{selectedBlueprint.lifecycle}</Badge>
                </Group>
              </Stack>
            </div>

            {/* Content Preview */}
            <div>
              <Text size="sm" fw={600} mb="xs">Content Preview</Text>
              <ScrollArea h={200}>
                <Code block>{selectedBlueprint.content.substring(0, 1000)}...</Code>
              </ScrollArea>
            </div>
          </Stack>
        )}
      </Modal>
    </Paper>
  );
}
