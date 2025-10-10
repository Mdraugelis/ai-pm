"""
Integration Tests for Claude SDK Integration
Geisinger AI Product Manager Agent

Tests the integration between Claude Agent SDK and Geisinger's
orchestration framework.

Tests:
- SDK Integration module
- LLM Interface layer
- Tool Bridge Adapter
- Orchestrator with SDK
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.llm_interface import LLMInterface
from src.agent.orchestrator import AgentOrchestrator, Task
from src.agent.sdk_integration import SDKIntegration
from src.tools.base import ExecutionContext, Tool, ToolResult, ToolStatus
from src.tools.sdk_tool_adapter import SDKToolAdapter


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_config():
    """Mock configuration for tests"""
    return {
        "model": "claude-sonnet-4-5-20250929",
        "max_iterations": 3,
        "confidence_threshold": 0.7,
        "retry_attempts": 2,
        "timeout_seconds": 5,
    }


@pytest.fixture
def mock_blueprint_loader():
    """Mock blueprint loader"""
    loader = MagicMock()
    loader.load_meta_blueprint.return_value = {
        "name": "Meta Blueprint",
        "policies": [
            {
                "id": "POL-001",
                "rule": "All actions must be verified",
                "enforcement": "MUST",
            }
        ],
    }
    loader.load_domain_blueprint.return_value = {
        "name": "Product Management Blueprint",
        "domain": "product_management",
        "policies": [],
        "guidelines": [],
    }
    return loader


@pytest.fixture
def mock_tool_registry():
    """Mock tool registry"""
    registry = MagicMock()
    registry.get_tool_ids.return_value = ["test_tool_1", "test_tool_2"]
    return registry


@pytest.fixture
def execution_context():
    """Create test execution context"""
    return ExecutionContext(
        session_id="test-session-123",
        initiative_id="test-initiative-456",
        user_id="test-user",
        task_description="Test task",
        blueprints={},
        memory={},
    )


class MockTool(Tool):
    """Mock tool for testing"""

    def __init__(self):
        self.tool_id = "mock_tool"
        self.description = "A mock tool for testing"
        self.parameters_schema = {
            "input": {"type": "string", "required": True, "description": "Test input"}
        }

    async def execute(self, parameters, context):
        """Execute mock tool"""
        return ToolResult(
            status=ToolStatus.SUCCESS,
            data={"output": f"Processed: {parameters.get('input')}"},
            tool_id=self.tool_id,
            execution_time_ms=10.0,
        )

    def verify_result(self, result):
        """Verify mock tool result"""
        return result.status == ToolStatus.SUCCESS


# ============================================================================
# SDK Integration Tests
# ============================================================================


@pytest.mark.integration
class TestSDKIntegration:
    """Test SDK Integration module"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    def test_sdk_initialization(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test SDK integration initializes correctly"""
        sdk = SDKIntegration(mock_config, mock_blueprint_loader, mock_tool_registry)

        assert sdk.config == mock_config
        assert sdk.blueprint_loader == mock_blueprint_loader
        assert sdk.tool_registry == mock_tool_registry
        mock_anthropic_class.assert_called_once_with(api_key="test-key-123")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    def test_system_prompt_includes_blueprints(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test system prompt includes blueprint policies"""
        sdk = SDKIntegration(mock_config, mock_blueprint_loader, mock_tool_registry)
        system_prompt = sdk._build_system_prompt()

        assert "Geisinger AI Product Manager Agent" in system_prompt
        assert "POL-001" in system_prompt
        assert "All actions must be verified" in system_prompt

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_generate_plan(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test plan generation via SDK"""
        # Mock Anthropic client response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"steps": [{"number": 1, "action": "Test step"}], "confidence": 0.85, "reasoning": "Test reasoning"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        sdk = SDKIntegration(mock_config, mock_blueprint_loader, mock_tool_registry)

        task = {"description": "Test task", "initiative_id": "test-123"}
        context = {"iteration": 0}

        plan = await sdk.generate_plan(task, context)

        assert "steps" in plan
        assert len(plan["steps"]) == 1
        assert plan["confidence"] == 0.85
        assert plan["reasoning"] == "Test reasoning"

    @patch.dict(os.environ, {})  # No API key
    def test_sdk_requires_api_key(self, mock_config):
        """Test SDK initialization fails without API key"""
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            SDKIntegration(mock_config)


# ============================================================================
# LLM Interface Tests
# ============================================================================


@pytest.mark.integration
class TestLLMInterface:
    """Test LLM Interface layer"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    def test_llm_interface_initialization(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test LLM interface initializes correctly"""
        llm = LLMInterface(mock_config, mock_blueprint_loader, mock_tool_registry)

        assert llm.config == mock_config
        assert llm.retry_attempts == 2
        assert llm.timeout_seconds == 5

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_generate_plan(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test plan generation through LLM interface"""
        # Mock Anthropic client response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"steps": [{"number": 1, "action": "Retrieve data"}], "confidence": 0.90, "reasoning": "Clear plan"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        llm = LLMInterface(mock_config, mock_blueprint_loader, mock_tool_registry)

        task = {"description": "Retrieve SNOW ticket"}
        context = {"iteration": 0}

        plan = await llm.generate_plan(task, context)

        assert plan["confidence"] == 0.90
        assert len(plan["steps"]) == 1

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_ask_question(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test asking questions via LLM interface"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="The risk level is HIGH")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        llm = LLMInterface(mock_config, mock_blueprint_loader, mock_tool_registry)

        response = await llm.ask_question("What is the risk level?")

        assert response == "The risk level is HIGH"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    def test_to_sdk_messages_conversion(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test conversion from Geisinger context to SDK messages"""
        llm = LLMInterface(mock_config, mock_blueprint_loader, mock_tool_registry)

        # Test with user message last (so tool results get appended)
        geisinger_context = {
            "conversation": [
                {"role": "user", "content": "What's the status?"},
            ],
            "tool_results": [
                {"tool_id": "test_tool", "summary": "Retrieved data"}
            ],
        }

        messages = llm.to_sdk_messages(geisinger_context)

        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert "Recent tool results" in messages[0]["content"]


# ============================================================================
# Tool Bridge Adapter Tests
# ============================================================================


@pytest.mark.integration
class TestSDKToolAdapter:
    """Test SDK Tool Bridge Adapter"""

    def test_tool_adapter_initialization(self):
        """Test adapter initializes correctly"""
        adapter = SDKToolAdapter()
        assert adapter is not None

    @pytest.mark.asyncio
    async def test_convert_geisinger_tool_to_sdk(self, execution_context):
        """Test converting Geisinger tool to SDK format"""
        adapter = SDKToolAdapter()
        geisinger_tool = MockTool()

        sdk_tool = adapter.to_sdk_tool(geisinger_tool, execution_context)

        assert sdk_tool["name"] == "mock_tool"
        assert sdk_tool["description"] == "A mock tool for testing"
        assert "input" in sdk_tool["parameters"]["properties"]
        assert callable(sdk_tool["execute"])

    @pytest.mark.asyncio
    async def test_sdk_tool_execute_wraps_geisinger(self, execution_context):
        """Test SDK tool execute wraps Geisinger execution"""
        adapter = SDKToolAdapter()
        geisinger_tool = MockTool()

        sdk_tool = adapter.to_sdk_tool(geisinger_tool, execution_context)

        # Execute SDK tool
        result = await sdk_tool["execute"]({"input": "test data"})

        assert "Processed: test data" in result
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_convert_multiple_tools(self, execution_context):
        """Test converting multiple Geisinger tools"""
        adapter = SDKToolAdapter()
        geisinger_tools = [MockTool(), MockTool()]

        sdk_tools = adapter.to_sdk_tools(geisinger_tools, execution_context)

        assert len(sdk_tools) == 2
        assert all("name" in tool for tool in sdk_tools)

    def test_parameter_schema_conversion(self):
        """Test parameter schema conversion"""
        adapter = SDKToolAdapter()

        geisinger_schema = {
            "param1": {"type": "string", "required": True, "description": "Param 1"},
            "param2": {"type": "integer", "required": False, "description": "Param 2"},
        }

        sdk_schema = adapter._convert_parameter_schema(geisinger_schema)

        assert sdk_schema["type"] == "object"
        assert "param1" in sdk_schema["properties"]
        assert "param2" in sdk_schema["properties"]
        assert "param1" in sdk_schema["required"]
        assert "param2" not in sdk_schema["required"]


# ============================================================================
# Orchestrator Integration Tests
# ============================================================================


@pytest.mark.integration
class TestOrchestratorSDKIntegration:
    """Test orchestrator with SDK integration"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test orchestrator initializes with SDK"""
        orchestrator = AgentOrchestrator(
            mock_config, mock_blueprint_loader, mock_tool_registry
        )

        assert orchestrator.llm is not None
        assert orchestrator.tool_adapter is not None
        assert orchestrator.max_iterations == 3

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_orchestrator_execute_task_with_sdk(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test orchestrator executes task using SDK for planning"""
        # Mock Anthropic client response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"steps": [{"number": 1, "action": "Complete task"}], "confidence": 0.95, "reasoning": "Simple task"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        orchestrator = AgentOrchestrator(
            mock_config, mock_blueprint_loader, mock_tool_registry
        )

        task = Task(description="Test task", initiative_id="test-123")

        response = await orchestrator.execute_task(task)

        assert response.status == "SUCCESS"
        assert response.verification is not None
        assert len(response.trace) > 0

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_orchestrator_max_iterations(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test orchestrator respects max iterations"""
        # Mock Anthropic client to always return incomplete plan
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"steps": [{"number": 1, "action": "Try again"}], "confidence": 0.50, "reasoning": "Needs more work"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        # Lower max iterations for test
        test_config = mock_config.copy()
        test_config["max_iterations"] = 2

        orchestrator = AgentOrchestrator(
            test_config, mock_blueprint_loader, mock_tool_registry
        )

        # Mock verification to never complete
        orchestrator._verify_result = AsyncMock(
            return_value={"passed": False, "complete": False, "issues": ["Incomplete"]}
        )

        task = Task(description="Difficult task")

        response = await orchestrator.execute_task(task)

        assert response.status == "MAX_ITERATIONS"
        assert len(response.trace) == 2 * 4  # 2 iterations × 4 steps (gather, plan, execute, verify)


# ============================================================================
# End-to-End Integration Tests
# ============================================================================


@pytest.mark.integration
class TestEndToEndSDKIntegration:
    """End-to-end tests of SDK integration"""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_full_workflow_with_sdk(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, mock_tool_registry
    ):
        """Test complete workflow using SDK integration"""
        # Mock Anthropic client responses for plan generation
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"steps": [{"number": 1, "action": "Process SNOW ticket", "tool": "servicenow", "verification": "Ticket retrieved"}], "confidence": 0.88, "reasoning": "Standard intake process"}')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        # Create orchestrator
        orchestrator = AgentOrchestrator(
            mock_config, mock_blueprint_loader, mock_tool_registry
        )

        # Create task
        task = Task(
            description="Process SNOW ticket INC0012345",
            initiative_id="test-initiative-789",
            domain="product_management",
        )

        # Execute task
        response = await orchestrator.execute_task(task)

        # Verify response structure
        assert response.status in ["SUCCESS", "MAX_ITERATIONS"]
        assert response.trace is not None
        assert response.reasoning is not None

        # Verify trace includes all steps
        trace_steps = [entry["step"] for entry in response.trace]
        assert "gather" in trace_steps
        assert "plan" in trace_steps
        assert "execute" in trace_steps
        assert "verify" in trace_steps

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-123"})
    @patch("src.agent.sdk_integration.Anthropic")
    @pytest.mark.asyncio
    async def test_sdk_with_tool_execution(
        self, mock_anthropic_class, mock_config, mock_blueprint_loader, execution_context
    ):
        """Test SDK integration with actual tool execution"""
        # Create adapter and tool
        adapter = SDKToolAdapter()
        geisinger_tool = MockTool()

        # Convert to SDK tool
        sdk_tool = adapter.to_sdk_tool(geisinger_tool, execution_context)

        # Execute SDK tool
        result = await sdk_tool["execute"]({"input": "test data"})

        # Verify execution
        assert "Processed: test data" in result
        assert "Execution time:" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
