# CLAUDE.md - Instructions for AI Assistant
## Working on AI Product Manager Agent Codebase

> **Purpose**: This document provides instructions for Claude (AI assistant) when helping develop, debug, or extend the AI Product Manager Agent.

---

## 🎯 Project Context

You are working on **Geisinger's first production agentic AI system** - an AI Product Manager that helps navigate the ServiceNow intake process and AI governance workflow.

### Critical Understanding

This is NOT a chatbot. This is NOT a simple automation. This IS:
- An **autonomous agent** that dynamically plans and adapts
- A **self-verifying system** that checks its own work
- A **governed AI** that respects human oversight
- A **learning system** that improves over time

**Your role**: Help implement the Geisinger Agentic Architecture principles while keeping the code simple, testable, and production-ready.

---

## 📋 Core Principles (Never Compromise These)

### 1. Agency Over Workflows
```python
# ❌ WRONG: Hardcoded workflow
def process_intake():
    step1()
    step2()
    step3()
    return result

# ✅ RIGHT: Agent loop
def process_intake(task):
    while not complete:
        context = gather_context()
        plan = create_plan(context)
        result = execute_plan(plan)
        verification = verify_result(result)
        if verification.passed:
            complete = True
        else:
            adapt_plan(verification.issues)
    return result
```

### 2. Self-Verification First
Every agent output MUST be verified before human review:
```python
# Always include verification
result = agent.execute(task)
verification = self_verifier.verify(result)

if not verification.passed:
    # Agent tries again, doesn't just send to human
    result = agent.retry_with_feedback(verification.issues)
```

### 3. Explainability Always
Every decision must be traceable:
```python
# ✅ Always include reasoning
return AgentResponse(
    result=output,
    reasoning=[
        "Step 1: Analyzed SNOW ticket fields",
        "Step 2: Identified missing vendor info",
        "Step 3: Ran vendor search",
        "Step 4: Populated brief template"
    ],
    confidence=0.85,
    data_sources=["SNOW-INC0012345", "VendorDB", "PolicyDoc-v2.1"]
)
```

### 4. HITL Interactions Are Conversations
When asking for approval, use the Interaction Layer:
```python
# ✅ Approval is a conversation (Layer 6 - Interactions)
approval = await interaction_layer.request_approval(
    proposal=ActionProposal(
        action="Submit Discovery Form",
        reasoning="All required fields complete...",
        confidence=0.92
    ),
    requirements=ApprovalRequirements(tier=HITLTier.TIER_3)
)

# ❌ WRONG: Don't mix governance and interaction
if needs_approval:
    # Don't just set a flag and move on
    approved = True  # This bypasses the conversation!
```

---

## 🏗️ Architecture Layers (What Each Does)

### Layer 1: Core Agent Runtime (`src/agent/`)

**Orchestrator** (`orchestrator.py`)
- Implements the main agent loop
- Coordinates planner, executor, verifier
- Manages iteration count
- Returns final agent response

**Example pattern**:
```python
class AgentOrchestrator:
    async def execute_task(self, task: Task) -> AgentResponse:
        # Load blueprints (always)
        meta_bp = await self.load_meta_blueprint()
        domain_bp = await self.load_domain_blueprint(task.domain)
        
        # Agent loop
        for iteration in range(self.max_iterations):
            # 1. GATHER
            context = await self.gather_context(task, iteration)
            
            # 2. PLAN
            plan = await self.planner.create_plan(task, context)
            
            # 3. ACT
            result = await self.executor.execute(plan)
            
            # 4. VERIFY
            verification = await self.verifier.verify(result, plan)
            
            # 5. ITERATE/ADAPT
            if verification.complete:
                return self._build_response(result, verification)
            
            # Learn from verification, try again
            task = self._adapt_task(task, verification)
        
        # Max iterations reached
        return self._escalate("max_iterations_reached")
```

### Layer 2: Memory & Context (`src/memory/`)

