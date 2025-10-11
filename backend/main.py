"""
FastAPI Backend Main Application
Geisinger AI Product Manager Agent - Backend API

Main FastAPI application with CORS and error handling.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# ============================================================================
# Environment Variable Loading - MUST BE FIRST
# ============================================================================

# Try to find .env file (searches upward from current directory)
env_file = find_dotenv()

if env_file:
    print(f"[ENV] Found .env file at: {env_file}")
    load_result = load_dotenv(dotenv_path=env_file, verbose=True, override=True)
    print(f"[ENV] Load result: {load_result}")
else:
    # Fallback: explicit path relative to this file
    env_path = Path(__file__).parent.parent / ".env"
    print(f"[ENV] Using explicit path: {env_path}")
    if env_path.exists():
        print(f"[ENV] File exists: {env_path}")
        load_result = load_dotenv(dotenv_path=env_path, verbose=True, override=True)
        print(f"[ENV] Load result: {load_result}")
    else:
        print(f"[ENV] ERROR: .env file not found at {env_path}")

# CRITICAL: Validate ANTHROPIC_API_KEY is present
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"[ENV] ANTHROPIC_API_KEY present: {bool(api_key)}")
print(f"[ENV] ANTHROPIC_API_KEY length: {len(api_key) if api_key else 0}")

if not api_key:
    print("\n" + "="*80)
    print("FATAL ERROR: ANTHROPIC_API_KEY environment variable not set!")
    print("="*80)
    print("\nPlease ensure your .env file contains:")
    print("  ANTHROPIC_API_KEY=your_key_here")
    print("\nCurrent working directory:", os.getcwd())
    print("Env file path:", env_file or env_path)
    print("="*80 + "\n")
    sys.exit(1)

# IMPORTANT: Explicitly set in os.environ to ensure it's inherited by worker processes
# This is critical for uvicorn reload mode where workers are spawned as subprocesses
os.environ["ANTHROPIC_API_KEY"] = api_key

print(f"[ENV] ✓ Environment configuration loaded successfully\n")

# ============================================================================
# Import Application Dependencies
# ============================================================================

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from backend.config import config
from backend.api.routes import api_router
from backend.middleware.error_handlers import (
    validation_exception_handler,
    mode_not_set_exception_handler,
    agent_execution_exception_handler,
    generic_exception_handler,
)
from backend.api.services.agent_service import (
    ModeNotSetError,
    AgentExecutionError,
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger(__name__)

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="AI Atlas API",
    description="Geisinger's conversational AI Product Manager with SSE streaming - Navigate AI initiatives with intelligent assistance",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
    expose_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================

app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(ModeNotSetError, mode_not_set_exception_handler)
app.add_exception_handler(AgentExecutionError, agent_execution_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ============================================================================
# Include Routers
# ============================================================================

app.include_router(api_router)

# ============================================================================
# Startup/Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    # Double-check API key is still present at runtime
    api_key_check = os.getenv("ANTHROPIC_API_KEY")
    if not api_key_check:
        logger.error("CRITICAL: ANTHROPIC_API_KEY not found at startup!")
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set at startup")

    logger.info(
        "Starting AI Atlas Backend",
        host=config.host,
        port=config.port,
        cors_origins=config.cors_origins,
        api_key_configured=True,
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down AI Atlas Backend")


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/")
async def root():
    """
    Root endpoint with API information

    Returns:
        API info and links
    """
    return {
        "name": "AI Atlas",
        "tagline": "Navigate AI initiatives with intelligent assistance",
        "version": "1.0.0",
        "description": "Geisinger's conversational AI Product Manager with SSE streaming",
        "docs": "/api/docs",
        "health": "/api/health",
        "endpoints": {
            "agent": "/api/agent",
            "documents": "/api/documents",
        },
    }


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level,
    )
