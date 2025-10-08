# AI Product Manager Agent (v0.1.0)
## Geisinger's First Production Agent - Program Intake & Governance Assistant

> **Project Status**: Phase 1 - Foundation (In Development)
> **Domain**: Product Management (Non-PHI)
> **Risk Tier**: Tier 2-3 (Medium - requires human approval for key actions)
> **Technology**: Python 3.11+ with Anthropic's `claude-agent-sdk`

---

## 🚀 Quick Start

```bash
# 1. Clone and enter repository
cd ai-pm

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
make dev-install

# 4. Setup environment
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and other credentials

# 5. Start database
make db-up

# 6. Run migrations
make db-migrate

# 7. Seed sample data (optional)
make db-seed

# 8. Run the agent
python src/main.py interactive
```

---

## 🎯 Project Overview

The AI Product Manager Agent assists Program Owners in navigating Geisinger's AI program intake and governance process. It transforms complex ServiceNow intake tickets into structured documentation, guides contract negotiations, and ensures compliance with AI governance policies.

**Built with Anthropic's `claude-agent-sdk`** - Extended with custom Geisinger components for BluePrints, HITL governance, and self-verification.

### What This Agent Does

**Primary Function**: Guide AI program initiatives from intake through deployment

**Key Capabilities**:
1. **ServiceNow Intake Processing** → Structured Intake Brief (24-48 hours)
2. **AI Discovery Form Generation** → Comprehensive program documentation
3. **Risk Assessment & Guardrails** → Automated risk screening + mitigation plans
4. **Design & Monitoring Support** → Pilot design, equity assessments, dashboards

**What Makes This "Agentic"**:
- ✅ Dynamically plans approach based on ticket content
- ✅ Iterates when information is incomplete
- ✅ Self-verifies outputs against governance policies
- ✅ Adapts strategy based on risk level
- ❌ NOT a rigid workflow - makes decisions autonomously

---

## 🏗️ Architecture Alignment

This project implements the **Geisinger Agentic Architecture v1.0** with simplified components for Phase 1.

