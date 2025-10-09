"""
Tool Framework
Geisinger AI Product Manager Agent - Layer 3

This package contains the Tool Framework for the agent, including:
- Base tool classes and interfaces
- Tool registry for discovery and management
- Concrete tool implementations (ServiceNow, Azure DevOps, etc.)

All tools must inherit from the Tool base class.
"""

from src.tools.base import (
    ExecutionContext,
    RiskTier,
    Tool,
    ToolError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolRegistryError,
    ToolResult,
    ToolSpecification,
    ToolStatus,
    ToolTimeoutError,
    ToolValidationError,
    VerificationCheck,
    create_error_result,
    execute_with_timeout,
)

__all__ = [
    # Base classes
    "Tool",
    # Data classes
    "ToolResult",
    "ExecutionContext",
    "ToolSpecification",
    "VerificationCheck",
    # Enums
    "ToolStatus",
    "RiskTier",
    # Exceptions
    "ToolError",
    "ToolExecutionError",
    "ToolValidationError",
    "ToolTimeoutError",
    "ToolNotFoundError",
    "ToolRegistryError",
    # Helpers
    "execute_with_timeout",
    "create_error_result",
]

__version__ = "0.1.0"
