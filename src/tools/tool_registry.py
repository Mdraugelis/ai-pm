"""
Tool Registry
Geisinger AI Product Manager Agent - Layer 3

Central registry for all tools in the system.
Provides tool discovery, retrieval, and management capabilities.

Usage:
    registry = ToolRegistry()
    registry.register_tool(AzureDevOpsTool())
    tool = registry.get_tool("azure_devops_client")
    tools = registry.search_tools(capabilities=["query_work_items"])
"""

from typing import Any, Dict, List, Optional

import structlog

from src.tools.base import (
    Tool,
    ToolNotFoundError,
    ToolRegistryError,
    ToolSpecification,
)

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """
    Central registry for all tools

    Manages tool registration, discovery, and retrieval.
    Provides search capabilities to find tools by various criteria.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register_tool(AzureDevOpsTool())
        >>> tool = registry.get_tool("azure_devops_client")
        >>> tools = registry.list_all_tools()
    """

    def __init__(self):
        """Initialize tool registry"""
        self._tools: Dict[str, Tool] = {}
        self._specifications: Dict[str, ToolSpecification] = {}
        self.logger = structlog.get_logger(__name__)

        self.logger.info("Tool registry initialized")

    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool in the registry

        Args:
            tool: Tool instance to register

        Raises:
            ToolRegistryError: If tool with same ID already registered
            ValueError: If tool is invalid
        """
        if not isinstance(tool, Tool):
            raise ValueError(f"Invalid tool: must inherit from Tool base class")

        tool_id = tool.tool_id

        if not tool_id:
            raise ValueError("Tool must have a tool_id")

        # Check for duplicates
        if tool_id in self._tools:
            raise ToolRegistryError(
                f"Tool '{tool_id}' is already registered. "
                f"Use update_tool() to modify existing tools."
            )

        # Register tool and specification
        self._tools[tool_id] = tool
        self._specifications[tool_id] = tool.get_specification()

        self.logger.info(
            "Tool registered",
            tool_id=tool_id,
            tool_name=tool.name,
            version=tool.version,
        )

    def get_tool(self, tool_id: str) -> Tool:
        """
        Get tool by ID

        Args:
            tool_id: Unique tool identifier

        Returns:
            Tool instance

        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self._tools:
            available = list(self._tools.keys())
            raise ToolNotFoundError(
                f"Tool '{tool_id}' not found. Available tools: {available}"
            )

        return self._tools[tool_id]

    def get_specification(self, tool_id: str) -> ToolSpecification:
        """
        Get tool specification by ID

        Args:
            tool_id: Unique tool identifier

        Returns:
            ToolSpecification

        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self._specifications:
            available = list(self._specifications.keys())
            raise ToolNotFoundError(
                f"Tool specification for '{tool_id}' not found. Available: {available}"
            )

        return self._specifications[tool_id]

    def list_all_tools(self) -> List[ToolSpecification]:
        """
        List all registered tools

        Returns:
            List of tool specifications
        """
        return list(self._specifications.values())

    def search_tools(
        self,
        capabilities: Optional[List[str]] = None,
        name_contains: Optional[str] = None,
        risk_tier_max: Optional[str] = None,
    ) -> List[ToolSpecification]:
        """
        Search for tools matching criteria

        Args:
            capabilities: List of required capabilities
            name_contains: Search by name (case-insensitive)
            risk_tier_max: Maximum risk tier (e.g., "TIER_2")

        Returns:
            List of matching tool specifications

        Example:
            >>> # Find tools that can query work items
            >>> tools = registry.search_tools(capabilities=["query_work_items"])
            >>>
            >>> # Find tools with "devops" in name
            >>> tools = registry.search_tools(name_contains="devops")
        """
        results = []

        for spec in self._specifications.values():
            # Filter by capabilities
            if capabilities:
                if not all(cap in spec.capabilities for cap in capabilities):
                    continue

            # Filter by name
            if name_contains:
                if name_contains.lower() not in spec.name.lower():
                    continue

            # Filter by risk tier
            if risk_tier_max:
                # Compare risk tiers (TIER_1 < TIER_2 < TIER_3 < TIER_4)
                tier_order = {"TIER_1": 1, "TIER_2": 2, "TIER_3": 3, "TIER_4": 4}
                if tier_order.get(spec.risk_tier.value, 99) > tier_order.get(
                    risk_tier_max, 0
                ):
                    continue

            results.append(spec)

        self.logger.debug(
            "Tool search completed",
            criteria={
                "capabilities": capabilities,
                "name_contains": name_contains,
                "risk_tier_max": risk_tier_max,
            },
            results_count=len(results),
        )

        return results

    def update_tool(self, tool: Tool) -> None:
        """
        Update existing tool registration

        Args:
            tool: Updated tool instance

        Raises:
            ToolNotFoundError: If tool not registered
        """
        tool_id = tool.tool_id

        if tool_id not in self._tools:
            raise ToolNotFoundError(
                f"Tool '{tool_id}' not found. Use register_tool() for new tools."
            )

        # Update
        self._tools[tool_id] = tool
        self._specifications[tool_id] = tool.get_specification()

        self.logger.info("Tool updated", tool_id=tool_id, version=tool.version)

    def unregister_tool(self, tool_id: str) -> None:
        """
        Remove tool from registry

        Args:
            tool_id: Tool identifier to remove

        Raises:
            ToolNotFoundError: If tool not found
        """
        if tool_id not in self._tools:
            raise ToolNotFoundError(f"Tool '{tool_id}' not found")

        del self._tools[tool_id]
        del self._specifications[tool_id]

        self.logger.info("Tool unregistered", tool_id=tool_id)

    def is_registered(self, tool_id: str) -> bool:
        """
        Check if tool is registered

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool is registered, False otherwise
        """
        return tool_id in self._tools

    def get_tool_count(self) -> int:
        """
        Get number of registered tools

        Returns:
            Count of registered tools
        """
        return len(self._tools)

    def get_tool_ids(self) -> List[str]:
        """
        Get list of all registered tool IDs

        Returns:
            List of tool IDs
        """
        return list(self._tools.keys())

    def clear(self) -> None:
        """
        Clear all registered tools

        Warning: This removes all tools from the registry.
        Use with caution, typically only in testing.
        """
        count = len(self._tools)
        self._tools.clear()
        self._specifications.clear()

        self.logger.warning("Tool registry cleared", tools_removed=count)


# ============================================================================
# Global Registry Instance
# ============================================================================

# Singleton instance for application-wide use
_global_registry: Optional[ToolRegistry] = None


def get_global_registry() -> ToolRegistry:
    """
    Get the global tool registry instance

    Returns:
        Global ToolRegistry instance

    Example:
        >>> registry = get_global_registry()
        >>> registry.register_tool(MyTool())
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = ToolRegistry()
        logger.info("Global tool registry created")

    return _global_registry