**Working Memory** (`working_memory.py`)
- Stores current session state
- Tracks conversation history
- Caches tool results
- Manages token budget

**Key pattern**:
```python
class WorkingMemory:
    def __init__(self, max_tokens=50000):
        self.conversation: List[Turn] = []
        self.task_state: TaskState = TaskState()
        self.tool_results: Dict[str, CachedResult] = {}
        self.token_count = 0
    
    def add_turn(self, turn: Turn):
        self.conversation.append(turn)
        self.token_count += count_tokens(turn)
        
        # Check budget
        if self.token_count > self.max_tokens * 0.8:
            self._trigger_compaction()
```

**Database Interface** (`database.py`)
- PostgreSQL connection
- CRUD operations for initiatives, sessions, actions
- Transaction management

### Layer 3: Tool Framework (`src/tools/`)

**Tool Registry** (`tool_registry.py`)
- Central catalog of all tools
- Tool discovery and retrieval
- Version management

**Tool Pattern** (all tools should follow this):
```python
class ServiceNowClient(Tool):
    """Tool for retrieving ServiceNow tickets"""
    
    def __init__(self):
        self.tool_id = "servicenow_ticket_retrieval"
        self.description = "Retrieves SNOW ticket details by ticket number"
        self.parameters_schema = {
            "ticket_number": {"type": "string", "required": True}
        }
    
    async def execute(
        self, 
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        # 1. Validate inputs
        self._validate_parameters(parameters)
        
        # 2. Execute
        try:
            ticket_data = await self._fetch_ticket(
                parameters["ticket_number"]
            )
            
            # 3. Format result
            return ToolResult(
                status="SUCCESS",
                data=ticket_data,
                tool_id=self.tool_id,
                citations=[f"SNOW-{parameters['ticket_number']}"]
            )
        except Exception as e:
            return ToolResult(
                status="FAILED",
                error=str(e),
                tool_id=self.tool_id
            )
    
    def verify_result(self, result: ToolResult) -> bool:
        """Self-check: Did we get valid data?"""
        if result.status != "SUCCESS":
            return False
        
        required_fields = ["requestor", "description", "department"]
        return all(field in result.data for field in required_fields)
```

### Layer 6: Interaction Layer (`src/interaction/`)

**Approval UI** (`approval_ui.py`)
- Presents proposals to users
- Handles user responses (Approve/Deny/Modify)
- Shows explanations on request

**Pattern**:
```python
class ApprovalUI:
    async def request_approval(
        self,
        proposal: ActionProposal,
        requirements: ApprovalRequirements
    ) -> ApprovalResponse:
        # Build rich UI
        ui = self._build_approval_dialog(proposal)
        
        # Present to user (CLI, web, etc.)
        user_input = await self._display_and_wait(ui)
        
        # Parse response
        if user_input.action == "APPROVE":
            return ApprovalResponse(
                decision="APPROVED",
                timestamp=datetime.now()
            )
        elif user_input.action == "MODIFY":
            return ApprovalResponse(
                decision="MODIFY",
                modifications=user_input.changes
            )
        # ... handle other responses
```

### Layer 7: Knowledge Management (`src/knowledge/`)

**Blueprint Loader** (`blueprint_loader.py`)
- Loads YAML blueprints
- Validates blueprint structure
- Provides policy lookup

**Blueprint Structure**:
```yaml
# blueprints/product-mgmt-blueprint.yaml
name: "Product Management AI Governance"
domain: "product_management"
version: "1.0"

policies:
  - id: "PM-POL-001"
    rule: "All Significant Risk AI programs require equity audit"
    enforcement: "MUST"
  
  - id: "PM-POL-002"
    rule: "Discovery forms must include workflow integration diagram"
    enforcement: "MUST"

guidelines:
  - id: "PM-GUIDE-001"
    recommendation: "Prefer evidence-based metrics over proxy metrics"
    enforcement: "SHOULD"

procedures:
  - id: "PM-PROC-001"
    name: "Intake Brief Generation"
    steps:
      - "Extract SNOW ticket fields"
      - "Research vendor information"
      - "Run risk screener"
      - "Populate brief template"
      - "Self-verify completeness"
      - "Request approval"
```

