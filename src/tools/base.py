"""
Tool Framework Base Classes
Geisinger AI Product Manager Agent

This module defines the base classes and interfaces for the Tool Framework (Layer 3).
All tools must inherit from the Tool base class and implement the required methods.

Following Geisinger Agentic Architecture v1.0
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Enums and Constants
# ============================================================================


class ToolStatus(str, Enum):
    """Status of tool execution"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    TIMEOUT = "TIMEOUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_INPUT = "INVALID_INPUT"


class RiskTier(str, Enum):
    """Risk tier classification for tools"""

    TIER_1 = "TIER_1"  # Auto-approve (low risk)
    TIER_2 = "TIER_2"  # Passive review
    TIER_3 = "TIER_3"  # Active approval
    TIER_4 = "TIER_4"  # Critical decision


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ToolResult:
    """
    Result of tool execution

    Attributes:
        status: Execution status (SUCCESS, FAILED, etc.)
        data: Output data from the tool
        tool_id: Unique identifier of the tool
        error: Error message if status is FAILED
        citations: Data sources used (for explainability)
        execution_time_ms: Time taken to execute in milliseconds
        verification_checks: List of verification checks performed
        metadata: Additional metadata about execution
    """

    status: ToolStatus
    tool_id: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    citations: List[str] = field(default_factory=list)
    execution_time_ms: Optional[float] = None
    verification_checks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """Check if execution was successful"""
        return self.status == ToolStatus.SUCCESS

    def is_failed(self) -> bool:
        """Check if execution failed"""
        return self.status in [
            ToolStatus.FAILED,
            ToolStatus.TIMEOUT,
            ToolStatus.UNAUTHORIZED,
            ToolStatus.INVALID_INPUT,
        ]


@dataclass
class ExecutionContext:
    """
    Context for tool execution

    Provides tools with access to:
    - Current session information
    - User/requestor information
    - Initiative/task context
    - Memory and state
    - Blueprints and policies

    Attributes:
        session_id: Current agent session ID
        initiative_id: Initiative being worked on
        user_id: User who initiated the request
        task_description: Description of current task
        iteration: Current iteration in agent loop
        memory: Access to working memory
        blueprints: Policy blueprints
        allowed_risk_tier: Maximum risk tier allowed
        timeout_seconds: Maximum execution time
        metadata: Additional context information
    """

    session_id: str
    initiative_id: Optional[str] = None
    user_id: Optional[str] = None
    task_description: Optional[str] = None
    iteration: int = 0
    memory: Optional[Any] = None  # WorkingMemory reference
    blueprints: Optional[Dict[str, Any]] = None
    allowed_risk_tier: RiskTier = RiskTier.TIER_3
    timeout_seconds: int = 30
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSpecification:
    """
    Specification for tool registration

    Defines tool capabilities, requirements, and constraints
    for the Tool Registry.

    Attributes:
        id: Unique tool identifier (e.g., "azure_devops_client")
        name: Human-readable name
        version: Tool version (semver)
        description: Detailed description of tool capabilities
        capabilities: List of capabilities (e.g., ["query_work_items", "update_status"])
        parameter_schema: JSON schema for input parameters
        output_schema: JSON schema for output data
        risk_tier: Risk classification for HITL governance
        requires_consent: Whether user consent is needed
        timeout_seconds: Default timeout for execution
        cacheable: Whether results can be cached
        cache_ttl_seconds: Cache time-to-live if cacheable
        examples: Usage examples
        dependencies: External dependencies required
    """

    id: str
    name: str
    version: str
    description: str
    capabilities: List[str]
    parameter_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    risk_tier: RiskTier = RiskTier.TIER_2
    requires_consent: bool = False
    timeout_seconds: int = 30
    cacheable: bool = False
    cache_ttl_seconds: Optional[int] = None
    examples: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class VerificationCheck:
    """
    Result of a single verification check

    Used in self-verification of tool outputs

    Attributes:
        check_name: Name of the check (e.g., "schema_validation")
        passed: Whether the check passed
        message: Description of check result
        details: Additional details about the check
    """

    check_name: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# Base Tool Class
# ============================================================================


