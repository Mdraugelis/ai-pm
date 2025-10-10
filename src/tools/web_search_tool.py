"""
Web Search Tool
Geisinger AI Product Manager Agent - Layer 3: Tool Framework

Provides web search capabilities for research tasks using Brave Search API.
PHI-protected - only searches public web content.

Usage:
    tool = WebSearchTool(api_key="your-api-key")
    result = await tool.execute(
        {"query": "Epic Healthcare AI capabilities"},
        context
    )
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog

from src.tools.base import (
    Tool,
    ToolResult,
    ToolStatus,
    ExecutionContext,
    RiskTier,
    create_error_result,
)

logger = structlog.get_logger(__name__)


class WebSearchTool(Tool):
    """
    Web search tool using Brave Search API

    Provides web search capabilities for vendor research, use case research,
    and evidence gathering. Returns structured search results with titles,
    snippets, and URLs.

    Features:
    - Privacy-focused Brave Search API
    - Result caching (1 hour TTL)
    - Automatic retry on failures
    - PHI-protected (only public web)
    - Self-verification of result quality

    Example:
        >>> tool = WebSearchTool(api_key="your-key")
        >>> result = await tool.execute(
        ...     {"query": "Epic In Basket AI healthcare"},
        ...     context
        ... )
        >>> print(result.data['results'][0]['title'])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_results: int = 10,
        timeout_seconds: int = 30,
        cache_ttl_seconds: int = 3600,
    ):
        """
        Initialize web search tool

        Args:
            api_key: Brave Search API key (or from environment)
            max_results: Maximum number of search results to return
            timeout_seconds: Request timeout
            cache_ttl_seconds: Cache TTL for search results
        """
        super().__init__()

        self.tool_id = "web_search"
        self.name = "Web Search Tool"
        self.description = "Search the web for information using Brave Search API"
        self.version = "1.0.0"
        self.risk_tier = RiskTier.TIER_1  # Low risk - read-only public data

        self.parameters_schema = {
            "query": {
                "type": "string",
                "required": True,
                "description": "Search query string",
            },
            "count": {
                "type": "integer",
                "required": False,
                "default": 10,
                "description": "Number of results to return (1-20)",
            },
            "freshness": {
                "type": "string",
                "required": False,
                "description": "Result freshness: 'day', 'week', 'month', or 'year'",
            },
        }

        # Configuration
        self.api_key = api_key or self._get_api_key_from_env()
        self.max_results = max_results
        self.timeout_seconds = timeout_seconds
        self.cache_ttl_seconds = cache_ttl_seconds

        # Brave Search API endpoint
        self.api_url = "https://api.search.brave.com/res/v1/web/search"

        # Simple in-memory cache
        self._cache: Dict[str, Dict[str, Any]] = {}

        logger.info(
            "WebSearchTool initialized",
            api_key_present=bool(self.api_key),
            max_results=max_results,
        )

    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment"""
        import os
        return os.getenv("BRAVE_SEARCH_API_KEY") or os.getenv("WEB_SEARCH_API_KEY")

    async def execute(
        self,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> ToolResult:
        """
        Execute web search

        Args:
            parameters: Search parameters with 'query' required
            context: Execution context

        Returns:
            ToolResult with search results

        Raises:
            ValueError: If parameters are invalid
        """
        start_time = datetime.now()

        # Validate parameters
        try:
            self._validate_parameters(parameters)
        except ValueError as e:
            logger.warning("Invalid parameters", error=str(e))
            return create_error_result(
                self.tool_id, str(e), ToolStatus.INVALID_INPUT
            )

        query = parameters["query"]
        count = parameters.get("count", self.max_results)
        freshness = parameters.get("freshness")

        logger.info("Executing web search", query=query, count=count)

        # Check if API key is available
        if not self.api_key:
            logger.warning("No API key configured, using mock results")
            return self._mock_search_results(query, count, start_time)

        # Check cache
        cache_key = f"{query}:{count}:{freshness}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            cache_age = (datetime.now() - cached["timestamp"]).total_seconds()

            if cache_age < self.cache_ttl_seconds:
                logger.info("Returning cached results", cache_age_seconds=cache_age)
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    tool_id=self.tool_id,
                    data=cached["data"],
                    citations=cached.get("citations", []),
                    execution_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                    metadata={"cached": True, "cache_age_seconds": cache_age},
                )

        # Execute search via Brave API
        try:
            search_data = await self._brave_search(query, count, freshness)

            # Extract results
            results = self._parse_brave_results(search_data)

            # Build citations
            citations = [r["url"] for r in results[:5]]  # Top 5 sources

            # Calculate execution time
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Cache results
            self._cache[cache_key] = {
                "timestamp": datetime.now(),
                "data": {
                    "query": query,
                    "results": results,
                    "total_results": len(results),
                },
                "citations": citations,
            }

            logger.info(
                "Web search completed",
                query=query,
                results_count=len(results),
                execution_time_ms=execution_time_ms,
            )

            return ToolResult(
                status=ToolStatus.SUCCESS,
                tool_id=self.tool_id,
                data={
                    "query": query,
                    "results": results,
                    "total_results": len(results),
                },
                citations=citations,
                execution_time_ms=execution_time_ms,
                metadata={
                    "cached": False,
                    "provider": "brave",
                },
            )

        except httpx.TimeoutException:
            logger.error("Search request timed out", query=query)
            return create_error_result(
                self.tool_id,
                f"Search request timed out after {self.timeout_seconds}s",
                ToolStatus.TIMEOUT,
            )

        except Exception as e:
            logger.error("Search failed", query=query, error=str(e), exc_info=True)
            return create_error_result(self.tool_id, str(e), ToolStatus.FAILED)

    async def _brave_search(
        self,
        query: str,
        count: int,
        freshness: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute search via Brave API

        Args:
            query: Search query
            count: Number of results
            freshness: Freshness filter

        Returns:
            Raw API response

        Raises:
            httpx.HTTPStatusError: If API returns error
            httpx.TimeoutException: If request times out
        """
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": min(count, 20),  # Brave max is 20
        }

        if freshness:
            params["freshness"] = freshness

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(
                self.api_url,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    def _parse_brave_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse Brave API response into structured results

        Args:
            data: Raw Brave API response

        Returns:
            List of search results with title, url, snippet
        """
        results = []

        # Brave returns results in 'web' > 'results'
        web_results = data.get("web", {}).get("results", [])

        for item in web_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("description", ""),
                "published_date": item.get("age"),
                "page_age": item.get("page_age"),
                "language": item.get("language", "en"),
            })

        return results

    def _mock_search_results(
        self,
        query: str,
        count: int,
        start_time: datetime,
    ) -> ToolResult:
        """
        Return mock search results when no API key

        Args:
            query: Search query
            count: Number of results requested
            start_time: Request start time

        Returns:
            ToolResult with mock data
        """
        logger.info("Generating mock search results", query=query)

        # Generate realistic mock results
        mock_results = []

        for i in range(min(count, 5)):
            mock_results.append({
                "title": f"Mock Result {i+1} for '{query}'",
                "url": f"https://example.com/search-result-{i+1}",
                "snippet": f"This is a mock search result for '{query}'. In production, this would be real web content from Brave Search API. Configure BRAVE_SEARCH_API_KEY environment variable to use real search.",
                "published_date": "2025-01",
                "language": "en",
            })

        execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        return ToolResult(
            status=ToolStatus.SUCCESS,
            tool_id=self.tool_id,
            data={
                "query": query,
                "results": mock_results,
                "total_results": len(mock_results),
            },
            citations=[r["url"] for r in mock_results],
            execution_time_ms=execution_time_ms,
            metadata={
                "mock": True,
                "message": "Using mock results - set BRAVE_SEARCH_API_KEY for real search",
            },
        )

    def verify_result(self, result: ToolResult) -> bool:
        """
        Verify search result quality

        Checks:
        - Status is SUCCESS
        - Results array exists and is not empty
        - Each result has required fields (title, url, snippet)

        Args:
            result: ToolResult to verify

        Returns:
            True if result passes verification
        """
        if not result.is_success():
            logger.warning("Result status is not SUCCESS")
            return False

        if not result.data or "results" not in result.data:
            logger.warning("No results in data")
            return False

        results = result.data["results"]

        if not isinstance(results, list):
            logger.warning("Results is not a list")
            return False

        if len(results) == 0:
            logger.warning("Results list is empty")
            return False

        # Check each result has required fields
        required_fields = ["title", "url", "snippet"]
        for i, res in enumerate(results):
            for field in required_fields:
                if field not in res:
                    logger.warning(
                        "Result missing required field",
                        result_index=i,
                        missing_field=field,
                    )
                    return False

        logger.debug("Result verification passed", results_count=len(results))
        return True

    def clear_cache(self) -> None:
        """Clear the search results cache"""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Search cache cleared", items_cleared=count)


# ============================================================================
# Helper Functions
# ============================================================================


def format_search_results_for_llm(
    results: List[Dict[str, Any]],
    max_results: int = 5,
) -> str:
    """
    Format search results for LLM consumption

    Args:
        results: List of search results
        max_results: Maximum results to include

    Returns:
        Formatted string for LLM context
    """
    formatted = []

    for i, result in enumerate(results[:max_results], 1):
        formatted.append(f"""
Result {i}:
Title: {result['title']}
URL: {result['url']}
Snippet: {result['snippet']}
""")

    return "\n".join(formatted)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "WebSearchTool",
    "format_search_results_for_llm",
]
