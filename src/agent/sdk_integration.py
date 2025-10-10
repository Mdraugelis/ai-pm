"""
Claude Agent SDK Integration
Geisinger AI Product Manager Agent

This module provides the bridge between Claude Agent SDK (LLM interface)
and Geisinger's enterprise agent orchestration framework.

IMPORTANT: SDK is used ONLY for LLM interface. All orchestration, verification,
and HITL logic remains in Geisinger's framework.

Architecture:
- SDK Layer: LLM calls, tool definitions, message management
- Geisinger Layer: Agent loops, verification, blueprints, HITL

Following patterns from geisinger-sdk-integrator agent guidance.
"""

import os
from typing import Any, Dict, List, Optional

import structlog
from anthropic import Anthropic

logger = structlog.get_logger(__name__)


class SDKIntegration:
    """
    Bridge between Claude Agent SDK and Geisinger orchestration

    This class:
    - Wraps Claude SDK Agent with Geisinger configuration
    - Converts blueprints to system prompts
    - Manages LLM calls for the orchestrator
    - Does NOT handle orchestration, verification, or HITL (that's Geisinger's job)

    Example:
        >>> sdk = SDKIntegration(config, blueprint_loader, tool_registry)
        >>> response = await sdk.generate_plan(task, context)
    """

    def __init__(
        self,
        config: Dict[str, Any],
        blueprint_loader: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
    ):
        """
        Initialize SDK integration

        Args:
            config: Agent configuration dict
            blueprint_loader: Geisinger BlueprintLoader instance (optional)
            tool_registry: Geisinger ToolRegistry instance (optional)
        """
        self.config = config
        self.blueprint_loader = blueprint_loader
        self.tool_registry = tool_registry

        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)

        # Store model and system prompt for LLM calls
        self.model = config.get("model", "claude-sonnet-4-5-20250929")
        self.system_prompt = self._build_system_prompt()

        logger.info(
            "SDK integration initialized",
            model=self.model,
            has_blueprints=blueprint_loader is not None,
            has_tools=tool_registry is not None,
        )

    def _build_system_prompt(self) -> str:
        """
        Build system prompt from Geisinger blueprints

        Converts Geisinger's rich blueprint structure into
        a system prompt for Claude SDK.

        Returns:
            System prompt string with embedded policies
        """
        base_prompt = """You are a Geisinger AI Product Manager Agent.

Your role is to assist Program Owners in navigating the AI program intake
and governance process.

You operate with these core principles:
1. Agency over workflows - Plan dynamically, don't follow rigid scripts
2. Self-verification first - Check your work before human review
3. Explainability always - Every decision must be traceable
4. HITL as conversations - Approvals are collaborative, not just checkboxes

You must:
- Plan actions step-by-step with clear reasoning
- Verify outputs against governance policies
- Cite sources for all data
- Escalate when confidence < 70%
- Request human approval for critical decisions
"""

        # Add blueprint policies if available
        if self.blueprint_loader:
            try:
                meta_blueprint = self.blueprint_loader.load_meta_blueprint()
                base_prompt += f"\n\nCore Governance Policies:\n"

                for policy in meta_blueprint.get("policies", []):
                    base_prompt += f"\n- {policy.get('id')}: {policy.get('rule')}"

            except Exception as e:
                logger.warning(
                    "Failed to load blueprints for system prompt", error=str(e)
                )

        return base_prompt

    async def generate_plan(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use SDK to generate execution plan from task

        Args:
            task: Task description and requirements
            context: Current execution context

        Returns:
            Plan dict with steps and verification criteria

        Note:
            This uses SDK for LLM call only. Plan EXECUTION and VERIFICATION
            happen in Geisinger's orchestrator, not here.
        """
        prompt = self._build_planning_prompt(task, context)

        logger.debug("Generating plan via SDK", task_description=task.get("description"))

        # Use Anthropic SDK for LLM call
        response = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )

        # Extract text content
        response_text = response.content[0].text if response.content else ""

        # Parse response into Geisinger plan format
        plan = self._parse_plan_response(response_text)

        logger.info(
            "Plan generated via SDK",
            step_count=len(plan.get("steps", [])),
            confidence=plan.get("confidence"),
        )

        return plan

    def _build_planning_prompt(
        self, task: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """
        Build planning prompt with task and context

        Args:
            task: Task to plan for
            context: Current execution context

        Returns:
            Formatted prompt for planning
        """
        prompt = f"""Task: {task.get('description')}

Initiative ID: {task.get('initiative_id', 'N/A')}
Current Iteration: {context.get('iteration', 0)}

Please create an execution plan with:
1. Ordered steps to complete the task
2. Tools needed for each step
3. Verification criteria for each step
4. Expected confidence level

Respond in JSON format:
{{
    "steps": [
        {{
            "number": 1,
            "action": "description",
            "tool": "tool_name",
            "verification": "how to verify this step"
        }}
    ],
    "confidence": 0.85,
    "reasoning": "why this plan will work"
}}
"""

        # Add relevant context from memory
        if context.get("previous_attempts"):
            prompt += f"\n\nPrevious attempts:\n{context['previous_attempts']}"

        return prompt

    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """
        Parse SDK response into Geisinger plan format

        Args:
            response: Raw LLM response

        Returns:
            Structured plan dict
        """
        import json

        try:
            # Try to parse as JSON
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # Fallback: Extract structured data from text
            logger.warning("Failed to parse plan as JSON, using fallback")
            return {
                "steps": [
                    {
                        "number": 1,
                        "action": "Process task manually",
                        "tool": "manual_review",
                        "verification": "Human review required",
                    }
                ],
                "confidence": 0.5,
                "reasoning": "Could not parse structured plan",
                "raw_response": response,
            }

    async def generate_response(
        self, messages: List[Dict[str, str]], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate LLM response from messages

        Args:
            messages: List of message dicts with role and content
            context: Optional execution context

        Returns:
            LLM response text

        Note:
            This is a simple LLM call. Any verification or HITL logic
            should be in Geisinger's orchestrator, not here.
        """
        # Convert Geisinger messages to SDK format if needed
        sdk_messages = self._convert_to_sdk_messages(messages)

        logger.debug("Generating response via SDK", message_count=len(sdk_messages))

        # Anthropic SDK call
        response = self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=sdk_messages if sdk_messages else [{"role": "user", "content": "Please provide guidance."}],
            max_tokens=4096,
        )

        # Extract text content
        response_text = response.content[0].text if response.content else ""

        return response_text

    def _convert_to_sdk_messages(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Convert Geisinger message format to SDK format

        Args:
            messages: Geisinger messages

        Returns:
            SDK-compatible messages
        """
        # For now, assume compatible format
        # In future, may need to enrich/transform
        return messages

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names from registry

        Returns:
            List of tool IDs
        """
        if not self.tool_registry:
            return []

        return self.tool_registry.get_tool_ids()


# ============================================================================
# Helper Functions for SDK-Geisinger Bridge
# ============================================================================


def convert_blueprint_to_prompt(blueprint: Dict[str, Any]) -> str:
    """
    Convert Geisinger blueprint to SDK system prompt fragment

    Args:
        blueprint: Geisinger blueprint dict

    Returns:
        System prompt fragment with policies
    """
    prompt = f"\n\nDomain: {blueprint.get('name', 'Unknown')}\n"
    prompt += f"Version: {blueprint.get('version', '1.0')}\n\n"

    # Add policies
    if "policies" in blueprint:
        prompt += "Policies:\n"
        for policy in blueprint["policies"]:
            enforcement = policy.get("enforcement", "SHOULD")
            prompt += f"- [{enforcement}] {policy.get('rule')}\n"

    # Add guidelines
    if "guidelines" in blueprint:
        prompt += "\nGuidelines:\n"
        for guideline in blueprint["guidelines"]:
            prompt += f"- {guideline.get('recommendation')}\n"

    return prompt


def extract_confidence_from_response(response: str) -> float:
    """
    Extract confidence score from LLM response

    Args:
        response: LLM response text

    Returns:
        Confidence score (0.0 to 1.0)
    """
    import re

    # Look for patterns like "confidence: 0.85" or "85% confident"
    patterns = [
        r"confidence[:\s]+([0-9.]+)",
        r"([0-9]+)%\s+confident",
        r"confidence.*?([0-9.]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # Normalize to 0.0-1.0 if needed
            if value > 1.0:
                value = value / 100.0
            return min(max(value, 0.0), 1.0)

    # Default confidence
    return 0.7


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "SDKIntegration",
    "convert_blueprint_to_prompt",
    "extract_confidence_from_response",
]
