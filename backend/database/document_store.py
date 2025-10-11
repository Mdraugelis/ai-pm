"""
Document Store
AI Product Manager Agent - Backend Database Layer

Handles persistent storage of documents using SQLite.
Supports dual-purpose document management:
- Input documents (temporary, task-specific)
- Blueprint knowledge documents (persistent, strategic)
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Document Store
# ============================================================================


class DocumentStore:
    """
    SQLite-based persistent storage for documents

    Features:
    - Dual-category support (input vs blueprint_knowledge)
    - Full-text search capability
    - Access logging for usage tracking
    - Project isolation for multi-tenancy
    - Automatic schema initialization
    """

    def __init__(self, db_path: str = "data/documents.db"):
        """
        Initialize document store

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        self._initialize_schema()

        logger.info("DocumentStore initialized", db_path=str(self.db_path))

    def _initialize_schema(self) -> None:
        """Initialize database schema from SQL file"""
        schema_path = Path(__file__).parent / "schema.sql"

        if not schema_path.exists():
            logger.warning("Schema file not found, creating minimal schema")
            # Minimal fallback schema
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS documents (
                        id TEXT PRIMARY KEY,
                        doc_category TEXT NOT NULL,
                        doc_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            return

        # Load and execute schema
        with open(schema_path, encoding="utf-8") as f:
            schema_sql = f.read()

        with self._get_connection() as conn:
            conn.executescript(schema_sql)

        logger.info("Database schema initialized")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get database connection

        Returns:
            SQLite connection with row_factory set
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    # ========================================================================
    # Document CRUD Operations
    # ========================================================================

    def create_document(
        self,
        content: str,
        doc_type: str,
        doc_category: str = "input",
        blueprint_subtype: Optional[str] = None,
        lifecycle: str = "temporary",
        project_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create new document

        Args:
            content: Document content
            doc_type: Document type (vendor_doc, research, policy, ticket, brief)
            doc_category: Category (input or blueprint_knowledge)
            blueprint_subtype: For blueprints (policy, guideline, procedure, reference, example)
            lifecycle: Lifecycle (temporary or persistent)
            project_id: Project identifier
            metadata: Additional metadata

        Returns:
            Document ID (UUID string)
        """
        doc_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata or {})

        # Extract filename if available
        filename = metadata.get("filename") if metadata else None

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    id, doc_category, doc_type, blueprint_subtype,
                    content, content_length, lifecycle, project_id,
                    filename, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    doc_category,
                    doc_type,
                    blueprint_subtype,
                    content,
                    len(content),
                    lifecycle,
                    project_id,
                    filename,
                    metadata_json,
                ),
            )
            conn.commit()

        logger.info(
            "Document created",
            doc_id=doc_id,
            doc_category=doc_category,
            doc_type=doc_type,
            content_length=len(content),
        )

        return doc_id

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document dict or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM documents WHERE id = ?
                """,
                (doc_id,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        # Update last accessed
        self._update_last_accessed(doc_id)

        return self._row_to_dict(row)

    def list_documents(
        self,
        doc_category: Optional[str] = None,
        blueprint_subtype: Optional[str] = None,
        lifecycle: Optional[str] = None,
        project_id: str = "default",
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List documents with filtering

        Args:
            doc_category: Filter by category (input or blueprint_knowledge)
            blueprint_subtype: Filter by blueprint subtype
            lifecycle: Filter by lifecycle (temporary or persistent)
            project_id: Filter by project
            limit: Maximum number of results

        Returns:
            List of document dicts
        """
        query = "SELECT * FROM documents WHERE project_id = ?"
        params = [project_id]

        if doc_category:
            query += " AND doc_category = ?"
            params.append(doc_category)

        if blueprint_subtype:
            query += " AND blueprint_subtype = ?"
            params.append(blueprint_subtype)

        if lifecycle:
            query += " AND lifecycle = ?"
            params.append(lifecycle)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def update_document(
        self, doc_id: str, updates: Dict[str, Any]
    ) -> bool:
        """
        Update document fields

        Args:
            doc_id: Document ID
            updates: Dict of fields to update

        Returns:
            True if updated, False if not found
        """
        # Build dynamic UPDATE query
        allowed_fields = {
            "blueprint_subtype",
            "extracted_text",
            "is_classified",
            "classification_confidence",
            "embedding_id",
            "has_embedding",
        }

        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            return False

        set_clause = ", ".join(f"{field} = ?" for field in update_fields.keys())
        values = list(update_fields.values()) + [doc_id]

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE documents SET {set_clause} WHERE id = ?",
                values,
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM documents WHERE id = ?",
                (doc_id,),
            )
            conn.commit()

        deleted = cursor.rowcount > 0

        if deleted:
            logger.info("Document deleted", doc_id=doc_id)

        return deleted

    def clear_temporary_documents(self, project_id: str = "default") -> int:
        """
        Clear all temporary documents for a project

        Args:
            project_id: Project identifier

        Returns:
            Number of documents deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM documents
                WHERE lifecycle = 'temporary' AND project_id = ?
                """,
                (project_id,),
            )
            conn.commit()

        count = cursor.rowcount
        logger.info("Temporary documents cleared", count=count, project_id=project_id)

        return count

    # ========================================================================
    # Blueprint-Specific Operations
    # ========================================================================

    def get_blueprints(
        self,
        blueprint_subtype: Optional[str] = None,
        project_id: str = "default",
    ) -> List[Dict[str, Any]]:
        """
        Get all blueprint knowledge documents

        Args:
            blueprint_subtype: Filter by subtype (policy, guideline, etc.)
            project_id: Project identifier

        Returns:
            List of blueprint documents
        """
        return self.list_documents(
            doc_category="blueprint_knowledge",
            blueprint_subtype=blueprint_subtype,
            project_id=project_id,
            limit=1000,  # Blueprints typically fewer
        )

    def get_blueprint_policies(self, project_id: str = "default") -> List[Dict[str, Any]]:
        """Get all blueprint documents classified as policies"""
        return self.get_blueprints(blueprint_subtype="policy", project_id=project_id)

    def get_blueprint_guidelines(self, project_id: str = "default") -> List[Dict[str, Any]]:
        """Get all blueprint documents classified as guidelines"""
        return self.get_blueprints(blueprint_subtype="guideline", project_id=project_id)

    # ========================================================================
    # Access Logging
    # ========================================================================

    def log_access(
        self,
        doc_id: str,
        access_type: str = "read",
        agent_mode: Optional[str] = None,
        task_description: Optional[str] = None,
    ) -> None:
        """
        Log document access

        Args:
            doc_id: Document ID
            access_type: Type of access (read, used_in_context, retrieved_semantic)
            agent_mode: Agent mode during access
            task_description: Task being performed
        """
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO document_access_log (
                    document_id, access_type, agent_mode, task_description
                ) VALUES (?, ?, ?, ?)
                """,
                (doc_id, access_type, agent_mode, task_description),
            )
            conn.commit()

    def _update_last_accessed(self, doc_id: str) -> None:
        """Update document's last accessed timestamp"""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE documents SET last_accessed_at = CURRENT_TIMESTAMP WHERE id = ?",
                (doc_id,),
            )
            conn.commit()

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """
        Convert SQLite row to dict

        Args:
            row: SQLite Row object

        Returns:
            Dict representation
        """
        doc_dict = dict(row)

        # Parse metadata JSON
        if doc_dict.get("metadata_json"):
            try:
                doc_dict["metadata"] = json.loads(doc_dict["metadata_json"])
            except json.JSONDecodeError:
                doc_dict["metadata"] = {}
        else:
            doc_dict["metadata"] = {}

        # Remove json field
        doc_dict.pop("metadata_json", None)

        return doc_dict

    def get_stats(self, project_id: str = "default") -> Dict[str, Any]:
        """
        Get document storage statistics

        Args:
            project_id: Project identifier

        Returns:
            Stats dict
        """
        with self._get_connection() as conn:
            # Total documents
            cursor = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE project_id = ?",
                (project_id,),
            )
            total_docs = cursor.fetchone()[0]

            # By category
            cursor = conn.execute(
                """
                SELECT doc_category, COUNT(*) as count
                FROM documents WHERE project_id = ?
                GROUP BY doc_category
                """,
                (project_id,),
            )
            by_category = {row["doc_category"]: row["count"] for row in cursor.fetchall()}

            # By lifecycle
            cursor = conn.execute(
                """
                SELECT lifecycle, COUNT(*) as count
                FROM documents WHERE project_id = ?
                GROUP BY lifecycle
                """,
                (project_id,),
            )
            by_lifecycle = {row["lifecycle"]: row["count"] for row in cursor.fetchall()}

            # Blueprint breakdown
            cursor = conn.execute(
                """
                SELECT blueprint_subtype, COUNT(*) as count
                FROM documents
                WHERE project_id = ? AND doc_category = 'blueprint_knowledge'
                GROUP BY blueprint_subtype
                """,
                (project_id,),
            )
            blueprint_breakdown = {row["blueprint_subtype"]: row["count"] for row in cursor.fetchall()}

        return {
            "total_documents": total_docs,
            "by_category": by_category,
            "by_lifecycle": by_lifecycle,
            "blueprint_breakdown": blueprint_breakdown,
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = ["DocumentStore"]
