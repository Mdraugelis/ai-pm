-- Database Schema for Dual-Purpose Document Management
-- AI Product Manager Agent - Persistent Storage
-- Version: 1.0

-- ============================================================================
-- Documents Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,  -- UUID as string
    doc_category TEXT NOT NULL CHECK(doc_category IN ('input', 'blueprint_knowledge')),
    doc_type TEXT NOT NULL,  -- vendor_doc, research, policy, ticket, brief
    blueprint_subtype TEXT CHECK(blueprint_subtype IN ('policy', 'guideline', 'procedure', 'reference', 'example')),

    -- Content
    content TEXT NOT NULL,
    extracted_text TEXT,  -- Processed/cleaned content
    content_length INTEGER NOT NULL,

    -- Metadata
    filename TEXT,
    file_extension TEXT,
    mime_type TEXT,

    -- Lifecycle
    lifecycle TEXT NOT NULL CHECK(lifecycle IN ('temporary', 'persistent')),
    project_id TEXT DEFAULT 'default',  -- For multi-project support

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,

    -- Classification (for blueprints)
    is_classified BOOLEAN DEFAULT FALSE,
    classification_confidence REAL,

    -- Embeddings (future semantic search)
    embedding_id TEXT,  -- Reference to vector store
    has_embedding BOOLEAN DEFAULT FALSE,

    -- Metadata JSON
    metadata_json TEXT  -- JSON string for flexible metadata
);

-- Index for fast querying by category
CREATE INDEX IF NOT EXISTS idx_documents_category
ON documents(doc_category);

-- Index for blueprints
CREATE INDEX IF NOT EXISTS idx_documents_blueprints
ON documents(doc_category, blueprint_subtype)
WHERE doc_category = 'blueprint_knowledge';

-- Index for lifecycle
CREATE INDEX IF NOT EXISTS idx_documents_lifecycle
ON documents(lifecycle);

-- Index for project
CREATE INDEX IF NOT EXISTS idx_documents_project
ON documents(project_id);

-- Index for timestamps
CREATE INDEX IF NOT EXISTS idx_documents_created
ON documents(created_at);

-- ============================================================================
-- Document Chunks Table (for large documents and semantic search)
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER,
    embedding_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_chunks_document
ON document_chunks(document_id);

-- ============================================================================
-- Document Access Log (tracking usage)
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type TEXT,  -- 'read', 'used_in_context', 'retrieved_semantic'
    agent_mode TEXT,  -- Which mode accessed it
    task_description TEXT
);

CREATE INDEX IF NOT EXISTS idx_access_log_document
ON document_access_log(document_id);

CREATE INDEX IF NOT EXISTS idx_access_log_time
ON document_access_log(accessed_at);

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update updated_at timestamp automatically
CREATE TRIGGER IF NOT EXISTS update_document_timestamp
AFTER UPDATE ON documents
BEGIN
    UPDATE documents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