### Layer 9: HITL Governance (`src/governance/`)

**Self-Verification** (`self_verification.py`)
- Runs policy compliance checks
- Validates completeness
- Checks consistency
- Assesses confidence

**Pattern**:
```python
class SelfVerificationSuite:
    async def verify(
        self,
        result: ExecutionResult,
        plan: Plan,
        context: ExecutionContext
    ) -> VerificationResult:
        checks = []
        
        # 1. Policy compliance
        policy_check = await self._check_policies(
            result,
            context.blueprints
        )
        checks.append(policy_check)
        
        # 2. Completeness
        completeness = self._check_completeness(
            result,
            plan.requirements
        )
        checks.append(completeness)
        
        # 3. Consistency
        consistency = self._check_consistency(result)
        checks.append(consistency)
        
        # 4. Confidence
        confidence = self._assess_confidence(result)
        
        # Aggregate
        all_passed = all(c.passed for c in checks)
        
        return VerificationResult(
            passed=all_passed,
            checks=checks,
            confidence_score=confidence,
            complete=all_passed and plan.is_complete
        )
```

**Tier Classifier** (`tier_classifier.py`)
- Determines HITL tier based on action risk
- Returns tier + requirements

```python
class TierClassifier:
    def classify_action(
        self,
        action: Action,
        context: ExecutionContext
    ) -> HITLTier:
        # Simple rules for Phase 1
        
        if action.type == "document_draft":
            return HITLTier.TIER_2  # Passive review
        
        elif action.type == "document_submit":
            return HITLTier.TIER_3  # Active approval
        
        elif action.type == "risk_determination":
            return HITLTier.TIER_4  # Critical decision
        
        else:
            return HITLTier.TIER_1  # Auto-approve
```

---

## 💻 Coding Standards

### Python Style
- Follow PEP 8
- Type hints for all functions
- Docstrings for all classes and public methods
- Use `async/await` for I/O operations

### Structure
```python
# Good module structure
"""
Module docstring explaining purpose
"""

# Imports grouped: stdlib, third-party, local
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass

from anthropic import Anthropic
import psycopg2

from src.agent.base import Agent
from src.memory.working_memory import WorkingMemory

# Constants
MAX_ITERATIONS = 10
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# Classes
@dataclass
class Config:
    """Configuration dataclass"""
    api_key: str
    max_iterations: int = MAX_ITERATIONS

class MyClass:
    """Class docstring"""
    
    def __init__(self, config: Config):
        """Initialize with config"""
        self.config = config
    
    async def do_something(self, param: str) -> Result:
        """
        Method docstring
        
        Args:
            param: Description
            
        Returns:
            Result object
        """
        # Implementation
        pass
```

### Error Handling
```python
# ✅ Good: Specific exceptions, logging, recovery
try:
    result = await tool.execute(params)
except ToolExecutionError as e:
    logger.error(f"Tool execution failed: {e}", exc_info=True)
    # Try alternative approach
    result = await self._try_alternative(params)
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Escalate to human
    return self._escalate("unexpected_error", str(e))

# ❌ Bad: Bare except, no logging
try:
    result = tool.execute(params)
except:
    return None
```

### Testing
Every new feature needs:
1. Unit tests (test individual functions)
2. Integration test (test component interaction)
3. Golden test (if workflow-level feature)

