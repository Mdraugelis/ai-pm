"""
Health Routes
Geisinger AI Product Manager Agent - Backend API

Health check endpoint.
"""

from datetime import datetime

from fastapi import APIRouter

from backend.api.models import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint

    Returns:
        HealthResponse with status, timestamp, and version
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
    )


__all__ = ["router"]
