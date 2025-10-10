"""
SDK Tool Bridge Adapter
Geisinger AI Product Manager Agent

Bridges Geisinger's sophisticated Tool framework with Claude Agent SDK's
simple tool format.

Architecture:
- Geisinger Tool: Rich execution, verification, audit logging, context-aware
- SDK Tool: Simple name, description, parameters, execute function
- Bridge: Converts between the two formats

Following patterns from geisinger-sdk-integrator agent guidance.
"""

from typing import Any, Callable, Dict, List

import structlog

from src.tools.base import ExecutionContext, Tool, ToolResult

logger = structlog.get_logger(__name__)


class SDKToolAdapter:
    """
    Adapter that bridges Geisinger Tools to SDK tool format

    This adapter:
    - Converts Geisinger Tool objects to SDK tool definitions
    - Wraps tool execution to preserve Geisinger's rich execution model
    - Maps ExecutionContext to SDK parameters
    - Translates results back to Geisinger format

    Example:
        >>> adapter = SDKToolAdapter()
        >>> geisinger_tool = AzureDevOpsTool()
        >>> sdk_tool_def = adapter.to_sdk_tool(geisinger_tool, context)
        >>> # sdk_tool_def can be used with Claude SDK
    """

    def __init__(self):
        """Initialize SDK tool adapter"""
        self.logger = structlog.get_logger(__name__)

    def to_sdk_tool(
        self, geisinger_tool: Tool, context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Convert Geisinger Tool to SDK tool definition

        Args:
            geisinger_tool: Geisinger Tool instance
            context: Execution context

        Returns:
            SDK tool definition dict with:
                - name: Tool identifier
                - description: What the tool does
                - parameters: Parameter schema
                - execute: Function to call

        Note:
            The execute function wraps Geisinger's rich execution
            while presenting a simple interface to SDK
        """
        # Create wrapped execution function
        async def sdk_execute(params: Dict[str, Any]) -> str:
            """
            SDK-compatible execute function

            Wraps Geisinger tool execution with:
            - Full ExecutionContext
            - ToolResult handling
            - Error conversion
            """
            self.logger.debug(
                "SDK tool execution",
                tool_id=geisinger_tool.tool_id,
                parameters=params,
            )

            try:
                # Call Geisinger tool (rich execution)
                result: ToolResult = await geisinger_tool.execute(params, context)

                # Convert ToolResult to simple string for SDK
                if result.is_success():
                    # Format successful result
                    output = self._format_tool_result(result)
                    self.logger.info(
                        "SDK tool execution successful",
                        tool_id=geisinger_tool.tool_id,
                    )
                    return output
                else:
                    # Format error result
                    error_msg = f"Tool execution failed: {result.error}"
                    self.logger.error(
                        "SDK tool execution failed",
                        tool_id=geisinger_tool.tool_id,
                        error=result.error,
                    )
                    return error_msg

            except Exception as e:
                self.logger.error(
                    "SDK tool execution exception",
                    tool_id=geisinger_tool.tool_id,
                    error=str(e),
                    exc_info=True,
                )
                return f"Tool error: {str(e)}"

        # Build SDK tool definition
        sdk_tool = {
            "name": geisinger_tool.tool_id,
            "description": geisinger_tool.description,
            "parameters": self._convert_parameter_schema(
                geisinger_tool.parameters_schema
            ),
            "execute": sdk_execute,
        }

        self.logger.debug(
            "Converted Geisinger tool to SDK format", tool_id=geisinger_tool.tool_id
        )

        return sdk_tool

    def to_sdk_tools(
        self, geisinger_tools: List[Tool], context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """
        Convert multiple Geisinger tools to SDK format

        Args:
            geisinger_tools: List of Geisinger Tool instances
            context: Execution context

        Returns:
            List of SDK tool definitions
        """
        sdk_tools = []

        for tool in geisinger_tools:
            try:
                sdk_tool = self.to_sdk_tool(tool, context)
                sdk_tools.append(sdk_tool)
            except Exception as e:
                self.logger.error(
                    "Failed to convert tool",
                    tool_id=getattr(tool, "tool_id", "unknown"),
                    error=str(e),
                )

        self.logger.info(
            "Converted Geisinger tools to SDK format",
            total_tools=len(geisinger_tools),
            successful=len(sdk_tools),
        )

        return sdk_tools

    def _convert_parameter_schema(
        self, geisinger_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert Geisinger parameter schema to SDK format

        Args:
            geisinger_schema: Geisinger parameter schema

        Returns:
            SDK-compatible parameter schema
        """
        # Geisinger schema is already JSON Schema-like
        # SDK expects similar format, so minimal conversion needed

        sdk_schema = {"type": "object", "properties": {}, "required": []}

        for param_name, param_spec in geisinger_schema.items():
            # Add to properties
            sdk_schema["properties"][param_name] = {
                "type": param_spec.get("type", "string"),
                "description": param_spec.get("description", ""),
            }

            # Track required parameters
            if param_spec.get("required", False):
                sdk_schema["required"].append(param_name)

            # Add enum if present
            if "enum" in param_spec:
                sdk_schema["properties"][param_name]["enum"] = param_spec["enum"]

        return sdk_schema

    def _format_tool_result(self, result: ToolResult) -> str:
        """
        Format Geisinger ToolResult for SDK consumption

        Args:
            result: Geisinger ToolResult

        Returns:
            Formatted string for SDK
        """
        import json

        output = ""

        # Add main data
        if result.data:
            try:
                output += json.dumps(result.data, indent=2)
            except Exception:
                output += str(result.data)

        # Add citations if present
        if result.citations:
            output += f"\n\nSources: {', '.join(result.citations)}"

        # Add execution metadata
        if result.execution_time_ms:
            output += f"\n(Execution time: {result.execution_time_ms:.0f}ms)"

        return output if output else "Tool executed successfully (no data returned)"


# ============================================================================
# Helper Functions
# ============================================================================


def create_sdk_tool_from_function(
    func: Callable,
    name: str,
    description: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create SDK tool definition from a simple function

    Useful for quick tool creation without full Geisinger Tool class.

    Args:
        func: Async function to execute
        name: Tool name
        description: Tool description
        parameters: Parameter schema

    Returns:
        SDK tool definition

    Example:
        >>> async def my_tool(params):
        ...     return f"Result: {params['input']}"
        >>>
        >>> sdk_tool = create_sdk_tool_from_function(
        ...     my_tool,
        ...     "my_tool",
        ...     "Does something useful",
        ...     {"input": {"type": "string", "required": True}}
        ... )
    """
    return {
        "name": name,
        "description": description,
        "parameters": parameters,
        "execute": func,
    }


def extract_tool_calls_from_response(response: str) -> List[Dict[str, Any]]:
    """
    Extract tool calls from LLM response

    Args:
        response: LLM response text

    Returns:
        List of tool call dicts with tool_name and parameters
    """
    import json
    import re

    tool_calls = []

    # Look for tool call patterns
    # Pattern 1: JSON format
    json_pattern = r'```json\s*(\{[^`]+\})\s*```'
    matches = re.findall(json_pattern, response, re.MULTILINE | re.DOTALL)

    for match in matches:
        try:
            data = json.loads(match)
            if "tool" in data and "parameters" in data:
                tool_calls.append(
                    {"tool_name": data["tool"], "parameters": data["parameters"]}
                )
        except json.JSONDecodeError:
            continue

    # Pattern 2: Structured format
    # TOOL: tool_name
    # PARAMETERS: {...}
    tool_pattern = r'TOOL:\s*(\w+)\s*PARAMETERS:\s*(\{[^}]+\})'
    matches = re.findall(tool_pattern, response, re.MULTILINE | re.DOTALL)

    for tool_name, params_str in matches:
        try:
            parameters = json.loads(params_str)
            tool_calls.append({"tool_name": tool_name, "parameters": parameters})
        except json.JSONDecodeError:
            continue

    return tool_calls


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "SDKToolAdapter",
    "create_sdk_tool_from_function",
    "extract_tool_calls_from_response",
]
