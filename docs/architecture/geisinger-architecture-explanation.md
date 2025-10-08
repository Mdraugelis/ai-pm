# Geisinger Enterprise Agentic Architecture
## High-Level Architecture Guide
**Version 1.0 | January 2025**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Component Breakdown](#component-breakdown)
3. [Information Flow](#information-flow)
4. [Key Design Patterns](#key-design-patterns)
5. [Implementation Modules](#implementation-modules)
6. [Deployment Considerations](#deployment-considerations)

---

## Architecture Overview

### Philosophy
The Geisinger Agentic Architecture implements **true agency** (not workflows) through:
- **Dynamic Agent Loop**: Autonomous plan → act → verify → iterate cycle
- **MCP-First Integration**: All enterprise connectors as MCP servers
- **Self-Verification First**: Agents validate before human review (60-80% burden reduction)
- **Domain Agnostic Core**: Same foundation across clinical, legal, product, and all domains

### Architectural Layers (11 Total + Meta)

```
┌─────────────────────────────────────────────────────────┐
│  Layer 8: META-BLUEPRINT (Universal Constitution)       │ ← ALWAYS ACTIVE
├─────────────────────────────────────────────────────────┤
│  Layer 1: Core Agent Orchestration (The Brain)          │
│  Layer 2: Memory & Context Management                   │
│  Layer 3: Tool Use Framework (Primary Building Blocks)  │
│  Layer 4: Agent Perceptions (Push/Pull Awareness)       │
│  Layer 5: Agent Interactions (Communication)            │
│  Layer 6: Domain Knowledge Base                         │
│  Layer 7: Strategic Knowledge (BluePrints)              │
├─────────────────────────────────────────────────────────┤
│  Layer 9: Human-in-the-Loop (Tiered Oversight)         │
│  Layer 10: Guardrails & Safety (Multi-Layer Defense)   │
│  Layer 11: Evaluation & Observability (Quality Gates)  │
└─────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 🤖 LAYER 1: Core Agent Orchestration Engine
**Purpose**: The autonomous reasoning system - the "brain" of the agent

#### The Agent Loop (Heart of Agency)
```
1. GATHER Context
   └─ From: Memory, Perceptions, BluePrints
   
2. PLAN Action
   └─ Consult: Domain & Strategic Knowledge
   └─ Select: Tools and approach
   
3. ACT (Execute Tools)
   └─ Via: MCP clients → MCP servers
   
4. SELF-VERIFY
   └─ Against: Meta-Blueprint, Domain policies
   └─ Check: Completeness, consistency, safety
   
5. ITERATE/ADAPT
   └─ If not complete → Loop back to GATHER
   └─ If complete → Proceed to HITL
```

#### Key Capabilities
- **Dynamic Planning**: No hardcoded workflows; adapts based on context
- **Tool Discovery**: Learns which tools work best for tasks
- **Failure Recovery**: Tries alternatives when primary approach fails
- **Subagent Spawning**: Creates specialized workers for complex tasks
- **Self-Correction**: Adjusts plans based on verification results

---

### 💾 LAYER 2: Memory & Context Management
**Purpose**: Maintains state and manages the 200K token context budget

#### Components

**Working Memory (50K token allocation)**
- Active conversation context (last 3 turns always loaded)
- Current task state and progress
- Recent tool results (5-minute TTL)
- Temporary reasoning conclusions
- Error history and lessons learned within session

**Long-Term Persistent Memory**
- Session summaries for continuity
- Learned patterns and successful strategies
- Entity relationships (patient, project, case)
- Performance metrics and outcomes

**Context Budget Manager**
- Total: 200K tokens (Claude Opus 4.1)
- Always-loaded: ~12K tokens (6% - Meta, task, safety)
- Dynamic pool: ~188K tokens (94% - flexible allocation)
- Emergency reserve: 8K tokens (4% - overflow protection)

**Auto-Compaction Service**
- Triggers at 80% capacity (160K tokens)
- Compression ratio target: 10:1
- Preserves: Goals, decisions, action items, safety-critical data
- Discards: Debug info, duplicate data, intermediate calculations

#### Context Loading Strategy
```
ALWAYS LOADED (~12K):
├─ Meta-Blueprint core principles (2K)
├─ Current task definition (1K)
├─ User role & permissions (1K)
├─ Active conversation (last 3 turns, ~3K)
├─ Working memory summary (5K)

ON-DEMAND RETRIEVAL:
├─ Domain BluePrints (loaded when classified)
├─ Historical context (retrieved via tools)
├─ Specific policy documents (as needed)
├─ Long documentation (fetched, not kept)
```

---

### 🔧 LAYER 3: Tool Use Framework
**Purpose**: Tools are the agent's "hands" - primary means of perception and action

#### Architecture

**Tool Registry (MCP-Based)**
```yaml
tool_entry:
  tool_id: UUID
  mcp_endpoint: "mcp://server.geisinger.org/tool-name"
  owner: "team@geisinger.org"
  version: "2.1.0"
  risk_tier: "MEDIUM"
  requires_consent: true
  rate_limit: "1000 req/min"
  sla:
    availability: "99.9%"
    response_p99: "1000ms"
```

**Tool Discovery Engine**
- Agents browse tool catalog at startup
- Track success rates per tool
- Learn optimal tool combinations
- Identify alternatives for failures

**Tool Execution Controller**
- Dynamic tool selection (not predefined sequences)
- Parallel execution when beneficial
- Automatic retry with backoff
- Result integration and caching

**Tool Verifier**
- Post-execution validation
- Output schema checking
- Result completeness verification
- Safety constraint enforcement

#### Tool Categories
1. **Perception Tools** (Pull data)
   - Database queries
   - API reads
   - Document retrieval
   - Search operations

2. **Action Tools** (Change state)
   - Database writes
   - Email sending
   - Calendar operations
   - Document generation

3. **Hybrid Tools** (Both)
   - Workflow systems
   - Communication platforms
   - Collaborative tools

---

### 👁️ LAYER 4: Agent Perceptions
**Purpose**: Environmental awareness through push and pull mechanisms

#### Push-Based Perceptions (Event-Driven)
```
Event Stream → Filter Rules → Agent Notification
                                  ↓
                    Automatic Context Loading
                                  ↓
                    Trigger Planning Module
```

**Sources**:
- Real-time system events
- Threshold-based alerts (e.g., "Lab result critical")
- State changes (e.g., "Patient admitted")
- Scheduled monitoring checks
- Subscription feeds

#### Pull-Based Perceptions (Query-Driven)
```
Agent Needs Info → Formulate Query
                       ↓
            Select Appropriate Tool
                       ↓
            Execute and Cache Result
                       ↓
            Integrate into Working Memory
```

**Mechanisms**:
- Direct queries (specific data requests)
- Search operations (fuzzy finding)
- Aggregations (summary statistics)
- Verification checks (fact validation)
- Context expansion (related data discovery)

---

### 💬 LAYER 5: Agent Interactions
**Purpose**: Multi-modal communication and collaboration with humans

#### Components

**Conversational Interface**
- Natural language dialogue
- Optional chain-of-thought visibility
- Source attribution with citations
- Confidence indicators
- Clarification loops for ambiguity

**Proactive Recommendations**
```json
{
  "recommendation": "Schedule code review for PR #1234",
  "justification": {
    "data_sources": ["GitHub API", "Team Calendar"],
    "blueprint_alignment": "Code Review Policy v2.1",
    "expected_outcome": "Faster merge, fewer bugs",
    "confidence": 0.87,
    "alternatives": ["Defer to next sprint", "Auto-merge with tests"]
  },
  "user_actions": ["approve", "modify", "reject", "discuss"]
}
```

**Explainability Engine**
- Decision reasoning chains
- Data source transparency
- Policy references
- Alternative options considered
- Confidence factors (supporting & limiting)

---

### 📖 LAYER 6: Domain Knowledge Base
**Purpose**: Authoritative, versioned domain expertise

#### Knowledge Categories
- **Policies**: Hard rules (MUST follow)
- **Guidelines**: Best practices (SHOULD follow)
- **Procedures**: Step-by-step processes (HOW to)
- **References**: Factual information
- **Examples**: Canonical cases
- **Exceptions**: Edge case handling

#### Version Control
```
Knowledge Update → Version Increment
                       ↓
            Change Documentation
                       ↓
            Agent Notification
                       ↓
            Gradual Migration
```

---

### 🧠 LAYER 7: Strategic Knowledge (BluePrints)
**Purpose**: Institutional wisdom - the agent's "extended mind" and constitution

#### BluePrint Structure
```yaml
blueprint:
  name: "Clinical Decision Support"
  type: "domain_specific"
  priority: "high"
  
  policies:
    - "Always verify patient identity"
    - "Check allergies before prescribing"
    - "Document all clinical reasoning"
  
  guidelines:
    - "Prefer evidence-based treatments"
    - "Consider patient preferences"
    - "Escalate uncertainty to physicians"
  
  best_practices:
    - approach: "Gather full medical history"
    - approach: "Consider differential diagnoses"
    - approach: "Validate with clinical guidelines"
  
  knowledge:
    key_facts: ["Clinical decision trees", "Drug interactions"]
    references: ["UpToDate", "Clinical pathways"]
    examples: ["Case studies", "Successful treatments"]
```

#### Multi-BluePrint Composition
When agents need multiple expertise areas:
```
Task: "Review contract for clinical trial"
  ↓
Load BluePrints:
├─ Legal Compliance
├─ Clinical Research
└─ HIPAA Privacy

Resolve Conflicts:
├─ Higher priority overrides lower
├─ Domain-specific beats general
├─ Safety rules ALWAYS win
└─ Log conflicts for review
```

---

### 📋 LAYER 8: Meta-Blueprint (Universal Constitution)
**Purpose**: Immutable principles governing ALL agent behavior

#### Core Principles (Never Override)
1. **Human Safety**: Wellbeing above all else
2. **Transparency**: All reasoning must be explainable
3. **Privacy**: Respect confidentiality always
4. **Compliance**: Follow all laws and regulations
5. **Learning**: Continuous improvement from experience

#### Problem-Solving Heuristics
- Break complex tasks into steps
- When uncertain, gather more information
- Verify assumptions before proceeding
- Document reasoning for auditability
- Consider multiple alternatives
- Learn from failures within session

#### Escalation Triggers (Auto-Stop)
- Confidence below 70%
- Potential policy violation detected
- Safety or risk concerns identified
- Novel situation without precedent
- Explicit user request for human

#### Operational Boundaries
- ❌ Never make irreversible changes without approval
- ❌ Never access data without authorization
- ❌ Never hide or obscure failures
- ❌ Never proceed when safety uncertain
- ❌ Never violate user trust

---

### 👥 LAYER 9: Human-in-the-Loop Integration
**Purpose**: Efficient oversight with minimal burden through self-verification

#### Self-Verification Pipeline (BEFORE Human Review)
```
Agent Output
    ↓
Internal Validation Suite:
├─ Policy Compliance (Blueprint alignment)
├─ Completeness Check (all requirements met)
├─ Consistency Check (no contradictions)
├─ Quality Assessment (meets standards)
└─ Confidence Evaluation (certainty level)
    ↓
All Checks Pass?
├─ NO → Return to Agent Loop (with specific feedback)
└─ YES → Determine Review Tier
    ↓
Review Tier Assessment
```

#### HITL Tiers (Risk-Based)

**Tier 1: No Review Needed**
- Low-impact reads (e.g., "Show calendar")
- Status checks (e.g., "Check ticket status")
- Summaries of public data
- **Action**: Auto-proceed

**Tier 2: Passive Review**
- Medium-impact operations
- Reversible writes (e.g., "Draft email")
- Internal data queries
- **Action**: Proceed, audit later (10% sampling)

**Tier 3: Active Approval**
- High-impact operations
- Legal drafts
- Scheduling commitments
- Resource allocations
- **Action**: Queue for human approval, wait

**Tier 4: Immediate Escalation**
- Clinical writebacks (e.g., "Submit order")
- Irreversible changes (e.g., "Deploy to production")
- Financial transactions
- Legal filings
- **Action**: Alert human immediately, block execution

#### Efficiency Gains
- **70-80%** reduction in human review needs
- Higher quality when review IS needed
- Clear justification for all review requests
- Batch approval capabilities
- Learning from approval patterns

---

### 🛡️ LAYER 10: Guardrails & Safety Framework
**Purpose**: Multi-layer defense with agent self-governance

#### Self-Governance Layer (NEW)
Agent monitors its own behavior:
- Deviation from normal patterns
- Unusual tool usage sequences
- Repeated failures on similar tasks
- Confidence degradation over time
- Policy near-misses

**Auto-Corrections**:
- Reset context if confused
- Reduce autonomy if failing
- Request help proactively
- Document issues for review

#### Traditional Safety Layers
```
Layer 1: Input Validation
    └─ Sanitize, validate types, check patterns
    
Layer 2: Planning Validation
    └─ Check proposed plan against policies
    
Layer 3: Execution Monitoring
    └─ Watch tool usage in real-time
    
Layer 4: Output Validation
    └─ Verify final results before delivery
    
Layer 5: Audit Trail
    └─ Complete action history (immutable)
```

#### Prompt Injection Defense
```python
# Structural Separation
[SYSTEM_INSTRUCTION]
Tool: fetch_patient_data
Parameters: {"patient_id": "validated_input"}
[END_SYSTEM_INSTRUCTION]

[USER_CONTENT_QUARANTINE]
{sanitized_user_input}
[END_USER_CONTENT_QUARANTINE]
```

**Defenses**:
- Remove control characters
- Escape special syntax
- Validate parameter types
- Length limits enforced
- Pattern matching for suspicious content
- Tool boundary protection
- Output validation for instruction leakage

---

### 📊 LAYER 11: Evaluation & Observability
**Purpose**: Continuous validation and transparency

#### Evaluation Components

**Golden Test Suite (Per Domain)**
- Canonical tasks that define success
- Example: "CLIN-001: Patient triage assessment"
- Pass criteria: Correct actions + correct outcomes
- Run frequency: Every commit, nightly, weekly

**Safety Test Suite**
- Prompt injection resistance
- Data leakage prevention
- Authorization compliance
- PHI/PII protection

**Regression Test Suite**
- Every fixed bug → permanent test
- Prevents backsliding
- Runs on every release candidate

**Performance Benchmarks**
- Latency targets (p50, p99)
- Throughput (QPS)
- Token efficiency
- Resource usage

**Red Team Testing**
- Adversarial prompting
- Multi-turn attacks
- Tool abuse attempts
- Authorization bypass attempts

**Shadow Testing**
- Candidate agent mirrors production traffic
- Results compared but not served
- Low-risk validation of changes

#### Metrics Dashboard
```
Real-Time:
├─ Current safety score
├─ Golden test pass rate
├─ Active regressions
└─ Shadow test variance

Trends:
├─ Score over time
├─ Regression frequency
├─ Performance degradation
└─ Safety incident rate

Alerts:
├─ Safety score drop >5%
├─ New critical regression
├─ Red team success
└─ Performance SLA breach
```

---

## Information Flow

### Primary Request Flow
```
1. User Request
    ↓
2. Conversational Interface (Layer 5)
    ↓
3. Input Validation (Layer 10)
    ↓
4. AGENT LOOP BEGINS (Layer 1)
    ├─ Load Meta-Blueprint (Layer 8) - ALWAYS
    ├─ Classify domain → Load Domain Blueprints (Layer 7)
    ├─ Gather Context (from Layer 2, 4, 6)
    ├─ Plan Action (consult Layer 7, 6)
    ├─ Execute Tools (via Layer 3 → MCP → External Systems)
    ├─ Self-Verify (against Layer 8, 10)
    └─ Iterate until complete
    ↓
5. Self-Verification Pipeline (Layer 9)
    ├─ Policy compliance check
    ├─ Completeness check
    ├─ Consistency check
    └─ Confidence assessment
    ↓
6. HITL Tier Assessment (Layer 9)
    ├─ Tier 1 → Auto-proceed
    ├─ Tier 2 → Proceed + audit
    ├─ Tier 3 → Wait for approval
    └─ Tier 4 → Immediate escalation
    ↓
7. Response Generation
    ↓
8. Output Validation (Layer 10)
    ↓
9. User Response (via Layer 5)
    ↓
10. Logging & Metrics (Layer 11)
```

### Tool Execution Flow (MCP-Based)
```
Agent (Layer 1)
    ↓ "I need patient data"
Tool Discovery (Layer 3)
    ↓ Check Tool Registry
Select Tool: "fetch_patient_data"
    ↓
RBAC Check (Cross-Cutting)
    ↓ Verify permissions
Consent Check (if required)
    ↓ Get user consent
MCP Client (Layer 3)
    ↓ Prepare MCP request
MCP Protocol
    ↓ "mcp://ehr.geisinger.org/patient_data"
MCP Server (External)
    ↓ Execute query
External System (EHR)
    ↓ Return data
MCP Server
    ↓ Format response
MCP Client
    ↓ Receive result
Tool Verifier (Layer 3)
    ↓ Validate output
Cache Result (Layer 2)
    ↓ Store with 5-min TTL
Return to Agent (Layer 1)
    ↓ Continue agent loop
```

### Context Management Flow
```
Request Arrives
    ↓
Context Budget Manager checks capacity
    ├─ < 80% → Normal operation
    ├─ 80-90% → Warning, start compaction prep
    ├─ 90-95% → Aggressive compaction
    └─ > 95% → Emergency compaction
    ↓
Load Always-Present Context (~12K)
    ├─ Meta-Blueprint (2K)
    ├─ Current task (1K)
    ├─ Recent conversation (3K)
    ├─ User context (1K)
    └─ Working memory summary (5K)
    ↓
Retrieve On-Demand Context (as needed)
    ├─ Domain BluePrints (when classified)
    ├─ Historical context (via tools)
    ├─ Specific documents (via tools)
    └─ Additional examples (if uncertain)
    ↓
Execute Agent Loop
    ↓
Update Working Memory
    ↓
Check TTL on cached items
    └─ Expire old data (5-30 min depending on type)
    ↓
If approaching limit (160K):
    ├─ Trigger auto-compaction
    ├─ Summarize conversation (10:1 ratio)
    ├─ Compress tool results
    └─ Move to long-term memory
```

---

## Key Design Patterns

### Pattern 1: MCP-First Integration
**Problem**: Fragmented enterprise integrations, duplicated code
**Solution**: All systems expose MCP servers; all agents use MCP clients

```
Traditional Approach:
Agent → Custom Connector 1 → EHR
     → Custom Connector 2 → JIRA
     → Custom Connector 3 → SharePoint
     (N different integration patterns)

MCP Approach:
Agent → MCP Client → MCP Protocol → MCP Server (EHR)
                                  → MCP Server (JIRA)
                                  → MCP Server (SharePoint)
     (One universal protocol)
```

**Benefits**:
- Single integration pattern
- Reusable across all agents
- Versioned, discoverable
- Security at protocol level
- Easy to add new systems

### Pattern 2: Self-Verification First
**Problem**: Human review bottleneck, low-quality agent outputs
**Solution**: Agents validate their own work before requesting human review

```
Old Pattern:
Agent Output → Human Review → Approve/Reject
(100% human review burden)

New Pattern:
Agent Output → Self-Verification Suite → 70% Auto-Approved
                                      → 30% to Human Review
(70-80% reduction in human burden)
```

**Self-Verification Checks**:
1. Policy compliance (against BluePrints)
2. Completeness (all requirements met)
3. Consistency (no contradictions)
4. Confidence (above threshold)
5. Safety (PHI, authorization)

### Pattern 3: Dynamic Agent Loop (Not Workflows)
**Problem**: Brittle, predefined workflows that can't adapt
**Solution**: Autonomous loop that plans, acts, verifies, iterates

```
Workflow (Brittle):
Step 1 → Step 2 → Step 3 → Done
(Fails if Step 2 doesn't work)

Agent Loop (Adaptive):
Goal → Plan → Act → Verify → Iterate
    ↑_____________________________|
(Tries alternatives if action fails)
```

**Example**:
```
Goal: "Schedule team meeting"
  ↓
Attempt 1: Check everyone's calendar
  ├─ Tool fails (calendar API down)
  └─ Iterate: Try alternative approach
  ↓
Attempt 2: Email team for availability
  ├─ Success: Got responses
  └─ Continue
  ↓
Attempt 3: Book conference room
  ├─ Room unavailable
  └─ Iterate: Find alternative room
  ↓
Success: Meeting scheduled
```

### Pattern 4: Context as a Budget
**Problem**: Context overflow, important data lost, poor performance
**Solution**: Treat context as managed resource with budgets and compaction

```
Context Management:
├─ Total Budget: 200K tokens
├─ Always-Loaded: 12K (fixed allocation)
├─ Dynamic Pool: 188K (flexible)
└─ Emergency Reserve: 8K

Triggers:
├─ 80% → Start compaction prep
├─ 90% → Aggressive compaction
└─ 95% → Emergency procedures

Compaction Strategy:
├─ Summarize conversations (10:1)
├─ Compress tool results
├─ Move to long-term memory
└─ Keep safety-critical data
```

### Pattern 5: Multi-Agent Orchestration
**Problem**: Single agent can't handle breadth-heavy or parallel tasks efficiently
**Solution**: Lead agent spawns specialized worker agents

```
Complex Task: "Analyze Q4 performance across all departments"
    ↓
Lead Agent (Orchestrator)
    ├─ Spawns Worker 1: Finance analysis
    ├─ Spawns Worker 2: Operations analysis  
    ├─ Spawns Worker 3: Sales analysis
    └─ Spawns Worker 4: Customer satisfaction analysis
    ↓
Parallel Execution (faster)
    ↓
Lead Agent Integrates Results
    ↓
Final Report
```

**When to Use**:
- Breadth-heavy tasks (multiple domains)
- Time constraints (need speed)
- Cross-domain evidence gathering
- Isolation of concerns for safety

**Limits**:
- Cap fan-out (max 5-10 workers)
- Enforce budgets per worker
- Aggregate confidence scores
- Fail fast on weak signals

---

## Implementation Modules

Based on the architecture, here are the primary implementation modules:

### Module 1: Core Agent Runtime
```
geisinger-agent-core/
├─ orchestrator/
│  ├─ agent_loop.py
│  ├─ planner.py
│  ├─ executor.py
│  └─ verifier.py
├─ memory/
│  ├─ working_memory.py
│  ├─ long_term_memory.py
│  ├─ context_manager.py
│  └─ compaction_service.py
└─ config/
   ├─ meta_blueprint.yaml
   └─ agent_config.yaml
```

### Module 2: Tool Framework & MCP Integration
```
geisinger-tools/
├─ registry/
│  ├─ tool_registry.py
│  ├─ tool_spec.yaml
│  └─ registry_api.py
├─ mcp/
│  ├─ mcp_client.py
│  ├─ mcp_server_base.py
│  └─ protocol_handlers.py
├─ discovery/
│  ├─ tool_discovery.py
│  └─ capability_matcher.py
└─ execution/
   ├─ tool_executor.py
   ├─ parallel_executor.py
   └─ result_cache.py
```

### Module 3: MCP Servers (Enterprise Connectors)
```
geisinger-mcp-servers/
├─ ehr_server/
│  ├─ mcp_ehr_server.py
│  ├─ ehr_client.py
│  └─ server_config.yaml
├─ jira_server/
│  ├─ mcp_jira_server.py
│  ├─ jira_client.py
│  └─ server_config.yaml
├─ sharepoint_server/
│  └─ ...
└─ shared/
   ├─ auth_handler.py
   ├─ rate_limiter.py
   └─ audit_logger.py
```

### Module 4: Perceptions System
```
geisinger-perceptions/
├─ push/
│  ├─ event_listener.py
│  ├─ alert_processor.py
│  └─ stream_handlers.py
├─ pull/
│  ├─ query_engine.py
│  ├─ search_service.py
│  └─ aggregation_service.py
└─ integration/
   └─ perception_router.py
```

### Module 5: Interaction Layer
```
geisinger-interactions/
├─ conversation/
│  ├─ chat_interface.py
│  ├─ dialogue_manager.py
│  └─ clarification_handler.py
├─ recommendations/
│  ├─ proactive_recommender.py
│  └─ justification_builder.py
└─ explainability/
   ├─ reasoning_tracer.py
   ├─ citation_manager.py
   └─ confidence_explainer.py
```

### Module 6: Knowledge Management
```
geisinger-knowledge/
├─ domain_kb/
│  ├─ policy_store.py
│  ├─ guideline_store.py
│  ├─ procedure_store.py
│  └─ knowledge_api.py
├─ blueprints/
│  ├─ blueprint_loader.py
│  ├─ blueprint_composer.py
│  ├─ clinical_bp.yaml
│  ├─ legal_bp.yaml
│  └─ product_bp.yaml
└─ versioning/
   └─ knowledge_version_control.py
```

### Module 7: HITL System
```
geisinger-hitl/
├─ verification/
│  ├─ self_verification_suite.py
│  ├─ policy_checker.py
│  ├─ completeness_checker.py
│  └─ consistency_checker.py
├─ approval/
│  ├─ tier_classifier.py
│  ├─ approval_queue.py
│  └─ feedback_integrator.py
└─ ui/
   ├─ approval_dashboard.py
   └─ batch_approval_ui.py
```

### Module 8: Safety & Guardrails
```
geisinger-safety/
├─ input_validation/
│  ├─ sanitizer.py
│  ├─ prompt_injection_detector.py
│  └─ type_validator.py
├─ execution_monitoring/
│  ├─ real_time_monitor.py
│  └─ anomaly_detector.py
├─ output_validation/
│  ├─ output_checker.py
│  └─ phi_scanner.py
└─ audit/
   ├─ audit_logger.py
   └─ compliance_reporter.py
```

### Module 9: Evaluation Harness
```
geisinger-evaluation/
├─ golden_tests/
│  ├─ clinical_golden_tests.py
│  ├─ legal_golden_tests.py
│  └─ product_golden_tests.py
├─ safety_tests/
│  ├─ prompt_injection_tests.py
│  ├─ data_leakage_tests.py
│  └─ authorization_tests.py
├─ regression_tests/
│  ├─ regression_suite.py
│  └─ bug_to_test_mapper.py
├─ performance_tests/
│  ├─ latency_benchmarks.py
│  └─ resource_benchmarks.py
├─ red_team/
│  ├─ adversarial_prompting.py
│  └─ tool_abuse_tests.py
└─ shadow_testing/
   ├─ shadow_runner.py
   └─ response_comparator.py
```

### Module 10: Observability & Metrics
```
geisinger-observability/
├─ metrics/
│  ├─ metrics_collector.py
│  ├─ metrics_aggregator.py
│  └─ metrics_exporter.py
├─ tracing/
│  ├─ execution_tracer.py
│  └─ decision_tracer.py
├─ dashboard/
│  ├─ real_time_dashboard.py
│  └─ trend_analyzer.py
└─ alerting/
   ├─ alert_manager.py
   └─ escalation_handler.py
```

### Module 11: Cross-Cutting Concerns
```
geisinger-shared/
├─ security/
│  ├─ rbac_manager.py
│  ├─ consent_manager.py
│  ├─ encryption_service.py
│  └─ token_manager.py
├─ config/
│  ├─ environment_config.py
│  └─ feature_flags.py
└─ utils/
   ├─ token_counter.py
   ├─ error_handler.py
   └─ retry_logic.py
```

---

## Deployment Considerations

### Infrastructure Requirements

#### Compute
```
Production Agent Runtime:
├─ CPU: 4-8 cores
├─ Memory: 16-32 GB
├─ GPU: Optional (for model inference)
└─ Instances: 3+ (HA)

MCP Servers (per server):
├─ CPU: 2-4 cores
├─ Memory: 4-8 GB
└─ Instances: 2+ (HA)

Evaluation Harness:
├─ CPU: 8-16 cores
├─ Memory: 32-64 GB
└─ Instances: Dedicated test cluster
```

#### Storage
```
Short-Term (Redis/Memory):
├─ Working Memory: 10 GB per agent
├─ Tool Results Cache: 5 GB per agent
└─ Session State: 2 GB per agent

Long-Term (Database):
├─ Persistent Memory: PostgreSQL
├─ Audit Logs: Time-series DB
├─ Knowledge Base: Document store
└─ Metrics: Prometheus/InfluxDB
```

#### Network
```
Internal:
├─ Agent ↔ MCP Servers: Low latency (<10ms)
├─ MCP Servers ↔ Enterprise Systems: <50ms
└─ Agent ↔ Memory Store: <5ms

External:
└─ Anthropic API: Internet access (for model inference)
```

### Deployment Topology

#### Option 1: Kubernetes (Recommended)
```yaml
Namespaces:
├─ geisinger-agents-prod
├─ geisinger-agents-staging
├─ geisinger-mcp-servers
├─ geisinger-eval-harness
└─ geisinger-monitoring

Components:
├─ Agent Pods (StatefulSet, 3 replicas)
├─ MCP Server Pods (Deployment, 2+ replicas each)
├─ Memory Store (Redis, 3 replicas)
├─ Knowledge Base (PostgreSQL, HA)
└─ Metrics (Prometheus + Grafana)
```

#### Option 2: Azure (Native)
```
Resource Groups:
├─ RG-Geisinger-Agents-Prod
├─ RG-Geisinger-MCP-Servers
└─ RG-Geisinger-Data

Services:
├─ Azure Container Instances (Agents)
├─ Azure Kubernetes Service (MCP Servers)
├─ Azure Cache for Redis (Memory)
├─ Azure Database for PostgreSQL (Knowledge)
└─ Azure Monitor (Observability)
```

### Security Zones

```
Zone 1: Public (Internet-facing)
└─ Conversational UI (with auth)

Zone 2: Application (DMZ)
├─ Agent Runtime
└─ Interaction Layer

Zone 3: Services (Internal)
├─ MCP Clients
├─ Memory Management
└─ Knowledge Management

Zone 4: Integration (Restricted)
├─ MCP Servers
└─ Tool Execution

Zone 5: Data (Highly Restricted)
├─ Enterprise Systems (EHR, etc.)
└─ PHI/PII Data Stores

Firewall Rules:
├─ Zone 1 → Zone 2: HTTPS only
├─ Zone 2 → Zone 3: Internal API
├─ Zone 3 → Zone 4: MCP Protocol
├─ Zone 4 → Zone 5: Encrypted, audited
└─ No Zone 5 → Any (no outbound)
```

### Environment Strategy

```
Development:
├─ Synthetic data only
├─ Mock MCP servers
├─ Local evaluation harness
└─ No PHI

Staging:
├─ De-identified data
├─ Partial MCP servers (non-prod endpoints)
├─ Full evaluation harness
└─ Shadow testing enabled

Production:
├─ Real data (PHI)
├─ All MCP servers
├─ Continuous evaluation
├─ Full monitoring & alerting
└─ HITL enforced
```

---

## Deployment Phases (Recommended)

### Phase 1: Foundation (Months 1-2)
**Goal**: Build testable core components

```
Deliverables:
├─ Module 1: Core Agent Runtime
├─ Module 2: Tool Framework (basic)
├─ Module 7: HITL System (Tier 3/4 only)
├─ Module 8: Safety & Guardrails (basic)
└─ Module 9: Evaluation Harness (golden tests)

First Domain: Product Management (non-PHI)
├─ JIRA MCP Server
├─ GitHub MCP Server
└─ Product Management BluePrints

Validation:
└─ Run 10 golden tests, achieve 90% pass rate
```

### Phase 2: Memory & Context (Month 3)
**Goal**: Implement sophisticated context management

```
Deliverables:
├─ Working memory implementation
├─ Long-term memory store
├─ Context budget management
└─ Auto-compaction service

Validation:
├─ Handle 50-turn conversations
├─ Stay within 200K token budget
└─ Maintain >90% recall after compaction
```

### Phase 3: Enhanced Tools & MCP (Month 4)
**Goal**: Scale MCP integration

```
Deliverables:
├─ 5+ MCP servers operational
├─ Tool discovery engine
├─ Parallel execution
└─ Advanced tool registry

Validation:
├─ Execute 3+ tools in parallel
├─ Tool discovery works for new additions
└─ All MCP servers pass safety tests
```

### Phase 4: Clinical Read-Only (Months 5-6)
**Goal**: Deploy first clinical agent (no writes)

```
Deliverables:
├─ EHR MCP Server (read-only)
├─ Clinical BluePrints
├─ Enhanced PHI protection
└─ Clinical golden test suite

Constraints:
├─ Zero write operations
├─ Strict citations required
├─ Tier 2-3 HITL only

Validation:
└─ Zero PHI leakage in 1000 test runs
```

### Phase 5: Multi-Agent & Legal (Month 7)
**Goal**: Orchestration and second domain

```
Deliverables:
├─ Multi-agent orchestrator
├─ Legal domain MCP servers
├─ Legal BluePrints
└─ Parallel task execution

Use Case: Contract analysis
├─ Spawn 3 workers (compliance, risk, financial)
├─ Integrate results
└─ Tier 3 approval for recommendations

Validation:
└─ 2x faster than single-agent approach
```

### Phase 6: Limited Writes (Month 8-9)
**Goal**: Enable reversible write operations

```
Deliverables:
├─ Write-capable MCP servers
├─ Enhanced self-verification
├─ Rollback mechanisms
└─ Tier 4 HITL enforcement

Allowed Actions:
├─ Draft document generation
├─ Calendar scheduling
├─ Email sending
└─ Ticket creation

Constraints:
├─ All writes require approval
├─ Rollback tested for each action
└─ Enhanced audit logging

Validation:
└─ Zero unauthorized writes in shadow testing
```

### Phase 7: Production Scale (Month 10-12)
**Goal**: Enterprise-wide deployment

```
Deliverables:
├─ HA deployment (Kubernetes)
├─ Full observability stack
├─ Continuous evaluation pipeline
├─ Self-service agent creation
└─ Performance optimization

Scale Targets:
├─ Support 100+ concurrent agents
├─ Handle 10,000 requests/day
├─ Maintain <2s p99 latency
└─ >99.9% availability

Validation:
└─ Pass load testing at 2x expected traffic
```

---

## Success Criteria

### Technical Metrics
```
Performance:
├─ Agent Loop Latency: p99 < 15s
├─ Tool Execution: p99 < 1s
├─ Context Management: Compaction < 500ms
└─ Throughput: >100 QPS

Quality:
├─ Golden Test Pass Rate: >90%
├─ Self-Verification Accuracy: >85%
├─ Regression Rate: <1% per release
└─ User Approval Rate: >80%

Safety:
├─ PHI Leakage: 0 incidents
├─ Prompt Injection: 100% blocked
├─ Authorization Violations: 0 incidents
└─ Audit Trail: 100% coverage
```

### Business Metrics
```
Efficiency:
├─ Human Review Reduction: >70%
├─ Task Completion Speed: 3x faster
├─ Error Rate: <5%
└─ Cost per Task: <$0.50

Adoption:
├─ Active Users: 100+ in 6 months
├─ Domains Deployed: 3+ in 12 months
├─ Satisfaction Score: >4.0/5
└─ Reuse Rate: >70% of components
```

---

## Conclusion

This architecture provides:

✅ **True Agency** - Agents that dynamically plan and adapt, not workflows
✅ **Safety by Design** - Multi-layer defense with self-verification
✅ **Scalable Foundation** - MCP-based integration, reusable components
✅ **Efficient Oversight** - 70-80% reduction in human review burden
✅ **Domain Agnostic** - Same core works across clinical, legal, product, etc.
✅ **Transparent & Auditable** - Complete traceability and explainability
✅ **Incremental Deployment** - Build, test, learn, scale

**The Geisinger Way**: *Small steps, testable outcomes, trusted agents.*

---

## Next Steps

1. **Review with stakeholders** - AVP of AI, Security, Compliance, Domain leads
2. **Prioritize domains** - Start with non-PHI (Product) then Clinical read-only
3. **Establish tooling** - ADO templates, CI/CD pipelines, monitoring dashboards
4. **Build core team** - Assign owners per module (see Implementation Modules)
5. **Create 30/60/90 roadmap** - Break down phases into concrete epics
6. **Set up governance** - Weekly architecture reviews, monthly red team tests

**Key Principle**: Ship small, testable slices every 2 weeks. Each must pass golden tests, safety tests, and gain human approval before proceeding.

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Owner**: Senior Architect AI
**Review Cycle**: Bi-weekly with AVP of AI
