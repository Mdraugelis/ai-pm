import React, { useState, useEffect } from 'react';
import { Paper, Group, Text, Button, Stack, Badge, ActionIcon, FileButton, List, Alert, ScrollArea } from '@mantine/core';
import { IconUpload, IconFile, IconTrash, IconFilePlus } from '@tabler/icons-react';
import { uploadDocument, getDocuments, deleteDocument } from '../api/agent';
import type { DocumentInfo } from '../types/agent';
import { notifications } from '@mantine/notifications';

export function DocumentUpload() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load documents',
        color: 'red'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File | null) => {
    if (!file) return;

    try {
      setIsUploading(true);

      // Read file content
      const content = await file.text();

      // Determine document type from extension or default to 'ticket'
      // Backend expects: vendor_doc, research, policy, ticket, brief
      const extension = file.name.split('.').pop()?.toLowerCase();
      let documentType: string = 'ticket'; // default type

      // Try to infer type from filename
      if (file.name.toLowerCase().includes('vendor')) documentType = 'vendor_doc';
      else if (file.name.toLowerCase().includes('research')) documentType = 'research';
      else if (file.name.toLowerCase().includes('policy')) documentType = 'policy';
      else if (file.name.toLowerCase().includes('brief')) documentType = 'brief';

      // Upload document
      const uploadedDoc = await uploadDocument(content, documentType, file.name);

      // Add to list
      setDocuments(prev => [...prev, uploadedDoc]);

      notifications.show({
        title: 'Document Uploaded',
        message: `Successfully uploaded ${file.name}`,
        color: 'green'
      });
    } catch (error) {
      console.error('Failed to upload document:', error);
      notifications.show({
        title: 'Upload Failed',
        message: 'Failed to upload document',
        color: 'red'
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: number, filename: string) => {
    try {
      await deleteDocument(id);
      setDocuments(prev => prev.filter(doc => doc.doc_id !== id));

      notifications.show({
        title: 'Document Deleted',
        message: `Deleted ${filename}`,
        color: 'orange'
      });
    } catch (error) {
      console.error('Failed to delete document:', error);
      notifications.show({
        title: 'Delete Failed',
        message: 'Failed to delete document',
        color: 'red'
      });
    }
  };

  const handlePasteText = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (!text) {
        notifications.show({
          title: 'No Content',
          message: 'Clipboard is empty',
          color: 'yellow'
        });
        return;
      }

      setIsUploading(true);

      // Upload as ticket document (default type)
      const uploadedDoc = await uploadDocument(
        text,
        'ticket',
        `pasted_${Date.now()}.txt`
      );

      setDocuments(prev => [...prev, uploadedDoc]);

      notifications.show({
        title: 'Text Uploaded',
        message: 'Successfully uploaded text from clipboard',
        color: 'green'
      });
    } catch (error) {
      console.error('Failed to paste text:', error);
      notifications.show({
        title: 'Paste Failed',
        message: 'Failed to read from clipboard',
        color: 'red'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Paper p="md" radius="md" withBorder>
      <Group justify="space-between" mb="md">
        <Group gap="xs">
          <IconFile size={20} />
          <Text fw={500}>Documents</Text>
          <Badge variant="filled" size="sm">{documents.length}</Badge>
        </Group>

        <Group gap="xs">
          <FileButton
            onChange={handleFileUpload}
            accept=".txt,.json,.yaml,.yml,.md,.pdf"
            disabled={isUploading}
          >
            {(props) => (
              <Button
                {...props}
                leftSection={<IconUpload size={16} />}
                size="sm"
                loading={isUploading}
              >
                Upload File
              </Button>
            )}
          </FileButton>

          <Button
            leftSection={<IconFilePlus size={16} />}
            size="sm"
            variant="light"
            onClick={handlePasteText}
            disabled={isUploading}
          >
            Paste Text
          </Button>
        </Group>
      </Group>

      {documents.length === 0 ? (
        <Alert
          icon={<IconFile />}
          color="gray"
          variant="light"
          radius="md"
        >
          <Text size="sm">
            No documents uploaded yet. Upload documents to provide context for the AI assistant.
            Supported formats: TXT, JSON, YAML, Markdown, PDF
          </Text>
        </Alert>
      ) : (
        <ScrollArea h={200}>
          <List spacing="xs" size="sm">
            {documents.map(doc => {
              const filename = doc.metadata?.filename || 'Unnamed document';
              return (
                <List.Item
                  key={doc.doc_id}
                  icon={
                    <Badge
                      variant="light"
                      size="sm"
                      color={
                        doc.doc_type === 'vendor_doc' ? 'blue' :
                        doc.doc_type === 'research' ? 'green' :
                        doc.doc_type === 'policy' ? 'purple' :
                        doc.doc_type === 'brief' ? 'cyan' :
                        doc.doc_type === 'ticket' ? 'orange' :
                        'gray'
                      }
                    >
                      {doc.doc_type.toUpperCase()}
                    </Badge>
                  }
                >
                  <Group justify="space-between">
                    <div>
                      <Text size="sm" fw={500}>{filename}</Text>
                      <Text size="xs" c="dimmed">
                        Uploaded {new Date(doc.added_at).toLocaleString()} • {doc.content_length} bytes
                      </Text>
                    </div>

                    <ActionIcon
                      color="red"
                      variant="subtle"
                      size="sm"
                      onClick={() => handleDelete(doc.doc_id, filename)}
                      title="Delete document"
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Group>
                </List.Item>
              );
            })}
          </List>
        </ScrollArea>
      )}
    </Paper>
  );
}