```python
# tests/unit/test_risk_assessor.py
def test_risk_screener_identifies_high_risk():
    """Unit test: Risk screener correctly identifies high risk"""
    screener = RiskScreener()
    
    responses = {
        "q1_affects_patient_care": True,
        "q2_autonomous_decisions": True,
        "q3_high_stakes": True,
        "q4_reversibility": False,
        "q5_protected_characteristics": True
    }
    
    result = screener.assess(responses)
    
    assert result.risk_level == "significant"
    assert result.requires_enhanced_documentation == True

# tests/golden/test_intake_processing.py
@pytest.mark.golden
async def test_complete_intake_workflow():
    """Golden test: End-to-end intake processing"""
    agent = AgentOrchestrator(test_config)
    
    result = await agent.execute_task(
        Task(
            description="Process SNOW ticket INC0012345",
            initiative_id="test-initiative-1"
        )
    )
    
    # Verify workflow completed
    assert result.status == "SUCCESS"
    assert result.verification.passed == True
    
    # Verify intake brief generated
    brief = result.output["intake_brief"]
    assert brief["program_title"]
    assert brief["risk_level"]
    
    # Verify approval required
    assert result.requires_approval == True
    assert result.hitl_tier == "TIER_3"
```

---

## 🔍 When to Ask Questions

### Always Ask When:
1. **Unclear requirements**: If task description is ambiguous
2. **Policy conflicts**: If blueprints seem contradictory
3. **Security concerns**: If action might expose sensitive data
4. **Breaking changes**: If modification affects existing APIs
5. **Missing context**: If you need domain knowledge not in docs

### Don't Ask When:
1. **Coding patterns**: Follow examples in existing code
2. **Standard practices**: Use established Python conventions
3. **Testing approach**: Follow golden/unit/integration pattern
4. **Error handling**: Use try/except with logging
5. **Documentation**: Follow existing format

---

## 🎯 Implementation Checklist

### For Every New Tool:
- [ ] Inherits from `Tool` base class
- [ ] Has clear `tool_id` and `description`
- [ ] Defines `parameters_schema`
- [ ] Implements `execute()` method
- [ ] Implements `verify_result()` self-check
- [ ] Has error handling with logging
- [ ] Returns structured `ToolResult`
- [ ] Has unit tests (≥80% coverage)
- [ ] Registered in `tool_registry.py`
- [ ] Has usage example in docstring

### For Every Agent Function:
- [ ] Takes `Task` or `ExecutionContext` as input
- [ ] Returns structured response (not just raw data)
- [ ] Includes reasoning chain
- [ ] Logs all actions
- [ ] Has self-verification
- [ ] Determines HITL tier
- [ ] Has rollback plan (if writes data)
- [ ] Has golden test
- [ ] Updates session state
- [ ] Records audit trail

### For Every Blueprint Policy:
- [ ] Has unique ID
- [ ] Has clear rule statement
- [ ] Specifies enforcement (MUST/SHOULD/MAY)
- [ ] Has verification logic in code
- [ ] Is tested (policy compliance test)
- [ ] Is documented in README
- [ ] Has examples of compliance/violation

---

## 🚨 Critical Safety Rules

### 1. Never Skip Self-Verification
```python
# ❌ WRONG
result = agent.execute(task)
return result  # Sent directly to user!

# ✅ RIGHT
result = agent.execute(task)
verification = self_verifier.verify(result)
if not verification.passed:
    result = agent.retry(verification.issues)
return result
```

### 2. Always Log Actions
```python
# Every tool execution
await audit_logger.log_action(
    session_id=context.session_id,
    action_type="tool_execution",
    tool_used="servicenow_client",
    input=parameters,
    output=result,
    timestamp=datetime.now()
)
```

### 3. Never Auto-Approve Tier 3/4
```python
# ✅ RIGHT
if tier in [HITLTier.TIER_3, HITLTier.TIER_4]:
    approval = await interaction_layer.request_approval(proposal)
    if approval.decision != "APPROVED":
        return  # Don't proceed

# ❌ WRONG
if tier == HITLTier.TIER_3:
    # TODO: Add approval later
    pass  # This bypasses approval!
```

