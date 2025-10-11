"""
API Models
AI Atlas - Geisinger AI Product Manager Agent

Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Request Models
# ============================================================================


class SetModeRequest(BaseModel):
    """Request to set agent mode"""

    mode: Literal["ai_discovery", "risk_assessment", "poc_planning", "general"] = Field(
        ...,
        description="Operating mode for the agent",
    )


class SendMessageRequest(BaseModel):
    """Request to send a message to the agent"""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's message to the agent",
    )


class UploadDocumentRequest(BaseModel):
    """Request to upload a context document"""

    content: str = Field(
        ...,
        min_length=1,
        description="Document content",
    )
    doc_type: Literal["vendor_doc", "research", "policy", "ticket", "brief"] = Field(
        ...,
        description="Type of document being uploaded",
    )
    doc_category: Literal["input", "blueprint_knowledge"] = Field(
        default="input",
        description="Document category: 'input' for temporary task documents, 'blueprint_knowledge' for persistent strategic documents",
    )
    blueprint_subtype: Optional[Literal["policy", "guideline", "procedure", "reference", "example"]] = Field(
        default=None,
        description="For blueprint_knowledge documents: specific subtype classification",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the document",
    )


# ============================================================================
# Response Models
# ============================================================================


class AgentStatusResponse(BaseModel):
    """Agent's current status"""

    mode: Optional[str] = Field(
        None,
        description="Current operating mode",
    )
    conversation_turns: int = Field(
        ...,
        description="Number of conversation turns",
    )
    documents_count: int = Field(
        ...,
        description="Number of uploaded documents",
    )
    ready: bool = Field(
        ...,
        description="Whether agent is ready to process messages",
    )


class ConversationTurn(BaseModel):
    """Single turn in conversation"""

    role: Literal["user", "assistant"] = Field(
        ...,
        description="Who said this",
    )
    content: str = Field(
        ...,
        description="Message content",
    )
    timestamp: datetime = Field(
        ...,
        description="When this turn occurred",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional turn metadata",
    )


class ConversationHistoryResponse(BaseModel):
    """Conversation history"""

    turns: List[ConversationTurn] = Field(
        ...,
        description="List of conversation turns",
    )
    mode: Optional[str] = Field(
        None,
        description="Current mode",
    )


class DocumentInfo(BaseModel):
    """Information about an uploaded document"""

    doc_id: int = Field(
        ...,
        description="Document ID (index in list)",
    )
    doc_type: str = Field(
        ...,
        description="Type of document",
    )
    doc_category: str = Field(
        default="input",
        description="Document category: 'input' or 'blueprint_knowledge'",
    )
    blueprint_subtype: Optional[str] = Field(
        default=None,
        description="Blueprint subtype if doc_category is 'blueprint_knowledge'",
    )
    lifecycle: str = Field(
        default="temporary",
        description="Document lifecycle: 'temporary' or 'persistent'",
    )
    added_at: datetime = Field(
        ...,
        description="When document was added",
    )
    content_length: int = Field(
        ...,
        description="Length of document content",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata",
    )


class DocumentListResponse(BaseModel):
    """List of uploaded documents"""

    documents: List[DocumentInfo] = Field(
        ...,
        description="List of documents",
    )
    total_count: int = Field(
        ...,
        description="Total number of documents",
    )


class UploadDocumentResponse(BaseModel):
    """Response after uploading a document"""

    doc_id: int = Field(
        ...,
        description="ID of uploaded document",
    )
    message: str = Field(
        ...,
        description="Success message",
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: Literal["healthy", "unhealthy"] = Field(
        ...,
        description="Health status",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Health check timestamp",
    )
    version: str = Field(
        default="1.0.0",
        description="Backend version",
    )


class ErrorResponse(BaseModel):
    """Error response"""

    error: str = Field(
        ...,
        description="Error type",
    )
    message: str = Field(
        ...,
        description="Error message",
    )
    detail: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details",
    )


# ============================================================================
# Server-Sent Events Models
# ============================================================================


class ThinkingEventData(BaseModel):
    """Data for a 'thinking' event (agent reasoning step)"""

    step: Literal["gather", "plan", "execute", "verify"] = Field(
        ...,
        description="Agent loop step",
    )
    iteration: int = Field(
        ...,
        description="Current iteration number",
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for this step",
    )
    reasoning: Optional[str] = Field(
        None,
        description="Summary reasoning for this step (for card display)",
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Full trace details (for expandable section)",
    )


class IterationEventData(BaseModel):
    """Data for an 'iteration' event (iteration progress)"""

    iteration: int = Field(
        ...,
        description="Iteration number",
    )
    total_iterations: int = Field(
        ...,
        description="Maximum iterations allowed",
    )
    status: str = Field(
        ...,
        description="Iteration status",
    )


class ResponseEventData(BaseModel):
    """Data for a 'response' event (agent's final response)"""

    content: str = Field(
        ...,
        description="Response text from agent",
    )


class CompleteEventData(BaseModel):
    """Data for a 'complete' event (task completion)"""

    status: Literal["SUCCESS", "FAILED", "ESCALATED", "MAX_ITERATIONS"] = Field(
        ...,
        description="Final task status",
    )
    requires_approval: bool = Field(
        default=False,
        description="Whether this result requires human approval",
    )
    hitl_tier: Optional[str] = Field(
        None,
        description="HITL tier if approval required",
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Final confidence score",
    )


class ErrorEventData(BaseModel):
    """Data for an 'error' event"""

    error: str = Field(
        ...,
        description="Error type",
    )
    message: str = Field(
        ...,
        description="Error message",
    )


class StreamEvent(BaseModel):
    """
    Server-Sent Event for streaming agent responses

    This model supports streaming thinking indicators that can be
    expanded by the user to see full reasoning details.
    """

    event: Literal["thinking", "iteration", "response", "complete", "error"] = Field(
        ...,
        description="Event type",
    )
    data: (
        ThinkingEventData
        | IterationEventData
        | ResponseEventData
        | CompleteEventData
        | ErrorEventData
    ) = Field(
        ...,
        description="Event data (type depends on event)",
    )

    def to_sse_format(self) -> str:
        """
        Convert to SSE format

        Returns:
            SSE-formatted string (event: ...\ndata: ...\n\n)
        """
        return f"event: {self.event}\ndata: {self.data.model_dump_json()}\n\n"


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Request models
    "SetModeRequest",
    "SendMessageRequest",
    "UploadDocumentRequest",
    # Response models
    "AgentStatusResponse",
    "ConversationTurn",
    "ConversationHistoryResponse",
    "DocumentInfo",
    "DocumentListResponse",
    "UploadDocumentResponse",
    "HealthResponse",
    "ErrorResponse",
    # SSE Event models
    "StreamEvent",
    "ThinkingEventData",
    "IterationEventData",
    "ResponseEventData",
    "CompleteEventData",
    "ErrorEventData",
]