### Implemented Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 8: Meta-Blueprint (Universal Safety)              │
│  ✓ AI Governance Policy                                  │
│  ✓ Transparency Requirements                             │
│  ✓ Equity Standards                                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Core Agent Runtime                             │
│  ✓ Agent Loop (Gather → Plan → Act → Verify → Iterate) │
│  ✓ Basic Planner (step-by-step execution)               │
│  ✓ Executor (tool orchestration)                         │
│  ✓ Self-Verifier (policy compliance checks)              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Memory & Context Management                    │
│  ✓ Working Memory (PostgreSQL session state)             │
│  ✓ Context Budget Manager (simplified)                   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Tool Framework                                 │
│  ✓ ServiceNow Ticket Retrieval                          │
│  ✓ Document Generation (Brief, Discovery Form)           │
│  ✓ Risk Assessment Calculator                            │
│  ✓ Template Population Engine                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 6: Interaction Layer                              │
│  ✓ Conversational UI (chat-based)                        │
│  ✓ Approval Interactions (Approve/Deny/Modify)           │
│  ✓ Explanation Interface (show reasoning)                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 7: Domain Knowledge (Product Management)          │
│  ✓ AI Governance Policy (Blueprint)                      │
│  ✓ Intake Process Guidelines                             │
│  ✓ Risk Assessment Rules (5-question screener)           │
│  ✓ Document Templates                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 9: HITL Governance                                │
│  ✓ Self-Verification (policy compliance)                 │
│  ✓ Tier Classification (Tier 2-3 for this agent)        │
│  ✓ Approval Required for: Document submission,           │
│                            Risk determinations            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  LAYER 10: Safety & Guardrails                           │
│  ✓ Input Validation (SNOW ticket format)                 │
│  ✓ Output Validation (document completeness)             │
│  ✓ Audit Logging (all actions logged)                    │
└─────────────────────────────────────────────────────────┘
```

### Simplified for Phase 1

**What We're NOT Building Yet**:
- ❌ MCP integration (using direct API calls instead)
- ❌ Vector databases (using structured PostgreSQL only)
- ❌ Multi-agent orchestration (single agent only)
- ❌ Advanced perceptions (basic pull-only)
- ❌ Clinical domain features

**Focus Areas**:
- ✅ **Agent Loop**: Get the core iteration pattern working
- ✅ **Self-Verification**: Build the policy compliance checks
- ✅ **Tool Execution**: Implement 5-7 basic tools
- ✅ **HITL Interactions**: Approval UI for document review
- ✅ **BluePrint Loading**: Product management policies

---

## 📋 Available Commands

```bash
make help              # Show all available commands
make dev-install       # Install development dependencies
make test              # Run all tests
make test-golden       # Run golden tests only
make lint              # Run linters (flake8, mypy)
make format            # Format code (black, isort)
make db-up             # Start PostgreSQL
make db-migrate        # Run database migrations
make db-seed           # Load sample data
make run               # Run agent interactively
```

---

## 🗂️ Project Structure

```
ai-pm/
├── README.md                          # This file
├── CLAUDE.md                          # Instructions for Claude Code
├── docs/
│   ├── architecture/                  # Architecture documentation
│   │   ├── geisinger-architecture-explanation.md
│   │   ├── geisinger-module-design.md
│   │   ├── geisinger-quick-reference.md
│   │   └── refined-hitl-interaction-architecture.md
│   ├── blueprints/                    # Policy files
│   │   ├── meta-blueprint.yaml        # Universal safety rules
│   │   └── product-mgmt-blueprint.yaml # Product management domain
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py            # Main agent loop
│   │   ├── planner.py                 # Task planning
│   │   ├── executor.py                # Tool execution
│   │   └── verifier.py                # Self-verification
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── working_memory.py          # Session state
│   │   ├── database.py                # PostgreSQL interface
│   │   └── context_manager.py         # Context budget
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tool_registry.py           # Tool catalog
│   │   ├── servicenow_client.py       # SNOW integration
│   │   ├── document_generator.py      # Template population
│   │   ├── risk_assessor.py           # Risk screening
│   │   └── vendor_scanner.py          # Vendor research
│   ├── interaction/
│   │   ├── __init__.py
│   │   ├── chat_ui.py                 # Conversational interface
│   │   ├── approval_ui.py             # HITL approval dialogs
│   │   └── explainer.py               # Reasoning display
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── blueprint_loader.py        # Load policies
│   │   └── templates/
│   │       ├── intake_brief.md        # Brief template
│   │       ├── discovery_form.md      # Discovery template
│   │       └── risk_mitigation.md     # Risk plan template
│   ├── governance/
│   │   ├── __init__.py
│   │   ├── self_verification.py       # Policy checks
│   │   ├── tier_classifier.py         # Risk tier determination
│   │   └── audit_logger.py            # Action logging
│   └── main.py                        # Application entry point
├── tests/
│   ├── golden/
│   │   ├── test_intake_processing.py  # Golden test: Process SNOW ticket
│   │   ├── test_discovery_form.py     # Golden test: Generate discovery form
│   │   └── test_risk_assessment.py    # Golden test: Risk screening
│   ├── unit/
│   │   └── ...                        # Unit tests per component
│   └── integration/
│       └── ...                        # End-to-end tests
├── database/
│   ├── migrations/
│   │   └── 001_initial_schema.sql     # Database schema
│   └── seeds/
│       └── sample_initiatives.sql     # Sample data
├── config/
│   ├── development.yaml               # Dev config
│   ├── staging.yaml                   # Staging config
│   └── production.yaml                # Prod config
├── requirements.txt                   # Python dependencies
├── docker-compose.yml                 # Local development stack
└── .env.example                       # Environment variables template
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose (for local dev)
- Access to ServiceNow API (credentials required)
- Anthropic API key (for Claude)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/geisinger/ai-product-manager-agent.git
cd ai-product-manager-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# 5. Start local services (PostgreSQL)
docker-compose up -d

# 6. Run database migrations
python -m alembic upgrade head

# 7. Seed sample data
psql -h localhost -U postgres -d ai_pm_agent -f database/seeds/sample_initiatives.sql

# 8. Run the agent
python src/main.py
```

### First Run

```bash
# Interactive mode
python src/main.py --interactive

# Process specific SNOW ticket
python src/main.py --ticket INC0012345