### 4. Validate All Inputs
```python
def execute(self, parameters: Dict[str, Any]):
    # ✅ Validate first
    if not parameters.get("ticket_number"):
        raise ValueError("ticket_number is required")
    
    if not re.match(r"INC\d{7}", parameters["ticket_number"]):
        raise ValueError("Invalid ticket format")
    
    # Then execute
    ...
```

---

## 📝 Documentation Standards

### Code Comments
```python
# ✅ Good comments explain WHY
# We use exponential backoff here because SNOW API 
# rate limits are aggressive (100 req/min)
await asyncio.sleep(2 ** attempt)

# ❌ Bad comments explain WHAT (code already shows this)
# Sleep for 2^attempt seconds
await asyncio.sleep(2 ** attempt)
```

### Docstrings
```python
async def create_plan(
    self,
    task: Task,
    context: ExecutionContext
) -> Plan:
    """
    Generate execution plan for task.
    
    Creates a step-by-step plan by:
    1. Analyzing task requirements
    2. Consulting blueprints for guidance
    3. Selecting appropriate tools
    4. Defining success criteria
    
    Args:
        task: The task to plan for
        context: Current execution context with memory and blueprints
    
    Returns:
        Plan object with ordered steps and tool requirements
        
    Raises:
        PlanningError: If task requirements cannot be satisfied
        
    Example:
        >>> plan = await planner.create_plan(
        ...     Task(description="Process SNOW ticket"),
        ...     context
        ... )
        >>> print(plan.steps)
        [Step(1: "Retrieve ticket"), Step(2: "Parse fields"), ...]
    """
```

### README Updates
When adding new features, update:
1. **Agent Workflows** section (if new workflow)
2. **Database Schema** (if new tables)
3. **Configuration** (if new settings)
4. **Testing** (if new test category)

---

## 🔄 Git Workflow

### Commit Messages
```bash
# Format: <type>(<scope>): <subject>

# Examples:
feat(tools): add vendor scanner tool
fix(agent): correct iteration count bug
docs(readme): update deployment section
test(golden): add risk assessment workflow test
refactor(memory): improve token counting efficiency
```

### Branch Naming
```bash
# Format: <type>/<short-description>

feature/vendor-scanner
bugfix/memory-leak-session
docs/api-reference
test/golden-discovery-form
```

---

## 🎓 Learning Resources

### Understanding the Architecture
1. Read: `geisinger-architecture-explanation.md`
2. Review: `refined-hitl-interaction-architecture.md`
3. Study: `geisinger-quick-reference.md`

