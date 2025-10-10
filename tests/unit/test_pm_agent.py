"""
Unit Tests for Product Manager Agent
Geisinger AI Product Manager Agent

Tests the ProductManagerAgent class methods and workflow execution.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent.pm_agent import (
    ProductManagerAgent,
    TicketInfo,
    ResearchContext,
    ProcessingResult,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_config():
    """Mock agent configuration"""
    return {
        "agent": {
            "model": "claude-sonnet-4-5-20250929",
            "max_iterations": 10,
            "confidence_threshold": 0.7,
        },
        "blueprints": {
            "directory": "docs/blueprints",
            "templates": {"ai_discovery_form": "ai-discovery-form.yaml"},
            "workflows": {"discovery": "discovery-workflow.yaml"},
        },
    }


@pytest.fixture
def mock_llm():
    """Mock LLM interface"""
    llm = AsyncMock()
    return llm


@pytest.fixture
def agent(mock_config, mock_llm):
    """Create ProductManagerAgent instance with mocked dependencies"""
    with patch("src.agent.pm_agent.LLMInterface") as MockLLM:
        MockLLM.return_value = mock_llm
        agent = ProductManagerAgent(
            config=mock_config,
            orchestrator=None,  # Will be mocked
            blueprint_loader=None,
            tool_registry=None,
            memory_manager=None,
        )
        agent.llm = mock_llm  # Inject our mock
        return agent


@pytest.fixture
def sample_ticket():
    """Sample ServiceNow ticket text"""
    return """
ServiceNow Ticket INC0012345

Department: Cardiology
Requestor: Dr. Sarah Johnson
Title: Epic In Basket AI Priority Scoring

Description:
We would like to implement Epic's In Basket AI feature to help cardiologists
prioritize their inbox messages. The AI would score messages by urgency and
clinical importance, allowing physicians to address critical items first.

