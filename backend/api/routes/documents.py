"""
Document Routes
Geisinger AI Product Manager Agent - Backend API

Routes for document upload and management.
Supports both in-session documents and persistent blueprint knowledge documents.
"""

import os
from typing import Optional

import structlog
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form

from backend.api.models import (
    UploadDocumentRequest,
    UploadDocumentResponse,
    DocumentListResponse,
)
from backend.api.services.agent_service import get_agent_service
from backend.config import config
from backend.database.document_store import DocumentStore
from backend.services.knowledge_extractor import KnowledgeExtractor
from backend.services.document_processor import DocumentProcessor

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Initialize persistent storage services
document_store = DocumentStore()
knowledge_extractor = KnowledgeExtractor(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-sonnet-4-5-20250929",
)
document_processor = DocumentProcessor()


# ============================================================================
# Document Endpoints
# ============================================================================


@router.post("/upload", response_model=UploadDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(request: UploadDocumentRequest) -> UploadDocumentResponse:
    """
    Upload context document

    Supports uploading:
    - ServiceNow tickets (doc_type="ticket")
    - Vendor documentation (doc_type="vendor_doc")
    - Research papers (doc_type="research")
    - Policy documents (doc_type="policy")
    - Intake briefs (doc_type="brief")

    Args:
        request: UploadDocumentRequest with content, doc_type, metadata

    Returns:
        UploadDocumentResponse with doc_id and success message

    Raises:
        HTTPException: If document is too large or invalid
    """
    logger.info(
        "Uploading document",
        doc_type=request.doc_type,
        content_length=len(request.content),
    )

    # Validate document size
    if len(request.content) > config.max_document_size:
        logger.error(
            "Document too large",
            size=len(request.content),
            max_size=config.max_document_size,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Document exceeds maximum size of {config.max_document_size} bytes",
        )

    # Validate content is not empty
    if not request.content.strip():
        logger.error("Empty document content")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty",
        )

    agent_service = get_agent_service()

    try:
        # Add document to agent
        doc_id = await agent_service.add_document(
            content=request.content,
            doc_type=request.doc_type,
            metadata=request.metadata,
        )

        logger.info("Document uploaded successfully", doc_id=doc_id, doc_type=request.doc_type)

        return UploadDocumentResponse(
            doc_id=doc_id,
            message=f"{request.doc_type} uploaded successfully",
        )

    except Exception as e:
        logger.error("Failed to upload document", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}",
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """
    List all uploaded documents

    Returns:
        DocumentListResponse with list of documents and total count
    """
    logger.info("Listing documents")

    agent_service = get_agent_service()

    documents = await agent_service.get_documents()

    return DocumentListResponse(
        documents=documents,
        total_count=len(documents),
    )


