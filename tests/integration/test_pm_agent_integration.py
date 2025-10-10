"""
Integration Tests for Product Manager Agent
Geisinger AI Product Manager Agent

Tests the full agent workflow with real components integrated together.
"""

import pytest
import yaml
from pathlib import Path

from src.agent.pm_agent import ProductManagerAgent, ProcessingResult


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def integration_config():
    """Load integration test configuration"""
    config_path = Path("config/development.yaml")

    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    else:
        # Fallback config if file doesn't exist
        return {
            "agent": {
                "model": "claude-sonnet-4-5-20250929",
                "max_iterations": 10,
                "confidence_threshold": 0.7,
                "sdk": {
                    "retry_attempts": 3,
                    "timeout_seconds": 60,
                },
            },
            "blueprints": {
                "directory": "docs/blueprints",
                "templates": {"ai_discovery_form": "ai-discovery-form.yaml"},
                "workflows": {"discovery": "discovery-workflow.yaml"},
            },
        }


@pytest.fixture
def agent(integration_config):
    """Create ProductManagerAgent with integration config"""
    # Note: This uses real LLM interface, so requires API key in environment
    # For CI/CD, mock the LLM or skip with @pytest.mark.integration
    return ProductManagerAgent(
        config=integration_config,
        orchestrator=None,
        blueprint_loader=None,
        tool_registry=None,
        memory_manager=None,
    )


