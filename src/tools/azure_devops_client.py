"""
Azure DevOps Client Tool
Geisinger AI Product Manager Agent

This tool provides integration with Azure DevOps Services via the Azure DevOps CLI.
Supports work item management, board operations, and project queries.

Usage:
    tool = AzureDevOpsTool(org_url="https://dev.azure.com/yourorg", pat="your-pat")
    result = await tool.execute({
        "operation": "get_work_item",
        "work_item_id": "12345"
    }, context)

Requires:
    - Azure CLI installed (brew install azure-cli)
    - Azure DevOps extension (az extension add --name azure-devops)
    - Personal Access Token (PAT) for authentication
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

from src.tools.base import (
    ExecutionContext,
    RiskTier,
    Tool,
    ToolResult,
    ToolStatus,
    ToolValidationError,
    create_error_result,
)

logger = structlog.get_logger(__name__)


class AzureDevOpsTool(Tool):
    """
    Azure DevOps integration tool

    Provides access to Azure DevOps boards, work items, and projects
    via the Azure DevOps CLI.

    Supported Operations:
        - list_projects: List all projects in the organization
        - get_project: Get details of a specific project
        - list_work_items: List work items with optional filters
        - get_work_item: Get details of a specific work item
        - update_work_item: Update work item fields
        - query_work_items: Execute WIQL query
        - list_boards: List boards in a project

    Authentication:
        Requires Azure DevOps organization URL and Personal Access Token (PAT)
    """

    def __init__(
        self,
        org_url: Optional[str] = None,
        pat: Optional[str] = None,
        default_project: Optional[str] = None,
    ):
        """
        Initialize Azure DevOps tool

        Args:
            org_url: Azure DevOps organization URL (e.g., https://dev.azure.com/yourorg)
            pat: Personal Access Token for authentication
            default_project: Default project name to use (optional)
        """
        super().__init__()

        # Tool metadata
        self.tool_id = "azure_devops_client"
        self.name = "Azure DevOps Client"
        self.description = (
            "Integrates with Azure DevOps to manage work items, boards, and projects"
        )
        self.version = "1.0.0"
        self.risk_tier = RiskTier.TIER_2  # Passive review

        # Configuration
        self.org_url = org_url or os.getenv("AZURE_DEVOPS_ORG_URL")
        self.pat = pat or os.getenv("AZURE_DEVOPS_PAT")
        self.default_project = default_project or os.getenv("AZURE_DEVOPS_PROJECT")

        # Parameter schema
        self.parameters_schema = {
            "operation": {
                "type": "string",
                "required": True,
                "enum": [
                    "list_projects",
                    "get_project",
                    "list_work_items",
                    "get_work_item",
                    "update_work_item",
                    "query_work_items",
                    "list_boards",
                ],
                "description": "Operation to perform",
            },
            "project": {
                "type": "string",
                "required": False,
                "description": "Project name (uses default if not specified)",
            },
            "work_item_id": {
                "type": "string",
                "required": False,
                "description": "Work item ID for get/update operations",
            },
            "fields": {
                "type": "object",
                "required": False,
                "description": "Fields to update (for update_work_item operation)",
            },
            "query": {
                "type": "string",
                "required": False,
                "description": "WIQL query string (for query_work_items operation)",
            },
            "state": {
                "type": "string",
                "required": False,
                "description": "Work item state filter (e.g., Active, Closed)",
            },
            "assigned_to": {
                "type": "string",
                "required": False,
                "description": "Filter by assigned user",
            },
            "top": {
                "type": "integer",
                "required": False,
                "description": "Limit number of results (default: 50)",
            },
        }

        self.logger = structlog.get_logger(__name__).bind(
            tool_id=self.tool_id, org_url=self.org_url
        )

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ToolResult:
        """
        Execute Azure DevOps operation

        Args:
            parameters: Operation parameters
            context: Execution context

        Returns:
            ToolResult with operation output
        """
        start_time = datetime.now()

        try:
            # Validate parameters
            self._validate_parameters(parameters)

            # Check configuration
            if not self.org_url:
                raise ToolValidationError(
                    "Azure DevOps organization URL not configured. "
                    "Set AZURE_DEVOPS_ORG_URL environment variable."
                )

            if not self.pat:
                raise ToolValidationError(
                    "Azure DevOps PAT not configured. "
                    "Set AZURE_DEVOPS_PAT environment variable."
                )

            operation = parameters["operation"]

            self.logger.info(
                "Executing Azure DevOps operation",
                operation=operation,
                parameters=parameters,
            )

            # Route to appropriate operation handler
            if operation == "list_projects":
                data = await self._list_projects()
            elif operation == "get_project":
                data = await self._get_project(parameters["project"])
            elif operation == "list_work_items":
                data = await self._list_work_items(parameters)
            elif operation == "get_work_item":
                data = await self._get_work_item(parameters["work_item_id"])
            elif operation == "update_work_item":
                data = await self._update_work_item(
                    parameters["work_item_id"], parameters.get("fields", {})
                )
            elif operation == "query_work_items":
                data = await self._query_work_items(
                    parameters.get("query"), parameters.get("project")
                )
            elif operation == "list_boards":
                data = await self._list_boards(
                    parameters.get("project", self.default_project)
                )
            else:
                raise ToolValidationError(f"Unknown operation: {operation}")

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            result = ToolResult(
                status=ToolStatus.SUCCESS,
                tool_id=self.tool_id,
                data=data,
                citations=[f"Azure DevOps: {self.org_url}"],
                execution_time_ms=execution_time,
                metadata={"operation": operation, "parameters": parameters},
            )

            self.logger.info(
                "Azure DevOps operation completed",
                operation=operation,
                execution_time_ms=execution_time,
            )

            return result

        except ToolValidationError as e:
            self.logger.error("Validation error", error=str(e))
            return create_error_result(
                self.tool_id, str(e), ToolStatus.INVALID_INPUT
            )
        except subprocess.TimeoutExpired:
            self.logger.error("Azure CLI command timeout")
            return create_error_result(self.tool_id, "Command timeout", ToolStatus.TIMEOUT)
        except Exception as e:
            self.logger.error("Azure DevOps operation failed", error=str(e), exc_info=True)
            return create_error_result(self.tool_id, str(e))

    def verify_result(self, result: ToolResult) -> bool:
        """
        Verify tool execution result

        Args:
            result: Tool result to verify

        Returns:
            True if result is valid, False otherwise
        """
        # Check status
        if not result.is_success():
            self.logger.warning(
                "Result verification failed - non-success status", status=result.status
            )
            return False

        # Check data exists
        if result.data is None:
            self.logger.warning("Result verification failed - no data")
            return False

        # Operation-specific checks
        operation = result.metadata.get("operation")

        if operation in ["get_work_item", "update_work_item"]:
            # Should have work item data
            if "id" not in result.data:
                self.logger.warning("Result verification failed - missing work item ID")
                return False

        elif operation in ["list_projects", "list_work_items", "list_boards"]:
            # Should have a list
            if not isinstance(result.data, dict) or "value" not in result.data:
                self.logger.warning("Result verification failed - invalid list format")
                return False

        self.logger.debug("Result verification passed", operation=operation)
        return True

    # ========================================================================
    # Private Helper Methods - Azure CLI Wrappers
    # ========================================================================

    async def _run_az_command(
        self, args: List[str], timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Run Azure CLI command

        Args:
            args: Command arguments (after 'az')
            timeout: Command timeout in seconds

        Returns:
            Parsed JSON output

        Raises:
            subprocess.CalledProcessError: If command fails
            subprocess.TimeoutExpired: If command times out
        """
        # Build full command
        cmd = ["az"] + args + ["--output", "json"]

        # Set environment variables for authentication
        env = os.environ.copy()
        env["AZURE_DEVOPS_EXT_PAT"] = self.pat

        self.logger.debug("Running Azure CLI command", command=" ".join(cmd))

        # Run command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8").strip()
                self.logger.error(
                    "Azure CLI command failed",
                    returncode=process.returncode,
                    stderr=error_msg,
                )
                raise subprocess.CalledProcessError(
                    process.returncode, cmd, stdout, stderr
                )

            # Parse JSON output
            output = stdout.decode("utf-8").strip()
            if not output:
                return {}

            return json.loads(output)

        except asyncio.TimeoutError:
            process.kill()
            raise subprocess.TimeoutExpired(cmd, timeout)

    async def _list_projects(self) -> Dict[str, Any]:
        """List all projects in the organization"""
        args = [
            "devops",
            "project",
            "list",
            "--organization",
            self.org_url,
        ]

        result = await self._run_az_command(args)

        return {
            "value": result.get("value", []),
            "count": len(result.get("value", [])),
        }

    async def _get_project(self, project_name: str) -> Dict[str, Any]:
        """Get project details"""
        args = [
            "devops",
            "project",
            "show",
            "--project",
            project_name,
            "--organization",
            self.org_url,
        ]

        return await self._run_az_command(args)

    async def _list_work_items(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """List work items with optional filters"""
        project = parameters.get("project", self.default_project)

        if not project:
            raise ToolValidationError(
                "Project name required for list_work_items operation"
            )

        # Build WIQL query
        query_parts = ["SELECT [System.Id], [System.Title], [System.State] FROM WorkItems"]

        where_clauses = []

        if "state" in parameters:
            where_clauses.append(f"[System.State] = '{parameters['state']}'")

        if "assigned_to" in parameters:
            where_clauses.append(f"[System.AssignedTo] = '{parameters['assigned_to']}'")

        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))

        query = " ".join(query_parts)

        # Execute query
        args = [
            "boards",
            "query",
            "--wiql",
            query,
            "--project",
            project,
            "--organization",
            self.org_url,
        ]

        result = await self._run_az_command(args, timeout=60)

        # Limit results
        top = parameters.get("top", 50)
        work_items = result.get("workItems", [])[:top]

        return {"value": work_items, "count": len(work_items), "query": query}

    async def _get_work_item(self, work_item_id: str) -> Dict[str, Any]:
        """Get work item details"""
        args = [
            "boards",
            "work-item",
            "show",
            "--id",
            work_item_id,
            "--organization",
            self.org_url,
        ]

        return await self._run_az_command(args)

    async def _update_work_item(
        self, work_item_id: str, fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update work item fields"""
        args = [
            "boards",
            "work-item",
            "update",
            "--id",
            work_item_id,
            "--organization",
            self.org_url,
        ]

        # Add field updates
        for field, value in fields.items():
            args.extend(["--fields", f"{field}={value}"])

        return await self._run_az_command(args)

    async def _query_work_items(
        self, query: Optional[str], project: Optional[str]
    ) -> Dict[str, Any]:
        """Execute WIQL query"""
        if not query:
            raise ToolValidationError("Query required for query_work_items operation")

        project = project or self.default_project
        if not project:
            raise ToolValidationError("Project name required for query operation")

        args = [
            "boards",
            "query",
            "--wiql",
            query,
            "--project",
            project,
            "--organization",
            self.org_url,
        ]

        result = await self._run_az_command(args, timeout=60)

        return {
            "value": result.get("workItems", []),
            "count": len(result.get("workItems", [])),
            "query": query,
        }

    async def _list_boards(self, project: str) -> Dict[str, Any]:
        """List boards in project"""
        if not project:
            raise ToolValidationError("Project name required for list_boards operation")

        # Get teams first (boards are team-specific)
        teams_args = [
            "devops",
            "team",
            "list",
            "--project",
            project,
            "--organization",
            self.org_url,
        ]

        teams_result = await self._run_az_command(teams_args)
        teams = teams_result.get("value", [])

        # Get boards for each team
        boards = []
        for team in teams:
            team_name = team.get("name")
            try:
                board_args = [
                    "boards",
                    "iteration",
                    "project",
                    "list",
                    "--project",
                    project,
                    "--team",
                    team_name,
                    "--organization",
                    self.org_url,
                ]

                board_result = await self._run_az_command(board_args)
                boards.append(
                    {
                        "team": team_name,
                        "boards": board_result.get("value", []),
                    }
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to get boards for team", team=team_name, error=str(e)
                )
                continue

        return {"value": boards, "count": len(boards), "teams": len(teams)}


# ============================================================================
# Module Exports
# ============================================================================

__all__ = ["AzureDevOpsTool"]
