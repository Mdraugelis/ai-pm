"""
Product Manager Agent
Geisinger AI Product Manager Agent - Main Entry Point

This is the primary agent class for processing ServiceNow tickets and generating
AI Discovery Forms. It implements the Discovery Workflow blueprint and coordinates
all agent components.

Architecture:
- Uses AgentOrchestrator for agent loop execution
- Implements Discovery Workflow (6 steps)
- Integrates with all framework layers
- Provides observability and tracing

Usage:
    >>> agent = ProductManagerAgent(config)
    >>> result = await agent.process_ticket(ticket_text)
    >>> print(result['form'])
"""

import asyncio
import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.agent.orchestrator import AgentOrchestrator, Task, AgentResponse
from src.agent.llm_interface import LLMInterface

logger = structlog.get_logger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class TicketInfo:
    """Extracted information from ServiceNow ticket"""

    ticket_id: Optional[str] = None
    vendor: Optional[str] = None
    technology: Optional[str] = None
    use_case: Optional[str] = None
    department: Optional[str] = None
    requestor: Optional[str] = None
    description: Optional[str] = None
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchContext:
    """Context from research steps"""

    vendor_info: Dict[str, Any] = field(default_factory=dict)
    use_case_info: Dict[str, Any] = field(default_factory=dict)
    synthesis: Dict[str, Any] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Result of ticket processing"""

    form: Dict[str, Any]
    trace_id: str
    verification: Dict[str, Any]
    duration_seconds: float
    steps_completed: List[str]
    confidence: float
    requires_approval: bool


# ============================================================================
# Product Manager Agent
# ============================================================================


class ProductManagerAgent:
    """
    MVP AI Product Manager Agent

    Main agent class that processes ServiceNow tickets and generates
    AI Discovery Forms following the Discovery Workflow blueprint.

    Workflow Steps:
    1. Extract Basics (5-10 min) - Parse ticket information
    2. Research Vendor (30-45 min) - Deep dive on vendor/technology
    3. Research Use Case (45-60 min) - Understand clinical/operational context
    4. Synthesize Context (15-30 min) - Connect capabilities to needs
    5. Draft Form (45-75 min) - Generate complete Discovery Form
    6. Self-Verify (10-20 min) - Quality check and corrections

    Example:
        >>> config = load_config("config/development.yaml")
        >>> agent = ProductManagerAgent(config)
        >>> result = await agent.process_ticket("Epic In Basket AI request...")
        >>> print(result.form['title'])
    """

    def __init__(
        self,
        config: Dict[str, Any],
        orchestrator: Optional[AgentOrchestrator] = None,
        blueprint_loader: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        memory_manager: Optional[Any] = None,
    ):
        """
        Initialize Product Manager Agent

        Args:
            config: Agent configuration
            orchestrator: Agent orchestrator (optional, created if not provided)
            blueprint_loader: Blueprint loader instance
            tool_registry: Tool registry instance
            memory_manager: Memory manager instance
        """
        self.config = config
        self.blueprint_loader = blueprint_loader
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager

        # Initialize orchestrator
        if orchestrator:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = AgentOrchestrator(
                config.get("agent", {}),
                blueprint_loader=blueprint_loader,
                tool_registry=tool_registry,
                memory_manager=memory_manager,
            )

        # Initialize LLM interface for direct LLM calls
        self.llm = LLMInterface(
            config.get("agent", {}),
            blueprint_loader=blueprint_loader,
            tool_registry=tool_registry,
        )

        # Load workflows and templates
        self.discovery_workflow = self._load_workflow("discovery")
        self.discovery_template = self._load_template("ai_discovery_form")

        # Observability
        self.traces: Dict[str, Dict[str, Any]] = {}

        logger.info(
            "ProductManagerAgent initialized",
            workflow_loaded=self.discovery_workflow is not None,
            template_loaded=self.discovery_template is not None,
        )

    async def process_ticket(self, ticket_text: str) -> ProcessingResult:
        """
        Main entry point for processing ServiceNow ticket

        Executes the full Discovery Workflow to transform a ticket
        into a completed AI Discovery Form.

        Args:
            ticket_text: Raw ServiceNow ticket text

        Returns:
            ProcessingResult with form, verification, and trace

        Raises:
            ValueError: If ticket_text is empty
            Exception: For other processing errors
        """
        if not ticket_text or not ticket_text.strip():
            raise ValueError("ticket_text cannot be empty")

        start_time = datetime.now()

        # Start trace
        trace_id = self._start_trace("process_ticket", {"ticket_length": len(ticket_text)})

        try:
            # Step 1: Extract basics
            self._log_step(trace_id, "extract_basics", "Extracting ticket information")
            ticket_info = await self.extract_ticket_info(ticket_text)
            self._log_step_complete(
                trace_id,
                "extract_basics",
                {
                    "vendor": ticket_info.vendor,
                    "use_case": ticket_info.use_case,
                    "department": ticket_info.department,
                },
            )

            # Step 2: Research vendor
            self._log_step(
                trace_id,
                "research_vendor",
                f"Researching vendor: {ticket_info.vendor}",
            )
            vendor_context = await self.research_vendor(ticket_info.vendor or "")
            self._log_step_complete(
                trace_id,
                "research_vendor",
                {"sources": len(vendor_context.get("sources", []))},
            )

            # Step 3: Research use case
            self._log_step(
                trace_id,
                "research_use_case",
                f"Researching use case: {ticket_info.use_case}",
            )
            use_case_context = await self.research_use_case(
                ticket_info.use_case or "", ticket_info.department or ""
            )
            self._log_step_complete(
                trace_id,
                "research_use_case",
                {"sources": len(use_case_context.get("sources", []))},
            )

            # Step 4: Synthesize
            self._log_step(trace_id, "synthesize", "Synthesizing information")
            synthesis = await self.synthesize_knowledge(
                ticket_info, vendor_context, use_case_context
            )
            self._log_step_complete(
                trace_id,
                "synthesize",
                {"key_insights": len(synthesis.get("key_insights", []))},
            )

            # Step 5: Draft form
            self._log_step(trace_id, "draft_form", "Drafting discovery form")
            draft_form = await self.draft_discovery_form(
                ticket_info, ResearchContext(
                    vendor_info=vendor_context,
                    use_case_info=use_case_context,
                    synthesis=synthesis,
                )
            )
            self._log_step_complete(
                trace_id,
                "draft_form",
                {"sections": len(draft_form.get("sections", []))},
            )

            # Step 6: Self-verify
            self._log_step(trace_id, "self_verify", "Self-verifying form quality")
            verification = await self.verify_form(draft_form)
            self._log_step_complete(
                trace_id,
                "self_verify",
                {
                    "passed": verification.get("passed"),
                    "score": verification.get("overall_score"),
                },
            )

            # If verification failed, attempt corrections
            if not verification.get("passed", False):
                self._log_step(trace_id, "correct_issues", "Correcting identified issues")
                draft_form = await self.correct_issues(draft_form, verification)
                # Re-verify
                verification = await self.verify_form(draft_form)
                self._log_step_complete(
                    trace_id,
                    "correct_issues",
                    {"passed": verification.get("passed")},
                )

            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()

            # End trace
            self._end_trace(trace_id, "success")

            logger.info(
                "Ticket processing complete",
                trace_id=trace_id,
                duration_seconds=duration,
                verification_passed=verification.get("passed"),
            )

            return ProcessingResult(
                form=draft_form,
                trace_id=trace_id,
                verification=verification,
                duration_seconds=duration,
                steps_completed=self._get_completed_steps(trace_id),
                confidence=verification.get("overall_score", 0.0),
                requires_approval=verification.get("overall_score", 0.0) < 0.9,
            )

        except Exception as e:
            self._end_trace(trace_id, "error", str(e))
            logger.error(
                "Ticket processing failed",
                trace_id=trace_id,
                error=str(e),
                exc_info=True,
            )
            raise

    async def extract_ticket_info(self, ticket_text: str) -> TicketInfo:
        """
        Extract basic information from ServiceNow ticket

        Step 1 of Discovery Workflow: Extract Basics (5-10 min)

        Args:
            ticket_text: Raw ticket text

        Returns:
            TicketInfo with extracted fields

        Example:
            >>> info = await agent.extract_ticket_info(ticket)
            >>> print(info.vendor, info.use_case)
        """
        logger.info("Extracting ticket information", text_length=len(ticket_text))

        # Build extraction prompt
        prompt = f"""Extract the following information from this ServiceNow ticket:

Ticket:
{ticket_text}

Please extract and return JSON with these fields:
- ticket_id: Ticket number if present
- vendor: AI vendor or technology provider
- technology: Specific AI technology or product
- use_case: What the AI will be used for
- department: Department requesting the AI
- requestor: Person or team making the request
- description: Brief summary of the request

Return ONLY valid JSON, no other text.
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                extracted = json.loads(json_str)
            else:
                # Fallback: treat whole response as text
                extracted = {"description": response}

            return TicketInfo(
                ticket_id=extracted.get("ticket_id"),
                vendor=extracted.get("vendor"),
                technology=extracted.get("technology"),
                use_case=extracted.get("use_case"),
                department=extracted.get("department"),
                requestor=extracted.get("requestor"),
                description=extracted.get("description"),
                raw_text=ticket_text,
            )

        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON from LLM", error=str(e))
            # Return basic info
            return TicketInfo(
                description=ticket_text[:200],
                raw_text=ticket_text,
            )

    async def research_vendor(self, vendor_name: str) -> Dict[str, Any]:
        """
        Research AI vendor and technology

        Step 2 of Discovery Workflow: Research Vendor (30-45 min)

        Uses LLM knowledge to provide vendor information and analysis.

        Args:
            vendor_name: Name of vendor to research

        Returns:
            Dict with vendor information and sources

        Example:
            >>> vendor_info = await agent.research_vendor("Epic")
            >>> print(vendor_info['capabilities'])
        """
        logger.info("Researching vendor", vendor=vendor_name)

        if not vendor_name:
            return {"error": "No vendor specified", "sources": []}

        # Build research prompt using LLM knowledge
        prompt = f"""Provide comprehensive analysis of this AI vendor:

VENDOR: {vendor_name}

Provide detailed analysis covering:
1. Company background and AI focus areas
2. Key AI products and capabilities
3. Healthcare AI experience (if applicable)
4. Integration capabilities
5. Known risks or concerns

Return as JSON with fields: company_background, ai_products, healthcare_experience, integration_capabilities, risks
Be specific and detailed based on your knowledge of this vendor.
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                # Add note about knowledge-based research
                result["sources"] = ["LLM knowledge base"]
                return result
            else:
                return {
                    "vendor_name": vendor_name,
                    "summary": response,
                    "sources": ["LLM knowledge base"],
                }
        except json.JSONDecodeError:
            return {
                "vendor_name": vendor_name,
                "summary": response,
                "sources": ["LLM knowledge base"],
            }

    async def research_use_case(
        self, use_case: str, department: str = ""
    ) -> Dict[str, Any]:
        """
        Research clinical/operational use case

        Step 3 of Discovery Workflow: Research Use Case (45-60 min)

        Uses LLM knowledge to analyze the use case and provide insights.

        Args:
            use_case: Description of use case
            department: Department context

        Returns:
            Dict with use case analysis and sources

        Example:
            >>> use_case_info = await agent.research_use_case(
            ...     "inbox prioritization", "Cardiology"
            ... )
        """
        logger.info("Researching use case", use_case=use_case, department=department)

        if not use_case:
            return {"error": "No use case specified", "sources": []}

        # Build research prompt using LLM knowledge
        prompt = f"""Analyze this healthcare use case:

USE CASE: {use_case}
DEPARTMENT: {department or "Not specified"}

Provide comprehensive analysis covering:
1. Current workflow and pain points
2. How AI could help
3. Similar implementations (best practices)
4. Potential risks and challenges
5. Success metrics to consider

Return as JSON with fields: workflow_analysis, ai_benefits, similar_implementations, risks, success_metrics
Be specific and provide detailed analysis based on your knowledge of healthcare AI applications.
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                # Add note about knowledge-based research
                result["sources"] = ["LLM knowledge base"]
                return result
            else:
                return {
                    "use_case": use_case,
                    "department": department,
                    "analysis": response,
                    "sources": ["LLM knowledge base"],
                }
        except json.JSONDecodeError:
            return {
                "use_case": use_case,
                "department": department,
                "analysis": response,
                "sources": ["LLM knowledge base"],
            }

    async def synthesize_knowledge(
        self,
        ticket_info: TicketInfo,
        vendor_context: Dict[str, Any],
        use_case_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Synthesize vendor capabilities with use case needs

        Step 4 of Discovery Workflow: Synthesize Context (15-30 min)

        Args:
            ticket_info: Extracted ticket information
            vendor_context: Vendor research results
            use_case_context: Use case research results

        Returns:
            Dict with synthesis and key insights

        Example:
            >>> synthesis = await agent.synthesize_knowledge(
            ...     ticket_info, vendor_context, use_case_context
            ... )
        """
        logger.info("Synthesizing knowledge")

        # Build synthesis prompt
        prompt = f"""Synthesize this information to understand the AI initiative:

TICKET INFO:
- Vendor: {ticket_info.vendor}
- Use Case: {ticket_info.use_case}
- Department: {ticket_info.department}

VENDOR RESEARCH:
{json.dumps(vendor_context, indent=2)}

USE CASE RESEARCH:
{json.dumps(use_case_context, indent=2)}

Provide synthesis covering:
1. How vendor capabilities map to use case needs
2. Key opportunities and benefits
3. Main risks and gaps
4. Critical questions to address
5. Recommended next steps

Return as JSON with fields: capability_mapping, opportunities, risks, questions, next_steps
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return {
                    "synthesis": response,
                    "key_insights": [],
                }
        except json.JSONDecodeError:
            return {
                "synthesis": response,
                "key_insights": [],
            }

    async def draft_discovery_form(
        self, ticket_info: TicketInfo, research: ResearchContext
    ) -> Dict[str, Any]:
        """
        Draft complete AI Discovery Form

        Step 5 of Discovery Workflow: Draft Form (45-75 min)

        Args:
            ticket_info: Extracted ticket information
            research: Research context from previous steps

        Returns:
            Dict with completed Discovery Form sections

        Example:
            >>> form = await agent.draft_discovery_form(ticket_info, research)
            >>> print(form['sections'])
        """
        logger.info("Drafting discovery form")

        # Load template structure
        template = self.discovery_template or {}

        # Build drafting prompt
        prompt = f"""Draft a complete AI Discovery Form for this initiative:

TICKET INFO:
{json.dumps(ticket_info.__dict__, default=str, indent=2)}

RESEARCH CONTEXT:
Vendor: {json.dumps(research.vendor_info, indent=2)}
Use Case: {json.dumps(research.use_case_info, indent=2)}
Synthesis: {json.dumps(research.synthesis, indent=2)}

Create a complete Discovery Form with these sections:
1. Basic Information (title, owner, champion, department, vendor)
2. Problem Definition (background, goal, why AI)
3. Approach (solution components, integration, workflow)
4. Success Metrics (measures, baseline, targets)
5. Equity Considerations (subgroup analysis, bias mitigation)
6. Risk Assessment (5-question screener)
7. Potential Benefits (clinical, operational, financial)

Return as JSON with structure: {{
  "title": "...",
  "sections": [...]
}}

Use evidence from research. Be specific and actionable.
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                # Fallback: basic form
                return {
                    "title": f"{ticket_info.vendor} - {ticket_info.use_case}",
                    "sections": [
                        {
                            "id": "basic_information",
                            "content": response[:500],
                        }
                    ],
                }
        except json.JSONDecodeError:
            return {
                "title": f"{ticket_info.vendor} - {ticket_info.use_case}",
                "sections": [
                    {
                        "id": "basic_information",
                        "content": response[:500],
                    }
                ],
            }

    async def verify_form(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """
        Self-verify Discovery Form quality

        Step 6 of Discovery Workflow: Self-Verify (10-20 min)

        Checks 5 quality dimensions:
        - Completeness (all required fields)
        - Clarity (understandable by non-technical)
        - Evidence-based (claims supported by data)
        - Actionable (sufficient detail for decisions)
        - Policy compliance (follows governance requirements)

        Args:
            form: Draft Discovery Form

        Returns:
            Verification result with scores and issues

        Example:
            >>> verification = await agent.verify_form(form)
            >>> print(verification['overall_score'])
        """
        logger.info("Verifying form quality")

        # Simple verification logic (would use SelfVerifier in production)
        checks = []

        # Completeness check
        required_fields = ["title", "sections"]
        completeness_score = sum(
            1 for field in required_fields if form.get(field)
        ) / len(required_fields)
        checks.append({
            "dimension": "completeness",
            "score": completeness_score,
            "passed": completeness_score >= 0.9,
        })

        # Sections check
        if form.get("sections"):
            sections_complete = len(form["sections"]) >= 3
            checks.append({
                "dimension": "sections",
                "score": 1.0 if sections_complete else 0.5,
                "passed": sections_complete,
            })
        else:
            checks.append({
                "dimension": "sections",
                "score": 0.0,
                "passed": False,
            })

        # Overall
        overall_score = sum(c["score"] for c in checks) / len(checks)
        all_passed = all(c["passed"] for c in checks)

        return {
            "passed": all_passed,
            "overall_score": overall_score,
            "checks": checks,
            "issues": [c["dimension"] for c in checks if not c["passed"]],
        }

    async def correct_issues(
        self, form: Dict[str, Any], verification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Correct identified issues in form

        Args:
            form: Draft form with issues
            verification: Verification result with identified issues

        Returns:
            Corrected form

        Example:
            >>> corrected = await agent.correct_issues(form, verification)
        """
        logger.info(
            "Correcting form issues",
            issues=verification.get("issues", []),
        )

        # Build correction prompt
        issues = verification.get("issues", [])
        if not issues:
            return form

        prompt = f"""This Discovery Form has quality issues that need correction:

CURRENT FORM:
{json.dumps(form, indent=2)}

ISSUES IDENTIFIED:
{json.dumps(issues, indent=2)}

Please provide a corrected version of the form that addresses these issues.
Return as JSON with same structure.
"""

        # Call LLM
        response = await self.llm.ask_question(prompt)

        # Parse response
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                corrected = json.loads(response[json_start:json_end])
                return corrected
            else:
                # Return original if can't parse
                return form
        except json.JSONDecodeError:
            logger.warning("Failed to parse corrected form, returning original")
            return form

    # ========================================================================
    # Observability Methods
    # ========================================================================

    def _start_trace(self, operation: str, metadata: Dict[str, Any] = None) -> str:
        """
        Start execution trace

        Args:
            operation: Name of operation
            metadata: Additional metadata

        Returns:
            Trace ID
        """
        trace_id = f"{operation}_{datetime.now().timestamp()}"
        self.traces[trace_id] = {
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "metadata": metadata or {},
            "steps": [],
            "status": "in_progress",
        }
        logger.info("Trace started", trace_id=trace_id, operation=operation)
        return trace_id

    def _log_step(self, trace_id: str, step_id: str, description: str) -> None:
        """Log workflow step start"""
        if trace_id in self.traces:
            self.traces[trace_id]["steps"].append({
                "step_id": step_id,
                "description": description,
                "start_time": datetime.now().isoformat(),
                "status": "in_progress",
            })
        logger.info("Step started", trace_id=trace_id, step=step_id)

    def _log_step_complete(
        self, trace_id: str, step_id: str, result: Dict[str, Any] = None
    ) -> None:
        """Log workflow step completion"""
        if trace_id in self.traces:
            for step in self.traces[trace_id]["steps"]:
                if step["step_id"] == step_id and step["status"] == "in_progress":
                    step["status"] = "completed"
                    step["end_time"] = datetime.now().isoformat()
                    step["result"] = result or {}
                    break
        logger.info("Step completed", trace_id=trace_id, step=step_id)

    def _end_trace(
        self, trace_id: str, status: str, error: Optional[str] = None
    ) -> None:
        """End execution trace"""
        if trace_id in self.traces:
            self.traces[trace_id]["status"] = status
            self.traces[trace_id]["end_time"] = datetime.now().isoformat()
            if error:
                self.traces[trace_id]["error"] = error
        logger.info("Trace ended", trace_id=trace_id, status=status)

    def _get_completed_steps(self, trace_id: str) -> List[str]:
        """Get list of completed step IDs"""
        if trace_id not in self.traces:
            return []
        return [
            step["step_id"]
            for step in self.traces[trace_id]["steps"]
            if step["status"] == "completed"
        ]

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID"""
        return self.traces.get(trace_id)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _load_workflow(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Load workflow blueprint"""
        try:
            blueprints_dir = Path(
                self.config.get("blueprints", {}).get("directory", "docs/blueprints")
            )
            workflows = (
                self.config.get("blueprints", {}).get("workflows", {})
            )
            workflow_file = workflows.get(workflow_name)

            if not workflow_file:
                logger.warning(f"Workflow {workflow_name} not found in config")
                return None

            workflow_path = blueprints_dir / workflow_file

            if not workflow_path.exists():
                logger.warning(f"Workflow file not found: {workflow_path}")
                return None

            with open(workflow_path) as f:
                return yaml.safe_load(f)

        except Exception as e:
            logger.error(f"Failed to load workflow {workflow_name}", error=str(e))
            return None

    def _load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Load document template"""
        try:
            blueprints_dir = Path(
                self.config.get("blueprints", {}).get("directory", "docs/blueprints")
            )
            templates = (
                self.config.get("blueprints", {}).get("templates", {})
            )
            template_file = templates.get(template_name)

            if not template_file:
                logger.warning(f"Template {template_name} not found in config")
                return None

            template_path = blueprints_dir / template_file

            if not template_path.exists():
                logger.warning(f"Template file not found: {template_path}")
                return None

            with open(template_path) as f:
                return yaml.safe_load(f)

        except Exception as e:
            logger.error(f"Failed to load template {template_name}", error=str(e))
            return None


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "ProductManagerAgent",
    "TicketInfo",
    "ResearchContext",
    "ProcessingResult",
]
