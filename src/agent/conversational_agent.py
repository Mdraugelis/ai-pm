"""
Conversational Agent
Geisinger AI Product Manager Agent - Layer 1: Conversational Interface

Mode-aware conversational agent that dynamically responds to user needs,
leveraging the orchestrator's agent loop and blueprints as knowledge.

This replaces the rigid hardcoded workflow in ProductManagerAgent.

Architecture:
- User messages → ConversationalAgent → Orchestrator (agent loop) → Tools/LLM
- Blueprints loaded as KNOWLEDGE, not hardcoded PROCESS
- Supports multiple modes: Discovery, Risk Assessment, POC Planning, etc.
- Maintains conversation history and context documents
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
import yaml

from src.agent.orchestrator import AgentOrchestrator, Task, AgentResponse
from src.knowledge.blueprint_loader import BlueprintLoader

logger = structlog.get_logger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ConversationTurn:
    """Single turn in conversation"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextDocument:
    """User-uploaded or system-provided context document"""

    content: str
    doc_type: str  # "vendor_doc", "research", "policy", etc.
    doc_category: str = "input"  # "input" or "blueprint_knowledge"
    blueprint_subtype: Optional[str] = None  # For blueprints: policy, guideline, procedure, reference, example
    lifecycle: str = "temporary"  # "temporary" or "persistent"
    added_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Conversational Agent
# ============================================================================