### Understanding Anthropic Patterns
1. [Claude Agent SDK Docs](https://docs.anthropic.com/agents)
2. [Building Effective Agents](https://docs.anthropic.com/agents/effective)
3. [Tool Use Best Practices](https://docs.anthropic.com/tools)

### Code Examples
Look at existing implementations:
- `src/agent/orchestrator.py` - Agent loop pattern
- `src/tools/servicenow_client.py` - Tool pattern
- `src/governance/self_verification.py` - Verification pattern
- `tests/golden/test_intake_processing.py` - Golden test pattern

---

## 🤔 Common Scenarios

### Scenario 1: User Asks to Add New Tool

**Steps**:
1. Create new file in `src/tools/`
2. Inherit from `Tool` base class
3. Implement `execute()` and `verify_result()`
4. Add to `tool_registry.py`
5. Write unit tests in `tests/unit/`
6. Update README with tool description
7. Test integration in golden test

**Template**:
```python
# src/tools/new_tool.py
class NewTool(Tool):
    """One-line description"""
    
    def __init__(self):
        self.tool_id = "new_tool_id"
        self.description = "Detailed description"
        self.parameters_schema = {...}
    
    async def execute(self, parameters, context) -> ToolResult:
        # Implementation
        pass
    
    def verify_result(self, result: ToolResult) -> bool:
        # Self-check
        pass
```

### Scenario 2: User Reports Agent Not Iterating

**Debug Steps**:
1. Check `max_iterations` in config
2. Review verification logic - is it ever returning `complete=True`?
3. Check if agent is stuck in same plan (not adapting)
4. Look at logs for iteration count
5. Review `_adapt_task()` logic

**Common Issues**:
```python
# Issue: Verification never completes
def verify(self, result):
    # ❌ This always fails!
    return False  

# Fix: Actually check result
def verify(self, result):
    return all(
        result.get(field) 
        for field in self.required_fields
    )
```

### Scenario 3: User Wants to Add New Policy

**Steps**:
1. Add policy to `blueprints/product-mgmt-blueprint.yaml`
2. Implement check in `self_verification.py`
3. Write test in `tests/unit/test_verification.py`
4. Document in README
5. Run golden tests to ensure no regression

**Example**:
```yaml
# Add to blueprint
policies:
  - id: "PM-POL-003"
    rule: "All high-risk programs must include monitoring plan"
    enforcement: "MUST"
    check_function: "has_monitoring_plan"
```

```python
# Add to verifier
def _check_policies(self, result, blueprints):
    checks = []
    
    # New policy check
    if result.risk_level == "high":
        has_monitoring = "monitoring_plan" in result.artifacts
        checks.append(PolicyCheck(
            policy_id="PM-POL-003",
            passed=has_monitoring,
            message="Monitoring plan required for high-risk"
        ))
    
    return checks
```

---

## 🎉 Success Criteria

You're doing well when:
- ✅ Code follows existing patterns
- ✅ Every feature has tests
- ✅ Golden tests pass
- ✅ Agent iterates and adapts (not rigid workflow)
- ✅ Self-verification catches issues
- ✅ HITL approvals work correctly
- ✅ Reasoning is explainable
- ✅ Audit logs are complete
- ✅ Documentation is updated
- ✅ No shortcuts on safety

---

## 📞 Getting Help

**In Code Comments**:
```python
# QUESTION: Should we cache vendor lookups? They're expensive.
# See discussion: https://github.com/geisinger/ai-pm-agent/issues/42

# TODO: Implement retry logic here
# Reference: Tool execution pattern in servicenow_client.py

# FIXME: This verification is too strict, needs adjustment
# Blocked by: Blueprint clarification from Policy team
```

**In Commit Messages**:
```bash
git commit -m "feat(tools): add vendor scanner (needs review)

Implementation follows tool pattern but unsure about:
- Should we cache results?
- What's the rate limit?
- Is 30s timeout appropriate?

Ref: Issue #42"
```

---

## 🎯 Remember

You are building **Geisinger's first production agent**. This will set the pattern for all future agents. 

**Core Values**:
1. **Safety First**: Never skip verification or approval
2. **Explainability**: Every decision must be traceable
3. **Simplicity**: Simple, testable code beats clever code
4. **Incrementality**: Small steps, frequent tests
5. **Learning**: Each iteration should improve

**The Geisinger Way**:
> "Small steps, testable outcomes, trusted agents."

---

## 📋 Quick Reference

```python
# Agent loop pattern
while not complete:
    context = gather()
    plan = plan(context)
    result = execute(plan)
    verification = verify(result)
    if verification.passed:
        complete = True
    else:
        adapt()

# Self-verification pattern
checks = [
    policy_check(result),
    completeness_check(result),
    consistency_check(result)
]
passed = all(c.passed for c in checks)

# HITL pattern
if tier in [TIER_3, TIER_4]:
    approval = await request_approval(proposal)
    if not approval.granted:
        return

# Tool pattern
class MyTool(Tool):
    async def execute(self, params, context):
        # validate, execute, format
        return ToolResult(...)
    
    def verify_result(self, result):
        # self-check
        return bool

# Testing pattern
@pytest.mark.golden
async def test_workflow():
    result = await agent.execute(task)
    assert result.status == "SUCCESS"
    assert result.verification.passed
```

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Maintained By**: AI Architecture Team

When in doubt, ask! Better to clarify than to implement incorrectly. 🚀
