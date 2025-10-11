"""
Backend Configuration
Geisinger AI Product Manager Agent - Backend API

Configuration for FastAPI backend server.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


class BackendConfig(BaseSettings):
    """Backend server configuration"""

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True  # Auto-reload in development
    log_level: str = "info"

    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",  # React dev server (CRA)
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Agent Configuration
    agent_config_path: str = "config/development.yaml"

    # Upload Settings
    max_document_size: int = 10_000_000  # 10MB
    allowed_file_types: List[str] = [".txt", ".pdf", ".md", ".json", ".yaml"]

    # Session Settings
    session_timeout_minutes: int = 60

    # Streaming Settings
    sse_retry_timeout_ms: int = 3000  # Client retry timeout
    sse_keepalive_interval_s: int = 15  # Send keepalive every 15s

    class Config:
        env_file = ".env"
        env_prefix = "BACKEND_"
        extra = "ignore"  # Ignore extra fields from .env


# Global configuration instance
config = BackendConfig()