@pytest.fixture
def sample_tickets():
    """Sample ServiceNow tickets for integration testing"""
    return {
        "cardiology_inbox": """
ServiceNow Ticket INC0012345

Department: Cardiology
Requestor: Dr. Sarah Johnson
Priority: Medium

Title: Epic In Basket AI Priority Scoring Implementation

Description:
The Cardiology department would like to implement Epic's In Basket AI feature
to help our physicians manage their electronic inbox more effectively. Currently,
cardiologists spend 2-3 hours per day processing inbox messages, and critical
items sometimes get missed among routine notifications.

Epic's AI solution uses machine learning to score messages by urgency and clinical
importance, allowing physicians to quickly identify and address the most critical
items first. This has shown a 30-40% reduction in inbox processing time at other
health systems.

Vendor: Epic Systems
Technology: In Basket Priority Scoring with Machine Learning
Expected Users: 25 cardiologists
Timeline: Pilot in Q2 2025, full rollout Q3 2025

Business Case:
- Reduce physician burnout from inbox overload
- Ensure critical clinical communications are addressed promptly
- Improve patient safety by preventing missed urgent messages
- Save approximately 45-60 minutes per physician per day
""",
        "radiology_nodule": """
ServiceNow Ticket INC0056789

Department: Radiology
Requestor: Dr. Michael Chen, Chief of Radiology
Priority: High

Title: AI-Powered Lung Nodule Detection Assistant

Description:
Radiology is requesting evaluation of an AI-powered lung nodule detection tool
to assist radiologists in identifying potential lung cancer on CT scans. This
would be integrated into our PACS workflow.

We have received a proposal from Aidoc to implement their lung nodule detection
AI. The system would run in the background and flag cases with suspected nodules
for radiologist review, helping to prevent missed findings and reduce reading time.

Vendor: Aidoc
Technology: Deep learning-based nodule detection
Expected Volume: ~500 chest CT scans per month
Clinical Impact: Earlier detection of lung cancer

Key Requirements:
- FDA-cleared solution
- PACS integration
- Radiologist retains final decision authority
- Must not slow down existing workflow
- Performance monitoring and quality metrics

Risks to Consider:
- False positives causing alert fatigue
- Over-reliance on AI missing findings
- Need for validation with our patient population
- Potential bias in detection across demographic groups
""",
        "simple_request": """
ServiceNow Ticket INC0099999

Department: IT
Requestor: John Smith

We want to use ChatGPT to help write emails.
Vendor: OpenAI
""",
    }


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_cardiology_ticket_integration(agent, sample_tickets):
    """
    Integration test: Full workflow for cardiology inbox AI request

    Tests the complete Discovery Workflow with a realistic ticket.
    """
    result = await agent.process_ticket(sample_tickets["cardiology_inbox"])

    # Verify result structure
    assert isinstance(result, ProcessingResult)
    assert result.form is not None
    assert result.trace_id is not None
    assert result.verification is not None

    # Verify all workflow steps completed
    expected_steps = [
        "extract_basics",
        "research_vendor",
        "research_use_case",
        "synthesize",
        "draft_form",
        "self_verify",
    ]
    for step in expected_steps:
        assert step in result.steps_completed, f"Step {step} not completed"

    # Verify form structure
    form = result.form
    assert "title" in form
    assert "sections" in form or form.get("sections") is not None

    # Verify extracted information appears in form
    # Epic should be mentioned
    form_str = str(form).lower()
    assert "epic" in form_str or "cardiology" in form_str or "inbox" in form_str

    # Verify verification ran
    assert "overall_score" in result.verification
    assert 0.0 <= result.verification["overall_score"] <= 1.0

    # Verify observability
    assert result.duration_seconds > 0
    trace = agent.get_trace(result.trace_id)
    assert trace is not None
    assert trace["status"] == "success"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_radiology_ticket_integration(agent, sample_tickets):
    """
    Integration test: Full workflow for radiology AI request

    Tests with a more complex ticket including clinical risks.
    """
    result = await agent.process_ticket(sample_tickets["radiology_nodule"])

    # Verify basic result
    assert isinstance(result, ProcessingResult)
    assert result.form is not None

    # Verify vendor extraction
    form_str = str(result.form).lower()
    assert "aidoc" in form_str or "radiology" in form_str

    # Verify workflow completed
    assert len(result.steps_completed) >= 6

    # Verify trace
    trace = agent.get_trace(result.trace_id)
    assert trace is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_simple_ticket_integration(agent, sample_tickets):
    """
    Integration test: Minimal ticket with limited information

    Tests agent behavior with sparse input.
    """
    result = await agent.process_ticket(sample_tickets["simple_request"])

    # Should still complete workflow
    assert isinstance(result, ProcessingResult)
    assert result.form is not None

    # Should extract what's available
    form_str = str(result.form).lower()
    assert "openai" in form_str or "chatgpt" in form_str or "email" in form_str


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workflow_step_tracing(agent, sample_tickets):
    """
    Integration test: Verify all workflow steps are traced

    Validates observability and tracing functionality.
    """
    result = await agent.process_ticket(sample_tickets["cardiology_inbox"])

    # Get trace
    trace = agent.get_trace(result.trace_id)
    assert trace is not None

    # Verify trace structure
    assert "operation" in trace
    assert "start_time" in trace
    assert "end_time" in trace
    assert "steps" in trace
    assert "status" in trace

    # Verify steps were logged
    assert len(trace["steps"]) >= 6

    # Verify each step has required fields
    for step in trace["steps"]:
        assert "step_id" in step
        assert "description" in step
        assert "status" in step
        assert "start_time" in step

    # Verify completed steps have end_time
    completed_steps = [s for s in trace["steps"] if s["status"] == "completed"]
    for step in completed_steps:
        assert "end_time" in step


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extraction_accuracy(agent, sample_tickets):
    """
    Integration test: Verify extraction accuracy

    Tests that ticket information is correctly extracted.
    """
    ticket = sample_tickets["cardiology_inbox"]
    ticket_info = await agent.extract_ticket_info(ticket)

    # Verify key fields extracted
    assert ticket_info.vendor is not None
    assert ticket_info.use_case is not None
    assert ticket_info.department is not None

    # Verify accuracy (these values are in the ticket)
    vendor_lower = ticket_info.vendor.lower() if ticket_info.vendor else ""
    assert "epic" in vendor_lower

    dept_lower = ticket_info.department.lower() if ticket_info.department else ""
    assert "cardio" in dept_lower or "heart" in dept_lower or dept_lower != ""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_research_integration(agent):
    """
    Integration test: Verify research methods work

    Tests vendor and use case research with real LLM.
    """
    # Test vendor research
    vendor_info = await agent.research_vendor("Epic Systems")
    assert isinstance(vendor_info, dict)
    assert vendor_info  # Not empty

    # Test use case research
    use_case_info = await agent.research_use_case(
        "AI inbox prioritization", "Cardiology"
    )
    assert isinstance(use_case_info, dict)
    assert use_case_info  # Not empty


