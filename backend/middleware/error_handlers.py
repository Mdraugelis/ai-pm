"""
Error Handlers
Geisinger AI Product Manager Agent - Backend API

Custom exception handlers for FastAPI.
"""

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.api.services.agent_service import ModeNotSetError, AgentExecutionError

logger = structlog.get_logger(__name__)


# ============================================================================
# Custom Exception Handlers
# ============================================================================


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors

    Args:
        request: FastAPI request
        exc: ValidationError

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        "Validation error",
        path=request.url.path,
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "detail": exc.errors(),
        },
    )


async def mode_not_set_exception_handler(
    request: Request, exc: ModeNotSetError
) -> JSONResponse:
    """
    Handle ModeNotSetError

    Args:
        request: FastAPI request
        exc: ModeNotSetError

    Returns:
        JSONResponse with error details
    """
    logger.warning(
        "Mode not set",
        path=request.url.path,
        error=str(exc),
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ModeNotSetError",
            "message": str(exc),
            "detail": {
                "hint": "Call POST /api/agent/mode to set the agent mode first",
            },
        },
    )


async def agent_execution_exception_handler(
    request: Request, exc: AgentExecutionError
) -> JSONResponse:
    """
    Handle AgentExecutionError

    Args:
        request: FastAPI request
        exc: AgentExecutionError

    Returns:
        JSONResponse with error details
    """
    logger.error(
        "Agent execution error",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "AgentExecutionError",
            "message": str(exc),
            "detail": {
                "hint": "Check agent logs for more details",
            },
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected exceptions

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse with error details
    """
    logger.error(
        "Unexpected error",
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
        },
    )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "validation_exception_handler",
    "mode_not_set_exception_handler",
    "agent_execution_exception_handler",
    "generic_exception_handler",
]