# Run with specific initiative
python src/main.py --initiative "Epic AI Inbox Prioritization"
```

---

## 📊 Database Schema

### Core Tables

#### `initiatives`
Tracks AI program initiatives from intake to deployment

```sql
CREATE TABLE initiatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    snow_ticket VARCHAR(50) UNIQUE,
    program_owner VARCHAR(255),
    department VARCHAR(255),
    status VARCHAR(50), -- intake, discovery, risk_assessment, design, pilot, production
    risk_tier VARCHAR(20), -- low, medium, high, significant
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `agent_sessions`
Tracks agent execution sessions

```sql
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiative_id UUID REFERENCES initiatives(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    status VARCHAR(50), -- active, completed, failed, escalated
    iteration_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0
);
```

#### `agent_actions`
Audit log of all agent actions

```sql
CREATE TABLE agent_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent_sessions(id),
    action_type VARCHAR(100), -- plan, execute_tool, verify, iterate
    tool_used VARCHAR(100),
    input JSONB,
    output JSONB,
    verification_result JSONB,
    hitl_required BOOLEAN DEFAULT FALSE,
    hitl_tier VARCHAR(10), -- tier_1, tier_2, tier_3, tier_4
    approved BOOLEAN,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### `documents`
Generated documents (briefs, forms, plans)

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    initiative_id UUID REFERENCES initiatives(id),
    document_type VARCHAR(100), -- intake_brief, discovery_form, risk_plan, etc.
    content TEXT,
    version INTEGER DEFAULT 1,
    status VARCHAR(50), -- draft, pending_review, approved, revised
    created_by VARCHAR(50) DEFAULT 'agent',
    reviewed_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Agent Workflows

### Workflow 1: ServiceNow Intake → Intake Brief

**User Action**: Selects initiative from list or provides SNOW ticket number

**Agent Execution**:

```
1. GATHER Context
   ├─ Load initiative from database
   ├─ Retrieve SNOW ticket via API
   └─ Load AI Governance Blueprint

2. PLAN Approach
   ├─ Determine which fields need extraction
   ├─ Identify information gaps
   └─ Select tools: [snow_parser, vendor_scanner, risk_screener]

3. ACT (Execute Tools)
   ├─ snow_parser: Extract structured fields
   ├─ vendor_scanner: Research vendor (if mentioned)
   ├─ risk_screener: Run 5-question assessment
   └─ document_generator: Populate intake brief template

4. VERIFY Output
   ├─ Check: All required fields populated?
   ├─ Check: Risk assessment complete?
   ├─ Check: Evidence sources cited?
   └─ Self-confidence: 85% (good)

5. ITERATE (if needed)
   ├─ If fields missing → Request info from user
   ├─ If vendor unclear → Run additional search
   └─ If confident → Present to user

6. HITL Approval (Tier 3)
   ┌─────────────────────────────────────────────┐
   │ I've created the Intake Brief:               │
   │                                              │
   │ • Program: Epic AI Inbox Prioritization      │
   │ • Requestor: Dr. Smith (Cardiology)          │
   │ • Problem: 200+ inbox messages per day       │
   │ • Risk Level: Medium (patient impact)        │
   │                                              │
   │ Summary: 8/10 sections complete              │
   │ Confidence: 85%                              │
   │                                              │
   │ [View Full Brief] [Approve] [Modify]        │
   └─────────────────────────────────────────────┘

7. User Approves → Save document, notify stakeholders
```

### Workflow 2: Draft AI Discovery Form

**Trigger**: Intake Brief approved → Agent automatically proceeds

**Agent Execution**:

```
1. GATHER Context
   ├─ Load approved Intake Brief
   ├─ Load previous initiative examples (similar programs)
   └─ Load Discovery Form template

2. PLAN Approach
   ├─ Identify which sections can be auto-populated
   ├─ Identify which need SME input
   └─ Select tools: [template_populator, workflow_analyzer, metric_designer]

3. ACT (Execute Tools)
   ├─ template_populator: Fill known fields from brief
   ├─ workflow_analyzer: Draft workflow integration plan
   ├─ metric_designer: Propose success metrics
   └─ document_generator: Create complete form

4. VERIFY Output
   ├─ Check: All required sections present?
   ├─ Check: Workflow diagram logical?
   ├─ Check: Metrics measurable?
   ├─ Check: Aligned with AI Governance Policy?
   └─ Self-confidence: 78% (needs review)

