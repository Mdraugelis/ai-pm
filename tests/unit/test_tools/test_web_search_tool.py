"""
Unit Tests for Web Search Tool
Geisinger AI Product Manager Agent

Tests the WebSearchTool class and its methods.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from src.tools.web_search_tool import WebSearchTool, format_search_results_for_llm
from src.tools.base import ExecutionContext, ToolStatus


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_brave_response():
    """Mock Brave Search API response"""
    return {
        "web": {
            "results": [
                {
                    "title": "Epic Healthcare AI Solutions",
                    "url": "https://www.epic.com/ai",
                    "description": "Epic provides AI-powered healthcare solutions...",
                    "age": "2025-01",
                    "language": "en",
                },
                {
                    "title": "Epic In Basket AI Features",
                    "url": "https://www.epic.com/inbox-ai",
                    "description": "In Basket Priority Scoring helps physicians...",
                    "age": "2024-12",
                    "language": "en",
                },
            ]
        }
    }


@pytest.fixture
def web_search_tool():
    """Create WebSearchTool without API key (uses mocks)"""
    return WebSearchTool(api_key=None)


@pytest.fixture
def execution_context():
    """Create execution context"""
    return ExecutionContext(session_id="test-session")


# ============================================================================
# Test Initialization
# ============================================================================


def test_initialization_without_api_key():
    """Test tool initializes without API key"""
    tool = WebSearchTool(api_key=None)

    assert tool.tool_id == "web_search"
    assert tool.name == "Web Search Tool"
    assert tool.api_key is None
    assert tool.max_results == 10


def test_initialization_with_api_key():
    """Test tool initializes with API key"""
    tool = WebSearchTool(api_key="test-key-123")

    assert tool.api_key == "test-key-123"


def test_initialization_custom_params():
    """Test tool initializes with custom parameters"""
    tool = WebSearchTool(
        api_key="test-key",
        max_results=20,
        timeout_seconds=60,
        cache_ttl_seconds=7200,
    )

    assert tool.max_results == 20
    assert tool.timeout_seconds == 60
    assert tool.cache_ttl_seconds == 7200


# ============================================================================
# Test Mock Search (No API Key)
# ============================================================================


@pytest.mark.asyncio
async def test_execute_without_api_key(web_search_tool, execution_context):
    """Test search executes with mock results when no API key"""
    result = await web_search_tool.execute(
        {"query": "Epic Healthcare AI"},
        execution_context
    )

    # Should return success with mock data
    assert result.status == ToolStatus.SUCCESS
    assert result.data is not None
    assert "results" in result.data
    assert len(result.data["results"]) > 0

    # Check metadata indicates mock
    assert result.metadata.get("mock") is True


@pytest.mark.asyncio
async def test_mock_results_structure(web_search_tool, execution_context):
    """Test mock results have correct structure"""
    result = await web_search_tool.execute(
        {"query": "test query"},
        execution_context
    )

    # Check structure
    assert "query" in result.data
    assert "results" in result.data
    assert "total_results" in result.data

    # Check each result has required fields
    for res in result.data["results"]:
        assert "title" in res
        assert "url" in res
        assert "snippet" in res


# ============================================================================
# Test Real Search (With API Key)
# ============================================================================


@pytest.mark.asyncio
async def test_execute_with_api_key(mock_brave_response, execution_context):
    """Test search executes with real API call"""
    tool = WebSearchTool(api_key="test-api-key")

    # Mock the HTTP client
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.json.return_value = mock_brave_response
        mock_response.raise_for_status = Mock()

        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            return_value=mock_response
        )

        result = await tool.execute(
            {"query": "Epic Healthcare AI", "count": 10},
            execution_context
        )

        # Verify success
        assert result.status == ToolStatus.SUCCESS
        assert result.data is not None
        assert len(result.data["results"]) == 2  # Mock has 2 results

        # Verify citations
        assert len(result.citations) > 0
        assert "https://www.epic.com/ai" in result.citations


@pytest.mark.asyncio
async def test_search_result_parsing(mock_brave_response):
    """Test Brave API response parsing"""
    tool = WebSearchTool(api_key="test-key")

    results = tool._parse_brave_results(mock_brave_response)

    assert len(results) == 2
    assert results[0]["title"] == "Epic Healthcare AI Solutions"
    assert results[0]["url"] == "https://www.epic.com/ai"
    assert "snippet" in results[0]


# ============================================================================
# Test Caching
# ============================================================================


@pytest.mark.asyncio
async def test_caching_works(web_search_tool, execution_context):
    """Test results are cached"""
    # First call
    result1 = await web_search_tool.execute(
        {"query": "test query", "count": 5},
        execution_context
    )

    # Second call with same query
    result2 = await web_search_tool.execute(
        {"query": "test query", "count": 5},
        execution_context
    )

    # Second call should be cached
    assert result2.metadata.get("cached") is True


@pytest.mark.asyncio
async def test_cache_different_queries(web_search_tool, execution_context):
    """Test different queries not cached together"""
    result1 = await web_search_tool.execute(
        {"query": "query one"},
        execution_context
    )

    result2 = await web_search_tool.execute(
        {"query": "query two"},
        execution_context
    )

    # Different queries, not cached
    assert result2.metadata.get("cached") is not True


def test_clear_cache(web_search_tool):
    """Test cache clearing"""
    # Add something to cache
    web_search_tool._cache["test_key"] = {"data": "test"}

    # Clear cache
    web_search_tool.clear_cache()

    assert len(web_search_tool._cache) == 0


# ============================================================================
# Test Parameter Validation
# ============================================================================


@pytest.mark.asyncio
async def test_missing_required_parameter(web_search_tool, execution_context):
    """Test error when query parameter missing"""
    result = await web_search_tool.execute(
        {},  # No query parameter
        execution_context
    )

    assert result.status == ToolStatus.INVALID_INPUT
    assert result.error is not None


@pytest.mark.asyncio
async def test_optional_parameters(web_search_tool, execution_context):
    """Test optional parameters are handled"""
    result = await web_search_tool.execute(
        {
            "query": "test",
            "count": 5,
            "freshness": "week",
        },
        execution_context
    )

    # Should succeed with optional params
    assert result.is_success()


# ============================================================================
# Test Result Verification
# ============================================================================


def test_verify_result_success(web_search_tool):
    """Test verification of successful result"""
    from src.tools.base import ToolResult

    result = ToolResult(
        status=ToolStatus.SUCCESS,
        tool_id="web_search",
        data={
            "query": "test",
            "results": [
                {
                    "title": "Test",
                    "url": "https://example.com",
                    "snippet": "Test snippet"
                }
            ],
            "total_results": 1,
        },
        citations=["https://example.com"],
    )

    assert web_search_tool.verify_result(result) is True


def test_verify_result_missing_fields(web_search_tool):
    """Test verification fails with missing fields"""
    from src.tools.base import ToolResult

    result = ToolResult(
        status=ToolStatus.SUCCESS,
        tool_id="web_search",
        data={
            "results": [
                {
                    "title": "Test",
                    # Missing url and snippet
                }
            ],
        },
    )

    assert web_search_tool.verify_result(result) is False


def test_verify_result_empty_results(web_search_tool):
    """Test verification fails with empty results"""
    from src.tools.base import ToolResult

    result = ToolResult(
        status=ToolStatus.SUCCESS,
        tool_id="web_search",
        data={
            "results": [],  # Empty results
        },
    )

    assert web_search_tool.verify_result(result) is False


def test_verify_result_failed_status(web_search_tool):
    """Test verification fails with failed status"""
    from src.tools.base import ToolResult

    result = ToolResult(
        status=ToolStatus.FAILED,
        tool_id="web_search",
        error="Search failed"
    )

    assert web_search_tool.verify_result(result) is False


# ============================================================================
# Test Helper Functions
# ============================================================================


def test_format_search_results_for_llm():
    """Test formatting search results for LLM"""
    results = [
        {
            "title": "Result 1",
            "url": "https://example.com/1",
            "snippet": "Snippet 1",
        },
        {
            "title": "Result 2",
            "url": "https://example.com/2",
            "snippet": "Snippet 2",
        },
    ]

    formatted = format_search_results_for_llm(results, max_results=2)

    assert "Result 1" in formatted
    assert "Result 2" in formatted
    assert "https://example.com/1" in formatted
    assert "Snippet 1" in formatted


def test_format_search_results_max_limit():
    """Test max_results limit is respected"""
    results = [{"title": f"Result {i}", "url": f"https://example.com/{i}", "snippet": f"Snippet {i}"} for i in range(10)]

    formatted = format_search_results_for_llm(results, max_results=3)

    # Should only have first 3 results
    assert "Result 1" in formatted
    assert "Result 2" in formatted
    assert "Result 3" in formatted
    assert "Result 4" not in formatted
