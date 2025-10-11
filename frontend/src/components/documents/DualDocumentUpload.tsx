import React, { useState } from 'react';
import {
  Paper,
  Grid,
  Stack,
  Text,
  Group,
  Badge,
  Progress,
  Alert,
  ThemeIcon,
  Box,
  rem
} from '@mantine/core';
import { Dropzone } from '@mantine/dropzone';
import type { FileWithPath } from 'react-dropzone';
import {
  IconUpload,
  IconFile,
  IconX,
  IconCheck,
  IconFileText,
  IconBook,
  IconAlertCircle
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { uploadDocument, uploadBlueprint, type BlueprintUploadResponse } from '../../api/agent';

// File type mappings
const ACCEPTED_MIME_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
  'text/markdown': ['.md'],
  'application/json': ['.json'],
  'text/yaml': ['.yaml', '.yml']
};

interface UploadState {
  isUploading: boolean;
  progress: number;
  fileName?: string;
  result?: BlueprintUploadResponse | { doc_id: number; message: string };
}

export function DualDocumentUpload() {
  const [inputUploadState, setInputUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0
  });

  const [blueprintUploadState, setBlueprintUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0
  });

  // Handle input document upload (temporary, session-based)
  const handleInputDocumentDrop = async (files: FileWithPath[]) => {
    if (files.length === 0) return;

    const file = files[0];
    setInputUploadState({
      isUploading: true,
      progress: 30,
      fileName: file.name
    });

    try {
      // Read file content
      const content = await file.text();

      // Determine document type
      let documentType = 'ticket';
      if (file.name.toLowerCase().includes('vendor')) documentType = 'vendor_doc';
      else if (file.name.toLowerCase().includes('research')) documentType = 'research';
      else if (file.name.toLowerCase().includes('policy')) documentType = 'policy';
      else if (file.name.toLowerCase().includes('brief')) documentType = 'brief';

      setInputUploadState(prev => ({ ...prev, progress: 60 }));

      // Upload document
      const result = await uploadDocument(content, documentType, file.name);

      setInputUploadState({
        isUploading: false,
        progress: 100,
        fileName: file.name,
        result: {
          doc_id: result.doc_id,
          message: `Uploaded successfully`
        }
      });

      notifications.show({
        title: 'Input Document Uploaded',
        message: `${file.name} is now available for this conversation`,
        color: 'blue',
        icon: <IconCheck size={16} />
      });

      // Reset after 3 seconds
      setTimeout(() => {
        setInputUploadState({ isUploading: false, progress: 0 });
      }, 3000);

    } catch (error) {
      console.error('Failed to upload input document:', error);
      setInputUploadState({ isUploading: false, progress: 0 });

      notifications.show({
        title: 'Upload Failed',
        message: `Failed to upload ${file.name}`,
        color: 'red',
        icon: <IconX size={16} />
      });
    }
  };

  // Handle blueprint document upload (persistent, knowledge base)
  const handleBlueprintDrop = async (files: FileWithPath[]) => {
    if (files.length === 0) return;

    const file = files[0];
    setBlueprintUploadState({
      isUploading: true,
      progress: 30,
      fileName: file.name
    });

    try {
      setBlueprintUploadState(prev => ({ ...prev, progress: 60 }));

      // Upload blueprint with auto-classification
      const result = await uploadBlueprint(file, 'policy', 'default');

      setBlueprintUploadState({
        isUploading: false,
        progress: 100,
        fileName: file.name,
        result
      });

      notifications.show({
        title: 'Blueprint Uploaded',
        message: (
          <Stack gap="xs">
            <Text size="sm">{file.name} classified as <strong>{result.blueprint_subtype}</strong></Text>
            <Text size="xs" c="dimmed">{result.summary}</Text>
          </Stack>
        ),
        color: 'violet',
        icon: <IconCheck size={16} />,
        autoClose: 8000
      });

      // Reset after 5 seconds
      setTimeout(() => {
        setBlueprintUploadState({ isUploading: false, progress: 0 });
      }, 5000);

    } catch (error) {
      console.error('Failed to upload blueprint:', error);
      setBlueprintUploadState({ isUploading: false, progress: 0 });

      notifications.show({
        title: 'Upload Failed',
        message: `Failed to upload ${file.name}`,
        color: 'red',
        icon: <IconX size={16} />
      });
    }
  };

  return (
    <Paper p="md" radius="md" withBorder>
      <Text size="lg" fw={600} mb="md">Document Upload</Text>

      <Grid>
        {/* Input Documents Dropzone (Left) */}
        <Grid.Col span={6}>
          <Stack gap="sm">
            <Group gap="xs">
              <ThemeIcon color="blue" variant="light" size="sm">
                <IconFileText size={16} />
              </ThemeIcon>
              <div>
                <Text fw={500} size="sm">Input Documents</Text>
                <Text size="xs" c="dimmed">Temporary, session-based</Text>
              </div>
            </Group>

            <Dropzone
              onDrop={handleInputDocumentDrop}
              onReject={(files) => {
                notifications.show({
                  title: 'Invalid File',
                  message: 'Please upload a supported file type',
                  color: 'orange'
                });
              }}
              maxSize={5 * 1024 ** 2}
              accept={ACCEPTED_MIME_TYPES}
              loading={inputUploadState.isUploading}
              styles={{
                root: {
                  borderColor: 'var(--mantine-color-blue-6)',
                  backgroundColor: inputUploadState.isUploading
                    ? 'var(--mantine-color-blue-0)'
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: 'var(--mantine-color-blue-0)'
                  }
                }
              }}
            >
              <Group justify="center" gap="xl" mih={120} style={{ pointerEvents: 'none' }}>
                <Dropzone.Accept>
                  <IconUpload
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-blue-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Accept>
                <Dropzone.Reject>
                  <IconX
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-red-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Reject>
                <Dropzone.Idle>
                  <IconFileText
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-blue-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Idle>

                <div>
                  <Text size="xl" inline>
                    Drag files here or click to select
                  </Text>
                  <Text size="sm" c="dimmed" inline mt={7}>
                    Upload documents for this conversation
                  </Text>
                </div>
              </Group>
            </Dropzone>

            {inputUploadState.isUploading && inputUploadState.fileName && (
              <Box>
                <Text size="sm" mb="xs">Uploading {inputUploadState.fileName}...</Text>
                <Progress value={inputUploadState.progress} color="blue" animated />
              </Box>
            )}

            {inputUploadState.result && !inputUploadState.isUploading && (
              <Alert icon={<IconCheck size={16} />} color="blue" variant="light">
                <Text size="sm" fw={500}>{inputUploadState.fileName} uploaded</Text>
                <Text size="xs" c="dimmed">Available for this conversation</Text>
              </Alert>
            )}

            <Alert icon={<IconAlertCircle size={16} />} color="blue" variant="light">
              <Text size="xs">
                <strong>Input documents</strong> are temporary and only available for this session.
                Supported formats: PDF, DOCX, TXT, MD, JSON, YAML
              </Text>
            </Alert>
          </Stack>
        </Grid.Col>

        {/* Blueprint Knowledge Dropzone (Right) */}
        <Grid.Col span={6}>
          <Stack gap="sm">
            <Group gap="xs">
              <ThemeIcon color="violet" variant="light" size="sm">
                <IconBook size={16} />
              </ThemeIcon>
              <div>
                <Text fw={500} size="sm">Blueprint Knowledge</Text>
                <Text size="xs" c="dimmed">Persistent, strategic documents</Text>
              </div>
            </Group>

            <Dropzone
              onDrop={handleBlueprintDrop}
              onReject={(files) => {
                notifications.show({
                  title: 'Invalid File',
                  message: 'Please upload a supported file type',
                  color: 'orange'
                });
              }}
              maxSize={100 * 1024 ** 2}
              accept={ACCEPTED_MIME_TYPES}
              loading={blueprintUploadState.isUploading}
              styles={{
                root: {
                  borderColor: 'var(--mantine-color-violet-6)',
                  backgroundColor: blueprintUploadState.isUploading
                    ? 'var(--mantine-color-violet-0)'
                    : 'transparent',
                  '&:hover': {
                    backgroundColor: 'var(--mantine-color-violet-0)'
                  }
                }
              }}
            >
              <Group justify="center" gap="xl" mih={120} style={{ pointerEvents: 'none' }}>
                <Dropzone.Accept>
                  <IconUpload
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-violet-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Accept>
                <Dropzone.Reject>
                  <IconX
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-red-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Reject>
                <Dropzone.Idle>
                  <IconBook
                    style={{ width: rem(52), height: rem(52), color: 'var(--mantine-color-violet-6)' }}
                    stroke={1.5}
                  />
                </Dropzone.Idle>

                <div>
                  <Text size="xl" inline>
                    Drag files here or click to select
                  </Text>
                  <Text size="sm" c="dimmed" inline mt={7}>
                    Upload strategic knowledge documents
                  </Text>
                </div>
              </Group>
            </Dropzone>

            {blueprintUploadState.isUploading && blueprintUploadState.fileName && (
              <Box>
                <Text size="sm" mb="xs">Processing {blueprintUploadState.fileName}...</Text>
                <Progress value={blueprintUploadState.progress} color="violet" animated />
              </Box>
            )}

            {blueprintUploadState.result && !blueprintUploadState.isUploading && 'blueprint_subtype' in blueprintUploadState.result && (
              <Alert icon={<IconCheck size={16} />} color="violet" variant="light">
                <Stack gap="xs">
                  <Group gap="xs">
                    <Text size="sm" fw={500}>{blueprintUploadState.fileName}</Text>
                    <Badge color="violet" size="sm">
                      {blueprintUploadState.result.blueprint_subtype}
                    </Badge>
                  </Group>
                  <Text size="xs" c="dimmed">
                    Confidence: {Math.round(blueprintUploadState.result.confidence * 100)}%
                  </Text>
                  {blueprintUploadState.result.key_concepts && blueprintUploadState.result.key_concepts.length > 0 && (
                    <Group gap={4}>
                      {blueprintUploadState.result.key_concepts.slice(0, 3).map((concept, idx) => (
                        <Badge key={idx} color="violet" variant="outline" size="xs">
                          {concept}
                        </Badge>
                      ))}
                    </Group>
                  )}
                </Stack>
              </Alert>
            )}

            <Alert icon={<IconAlertCircle size={16} />} color="violet" variant="light">
              <Text size="xs">
                <strong>Blueprint documents</strong> are automatically classified and stored permanently.
                They inform the agent's strategic planning. Max size: 100MB
              </Text>
            </Alert>
          </Stack>
        </Grid.Col>
      </Grid>
    </Paper>
  );
}
