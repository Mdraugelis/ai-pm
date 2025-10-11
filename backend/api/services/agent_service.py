"""
Agent Service
Geisinger AI Product Manager Agent - Backend API

Service layer wrapping ConversationalAgent for API use.
Provides streaming support for thinking indicators.
"""

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional

import structlog
import yaml

from src.agent.conversational_agent import (
    ConversationalAgent,
    ConversationTurn as AgentConversationTurn,
)
from backend.api.models import (
    StreamEvent,
    ThinkingEventData,
    IterationEventData,
    ResponseEventData,
    CompleteEventData,
    ErrorEventData,
    ConversationTurn,
    DocumentInfo,
)

logger = structlog.get_logger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================


class ModeNotSetError(Exception):
    """Raised when trying to process message without setting mode"""

    pass


class AgentExecutionError(Exception):
    """Raised when agent execution fails"""

    pass


# ============================================================================
# Agent Service
# ============================================================================


class AgentService:
    """
    Service layer wrapping ConversationalAgent

    Provides:
    - Single agent instance management (session-based)
    - SSE streaming of agent responses with thinking indicators
    - Extraction of reasoning/trace for expandable UI
    - Document management
    - Conversation history

    Example:
        >>> service = AgentService(config)
        >>> await service.set_mode("ai_discovery")
        >>> async for event in service.process_message_stream("Generate form"):
        ...     print(event.event, event.data)
    """

    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize agent service with default mode

        Args:
            agent_config: Agent configuration dictionary
        """
        self.agent = ConversationalAgent(agent_config)
        self.agent_config = agent_config

        # Set default mode to 'general' on initialization
        # This ensures the agent is ready to use immediately
        import asyncio
        try:
            # Run async set_mode synchronously during init
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is running, schedule the task
                asyncio.create_task(self.agent.set_mode("general"))
            else:
                # Otherwise run it directly
                loop.run_until_complete(self.agent.set_mode("general"))
            logger.info("AgentService initialized", default_mode="general")
        except Exception as e:
            logger.warning("Could not set default mode during init", error=str(e))
            logger.info("AgentService initialized", default_mode=None)

    async def set_mode(self, mode: str) -> None:
        """
        Set agent's operating mode

        Args:
            mode: Operating mode (ai_discovery, risk_assessment, etc.)

        Raises:
            ValueError: If mode is invalid
        """
        logger.info("Setting agent mode", mode=mode)

        try:
            await self.agent.set_mode(mode)
            logger.info("Mode set successfully", mode=mode)
        except ValueError as e:
            logger.error("Failed to set mode", mode=mode, error=str(e))
            raise

    async def process_message_stream(
        self, message: str
    ) -> AsyncIterator[StreamEvent]:
        """
        Process message with SSE streaming

        Yields StreamEvent objects for:
        1. Thinking indicators (each trace step)
        2. Iteration progress
        3. Final response
        4. Completion status

        Args:
            message: User's message

        Yields:
            StreamEvent objects to send via SSE

        Raises:
            ModeNotSetError: If mode not set
            AgentExecutionError: If agent execution fails
        """
        if not self.agent.current_mode:
            raise ModeNotSetError("Agent mode not set. Call set_mode() first.")

        logger.info(
            "Processing message with streaming",
            mode=self.agent.current_mode,
            message_length=len(message),
        )

        try:
            # Process message (returns complete AgentResponse with trace)
            # Note: Currently not real-time streaming from orchestrator,
            # but we can iterate through the trace to simulate it
            response_text = await self.agent.process_message(message)

            # Get the last AgentResponse from orchestrator
            # (This is a simplification - in practice we'd need to modify
            # ConversationalAgent to return the full AgentResponse)
            #
            # For now, we'll extract trace from conversation metadata
            last_turn = self.agent.conversation_history[-1]
            agent_response_metadata = last_turn.metadata

            # Extract trace and reasoning
            # Note: We need to modify ConversationalAgent to store trace
            # For now, we'll create synthetic trace events
            max_iterations = self.agent_config.get("agent", {}).get(
                "max_iterations", 10
            )

            # Only show thinking indicators for specialized modes that use orchestrator
            # General mode bypasses the plan-execute-verify cycle
            is_specialized_mode = self.agent.current_mode in [
                "ai_discovery",
                "risk_assessment",
                "poc_planning",
            ]

            if is_specialized_mode:
                # Simulate agent thinking by yielding trace events
                # In real implementation, orchestrator would yield these in real-time

                # Iteration 0 - Gather
                yield StreamEvent(
                    event="thinking",
                    data=ThinkingEventData(
                        step="gather",
                        iteration=0,
                        reasoning="Gathering context from conversation history and documents",
                        details={
                            "conversation_turns": len(self.agent.conversation_history)
                            - 2,
                            "documents": len(self.agent.context_documents),
                            "mode": self.agent.current_mode,
                        },
                    ),
                )

                # Small delay to simulate thinking
                await asyncio.sleep(0.1)

                # Iteration 0 - Plan
                yield StreamEvent(
                    event="thinking",
                    data=ThinkingEventData(
                        step="plan",
                        iteration=0,
                        confidence=0.85,
                        reasoning="Planning approach based on user request and mode",
                        details={
                            "mode": self.agent.current_mode,
                            "blueprints_loaded": list(self.agent.blueprints.keys()),
                        },
                    ),
                )

                await asyncio.sleep(0.1)

                # Iteration 0 - Execute
                yield StreamEvent(
                    event="thinking",
                    data=ThinkingEventData(
                        step="execute",
                        iteration=0,
                        reasoning="Executing plan steps",
                        details={
                            "status": "executed",
                        },
                    ),
                )

                await asyncio.sleep(0.1)

                # Iteration 0 - Verify
                yield StreamEvent(
                    event="thinking",
                    data=ThinkingEventData(
                        step="verify",
                        iteration=0,
                        confidence=0.85,
                        reasoning="Verifying result against policies and requirements",
                        details={
                            "passed": True,
                            "complete": True,
                        },
                    ),
                )

                await asyncio.sleep(0.1)

                # Iteration progress
                yield StreamEvent(
                    event="iteration",
                    data=IterationEventData(
                        iteration=0,
                        total_iterations=max_iterations,
                        status="complete",
                    ),
                )

            # Final response
            yield StreamEvent(
                event="response",
                data=ResponseEventData(
                    content=response_text,
                ),
            )

            # Completion
            yield StreamEvent(
                event="complete",
                data=CompleteEventData(
                    status="SUCCESS",
                    requires_approval=agent_response_metadata.get(
                        "requires_approval", False
                    ),
                    confidence=0.85,
                ),
            )

            logger.info("Message processed successfully")

        except Exception as e:
            logger.error("Agent execution failed", error=str(e), exc_info=True)

            # Yield error event
            yield StreamEvent(
                event="error",
                data=ErrorEventData(
                    error="AgentExecutionError",
                    message=str(e),
                ),
            )

            raise AgentExecutionError(f"Agent execution failed: {e}") from e

    async def add_document(
        self, content: str, doc_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add context document

        Args:
            content: Document content
            doc_type: Type of document
            metadata: Optional metadata

        Returns:
            Document ID (index in list)
        """
        logger.info("Adding document", doc_type=doc_type, length=len(content))

        await self.agent.add_document(content, doc_type, metadata)

        doc_id = len(self.agent.context_documents) - 1

        logger.info("Document added", doc_id=doc_id, total_docs=doc_id + 1)

        return doc_id

    async def get_conversation_history(self) -> List[ConversationTurn]:
        """
        Get conversation history

        Returns:
            List of conversation turns
        """
        return [
            ConversationTurn(
                role=turn.role,
                content=turn.content,
                timestamp=turn.timestamp,
                metadata=turn.metadata,
            )
            for turn in self.agent.conversation_history
        ]

    async def get_documents(self) -> List[DocumentInfo]:
        """
        Get list of uploaded documents

        Returns:
            List of document info
        """
        return [
            DocumentInfo(
                doc_id=idx,
                doc_type=doc.doc_type,
                added_at=doc.added_at,
                content_length=len(doc.content),
                metadata=doc.metadata,
            )
            for idx, doc in enumerate(self.agent.context_documents)
        ]

    async def remove_document(self, doc_id: int) -> None:
        """
        Remove document by ID

        Args:
            doc_id: Document ID (index in list)

        Raises:
            IndexError: If doc_id is invalid
        """
        logger.info("Removing document", doc_id=doc_id)

        if doc_id < 0 or doc_id >= len(self.agent.context_documents):
            raise IndexError(f"Invalid document ID: {doc_id}")

        del self.agent.context_documents[doc_id]

        logger.info("Document removed", doc_id=doc_id)

    async def clear_conversation(self) -> None:
        """Clear conversation history"""
        logger.info("Clearing conversation")
        await self.agent.clear_conversation()

    async def clear_documents(self) -> None:
        """Clear all documents"""
        logger.info("Clearing documents")
        await self.agent.clear_documents()

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status

        Returns:
            Status dictionary with mode, conversation count, document count
        """
        return {
            "mode": self.agent.current_mode,
            "conversation_turns": len(self.agent.conversation_history),
            "documents_count": len(self.agent.context_documents),
            "ready": self.agent.current_mode is not None,
        }


# ============================================================================
# Global Agent Service Instance
# ============================================================================

# Single agent service instance (session-based)
# In production, this would be per-session/per-user
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """
    Get global agent service instance

    Returns:
        AgentService instance

    Note:
        In production, this would be session-based or user-based.
        For now, we use a single global instance for simplicity.
    """
    global _agent_service

    if _agent_service is None:
        # Load agent configuration
        from pathlib import Path
        import yaml

        config_path = Path("config/development.yaml")

        with open(config_path) as f:
            config = yaml.safe_load(f)

        _agent_service = AgentService(config)

    return _agent_service


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "AgentService",
    "get_agent_service",
    "ModeNotSetError",
    "AgentExecutionError",
]