5. ITERATE
   ├─ Flag: "Technical integration section incomplete"
   ├─ Action: Draft placeholder + note for Program Owner
   └─ Continue

6. HITL Approval (Tier 3)
   ┌─────────────────────────────────────────────┐
   │ Discovery Form Draft Ready                   │
   │                                              │
   │ Completed: 12/15 sections (80%)              │
   │ Needs Input: Technical integration details   │
   │                                              │
   │ I'll send to:                                │
   │ • Program Owner (Dr. Smith) for review       │
   │ • AI Subcommittee for approval               │
   │                                              │
   │ Note: Marked "Equity Audit Required" based   │
   │ on patient impact analysis                   │
   │                                              │
   │ [Review Form] [Send to Owner] [Modify]      │
   └─────────────────────────────────────────────┘

7. User Sends → Email notifications, update status
```

### Workflow 3: Risk Assessment & Guardrails

**Trigger**: Discovery Form submitted → Risk determination needed

**Agent Execution**:

```
1. GATHER Context
   ├─ Load Discovery Form
   ├─ Load Risk Screener results (5 questions)
   └─ Load Significant Risk criteria

2. PLAN Approach
   ├─ Determine: Significant Risk AI or not?
   ├─ If YES → Trigger enhanced documentation
   └─ Select tools: [risk_calculator, guardrail_generator]

3. ACT
   ├─ risk_calculator: Analyze impact, autonomy, reversibility
   ├─ Decision: SIGNIFICANT RISK AI → Yes
   ├─ guardrail_generator: Generate required artifacts:
   │   ├─ Transparency Package template
   │   ├─ HITL Plan template
   │   ├─ Monitoring Plan template
   │   ├─ Equity KPI framework
   │   └─ Vendor mitigation checklist

4. VERIFY
   ├─ Check: Classification aligned with policy?
   ├─ Check: All required artifacts generated?
   └─ Self-confidence: 92% (high)

5. HITL Approval (Tier 4 - Critical Decision)
   ┌─────────────────────────────────────────────┐
   │ ⚠️ SIGNIFICANT RISK AI DETERMINATION        │
   │                                              │
   │ Classification: SIGNIFICANT RISK             │
   │                                              │
   │ Reasoning:                                   │
   │ ✓ Affects patient care decisions (Q1: Yes)  │
   │ ✓ Operates autonomously (Q2: Yes)            │
   │ ✓ Limited reversibility (Q4: Partial)        │
   │                                              │
   │ Required Actions:                            │
   │ • Enhanced transparency documentation        │
   │ • Human-in-the-loop checkpoints              │
   │ • Equity audit with subgroup analysis        │
   │ • Ongoing monitoring dashboard               │
   │                                              │
   │ This classification requires AVP approval    │
   │                                              │
   │ [Review Analysis] [Approve] [Override]      │
   └─────────────────────────────────────────────┘

6. AVP Approves → Generate all required documents
```

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_pm_agent
SERVICENOW_API_URL=https://geisinger.service-now.com/api/now
SERVICENOW_API_KEY=...
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Agent Configuration

```yaml
# config/development.yaml
agent:
  model: claude-sonnet-4-5-20250929
  max_iterations: 10
  confidence_threshold: 0.7
  
  context_budget:
    total_tokens: 200000
    working_memory: 50000
    blueprints: 20000
    reasoning: 40000
  
  self_verification:
    enabled: true
    checks:
      - policy_compliance
      - completeness
      - consistency
      - quality

hitl:
  tier_mapping:
    document_draft: tier_2
    document_submit: tier_3
    risk_determination: tier_4
    
tools:
  servicenow:
    timeout: 30
    retry_attempts: 3
  
  document_generator:
    output_format: markdown
    citation_required: true
```

---

## 🧪 Testing

### Golden Tests (Must Pass Before Release)

```bash
# Run all golden tests
pytest tests/golden/ -v

# Run specific workflow
pytest tests/golden/test_intake_processing.py -v

