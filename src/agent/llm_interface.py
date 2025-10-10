"""
LLM Interface Layer
Geisinger AI Product Manager Agent

Clean interface for LLM interactions that handles message formatting,
streaming, retries, and error handling.

This is the PRIMARY interface between Geisinger's orchestrator and the Claude SDK.
All LLM calls should go through this layer.

Architecture:
- Geisinger Context (rich) → This Layer → SDK Messages (simple) → LLM
- LLM Response → This Layer → Geisinger Format → Orchestrator
"""

import asyncio
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

import structlog

from src.agent.sdk_integration import SDKIntegration

logger = structlog.get_logger(__name__)


class LLMInterface:
    """
    Clean interface for LLM interactions

    Responsibilities:
    - Convert Geisinger context to SDK messages
    - Handle streaming vs single-turn responses
    - Implement retry logic and timeout handling
    - Parse LLM responses into structured formats
    - Track token usage and latency

    Does NOT handle:
    - Agent loops (orchestrator's job)
    - Verification (self_verifier's job)
    - HITL (governance layer's job)
    - Memory management (working_memory's job)

    Example:
        >>> llm = LLMInterface(config, blueprint_loader, tool_registry)
        >>> response = await llm.generate_plan(task, context)
        >>> result = await llm.ask_question("What is the risk level?", context)
    """

    def __init__(
        self,
        config: Dict[str, Any],
        blueprint_loader: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
    ):
        """
        Initialize LLM interface

        Args:
            config: Agent configuration
            blueprint_loader: Blueprint loader instance
            tool_registry: Tool registry instance
        """
        self.config = config
        self.sdk = SDKIntegration(config, blueprint_loader, tool_registry)
        self.retry_attempts = config.get("retry_attempts", 3)
        self.timeout_seconds = config.get("timeout_seconds", 60)

        logger.info("LLM interface initialized", retry_attempts=self.retry_attempts)

    async def generate_plan(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate execution plan for task

        Args:
            task: Task to plan for
            context: Execution context with memory and blueprints

        Returns:
            Plan dict with steps, tools, and verification criteria

        Raises:
            TimeoutError: If LLM call exceeds timeout
            Exception: For other LLM errors
        """
        start_time = datetime.now()

        logger.info(
            "Generating plan",
            task_description=task.get("description"),
            iteration=context.get("iteration", 0),
        )

        try:
            # Call SDK with retry logic
            plan = await self._retry_with_timeout(
                self.sdk.generate_plan(task, context)
            )

            # Calculate latency
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000

            logger.info("Plan generated", latency_ms=latency_ms, steps=len(plan.get("steps", [])))

            return plan

        except Exception as e:
            logger.error("Plan generation failed", error=str(e), exc_info=True)
            raise

    async def ask_question(
        self, question: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ask a question to the LLM

        Args:
            question: Question to ask
            context: Optional execution context

        Returns:
            LLM response text
        """
        messages = [{"role": "user", "content": question}]

        # Add context if available
        if context and context.get("conversation"):
            messages = context["conversation"] + messages

        logger.debug("Asking LLM question", question=question[:100])

        response = await self._retry_with_timeout(
            self.sdk.generate_response(messages, context)
        )

        return response

    async def generate_with_tools(
        self,
        prompt: str,
        available_tools: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response with tool use

        Args:
            prompt: User prompt
            available_tools: List of tool IDs available
            context: Optional execution context

        Returns:
            Dict with response and any tool calls
        """
        logger.info("Generating with tools", tool_count=len(available_tools))

        # For now, simple implementation
        # In future, SDK will handle tool calling directly
        response = await self.ask_question(
            f"{prompt}\n\nAvailable tools: {', '.join(available_tools)}", context
        )

        return {"response": response, "tool_calls": []}

    async def stream_response(
        self, prompt: str, context: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """
        Stream LLM response (for UI feedback)

        Args:
            prompt: User prompt
            context: Optional execution context

        Yields:
            Chunks of response text
        """
        # Placeholder for streaming implementation
        # SDK Agent supports streaming, will implement fully later
        logger.info("Streaming response (placeholder)")

        # For now, return single chunk
        response = await self.ask_question(prompt, context)
        yield response

    def to_sdk_messages(
        self, geisinger_context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Convert Geisinger's rich context to SDK message format

        Args:
            geisinger_context: Geisinger execution context with:
                - conversation: List of turns
                - task_state: Current task state
                - tool_results: Recent tool results
                - memory: Working memory

        Returns:
            List of SDK messages (role + content)
        """
        messages = []

        # Add conversation history
        if "conversation" in geisinger_context:
            for turn in geisinger_context["conversation"]:
                messages.append(
                    {"role": turn.get("role", "user"), "content": turn.get("content", "")}
                )

        # Add recent tool results as context (if relevant)
        if "tool_results" in geisinger_context:
            tool_context = "\n\nRecent tool results:\n"
            for tool_result in geisinger_context["tool_results"][-3:]:  # Last 3
                tool_context += f"- {tool_result.get('tool_id')}: {tool_result.get('summary', '')}\n"

            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] += tool_context

        return messages

    async def _retry_with_timeout(self, coro: Any) -> Any:
        """
        Execute coroutine with retry and timeout

        Args:
            coro: Coroutine to execute

        Returns:
            Result from coroutine

        Raises:
            TimeoutError: If exceeds timeout
            Exception: After max retries
        """
        for attempt in range(self.retry_attempts):
            try:
                result = await asyncio.wait_for(coro, timeout=self.timeout_seconds)
                return result

            except asyncio.TimeoutError:
                if attempt == self.retry_attempts - 1:
                    logger.error("LLM call timeout after retries", attempts=self.retry_attempts)
                    raise TimeoutError(f"LLM call exceeded {self.timeout_seconds}s timeout")

                logger.warning("LLM call timeout, retrying", attempt=attempt + 1)
                await asyncio.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                if attempt == self.retry_attempts - 1:
                    raise

                logger.warning("LLM call error, retrying", attempt=attempt + 1, error=str(e))
                await asyncio.sleep(2**attempt)


# ============================================================================
# Context Conversion Utilities
# ============================================================================


def build_context_summary(context: Dict[str, Any]) -> str:
    """
    Build a summary of execution context for LLM

    Args:
        context: Geisinger execution context

    Returns:
        Formatted context summary
    """
    summary = "Current Context:\n"

    if "task_description" in context:
        summary += f"Task: {context['task_description']}\n"

    if "iteration" in context:
        summary += f"Iteration: {context['iteration']}\n"

    if "previous_attempts" in context:
        summary += f"Previous attempts: {len(context['previous_attempts'])}\n"

    if "tool_results" in context:
        summary += f"Tool results available: {len(context['tool_results'])}\n"

    return summary


def extract_structured_data(response: str, expected_fields: List[str]) -> Dict[str, Any]:
    """
    Extract structured data from LLM response

    Args:
        response: LLM response text
        expected_fields: Fields to extract

    Returns:
        Dict with extracted fields
    """
    import json
    import re

    # Try JSON first
    try:
        data = json.loads(response)
        return {field: data.get(field) for field in expected_fields}
    except json.JSONDecodeError:
        pass

    # Fallback: Extract with regex
    extracted = {}
    for field in expected_fields:
        pattern = rf"{field}[:\s]+([^\n]+)"
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            extracted[field] = match.group(1).strip()

    return extracted


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "LLMInterface",
    "build_context_summary",
    "extract_structured_data",
]