def initialize_default_tools() -> ToolRegistry:
    """
    Initialize registry with default tools

    Registers all built-in tools (ServiceNow, Azure DevOps, etc.)

    Returns:
        Configured ToolRegistry

    Example:
        >>> registry = initialize_default_tools()
        >>> tool = registry.get_tool("azure_devops_client")
    """
    registry = get_global_registry()

    # Register Azure DevOps tool
    try:
        from src.tools.azure_devops_client import AzureDevOpsTool

        azure_tool = AzureDevOpsTool()
        registry.register_tool(azure_tool)
        logger.info("Azure DevOps tool registered")
    except ImportError as e:
        logger.warning("Failed to register Azure DevOps tool", error=str(e))
    except Exception as e:
        logger.error(
            "Error registering Azure DevOps tool", error=str(e), exc_info=True
        )

    # Register other tools here as they are implemented
    # Example:
    # try:
    #     from src.tools.servicenow_client import ServiceNowTool
    #     snow_tool = ServiceNowTool()
    #     registry.register_tool(snow_tool)
    # except Exception as e:
    #     logger.error("Error registering ServiceNow tool", error=str(e))

    logger.info(
        "Default tools initialized", tool_count=registry.get_tool_count()
    )

    return registry


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "ToolRegistry",
    "get_global_registry",
    "initialize_default_tools",
]