# Expected output:
# ✓ test_process_snow_ticket_to_brief
# ✓ test_brief_contains_all_required_fields
# ✓ test_risk_screener_identifies_high_risk
# ✓ test_agent_iterates_on_missing_info
```

### Golden Test: Process SNOW Ticket

```python
def test_process_snow_ticket_to_brief():
    """
    Golden Test: Agent processes SNOW ticket and creates Intake Brief
    
    Success Criteria:
    - Brief generated in <5 minutes
    - All required fields populated
    - Risk assessment complete
    - Vendor info researched (if applicable)
    - Self-verification passes
    - User can approve/modify
    """
    # Setup
    agent = AgentOrchestrator(config)
    snow_ticket = "INC0012345"  # Test ticket
    
    # Execute
    result = agent.execute_task(
        Task(
            description=f"Process SNOW ticket {snow_ticket} and create Intake Brief",
            initiative_id=test_initiative_id
        )
    )
    
    # Verify
    assert result.status == "SUCCESS"
    assert result.requires_approval == True
    assert result.hitl_tier == "TIER_3"
    
    brief = result.output["intake_brief"]
    assert brief.get("program_title")
    assert brief.get("requestor")
    assert brief.get("problem_statement")
    assert brief.get("risk_level") in ["low", "medium", "high", "significant"]
    assert brief.get("workflow_guess")
    assert brief.get("success_metric")
    
    # Verify self-checks passed
    assert result.verification.passed == True
    assert result.verification.confidence_score >= 0.7
```

---

## 📈 Success Metrics

### Agent Performance

- **Intake Brief Generation**: <2 hours from ticket assignment
- **Discovery Form Draft**: <24 hours from intake approval
- **Self-Verification Accuracy**: >85% (measured against human review)
- **Human Review Burden**: Reduce by 60% (vs. manual process)
- **Iteration Count**: Average <3 iterations per task

### Business Impact

- **Intake Processing Time**: Reduce from 5 days → 2 days
- **Documentation Quality**: 90% of drafts require <2 revisions
- **Compliance Rate**: 100% adherence to AI Governance Policy
- **User Satisfaction**: >4.0/5.0 (Program Owner feedback)

---

## 🚦 Deployment Plan

### Phase 1: Internal Pilot (Weeks 1-4)
- Deploy to 5 test initiatives
- Product Management team only
- Enhanced monitoring
- Manual approval for all actions

### Phase 2: Controlled Rollout (Weeks 5-8)
- Expand to 20 initiatives
- Multi-department (IT, Clinical, Operations)
- Tier 2 actions auto-approved
- Weekly review meetings

### Phase 3: Full Production (Weeks 9-12)
- Available for all new AI initiatives
- Self-service initiative selection
- Automated notifications
- Dashboard reporting

---

## 🔐 Security & Compliance

### Data Handling
- **No PHI**: This agent handles program metadata only (non-PHI)
- **Access Control**: RBAC via Azure AD integration
- **Audit Trail**: All actions logged to `agent_actions` table
- **Encryption**: Database encrypted at rest, TLS in transit

### Governance Alignment
- **AI Governance Policy**: Embedded in Meta-Blueprint
- **Significant Risk Criteria**: 5-question screener implemented
- **Equity Requirements**: Flagged automatically where applicable
- **Transparency**: All reasoning chains saved and explainable

---

## 🤝 Contributing

See [CLAUDE.md](CLAUDE.md) for instructions on how Claude should work on this codebase.

### Development Workflow

1. Create feature branch from `main`
2. Implement feature with tests
3. Run golden tests: `pytest tests/golden/`
4. Run safety tests: `pytest tests/safety/`
5. Update documentation
6. Submit PR with:
   - Description of changes
   - Test results
   - Blueprint compliance verification

---

## 📚 Additional Documentation

- [Architecture Deep Dive](docs/architecture.md)
- [Agent Flow Diagrams](docs/agent-flow.md)
- [Blueprint Specifications](docs/blueprints/)
- [API Reference](docs/api.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

---

## 🆘 Support

- **Technical Issues**: Create GitHub issue
- **Architecture Questions**: Contact AI Architecture Team
- **Urgent Issues**: Slack #ai-product-manager-agent

---

## 📄 License

Internal use only - Geisinger Health System
© 2025 Geisinger Health System. All rights reserved.

---

**Remember: Small steps, testable outcomes, trusted agents.**

Ship something that passes golden tests every 2 weeks! 🚀
