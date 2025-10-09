"""
Unit Tests for Azure DevOps Client Tool
Geisinger AI Product Manager Agent

Tests the AzureDevOpsTool class with mocked Azure CLI calls.

Run:
    pytest tests/unit/test_tools/test_azure_devops_client.py -v
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.tools.azure_devops_client import AzureDevOpsTool
from src.tools.base import ExecutionContext, ToolStatus


@pytest.fixture
def azure_tool():
    """Create Azure DevOps tool instance with test config"""
    tool = AzureDevOpsTool(
        org_url="https://dev.azure.com/testorg",
        pat="test-pat-token",
        default_project="TestProject",
    )
    return tool


@pytest.fixture
def execution_context():
    """Create execution context for tests"""
    return ExecutionContext(
        session_id="test-session-123",
        initiative_id="test-initiative-456",
        user_id="test-user",
        task_description="Test Azure DevOps operations",
    )


class TestAzureDevOpsToolInitialization:
    """Test tool initialization and configuration"""

    def test_tool_initialization(self, azure_tool):
        """Test tool is initialized with correct metadata"""
        assert azure_tool.tool_id == "azure_devops_client"
        assert azure_tool.name == "Azure DevOps Client"
        assert azure_tool.version == "1.0.0"
        assert azure_tool.org_url == "https://dev.azure.com/testorg"
        assert azure_tool.pat == "test-pat-token"
        assert azure_tool.default_project == "TestProject"

    def test_tool_parameters_schema(self, azure_tool):
        """Test parameters schema is defined correctly"""
        schema = azure_tool.parameters_schema

        assert "operation" in schema
        assert schema["operation"]["required"] is True
        assert "list_projects" in schema["operation"]["enum"]
        assert "get_work_item" in schema["operation"]["enum"]

    def test_tool_from_environment_variables(self, monkeypatch):
        """Test tool can be initialized from environment variables"""
        monkeypatch.setenv("AZURE_DEVOPS_ORG_URL", "https://dev.azure.com/envorg")
        monkeypatch.setenv("AZURE_DEVOPS_PAT", "env-pat-token")
        monkeypatch.setenv("AZURE_DEVOPS_PROJECT", "EnvProject")

        tool = AzureDevOpsTool()

        assert tool.org_url == "https://dev.azure.com/envorg"
        assert tool.pat == "env-pat-token"
        assert tool.default_project == "EnvProject"


class TestListProjects:
    """Test list_projects operation"""

    @pytest.mark.asyncio
    async def test_list_projects_success(self, azure_tool, execution_context):
        """Test successful project listing"""
        # Mock Azure CLI response
        mock_response = {
            "value": [
                {"id": "proj-1", "name": "Project 1"},
                {"id": "proj-2", "name": "Project 2"},
            ]
        }

        with patch.object(
            azure_tool, "_run_az_command", return_value=mock_response
        ) as mock_cmd:
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            # Verify command was called correctly
            mock_cmd.assert_called_once()
            args = mock_cmd.call_args[0][0]
            assert "devops" in args
            assert "project" in args
            assert "list" in args

            # Verify result
            assert result.is_success()
            assert result.data["count"] == 2
            assert len(result.data["value"]) == 2

    @pytest.mark.asyncio
    async def test_list_projects_no_org_url(self, execution_context):
        """Test error when organization URL is not configured"""
        tool = AzureDevOpsTool(pat="test-pat")  # No org_url

        result = await tool.execute({"operation": "list_projects"}, execution_context)

        assert result.status == ToolStatus.INVALID_INPUT
        assert "organization URL not configured" in result.error


class TestGetWorkItem:
    """Test get_work_item operation"""

    @pytest.mark.asyncio
    async def test_get_work_item_success(self, azure_tool, execution_context):
        """Test successful work item retrieval"""
        mock_response = {
            "id": 12345,
            "fields": {
                "System.Title": "Test Work Item",
                "System.State": "Active",
                "System.AssignedTo": "user@example.com",
            },
        }

        with patch.object(
            azure_tool, "_run_az_command", return_value=mock_response
        ) as mock_cmd:
            result = await azure_tool.execute(
                {"operation": "get_work_item", "work_item_id": "12345"},
                execution_context,
            )

            # Verify command
            args = mock_cmd.call_args[0][0]
            assert "boards" in args
            assert "work-item" in args
            assert "show" in args
            assert "12345" in args

            # Verify result
            assert result.is_success()
            assert result.data["id"] == 12345
            assert "Test Work Item" in result.data["fields"]["System.Title"]

    @pytest.mark.asyncio
    async def test_get_work_item_missing_id(self, azure_tool, execution_context):
        """Test error when work_item_id is missing"""
        result = await azure_tool.execute(
            {"operation": "get_work_item"},  # Missing work_item_id
            execution_context,
        )

        assert result.status == ToolStatus.INVALID_INPUT


class TestListWorkItems:
    """Test list_work_items operation"""

    @pytest.mark.asyncio
    async def test_list_work_items_with_filters(self, azure_tool, execution_context):
        """Test listing work items with state filter"""
        mock_response = {
            "workItems": [
                {"id": 1, "url": "https://..."},
                {"id": 2, "url": "https://..."},
            ]
        }

        with patch.object(
            azure_tool, "_run_az_command", return_value=mock_response
        ) as mock_cmd:
            result = await azure_tool.execute(
                {
                    "operation": "list_work_items",
                    "project": "TestProject",
                    "state": "Active",
                    "top": 10,
                },
                execution_context,
            )

            # Verify WIQL query contains state filter
            args = mock_cmd.call_args[0][0]
            query_arg_index = args.index("--wiql") + 1
            query = args[query_arg_index]
            assert "[System.State] = 'Active'" in query

            # Verify result
            assert result.is_success()
            assert result.data["count"] == 2

    @pytest.mark.asyncio
    async def test_list_work_items_no_project(self, execution_context):
        """Test error when project is not specified"""
        tool = AzureDevOpsTool(
            org_url="https://dev.azure.com/testorg",
            pat="test-pat",
            # No default_project
        )

        result = await tool.execute(
            {"operation": "list_work_items"},  # No project specified
            execution_context,
        )

        assert result.status == ToolStatus.INVALID_INPUT
        assert "Project name required" in result.error


class TestUpdateWorkItem:
    """Test update_work_item operation"""

    @pytest.mark.asyncio
    async def test_update_work_item_success(self, azure_tool, execution_context):
        """Test successful work item update"""
        mock_response = {
            "id": 12345,
            "fields": {
                "System.State": "Closed",
                "System.Title": "Updated Title",
            },
        }

        with patch.object(
            azure_tool, "_run_az_command", return_value=mock_response
        ) as mock_cmd:
            result = await azure_tool.execute(
                {
                    "operation": "update_work_item",
                    "work_item_id": "12345",
                    "fields": {
                        "System.State": "Closed",
                        "System.Title": "Updated Title",
                    },
                },
                execution_context,
            )

            # Verify command includes field updates
            args = mock_cmd.call_args[0][0]
            assert "update" in args
            assert "12345" in args
            assert "--fields" in args

            # Verify result
            assert result.is_success()
            assert result.data["id"] == 12345


class TestQueryWorkItems:
    """Test query_work_items operation"""

    @pytest.mark.asyncio
    async def test_query_work_items_success(self, azure_tool, execution_context):
        """Test successful WIQL query execution"""
        mock_response = {
            "workItems": [
                {"id": 100},
                {"id": 101},
                {"id": 102},
            ]
        }

        custom_query = (
            "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active'"
        )

        with patch.object(
            azure_tool, "_run_az_command", return_value=mock_response
        ) as mock_cmd:
            result = await azure_tool.execute(
                {
                    "operation": "query_work_items",
                    "query": custom_query,
                    "project": "TestProject",
                },
                execution_context,
            )

            # Verify query was passed correctly
            args = mock_cmd.call_args[0][0]
            query_arg_index = args.index("--wiql") + 1
            assert args[query_arg_index] == custom_query

            # Verify result
            assert result.is_success()
            assert result.data["count"] == 3
            assert result.data["query"] == custom_query


class TestListBoards:
    """Test list_boards operation"""

    @pytest.mark.asyncio
    async def test_list_boards_success(self, azure_tool, execution_context):
        """Test successful board listing"""
        # Mock teams response
        teams_response = {
            "value": [
                {"id": "team-1", "name": "Team Alpha"},
                {"id": "team-2", "name": "Team Beta"},
            ]
        }

        # Mock boards response
        boards_response = {"value": [{"id": "sprint-1", "name": "Sprint 1"}]}

        with patch.object(azure_tool, "_run_az_command") as mock_cmd:
            # Set up multiple return values
            mock_cmd.side_effect = [teams_response, boards_response, boards_response]

            result = await azure_tool.execute(
                {"operation": "list_boards", "project": "TestProject"},
                execution_context,
            )

            # Verify result
            assert result.is_success()
            assert result.data["teams"] == 2
            assert len(result.data["value"]) == 2


class TestVerification:
    """Test result verification"""

    @pytest.mark.asyncio
    async def test_verify_successful_result(self, azure_tool, execution_context):
        """Test verification of successful result"""
        mock_response = {"id": 12345, "fields": {}}

        with patch.object(azure_tool, "_run_az_command", return_value=mock_response):
            result = await azure_tool.execute(
                {"operation": "get_work_item", "work_item_id": "12345"},
                execution_context,
            )

            # Verify result passes verification
            assert azure_tool.verify_result(result) is True

    def test_verify_failed_result(self, azure_tool):
        """Test verification of failed result"""
        from src.tools.base import ToolResult

        failed_result = ToolResult(
            status=ToolStatus.FAILED, tool_id="azure_devops_client", error="Test error"
        )

        # Failed result should not pass verification
        assert azure_tool.verify_result(failed_result) is False

    def test_verify_result_missing_data(self, azure_tool):
        """Test verification fails when data is None"""
        from src.tools.base import ToolResult

        result = ToolResult(
            status=ToolStatus.SUCCESS, tool_id="azure_devops_client", data=None
        )

        # Result with no data should fail verification
        assert azure_tool.verify_result(result) is False


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_azure_cli_command_timeout(self, azure_tool, execution_context):
        """Test handling of command timeout"""
        import subprocess

        with patch.object(
            azure_tool,
            "_run_az_command",
            side_effect=subprocess.TimeoutExpired("az", 30),
        ):
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            assert result.status == ToolStatus.TIMEOUT
            assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_azure_cli_command_failure(self, azure_tool, execution_context):
        """Test handling of CLI command failure"""
        import subprocess

        with patch.object(
            azure_tool,
            "_run_az_command",
            side_effect=subprocess.CalledProcessError(1, "az", b"", b"CLI Error"),
        ):
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            assert result.status == ToolStatus.FAILED

    @pytest.mark.asyncio
    async def test_invalid_operation(self, azure_tool, execution_context):
        """Test handling of invalid operation"""
        result = await azure_tool.execute(
            {"operation": "invalid_operation"}, execution_context
        )

        assert result.status == ToolStatus.INVALID_INPUT
        assert "Unknown operation" in result.error


class TestExecutionMetrics:
    """Test execution metrics and metadata"""

    @pytest.mark.asyncio
    async def test_execution_time_recorded(self, azure_tool, execution_context):
        """Test that execution time is recorded"""
        mock_response = {"value": []}

        with patch.object(azure_tool, "_run_az_command", return_value=mock_response):
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            # Execution time should be recorded
            assert result.execution_time_ms is not None
            assert result.execution_time_ms > 0

    @pytest.mark.asyncio
    async def test_metadata_includes_operation(self, azure_tool, execution_context):
        """Test that metadata includes operation information"""
        mock_response = {"value": []}

        with patch.object(azure_tool, "_run_az_command", return_value=mock_response):
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            # Metadata should include operation
            assert "operation" in result.metadata
            assert result.metadata["operation"] == "list_projects"

    @pytest.mark.asyncio
    async def test_citations_include_org_url(self, azure_tool, execution_context):
        """Test that citations include organization URL"""
        mock_response = {"value": []}

        with patch.object(azure_tool, "_run_az_command", return_value=mock_response):
            result = await azure_tool.execute(
                {"operation": "list_projects"}, execution_context
            )

            # Citations should include Azure DevOps URL
            assert len(result.citations) > 0
            assert "dev.azure.com/testorg" in result.citations[0]


# ============================================================================
# Integration-like Tests (still mocked but test full flow)
# ============================================================================


class TestFullWorkflow:
    """Test complete workflows"""

    @pytest.mark.asyncio
    async def test_list_then_get_work_item(self, azure_tool, execution_context):
        """Test workflow: list work items, then get details"""
        # Mock list response
        list_response = {"workItems": [{"id": 123, "url": "https://..."}]}

        # Mock get response
        get_response = {
            "id": 123,
            "fields": {"System.Title": "Test Item", "System.State": "Active"},
        }

        with patch.object(azure_tool, "_run_az_command") as mock_cmd:
            mock_cmd.side_effect = [list_response, get_response]

            # Step 1: List work items
            list_result = await azure_tool.execute(
                {"operation": "list_work_items", "project": "TestProject"},
                execution_context,
            )

            assert list_result.is_success()
            work_item_id = list_result.data["value"][0]["id"]

            # Step 2: Get work item details
            get_result = await azure_tool.execute(
                {"operation": "get_work_item", "work_item_id": str(work_item_id)},
                execution_context,
            )

            assert get_result.is_success()
            assert get_result.data["id"] == 123
            assert get_result.data["fields"]["System.Title"] == "Test Item"


# ============================================================================
# Fixtures for pytest
# ============================================================================


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables before each test"""
    monkeypatch.delenv("AZURE_DEVOPS_ORG_URL", raising=False)
    monkeypatch.delenv("AZURE_DEVOPS_PAT", raising=False)
    monkeypatch.delenv("AZURE_DEVOPS_PROJECT", raising=False)