Vendor: Epic Systems
Technology: In Basket Priority Scoring with ML
Expected Impact: Reduce inbox processing time by 30%
"""


@pytest.fixture
def sample_ticket_info():
    """Sample extracted ticket information"""
    return TicketInfo(
        ticket_id="INC0012345",
        vendor="Epic Systems",
        technology="In Basket Priority Scoring with ML",
        use_case="Inbox message prioritization",
        department="Cardiology",
        requestor="Dr. Sarah Johnson",
        description="AI-powered inbox prioritization for cardiologists",
        raw_text="...",
    )


@pytest.fixture
def sample_vendor_context():
    """Sample vendor research context"""
    return {
        "vendor_name": "Epic Systems",
        "company_background": "Leading EHR vendor",
        "ai_products": ["In Basket Priority Scoring", "Sepsis Prediction"],
        "healthcare_experience": "Extensive healthcare AI deployment",
        "integration_capabilities": "Native EHR integration",
        "risks": ["Vendor lock-in", "Limited customization"],
        "sources": ["Epic website", "KLAS Research"],
    }


@pytest.fixture
def sample_use_case_context():
    """Sample use case research context"""
    return {
        "use_case": "Inbox message prioritization",
        "department": "Cardiology",
        "workflow_analysis": "Physicians spend 2+ hours daily on inbox",
        "ai_benefits": "Prioritize critical messages, reduce burnout",
        "similar_implementations": "Stanford Medicine successful pilot",
        "risks": ["Alert fatigue", "Over-reliance on AI"],
        "success_metrics": [
            "Time to critical message",
            "Inbox processing time",
            "Physician satisfaction",
        ],
        "sources": ["JAMA study", "Stanford case study"],
    }


@pytest.fixture
def sample_form():
    """Sample Discovery Form"""
    return {
        "title": "Epic In Basket AI - Cardiology Inbox Prioritization",
        "sections": [
            {
                "id": "basic_information",
                "title": "Basic Information",
                "fields": {
                    "program_owner": "Dr. Sarah Johnson",
                    "department": "Cardiology",
                    "vendor": "Epic Systems",
                },
            },
            {
                "id": "problem_definition",
                "title": "Problem Definition",
                "fields": {
                    "background": "Cardiologists spend 2+ hours daily on inbox",
                    "goal": "Reduce inbox time by prioritizing critical messages",
                },
            },
            {
                "id": "approach",
                "title": "Approach",
                "fields": {
                    "solution": "Epic In Basket AI Priority Scoring",
                },
            },
        ],
    }


# ============================================================================
# Test Extract Ticket Info
# ============================================================================


@pytest.mark.asyncio
async def test_extract_ticket_info_success(agent, mock_llm, sample_ticket):
    """Test successful ticket information extraction"""
    # Mock LLM response
    mock_llm.ask_question.return_value = json.dumps({
        "ticket_id": "INC0012345",
        "vendor": "Epic Systems",
        "technology": "In Basket Priority Scoring with ML",
        "use_case": "Inbox message prioritization",
        "department": "Cardiology",
        "requestor": "Dr. Sarah Johnson",
        "description": "AI-powered inbox prioritization",
    })

    result = await agent.extract_ticket_info(sample_ticket)

    # Verify
    assert isinstance(result, TicketInfo)
    assert result.ticket_id == "INC0012345"
    assert result.vendor == "Epic Systems"
    assert result.use_case == "Inbox message prioritization"
    assert result.department == "Cardiology"
    assert result.raw_text == sample_ticket

    # Verify LLM was called
    mock_llm.ask_question.assert_called_once()


@pytest.mark.asyncio
async def test_extract_ticket_info_invalid_json(agent, mock_llm, sample_ticket):
    """Test extraction with invalid JSON response"""
    # Mock LLM returns non-JSON
    mock_llm.ask_question.return_value = "This is not JSON at all"

    result = await agent.extract_ticket_info(sample_ticket)

    # Should return basic info without crashing
    assert isinstance(result, TicketInfo)
    assert result.raw_text == sample_ticket
    assert result.description is not None


@pytest.mark.asyncio
async def test_extract_ticket_info_partial_json(agent, mock_llm, sample_ticket):
    """Test extraction with partial JSON in text"""
    # Mock LLM returns JSON embedded in text
    mock_llm.ask_question.return_value = """
    Here's the extracted information:
    {"vendor": "Epic", "use_case": "Inbox prioritization"}
    That's what I found.
    """

    result = await agent.extract_ticket_info(sample_ticket)

    # Should extract the JSON
    assert isinstance(result, TicketInfo)
    assert result.vendor == "Epic"
    assert result.use_case == "Inbox prioritization"


# ============================================================================
# Test Research Methods
# ============================================================================


@pytest.mark.asyncio
async def test_research_vendor_success(agent, mock_llm):
    """Test successful vendor research"""
    # Mock LLM response
    mock_llm.ask_question.return_value = json.dumps({
        "vendor_name": "Epic Systems",
        "company_background": "Leading EHR vendor",
        "ai_products": ["In Basket AI", "Sepsis Prediction"],
        "sources": ["Epic website"],
    })

    result = await agent.research_vendor("Epic Systems")

    # Verify
    assert isinstance(result, dict)
    assert result["vendor_name"] == "Epic Systems"
    assert "ai_products" in result
    assert mock_llm.ask_question.called


@pytest.mark.asyncio
async def test_research_vendor_empty_name(agent, mock_llm):
    """Test vendor research with empty vendor name"""
    result = await agent.research_vendor("")

    # Should return error without calling LLM
    assert "error" in result
    assert not mock_llm.ask_question.called


@pytest.mark.asyncio
async def test_research_use_case_success(agent, mock_llm):
    """Test successful use case research"""
    # Mock LLM response
    mock_llm.ask_question.return_value = json.dumps({
        "use_case": "Inbox prioritization",
        "workflow_analysis": "Time-consuming task",
        "ai_benefits": "Prioritize critical items",
        "sources": ["JAMA study"],
    })

    result = await agent.research_use_case(
        "Inbox prioritization", "Cardiology"
    )

    # Verify
    assert isinstance(result, dict)
    assert "workflow_analysis" in result
    assert mock_llm.ask_question.called


@pytest.mark.asyncio
async def test_research_use_case_empty(agent, mock_llm):
    """Test use case research with empty use case"""
    result = await agent.research_use_case("", "")

    # Should return error without calling LLM
    assert "error" in result
    assert not mock_llm.ask_question.called


# ============================================================================
# Test Synthesis
# ============================================================================


@pytest.mark.asyncio
async def test_synthesize_knowledge(
    agent, mock_llm, sample_ticket_info, sample_vendor_context, sample_use_case_context
):
    """Test knowledge synthesis"""
    # Mock LLM response
    mock_llm.ask_question.return_value = json.dumps({
        "capability_mapping": "Epic AI maps well to inbox needs",
        "opportunities": ["Reduce physician burnout"],
        "risks": ["Alert fatigue"],
        "questions": ["What is baseline inbox time?"],
        "next_steps": ["Pilot with 5 cardiologists"],
    })

    result = await agent.synthesize_knowledge(
        sample_ticket_info, sample_vendor_context, sample_use_case_context
    )

    # Verify
    assert isinstance(result, dict)
    assert "capability_mapping" in result or "synthesis" in result
    assert mock_llm.ask_question.called


# ============================================================================
# Test Form Drafting
# ============================================================================


@pytest.mark.asyncio
async def test_draft_discovery_form(
    agent,
    mock_llm,
    sample_ticket_info,
    sample_vendor_context,
    sample_use_case_context,
):
    """Test Discovery Form drafting"""
    # Mock LLM response
    mock_llm.ask_question.return_value = json.dumps({
        "title": "Epic In Basket AI - Cardiology",
        "sections": [
            {"id": "basic_information", "content": "..."},
            {"id": "problem_definition", "content": "..."},
            {"id": "approach", "content": "..."},
        ],
    })

    research = ResearchContext(
        vendor_info=sample_vendor_context,
        use_case_info=sample_use_case_context,
        synthesis={"key_insights": []},
    )

    result = await agent.draft_discovery_form(sample_ticket_info, research)

    # Verify
    assert isinstance(result, dict)
    assert "title" in result
    assert "sections" in result
    assert len(result["sections"]) >= 1
    assert mock_llm.ask_question.called


# ============================================================================
# Test Verification
# ============================================================================


@pytest.mark.asyncio
async def test_verify_form_success(agent, sample_form):
    """Test form verification with valid form"""
    result = await agent.verify_form(sample_form)

    # Verify
    assert isinstance(result, dict)
    assert "passed" in result
    assert "overall_score" in result
    assert "checks" in result
    assert isinstance(result["checks"], list)


@pytest.mark.asyncio
async def test_verify_form_missing_fields(agent):
    """Test form verification with missing fields"""
    incomplete_form = {"title": "Test"}  # Missing sections

    result = await agent.verify_form(incomplete_form)

    # Should fail verification
    assert result["passed"] is False
    assert result["overall_score"] < 1.0
    assert len(result["issues"]) > 0


@pytest.mark.asyncio
async def test_verify_form_empty(agent):
    """Test form verification with empty form"""
    result = await agent.verify_form({})

    # Should fail all checks
    assert result["passed"] is False
    assert result["overall_score"] < 0.5


# ============================================================================
# Test Correction
# ============================================================================


@pytest.mark.asyncio
async def test_correct_issues(agent, mock_llm, sample_form):
    """Test issue correction"""
    # Mock verification with issues
    verification = {
        "passed": False,
        "issues": ["completeness", "clarity"],
        "overall_score": 0.6,
    }

    # Mock LLM correction response
    corrected_form = sample_form.copy()
    corrected_form["sections"].append({"id": "new_section", "content": "..."})
    mock_llm.ask_question.return_value = json.dumps(corrected_form)

    result = await agent.correct_issues(sample_form, verification)

    # Verify
    assert isinstance(result, dict)
    assert mock_llm.ask_question.called


@pytest.mark.asyncio
async def test_correct_issues_no_issues(agent, mock_llm, sample_form):
    """Test correction when no issues present"""
    verification = {"passed": True, "issues": []}

    result = await agent.correct_issues(sample_form, verification)

    # Should return original form without calling LLM
    assert result == sample_form
    assert not mock_llm.ask_question.called


# ============================================================================
# Test Process Ticket (Integration)
# ============================================================================


@pytest.mark.asyncio
async def test_process_ticket_success(agent, mock_llm, sample_ticket):
    """Test full ticket processing workflow"""
    # Mock all LLM calls
    mock_llm.ask_question.side_effect = [
        # Extract
        json.dumps({
            "vendor": "Epic",
            "use_case": "Inbox prioritization",
            "department": "Cardiology",
        }),
        # Research vendor
        json.dumps({"vendor_name": "Epic", "sources": []}),
        # Research use case
        json.dumps({"use_case": "Inbox", "sources": []}),
        # Synthesize
        json.dumps({"synthesis": "...", "key_insights": []}),
        # Draft form
        json.dumps({
            "title": "Epic In Basket AI",
            "sections": [
                {"id": "basic", "content": "..."},
                {"id": "problem", "content": "..."},
                {"id": "approach", "content": "..."},
            ],
        }),
    ]

    result = await agent.process_ticket(sample_ticket)

    # Verify result structure
    assert isinstance(result, ProcessingResult)
    assert result.form is not None
    assert result.trace_id is not None
    assert result.verification is not None
    assert result.duration_seconds > 0
    assert len(result.steps_completed) > 0
    assert 0.0 <= result.confidence <= 1.0

    # Verify workflow steps completed
    assert "extract_basics" in result.steps_completed
    assert "research_vendor" in result.steps_completed
    assert "research_use_case" in result.steps_completed
    assert "synthesize" in result.steps_completed
    assert "draft_form" in result.steps_completed
    assert "self_verify" in result.steps_completed


@pytest.mark.asyncio
async def test_process_ticket_empty_input(agent):
    """Test processing with empty ticket text"""
    with pytest.raises(ValueError, match="cannot be empty"):
        await agent.process_ticket("")


@pytest.mark.asyncio
async def test_process_ticket_with_correction(agent, mock_llm, sample_ticket):
    """Test processing that requires form correction"""
    # Mock LLM calls with initial verification failure
    mock_llm.ask_question.side_effect = [
        # Extract
        json.dumps({"vendor": "Epic"}),
        # Research vendor
        json.dumps({"vendor_name": "Epic"}),
        # Research use case
        json.dumps({"use_case": "Inbox"}),
        # Synthesize
        json.dumps({"synthesis": "..."}),
        # Draft form (incomplete)
        json.dumps({"title": "Test"}),  # Missing sections
        # Correction
        json.dumps({
            "title": "Test",
            "sections": [{"id": "basic", "content": "..."}],
        }),
    ]

    result = await agent.process_ticket(sample_ticket)

    # Should have completed correction step
    assert "correct_issues" in result.steps_completed


# ============================================================================
# Test Observability
# ============================================================================


def test_start_trace(agent):
    """Test trace start"""
    trace_id = agent._start_trace("test_operation", {"key": "value"})

    assert trace_id is not None
    assert trace_id in agent.traces
    assert agent.traces[trace_id]["operation"] == "test_operation"
    assert agent.traces[trace_id]["status"] == "in_progress"


def test_log_step(agent):
    """Test step logging"""
    trace_id = agent._start_trace("test")
    agent._log_step(trace_id, "step1", "Test step")

    assert len(agent.traces[trace_id]["steps"]) == 1
    assert agent.traces[trace_id]["steps"][0]["step_id"] == "step1"
    assert agent.traces[trace_id]["steps"][0]["status"] == "in_progress"


def test_log_step_complete(agent):
    """Test step completion logging"""
    trace_id = agent._start_trace("test")
    agent._log_step(trace_id, "step1", "Test step")
    agent._log_step_complete(trace_id, "step1", {"result": "success"})

    step = agent.traces[trace_id]["steps"][0]
    assert step["status"] == "completed"
    assert step["result"]["result"] == "success"
    assert "end_time" in step


def test_end_trace(agent):
    """Test trace end"""
    trace_id = agent._start_trace("test")
    agent._end_trace(trace_id, "success")

    assert agent.traces[trace_id]["status"] == "success"
    assert "end_time" in agent.traces[trace_id]


def test_end_trace_with_error(agent):
    """Test trace end with error"""
    trace_id = agent._start_trace("test")
    agent._end_trace(trace_id, "error", "Test error message")

    assert agent.traces[trace_id]["status"] == "error"
    assert agent.traces[trace_id]["error"] == "Test error message"


def test_get_trace(agent):
    """Test getting trace by ID"""
    trace_id = agent._start_trace("test")
    trace = agent.get_trace(trace_id)

    assert trace is not None
    assert trace["operation"] == "test"


def test_get_trace_not_found(agent):
    """Test getting non-existent trace"""
    trace = agent.get_trace("nonexistent")

    assert trace is None


def test_get_completed_steps(agent):
    """Test getting completed steps list"""
    trace_id = agent._start_trace("test")
    agent._log_step(trace_id, "step1", "Step 1")
    agent._log_step(trace_id, "step2", "Step 2")
    agent._log_step_complete(trace_id, "step1")

    completed = agent._get_completed_steps(trace_id)

    assert len(completed) == 1
    assert "step1" in completed
    assert "step2" not in completed


# ============================================================================
# Test Helper Methods
# ============================================================================


def test_load_workflow(agent):
    """Test workflow loading"""
    # This will attempt to load from filesystem
    # In real environment with files present, should work
    workflow = agent._load_workflow("discovery")

    # Will be None if file doesn't exist, dict if it does
    assert workflow is None or isinstance(workflow, dict)


def test_load_template(agent):
    """Test template loading"""
    template = agent._load_template("ai_discovery_form")

    # Will be None if file doesn't exist, dict if it does
    assert template is None or isinstance(template, dict)
