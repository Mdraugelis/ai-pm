import axios from 'axios';
import type { AgentMode, ConversationHistory, DocumentInfo } from '../types/agent';

const API_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Set the agent mode
export const setMode = async (mode: AgentMode): Promise<void> => {
  await api.post('/api/agent/mode', { mode });
};

// Send a message and return EventSource for SSE streaming
export const sendMessage = (message: string): EventSource => {
  const eventSource = new EventSource(
    `${API_URL}/api/agent/message/stream?message=${encodeURIComponent(message)}`
  );
  return eventSource;
};

// Alternative POST method for sending messages with streaming
export const sendMessagePost = async (message: string) => {
  const response = await fetch(`${API_URL}/api/agent/message/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.body;
};

// Get conversation history
export const getConversation = async (): Promise<ConversationHistory> => {
  const response = await api.get('/api/agent/conversation');
  return response.data;
};

// Clear conversation
export const clearConversation = async (): Promise<void> => {
  await api.post('/api/agent/conversation/clear');
};

// Upload a document
export const uploadDocument = async (
  content: string,
  documentType: string,
  filename?: string
): Promise<DocumentInfo> => {
  const response = await api.post('/api/documents/upload', {
    content,
    doc_type: documentType,
    metadata: filename ? { filename } : {}
  });
  return response.data;
};

// Get all documents
export const getDocuments = async (): Promise<DocumentInfo[]> => {
  const response = await api.get('/api/documents');
  return response.data.documents;
};

// Delete a document
export const deleteDocument = async (id: number): Promise<void> => {
  await api.delete(`/api/documents/${id}`);
};

// ============================================================================
// Blueprint Knowledge Document APIs
// ============================================================================

export interface BlueprintDocument {
  id: string;
  filename: string;
  doc_type: string;
  doc_category: string;
  blueprint_subtype: string;
  content: string;
  content_length: number;
  lifecycle: string;
  created_at: string;
  metadata: {
    filename?: string;
    classification_confidence?: number;
    classification_reasoning?: string;
    key_concepts?: string[];
    summary?: string;
  };
}

export interface BlueprintUploadResponse {
  doc_id: string;
  filename: string;
  blueprint_subtype: string;
  confidence: number;
  summary: string;
  key_concepts: string[];
  reasoning: string;
  content_length: number;
  message: string;
}

// Upload a blueprint document (with file)
export const uploadBlueprint = async (
  file: File,
  docType: string = 'policy',
  projectId: string = 'default'
): Promise<BlueprintUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('doc_type', docType);
  formData.append('project_id', projectId);

  const response = await axios.post(
    `${API_URL}/api/documents/blueprints`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  );
  return response.data;
};

// Get all blueprint documents
export const getBlueprints = async (
  blueprintSubtype?: string,
  projectId: string = 'default',
  limit: number = 100
): Promise<BlueprintDocument[]> => {
  const params = new URLSearchParams();
  if (blueprintSubtype) params.append('blueprint_subtype', blueprintSubtype);
  params.append('project_id', projectId);
  params.append('limit', limit.toString());

  const response = await api.get(`/api/documents/blueprints?${params.toString()}`);
  return response.data.blueprints;
};

// Get a specific blueprint document
export const getBlueprint = async (docId: string): Promise<BlueprintDocument> => {
  const response = await api.get(`/api/documents/blueprints/${docId}`);
  return response.data;
};

// Delete a blueprint document
export const deleteBlueprint = async (docId: string): Promise<void> => {
  await api.delete(`/api/documents/blueprints/${docId}`);
};

// Get blueprint statistics
export const getBlueprintStats = async (projectId: string = 'default') => {
  const response = await api.get(`/api/documents/blueprints/stats/summary?project_id=${projectId}`);
  return response.data;
};

// Health check
export const checkHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health');
    return response.status === 200;
  } catch {
    return false;
  }
};