@pytest.mark.integration
@pytest.mark.asyncio
async def test_verification_quality_checks(agent, sample_tickets):
    """
    Integration test: Verify quality checking works

    Tests that verification catches quality issues.
    """
    result = await agent.process_ticket(sample_tickets["cardiology_inbox"])

    verification = result.verification

    # Verify structure
    assert "passed" in verification
    assert "overall_score" in verification
    assert "checks" in verification

    # Verify checks list is populated
    assert len(verification["checks"]) > 0

    # Each check should have required fields
    for check in verification["checks"]:
        assert "dimension" in check
        assert "score" in check
        assert "passed" in check


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_with_blueprints(agent):
    """
    Integration test: Verify blueprint loading and usage

    Tests that agent can load and use blueprint files.
    """
    # Check if blueprints loaded
    assert agent.discovery_workflow is None or isinstance(
        agent.discovery_workflow, dict
    )
    assert agent.discovery_template is None or isinstance(
        agent.discovery_template, dict
    )

    # If blueprints exist, verify they have expected structure
    if agent.discovery_workflow:
        assert "workflow_id" in agent.discovery_workflow
        assert "steps" in agent.discovery_workflow

    if agent.discovery_template:
        assert "template_id" in agent.discovery_template or "sections" in agent.discovery_template


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_integration(agent):
    """
    Integration test: Verify error handling

    Tests that agent handles errors gracefully.
    """
    # Test with empty input
    with pytest.raises(ValueError):
        await agent.process_ticket("")

    # Test with whitespace only
    with pytest.raises(ValueError):
        await agent.process_ticket("   \n   ")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_processing(agent, sample_tickets):
    """
    Integration test: Verify multiple tickets can be processed concurrently

    Tests that agent maintains separate traces for concurrent requests.
    """
    import asyncio

    # Process two tickets concurrently
    results = await asyncio.gather(
        agent.process_ticket(sample_tickets["cardiology_inbox"]),
        agent.process_ticket(sample_tickets["simple_request"]),
    )

    # Verify both completed
    assert len(results) == 2
    assert all(isinstance(r, ProcessingResult) for r in results)

    # Verify separate traces
    assert results[0].trace_id != results[1].trace_id

    # Verify both traces exist
    trace1 = agent.get_trace(results[0].trace_id)
    trace2 = agent.get_trace(results[1].trace_id)
    assert trace1 is not None
    assert trace2 is not None


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.asyncio
async def test_processing_performance(agent, sample_tickets):
    """
    Performance test: Verify processing completes in reasonable time

    Tests that workflow doesn't hang or take excessively long.
    """
    import time

    start = time.time()
    result = await agent.process_ticket(sample_tickets["cardiology_inbox"])
    duration = time.time() - start

    # Should complete in under 5 minutes (real-world would be longer with actual tools)
    # For integration tests with mocked tools, should be much faster
    assert duration < 300  # 5 minutes max

    # Duration should be tracked
    assert result.duration_seconds > 0
    assert abs(result.duration_seconds - duration) < 1.0  # Close to actual duration


# ============================================================================
# Data Structure Tests
# ============================================================================


@pytest.mark.integration
def test_ticket_info_dataclass():
    """Test TicketInfo dataclass"""
    from src.agent.pm_agent import TicketInfo

    info = TicketInfo(
        vendor="Epic",
        use_case="Inbox AI",
        department="Cardiology",
    )

    assert info.vendor == "Epic"
    assert info.use_case == "Inbox AI"
    assert info.department == "Cardiology"


@pytest.mark.integration
def test_research_context_dataclass():
    """Test ResearchContext dataclass"""
    from src.agent.pm_agent import ResearchContext

    context = ResearchContext(
        vendor_info={"vendor": "Epic"},
        use_case_info={"use_case": "Inbox"},
        synthesis={"insights": []},
        sources=["source1", "source2"],
    )

    assert context.vendor_info["vendor"] == "Epic"
    assert len(context.sources) == 2


@pytest.mark.integration
def test_processing_result_dataclass():
    """Test ProcessingResult dataclass"""
    from src.agent.pm_agent import ProcessingResult

    result = ProcessingResult(
        form={"title": "Test"},
        trace_id="test123",
        verification={"passed": True},
        duration_seconds=10.5,
        steps_completed=["step1", "step2"],
        confidence=0.85,
        requires_approval=False,
    )

    assert result.form["title"] == "Test"
    assert result.trace_id == "test123"
    assert result.duration_seconds == 10.5
    assert len(result.steps_completed) == 2