class Tool(ABC):
    """
    Abstract base class for all tools

    All tools in the system must inherit from this class and implement:
    - execute(): Perform the tool's action
    - verify_result(): Self-verify the tool's output

    Tools should also define:
    - tool_id: Unique identifier
    - name: Human-readable name
    - description: What the tool does
    - parameters_schema: Expected input parameters
    - version: Tool version

    Example:
        >>> class MyTool(Tool):
        ...     def __init__(self):
        ...         self.tool_id = "my_tool"
        ...         self.name = "My Tool"
        ...         self.description = "Does something useful"
        ...         self.parameters_schema = {"param": {"type": "string"}}
        ...         self.version = "1.0.0"
        ...
        ...     async def execute(self, parameters, context):
        ...         # Implementation
        ...         return ToolResult(...)
        ...
        ...     def verify_result(self, result):
        ...         # Self-check
        ...         return True
    """

    def __init__(self):
        """Initialize tool with required attributes"""
        self.tool_id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.parameters_schema: Dict[str, Any] = {}
        self.version: str = "1.0.0"
        self.risk_tier: RiskTier = RiskTier.TIER_2
        self.logger = structlog.get_logger(__name__).bind(tool_id=self.tool_id)

    @abstractmethod
    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ToolResult:
        """
        Execute the tool's action

        This is the main method that performs the tool's function.

        Args:
            parameters: Input parameters (validated against parameters_schema)
            context: Execution context with session info, memory, etc.

        Returns:
            ToolResult with status, data, citations, etc.

        Raises:
            ValueError: If parameters are invalid
            TimeoutError: If execution exceeds timeout
            Exception: For other execution errors
        """
        pass

    @abstractmethod
    def verify_result(self, result: ToolResult) -> bool:
        """
        Self-verify tool execution result

        Performs basic sanity checks on the tool's output.
        This is part of the self-verification pattern.

        Args:
            result: The ToolResult to verify

        Returns:
            True if result passes verification, False otherwise

        Example checks:
            - Required fields are present
            - Data types are correct
            - Values are within expected ranges
            - No obvious errors or inconsistencies
        """
        pass

    def _validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate input parameters against schema

        Args:
            parameters: Input parameters to validate

        Raises:
            ValueError: If parameters don't match schema
        """
        # Basic validation - check required fields
        required_fields = [
            field
            for field, spec in self.parameters_schema.items()
            if spec.get("required", False)
        ]

        missing = [field for field in required_fields if field not in parameters]

        if missing:
            raise ValueError(f"Missing required parameters: {missing}")

        self.logger.debug(
            "Parameters validated", parameters=parameters, schema=self.parameters_schema
        )

    def get_specification(self) -> ToolSpecification:
        """
        Get tool specification for registration

        Returns:
            ToolSpecification with tool metadata
        """
        return ToolSpecification(
            id=self.tool_id,
            name=self.name,
            version=self.version,
            description=self.description,
            capabilities=[self.tool_id],  # Override in subclass if multiple capabilities
            parameter_schema=self.parameters_schema,
            output_schema={},  # Override in subclass
            risk_tier=self.risk_tier,
        )


# ============================================================================
# Exceptions
# ============================================================================


class ToolError(Exception):
    """Base exception for tool-related errors"""

    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails"""

    pass


class ToolValidationError(ToolError):
    """Raised when tool input validation fails"""

    pass


class ToolTimeoutError(ToolError):
    """Raised when tool execution exceeds timeout"""

    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool cannot be found"""

    pass


class ToolRegistryError(ToolError):
    """Raised for tool registry related errors"""

    pass


# ============================================================================
# Helper Functions
# ============================================================================


async def execute_with_timeout(
    coro: Any, timeout_seconds: int, tool_id: str
) -> ToolResult:
    """
    Execute a coroutine with timeout

    Args:
        coro: Coroutine to execute
        timeout_seconds: Maximum execution time
        tool_id: Tool identifier for error reporting

    Returns:
        ToolResult from the coroutine

    Raises:
        ToolTimeoutError: If execution exceeds timeout
    """
    try:
        result = await asyncio.wait_for(coro, timeout=timeout_seconds)
        return result
    except asyncio.TimeoutError:
        error_msg = f"Tool execution exceeded timeout of {timeout_seconds}s"
        logger.error("Tool timeout", tool_id=tool_id, timeout=timeout_seconds)
        raise ToolTimeoutError(error_msg)


def create_error_result(
    tool_id: str, error: Union[str, Exception], status: ToolStatus = ToolStatus.FAILED
) -> ToolResult:
    """
    Create an error ToolResult

    Args:
        tool_id: Tool identifier
        error: Error message or exception
        status: Error status type

    Returns:
        ToolResult with error information
    """
    error_message = str(error) if isinstance(error, Exception) else error

    return ToolResult(
        status=status, tool_id=tool_id, error=error_message, data=None, citations=[]
    )


# ============================================================================
# Module Metadata
# ============================================================================

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
