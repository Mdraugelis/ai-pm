"""
API Routes
Geisinger AI Product Manager Agent - Backend API

Aggregates all route modules.
"""

from fastapi import APIRouter

from backend.api.routes import agent, documents, health

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(agent.router)
api_router.include_router(documents.router)
api_router.include_router(health.router)

__all__ = ["api_router"]