@router.delete("/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_document(doc_id: int) -> dict:
    """
    Delete document by ID

    Args:
        doc_id: Document ID (index in list)

    Returns:
        Success message

    Raises:
        HTTPException: If doc_id is invalid
    """
    logger.info("Deleting document", doc_id=doc_id)

    agent_service = get_agent_service()

    try:
        await agent_service.remove_document(doc_id)

        logger.info("Document deleted successfully", doc_id=doc_id)

        return {"message": f"Document {doc_id} deleted successfully"}

    except IndexError:
        logger.error("Invalid document ID", doc_id=doc_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_documents() -> dict:
    """
    Clear all documents

    Returns:
        Success message
    """
    logger.info("Clearing all documents")

    agent_service = get_agent_service()

    await agent_service.clear_documents()

    logger.info("All documents cleared")

    return {"message": "All documents cleared successfully"}


# ============================================================================
# Blueprint Knowledge Document Endpoints (Persistent Storage)
# ============================================================================


@router.post(
    "/blueprints",
    status_code=status.HTTP_201_CREATED,
)
async def upload_blueprint_document(
    file: UploadFile = File(...),
    doc_type: str = Form("policy"),
    project_id: str = Form("default"),
) -> dict:
    """
    Upload blueprint knowledge document with automatic classification

    Processes file through:
    1. DocumentProcessor - Extract text content from file
    2. KnowledgeExtractor - Classify into policy/guideline/procedure/reference/example
    3. DocumentStore - Save to persistent database

    Args:
        file: File upload (PDF, DOCX, TXT, MD, etc.)
        doc_type: Initial document type hint
        project_id: Project identifier for multi-tenancy

    Returns:
        Document info with classification results

    Raises:
        HTTPException: If file processing fails
    """
    logger.info(
        "Uploading blueprint document",
        filename=file.filename,
        content_type=file.content_type,
        doc_type=doc_type,
    )

    try:
        # Read file content
        file_bytes = await file.read()

        # Validate file size
        if len(file_bytes) > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File exceeds 100MB limit",
            )

        # Extract content using DocumentProcessor
        extraction_result = document_processor.extract_content(
            file_path=file.filename, file_bytes=file_bytes
        )

        if extraction_result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract content: {extraction_result.get('error')}",
            )

        content = extraction_result["content"]

        # Classify content using KnowledgeExtractor
        classification = await knowledge_extractor.classify_blueprint(
            content=content, filename=file.filename
        )

        # Save to persistent storage
        doc_id = document_store.create_document(
            content=content,
            doc_type=doc_type,
            doc_category="blueprint_knowledge",
            blueprint_subtype=classification["blueprint_subtype"],
            lifecycle="persistent",
            project_id=project_id,
            metadata={
                "filename": file.filename,
                "file_extension": extraction_result["metadata"]["file_extension"],
                "mime_type": extraction_result["mime_type"],
                "classification_confidence": classification["confidence"],
                "classification_reasoning": classification["reasoning"],
                "key_concepts": classification.get("key_concepts", []),
                "summary": classification.get("summary", ""),
            },
        )

        # Update classification status
        document_store.update_document(
            doc_id=doc_id,
            updates={
                "is_classified": True,
                "classification_confidence": classification["confidence"],
            },
        )

        logger.info(
            "Blueprint document uploaded successfully",
            doc_id=doc_id,
            blueprint_subtype=classification["blueprint_subtype"],
            confidence=classification["confidence"],
        )

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "blueprint_subtype": classification["blueprint_subtype"],
            "confidence": classification["confidence"],
            "summary": classification.get("summary", ""),
            "key_concepts": classification.get("key_concepts", []),
            "reasoning": classification["reasoning"],
            "content_length": len(content),
            "message": f"Blueprint document classified as '{classification['blueprint_subtype']}' and saved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to upload blueprint document",
            filename=file.filename,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process blueprint document: {str(e)}",
        )


@router.get("/blueprints")
async def list_blueprint_documents(
    blueprint_subtype: Optional[str] = None,
    project_id: str = "default",
    limit: int = 100,
) -> dict:
    """
    List all blueprint knowledge documents

    Args:
        blueprint_subtype: Filter by subtype (policy, guideline, procedure, reference, example)
        project_id: Project identifier
        limit: Maximum number of results

    Returns:
        List of blueprint documents with metadata
    """
    logger.info(
        "Listing blueprint documents",
        blueprint_subtype=blueprint_subtype,
        project_id=project_id,
    )

    documents = document_store.get_blueprints(
        blueprint_subtype=blueprint_subtype,
        project_id=project_id,
    )

    # Limit results
    documents = documents[:limit]

    return {
        "blueprints": documents,
        "total_count": len(documents),
        "filtered_by": {
            "blueprint_subtype": blueprint_subtype,
            "project_id": project_id,
        },
    }


@router.get("/blueprints/{doc_id}")
async def get_blueprint_document(doc_id: str) -> dict:
    """
    Get specific blueprint document by ID

    Args:
        doc_id: Document UUID

    Returns:
        Full document with content and metadata

    Raises:
        HTTPException: If document not found
    """
    logger.info("Getting blueprint document", doc_id=doc_id)

    document = document_store.get_document(doc_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint document {doc_id} not found",
        )

    # Log access
    document_store.log_access(
        doc_id=doc_id,
        access_type="read",
        agent_mode="manual_retrieval",
    )

    return document


@router.delete("/blueprints/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_blueprint_document(doc_id: str) -> dict:
    """
    Delete blueprint document by ID

    Args:
        doc_id: Document UUID

    Returns:
        Success message

    Raises:
        HTTPException: If document not found
    """
    logger.info("Deleting blueprint document", doc_id=doc_id)

    deleted = document_store.delete_document(doc_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint document {doc_id} not found",
        )

    return {"message": f"Blueprint document {doc_id} deleted successfully"}


@router.get("/blueprints/stats/summary")
async def get_blueprint_stats(project_id: str = "default") -> dict:
    """
    Get blueprint storage statistics

    Args:
        project_id: Project identifier

    Returns:
        Statistics about blueprint documents
    """
    logger.info("Getting blueprint statistics", project_id=project_id)

    stats = document_store.get_stats(project_id=project_id)

    return {
        "project_id": project_id,
        "statistics": stats,
    }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = ["router"]