class ConversationalAgent:
    """
    Mode-aware conversational agent

    This agent processes user messages dynamically rather than following
    a hardcoded workflow. It uses the orchestrator's agent loop to
    plan and adapt based on context.

    Modes:
    - ai_discovery: Generate AI Discovery Forms
    - risk_assessment: Analyze AI risks
    - poc_planning: Plan proof of concepts
    - general: General product management questions

    Key Differences from ProductManagerAgent:
    - Conversational (processes messages, not just tickets)
    - Mode-aware (adapts behavior based on mode)
    - Blueprint-driven (uses blueprints as knowledge)
    - Orchestrator-first (leverages agent loop properly)

    Example:
        >>> agent = ConversationalAgent(config)
        >>> await agent.set_mode("ai_discovery")
        >>> response = await agent.process_message(
        ...     "I need a Discovery Form for Epic Inbox AI"
        ... )
        >>> print(response)
    """

    def __init__(
        self,
        config: Dict[str, Any],
        orchestrator: Optional[AgentOrchestrator] = None,
        document_store=None,
        project_id: str = "default",
    ):
        """
        Initialize conversational agent

        Args:
            config: Agent configuration
            orchestrator: Optional orchestrator instance (created if not provided)
            document_store: Optional DocumentStore for loading user-uploaded blueprints
            project_id: Project ID for loading user blueprints
        """
        self.config = config
        self.current_mode: Optional[str] = None
        self.conversation_history: List[ConversationTurn] = []
        self.context_documents: List[ContextDocument] = []
        self.blueprints: Dict[str, Any] = {}
        self.document_store = document_store
        self.project_id = project_id

        # Initialize orchestrator
        if orchestrator:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = AgentOrchestrator(
                config.get("agent", {}),
                blueprint_loader=None,  # Will load directly
                tool_registry=None,
                memory_manager=None,
            )

        # Blueprint directory
        self.blueprints_dir = Path(
            config.get("blueprints", {}).get("directory", "docs/blueprints")
        )

        # Initialize BlueprintLoader with DocumentStore
        self.blueprint_loader = BlueprintLoader(
            blueprints_dir=str(self.blueprints_dir),
            document_store=document_store
        )

        logger.info(
            "ConversationalAgent initialized",
            blueprints_dir=str(self.blueprints_dir),
            has_document_store=document_store is not None,
            project_id=project_id,
        )

    async def set_mode(self, mode: str) -> None:
        """
        Set agent's operating mode

        Args:
            mode: Operating mode
                - "ai_discovery": AI Discovery Form generation
                - "risk_assessment": Risk analysis
                - "poc_planning": POC planning
                - "general": General assistance

        Raises:
            ValueError: If mode is not supported
        """
        supported_modes = self.config.get("agent", {}).get(
            "supported_modes",
            ["ai_discovery", "risk_assessment", "poc_planning", "general"],
        )

        if mode not in supported_modes:
            raise ValueError(
                f"Unsupported mode: {mode}. Supported: {supported_modes}"
            )

        logger.info("Setting agent mode", mode=mode)

        self.current_mode = mode
        await self._load_mode_knowledge(mode)

        logger.info("Mode set successfully", mode=mode, blueprints_loaded=len(self.blueprints))

    async def process_message(self, message: str) -> str:
        """
        Process user message (conversationally, not rigid workflow)

        Args:
            message: User's message (question, request, context)

        Returns:
            Agent's response

        Raises:
            ValueError: If mode not set
            Exception: For processing errors

        Example:
            >>> response = await agent.process_message(
            ...     "Generate Discovery Form for Epic AI"
            ... )
        """
        if not self.current_mode:
            raise ValueError(
                "Mode not set. Call set_mode() before processing messages."
            )

        logger.info(
            "Processing message",
            mode=self.current_mode,
            message_length=len(message),
            conversation_turn=len(self.conversation_history),
        )

        # For general mode, use direct conversational response
        if self.current_mode == "general":
            response_text = await self._generate_conversational_response(message)
        else:
            # For specialized modes (discovery, risk assessment, POC), use orchestrator
            # Build task from message + context
            task = Task(
                description=message,
                domain="product_management",
                metadata={
                    "mode": self.current_mode,
                    "conversation_turn": len(self.conversation_history),
                    "documents_available": len(self.context_documents),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Build context with conversation history, documents, and blueprints
            context = {
                "conversation": [
                    {"role": turn.role, "content": turn.content}
                    for turn in self.conversation_history
                ],
                "mode": self.current_mode,
                "documents": [
                    {"type": doc.doc_type, "content": doc.content}
                    for doc in self.context_documents
                ],
                "blueprints": self.blueprints,  # Blueprints as KNOWLEDGE
            }

            # Let orchestrator handle it (agent loop!)
            result = await self.orchestrator.execute_task_with_context(task, context)

            # Extract response text from result
            response_text = self._extract_response_text(result)

        # Update conversation history
        self.conversation_history.append(
            ConversationTurn(
                role="user",
                content=message,
                metadata={"mode": self.current_mode},
            )
        )

        # Build assistant metadata based on mode
        assistant_metadata = {"mode": self.current_mode}
        if self.current_mode != "general":
            # For specialized modes, include result metadata
            assistant_metadata["status"] = result.status
            assistant_metadata["requires_approval"] = result.requires_approval

        self.conversation_history.append(
            ConversationTurn(
                role="assistant",
                content=response_text,
                metadata=assistant_metadata,
            )
        )

        # Log processing result
        log_metadata = {
            "response_length": len(response_text),
            "mode": self.current_mode,
        }
        if self.current_mode != "general":
            log_metadata["status"] = result.status

        logger.info("Message processed", **log_metadata)

        return response_text

    async def add_document(
        self, document: str, doc_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add context document (vendor docs, research, policy, etc.)

        Args:
            document: Document content
            doc_type: Type of document
                - "vendor_doc": Vendor documentation
                - "research": Research findings
                - "policy": Policy document
                - "ticket": ServiceNow ticket
                - "brief": Intake brief
            metadata: Optional additional metadata
        """
        logger.info("Adding context document", doc_type=doc_type, length=len(document))

        self.context_documents.append(
            ContextDocument(
                content=document,
                doc_type=doc_type,
                metadata=metadata or {},
            )
        )

        logger.info(
            "Document added",
            total_documents=len(self.context_documents),
        )

    async def clear_conversation(self) -> None:
        """Clear conversation history"""
        logger.info(
            "Clearing conversation",
            turns_cleared=len(self.conversation_history),
        )
        self.conversation_history = []

    async def clear_documents(self) -> None:
        """Clear context documents"""
        logger.info(
            "Clearing documents",
            documents_cleared=len(self.context_documents),
        )
        self.context_documents = []

    async def get_conversation_summary(self) -> str:
        """
        Get summary of current conversation

        Returns:
            Formatted conversation summary
        """
        if not self.conversation_history:
            return "No conversation history"

        summary = f"Conversation Summary (Mode: {self.current_mode})\n"
        summary += f"Turns: {len(self.conversation_history)}\n"
        summary += f"Documents: {len(self.context_documents)}\n\n"

        for i, turn in enumerate(self.conversation_history[-5:]):  # Last 5 turns
            summary += f"{turn.role.upper()}: {turn.content[:100]}...\n"

        return summary

    # ========================================================================
    # Internal Methods
    # ========================================================================

    async def _generate_conversational_response(self, message: str) -> str:
        """
        Generate direct conversational response for general mode

        For general mode, we want natural conversational responses
        without the complexity of the plan-execute-verify cycle.

        Args:
            message: User's message

        Returns:
            Natural language response
        """
        # Build conversation context
        messages = []

        # Add conversation history
        for turn in self.conversation_history[-5:]:  # Last 5 turns for context
            messages.append({"role": turn.role, "content": turn.content})

        # Add current message
        messages.append({"role": "user", "content": message})

        # Add blueprints as system context if available
        context = {}
        if self.blueprints:
            context["blueprints"] = self.blueprints

        # Call LLM directly for conversational response
        response = await self.orchestrator.llm.generate_response(messages, context)

        return response

    async def _load_mode_knowledge(self, mode: str) -> None:
        """
        Load blueprints for this mode as KNOWLEDGE (not process)

        Combines YAML blueprints with user-uploaded blueprints.
        User-uploaded blueprints take precedence.

        Args:
            mode: Operating mode
        """
        self.blueprints = {}  # Reset

        if mode == "ai_discovery":
            # Load Discovery workflow as GUIDANCE, not PROCESS
            discovery_workflow = self._load_yaml("discovery-workflow.yaml")
            if discovery_workflow:
                self.blueprints["discovery"] = {
                    "guidance": discovery_workflow.get("steps", []),
                    "success_criteria": discovery_workflow.get(
                        "workflow_success_metrics", {}
                    ),
                    "examples": discovery_workflow.get("example_execution", {}),
                }

            # Load form template
            form_template = self._load_yaml("ai-discovery-form.yaml")
            if form_template:
                self.blueprints["form_template"] = form_template

            # Load product management blueprint
            pm_blueprint = self._load_yaml("product-mgmt-blueprint.yaml")
            if pm_blueprint:
                self.blueprints["domain_knowledge"] = pm_blueprint

        elif mode == "risk_assessment":
            # Load risk-related blueprints
            pm_blueprint = self._load_yaml("product-mgmt-blueprint.yaml")
            if pm_blueprint:
                self.blueprints["domain_knowledge"] = pm_blueprint

        elif mode == "poc_planning":
            # Load POC planning blueprints (when available)
            pm_blueprint = self._load_yaml("product-mgmt-blueprint.yaml")
            if pm_blueprint:
                self.blueprints["domain_knowledge"] = pm_blueprint

        else:  # general mode
            # Load general product management blueprint
            pm_blueprint = self._load_yaml("product-mgmt-blueprint.yaml")
            if pm_blueprint:
                self.blueprints["domain_knowledge"] = pm_blueprint

        # Always load meta-blueprint (universal policies)
        meta_blueprint = self._load_yaml("meta-blueprint.yaml")
        if meta_blueprint:
            self.blueprints["meta"] = meta_blueprint

        # Load user-uploaded blueprints and merge them
        await self._load_user_blueprints()

        logger.info(
            "Mode knowledge loaded",
            mode=mode,
            blueprints=list(self.blueprints.keys()),
        )

    async def _load_user_blueprints(self) -> None:
        """
        Load user-uploaded blueprints and merge with YAML blueprints

        User-uploaded blueprints are added to the blueprints dictionary
        with their subtype as the key. They take precedence over YAML blueprints.
        """
        if not self.blueprint_loader or not self.document_store:
            logger.debug("No DocumentStore available, skipping user blueprints")
            return

        try:
            # Load all user blueprints for this project
            user_blueprints = self.blueprint_loader.load_user_blueprints(self.project_id)

            if not user_blueprints:
                logger.debug("No user-uploaded blueprints found", project_id=self.project_id)
                return

            # Get merged policies and guidelines (user + YAML, user first)
            all_policies = self.blueprint_loader.get_all_policies(self.project_id)
            all_guidelines = self.blueprint_loader.get_all_guidelines(self.project_id)

            # Update domain_knowledge with merged policies and guidelines
            if "domain_knowledge" in self.blueprints:
                self.blueprints["domain_knowledge"]["policies"] = all_policies
                self.blueprints["domain_knowledge"]["guidelines"] = all_guidelines
            else:
                self.blueprints["domain_knowledge"] = {
                    "policies": all_policies,
                    "guidelines": all_guidelines
                }

            # Add user blueprints by subtype for easy reference
            user_blueprints_by_type = {}
            for bp in user_blueprints:
                subtype = bp.get("blueprint_subtype", "unknown")
                if subtype not in user_blueprints_by_type:
                    user_blueprints_by_type[subtype] = []
                user_blueprints_by_type[subtype].append(bp)

            # Store user blueprints separately for reference
            self.blueprints["user_blueprints"] = {
                "by_subtype": user_blueprints_by_type,
                "all": user_blueprints,
                "count": len(user_blueprints)
            }

            logger.info(
                "User blueprints loaded and merged",
                project_id=self.project_id,
                total_user_blueprints=len(user_blueprints),
                subtypes=list(user_blueprints_by_type.keys()),
                total_policies=len(all_policies),
                total_guidelines=len(all_guidelines)
            )

        except Exception as e:
            logger.error(
                "Failed to load user blueprints",
                project_id=self.project_id,
                error=str(e),
                exc_info=True
            )

    def _load_yaml(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load YAML blueprint file

        Args:
            filename: Blueprint filename

        Returns:
            Blueprint data or None if not found
        """
        path = self.blueprints_dir / filename

        if not path.exists():
            logger.warning(f"Blueprint not found: {path}")
            return None

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                logger.debug(f"Loaded blueprint: {filename}")
                return data
        except Exception as e:
            logger.error(f"Failed to load blueprint {filename}", error=str(e))
            return None

    def _extract_response_text(self, result: AgentResponse) -> str:
        """
        Extract response text from AgentResponse

        Args:
            result: Agent response from orchestrator

        Returns:
            Response text to show user
        """
        if result.status == "SUCCESS":
            # Extract meaningful response from result
            if isinstance(result.result, dict):
                # If result contains a specific response field
                if "response" in result.result:
                    return result.result["response"]
                # If result contains generated form
                elif "form" in result.result:
                    return f"I've generated the Discovery Form. {self._format_form_summary(result.result['form'])}"
                # Otherwise format the result
                else:
                    return self._format_result_dict(result.result)
            elif isinstance(result.result, str):
                return result.result
            else:
                return str(result.result)

        elif result.status == "ESCALATED":
            return f"I need human input. {result.verification.get('escalation_reason', 'Unable to complete autonomously.')}"

        elif result.status == "MAX_ITERATIONS":
            return "I've reached my iteration limit. Let me summarize what I've found so far..."

        else:  # FAILED
            return f"I encountered an error: {result.verification.get('error', 'Unknown error')}"

    def _format_form_summary(self, form: Dict[str, Any]) -> str:
        """Format discovery form summary"""
        title = form.get("title", "Untitled")
        sections = form.get("sections", [])

        summary = f"\n\nTitle: {title}\n"
        summary += f"Sections completed: {len(sections)}\n"

        for section in sections[:3]:  # First 3 sections
            section_title = section.get("title", section.get("id", "Unknown"))
            summary += f"  - {section_title}\n"

        if len(sections) > 3:
            summary += f"  ... and {len(sections) - 3} more sections\n"

        return summary

    def _format_result_dict(self, result: Dict[str, Any]) -> str:
        """Format result dictionary as readable text"""
        # Simple formatting for now
        lines = []
        for key, value in result.items():
            if isinstance(value, (list, dict)):
                lines.append(f"{key}: {len(value)} items")
            else:
                lines.append(f"{key}: {value}")

        return "\n".join(lines)


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "ConversationalAgent",
    "ConversationTurn",
    "ContextDocument",
]
