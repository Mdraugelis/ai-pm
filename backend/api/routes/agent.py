"""
Agent Routes
Geisinger AI Product Manager Agent - Backend API

Routes for agent interaction with SSE streaming support.
"""

from typing import AsyncIterator

import structlog
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from backend.api.models import (
    SetModeRequest,
    SendMessageRequest,
    AgentStatusResponse,
    ConversationHistoryResponse,
    StreamEvent,
)
from backend.api.services.agent_service import (
    get_agent_service,
    ModeNotSetError,
    AgentExecutionError,
)

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/agent", tags=["agent"])


# ============================================================================
# SSE Stream Generator
# ============================================================================


async def event_stream_generator(message: str) -> AsyncIterator[str]:
    """
    Generate SSE event stream for agent message processing

    Args:
        message: User's message

    Yields:
        SSE-formatted strings (event: ...\ndata: ...\n\n)
    """
    agent_service = get_agent_service()

    try:
        # Stream events from agent service
        async for event in agent_service.process_message_stream(message):
            # Convert StreamEvent to SSE format
            yield event.to_sse_format()

    except ModeNotSetError as e:
        # Mode not set error
        error_event = StreamEvent(
            event="error",
            data={
                "error": "ModeNotSetError",
                "message": str(e),
            },
        )
        yield error_event.to_sse_format()

    except AgentExecutionError as e:
        # Agent execution error
        error_event = StreamEvent(
            event="error",
            data={
                "error": "AgentExecutionError",
                "message": str(e),
            },
        )
        yield error_event.to_sse_format()

    except Exception as e:
        # Unexpected error
        logger.error("Unexpected error in event stream", error=str(e), exc_info=True)
        error_event = StreamEvent(
            event="error",
            data={
                "error": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
            },
        )
        yield error_event.to_sse_format()


# ============================================================================
# Agent Endpoints
# ============================================================================


@router.post("/mode", status_code=status.HTTP_200_OK)
async def set_mode(request: SetModeRequest) -> dict:
    """
    Set agent's operating mode

    Sets the mode and loads appropriate blueprints.

    Args:
        request: SetModeRequest with mode

    Returns:
        Success message

    Raises:
        HTTPException: If mode is invalid
    """
    logger.info("Setting agent mode", mode=request.mode)

    agent_service = get_agent_service()

    try:
        await agent_service.set_mode(request.mode)

        return {
            "message": f"Mode set to {request.mode}",
            "mode": request.mode,
        }

    except ValueError as e:
        logger.error("Invalid mode", mode=request.mode, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mode: {str(e)}",
        )


@router.post("/message/stream")
async def send_message_stream(request: SendMessageRequest) -> StreamingResponse:
    """
    Send message to agent with SSE streaming (POST method)

    Returns a stream of events showing:
    - Thinking indicators (gather, plan, execute, verify steps)
    - Iteration progress
    - Final response
    - Completion status

    The UI can display thinking indicators and allow users to expand
    reasoning details.

    Args:
        request: SendMessageRequest with message

    Returns:
        StreamingResponse with SSE events

    Example SSE stream:
        event: thinking
        data: {"step": "gather", "iteration": 0, ...}

        event: thinking
        data: {"step": "plan", "iteration": 0, "confidence": 0.85, ...}

        event: response
        data: {"content": "I've analyzed your request..."}

        event: complete
        data: {"status": "SUCCESS", "requires_approval": false}
    """
    logger.info("Processing message stream", message_length=len(request.message))

    return StreamingResponse(
        event_stream_generator(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/message/stream")
async def send_message_stream_get(message: str) -> StreamingResponse:
    """
    Send message to agent with SSE streaming (GET method for EventSource)

    This endpoint supports browser EventSource API which only does GET requests.

    Args:
        message: User's message (query parameter)

    Returns:
        StreamingResponse with SSE events
    """
    logger.info("Processing message stream (GET)", message_length=len(message))

    return StreamingResponse(
        event_stream_generator(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/conversation", response_model=ConversationHistoryResponse)
async def get_conversation() -> ConversationHistoryResponse:
    """
    Get conversation history

    Returns:
        ConversationHistoryResponse with turns and mode
    """
    logger.info("Getting conversation history")

    agent_service = get_agent_service()

    turns = await agent_service.get_conversation_history()
    status_info = agent_service.get_status()

    return ConversationHistoryResponse(
        turns=turns,
        mode=status_info["mode"],
    )


@router.delete("/conversation", status_code=status.HTTP_200_OK)
async def clear_conversation() -> dict:
    """
    Clear conversation history

    Returns:
        Success message
    """
    logger.info("Clearing conversation")

    agent_service = get_agent_service()

    await agent_service.clear_conversation()

    return {"message": "Conversation cleared successfully"}


@router.get("/status", response_model=AgentStatusResponse)
async def get_status() -> AgentStatusResponse:
    """
    Get agent's current status

    Returns:
        AgentStatusResponse with mode, conversation count, etc.
    """
    logger.info("Getting agent status")

    agent_service = get_agent_service()

    status_info = agent_service.get_status()

    return AgentStatusResponse(
        mode=status_info["mode"],
        conversation_turns=status_info["conversation_turns"],
        documents_count=status_info["documents_count"],
        ready=status_info["ready"],
    )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = ["router"]
