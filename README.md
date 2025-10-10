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
│  ✓ Azure DevOps Client (Work Items, Boards, Projects)   │
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
│   │   ├── base.py                    # Tool base classes
│   │   ├── tool_registry.py           # Tool catalog
│   │   ├── azure_devops_client.py     # Azure DevOps integration
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

## 📋 AI Discovery Form

The **AI Discovery Form** is a foundational design document used by Geisinger stakeholders to assess proposed AI programs. The agent assists Program Owners in creating comprehensive, high-quality discovery forms that meet governance requirements.

### Purpose

The AI Discovery Form serves as:
- **Comprehensive program documentation** - Captures all essential information about the proposed AI initiative
- **Decision-making tool** - Enables clinical, technical, governance, and executive stakeholders to make informed decisions
- **Governance checkpoint** - Ensures compliance with Geisinger's AI Governance Policy
- **Planning foundation** - Provides the detail necessary for implementation planning

### Form Structure

The AI Discovery Form includes **7 major sections**:

#### 1. Basic Information
- **Title**: Clear, descriptive program title
- **Program Owner**: Individual/team responsible for oversight
- **Executive Champion**: Highest-level advocate and sponsor
- **Department(s)**: Operational ownership
- **AI Vendor or Internal Solution**: Solution source and vendor details

#### 2. Problem Definition
- **Background**: Detailed problem description with current workflow, scope data, and root cause
- **Goal**: Specific objectives including primary outcome, target metrics, timeline, population, and workflow impact
- **AI vs. Alternatives**: Justification for AI over simpler solutions (process improvement, RPA, etc.)

#### 3. Approach
- **Workflow Integration**: Detailed description for each user role:
  - Where/when they interact with AI
  - Inputs they provide
  - Outputs AI provides
  - Actions they may take in response
- **Technical Integration**: System connections, data flow diagram, Epic/EHR build requirements
- **AI Solution Components**:
  - Data sources (specific elements, frequency, format)
  - AI system details (type, prediction, training approach)
  - System outputs (format, visibility, storage)

#### 4. Success Metrics
- **Primary Goal**: Single most important success metric
- **Secondary Metrics**: Clinical outcomes, operational outcomes, process measures
- **Anticipated Benefits**: Expected changes to clinical practice, patient outcomes, and organizational performance

#### 5. Equity Considerations
- **Known Disparities**: Literature review of disparities in clinical area and similar AI solutions
- **Access Barriers**: Groups that might face barriers (language, literacy, digital access, geographic, socioeconomic)
- **Benefit Disparities**: Analysis of differential impact across populations
- **Status Quo Comparison**: Equity implications of current process vs. AI solution
- **Mitigation Plans**: Specific actions to address identified concerns

#### 6. Risk Assessment
For each identified risk:
- Risk description and scenario
- Impact assessment (patient care, legal, financial, operational)
- Likelihood and severity ratings
- Comparison to current process
- Mitigation strategies (prevention, detection, response)

#### 7. Potential Benefits
- **Patient Care Benefits**: Volume impact, specific care improvements (quantified)
- **Operational Benefits**: Efficiency gains, workflow improvements, capacity impact
- **Financial Benefits**: Cost reductions, revenue impact (with calculations)
- **Assumptions**: All assumptions underlying benefit calculations

### Quality Standards

The agent ensures discovery forms meet these criteria:

✅ **Completeness**: All required fields populated with sufficient detail
✅ **Clarity**: Plain language understandable by non-technical stakeholders
✅ **Evidence-Based**: Claims supported by data, calculations shown
✅ **Actionable**: Sufficient detail for stakeholder decision-making

### Agent Assistance

The agent helps create high-quality discovery forms by:

1. **Gathering Information**: Interviewing the user about the AI program, asking clarifying questions
2. **Drafting Content**: Using templates and examples to populate each section
3. **Ensuring Quality**: Verifying completeness, checking calculations, confirming plain language
4. **Iterating**: Reviewing with user, identifying gaps, refining until standards are met

### Review Process

Discovery Forms are reviewed by:
- **Clinical Lead**: Workflow integration, patient safety, clinical benefits
- **IT/Technical Lead**: Technical feasibility, system integration, data requirements
- **Compliance/Legal**: Regulatory compliance, risk assessment, legal implications
- **Equity and Inclusion**: Equity analysis, disparity assessment, access considerations
- **Finance**: Cost-benefit analysis, financial projections, ROI
- **Executive Sponsor**: Strategic alignment, resource allocation, final approval

### Related Documents

- **Blueprint**: `docs/blueprints/ai-discovery-form.yaml` - Complete form specification
- **Template**: Used by document generator tool
- **Examples**: Sample completed forms in `docs/templates/`

---

## 🎓 AI Product Manager Strategy

The agent is equipped with comprehensive strategic framework for AI Product Management, based on Andrew Ng's practical heuristics for high-impact, rapid-iteration AI development. This framework guides all AI program activities from discovery through deployment and scale.

### Mission

**Deliver AI solutions that measurably improve patient outcomes, staff efficiency, and system performance** by embedding intelligent automation and predictive insights directly into operational and clinical workflows.

### Core Mindsets

Seven fundamental principles guide all AI Product Manager activities:

1. **Prototype rapidly → learn through failure**
   - Build fast, fail fast, learn fast
   - Spend days, not weeks on first prototype
   - Treat every prototype as disposable

2. **Anchor on a single measurable metric → guide all iteration**
   - Define success upfront with one primary metric
   - Let data, not opinions, drive decisions
   - Measure metric in every iteration

3. **Analyze errors relentlessly → data, not intuition, drives improvements**
   - Every error is a learning opportunity
   - Classify, count, prioritize, and fix systematically
   - Validate that fixes work as expected

4. **Keep humans in control → safety, accountability, and adoption hinge on it**
   - AI assists, humans decide
   - Design for easy override and clear accountability
   - Track override rates as quality signal

5. **Design for change → data shifts, workflows evolve; AI must too**
   - Build for continuous improvement, not one-time deployment
   - Expect drift, plan for retraining
   - Version all models and data

6. **Empower decision speed → PMs are the bottleneck; reduce drag**
   - Fast decisions beat perfect decisions
   - Reduce approval overhead, enable experimentation
   - Trust teams within guardrails

7. **Celebrate learning → every iteration strengthens institutional capability**
   - Learning compounds
   - Share failures, reward pivots
   - Make it safe to experiment

### AI Product Lifecycle

The framework defines four phases aligned with Andrew Ng's heuristics:

#### 1. Discovery & Ideation (1-4 weeks)
**Objective**: Identify high-value, feasible problems and generate validated hypotheses quickly

**Key Practices**:
- **Rapid Throwaway Prototype**: Build minimal model in days to expose error classes
- **Primary Metric Early**: Choose single "north star" metric before building
- **Structured Error Analysis**: Classify errors, estimate uplift from fixes
- **Human-Level Benchmarking**: Confirm humans can perform task reliably
- **3-Filter Assessment**: Feasibility × ROI × Defensibility
- **Domain-Aligned Data Splits**: Ensure dev/test sets mirror operational reality

**Deliverables**: Problem statement, primary metric, prototype with error analysis, go/no-go recommendation

#### 2. Pilot / Validation (1-3 months)
**Objective**: Test in real-world settings with tight feedback loops

**Key Practices**:
- **Short Realistic Pilots**: Stress boundary cases early; collect telemetry and human feedback
- **Continuous Error Decomposition**: Treat each pilot as diagnostic cycle
- **Metric Adjustment**: Update metrics if they misalign with goals
- **Explicit Human-Machine Handoff**: Define where humans review, override, reject
- **Pilot Metric Guardrails**: Track accuracy, operational impact, safety, and equity

**Deliverables**: Pilot results, error analysis, human feedback, equity analysis, deployment recommendation

#### 3. Deployment / Scale (Ongoing)
**Objective**: Institutionalize solution with observability and continuous improvement

**Key Practices**:
- **Built-in Retraining Cadence**: Architect for periodic model updates
- **Drift Monitoring**: Alert on shifts in feature or label distributions
- **Feedback Ingestion Loop**: Log every human override or AI failure
- **Metric-Level Rollback Guards**: Automatic rollback if primary metric degrades
- **Measure True Impact**: Track operational and clinical outcomes, not just accuracy

**Deliverables**: Deployment plan, monitoring dashboard, retraining pipeline, quarterly reviews

#### 4. Organizational Enablement (Ongoing)
**Objective**: Build environment for PMs to iterate, learn, and deliver safely at speed

**Key Practices**:
- **Train PMs in Ng-Style Thinking**: Embed fast prototyping and error analysis habits
- **Shorten Feedback Loops**: Compress time between prototype, decision, and pilot
- **Empower Decision-Making**: Clear guardrails so PMs can pivot without delays
- **Cross-Functional Error Reviews**: Convene after major misclassifications
- **AI Thinking Reviews at Stage Gates**: Confirm principles before advancing
- **Promote Fast Failure Culture**: Celebrate discovery and learning cycles

### Roles and Responsibilities

The framework defines clear responsibilities for six key roles:

- **AI Product Manager**: Define vision, manage lifecycle, align technology with workflow needs, ensure measurable impact
- **Clinical Lead**: Define problem, own rollout, select KPIs, ensure safety and adoption
- **Data Scientist**: Develop and validate models, conduct error analysis, document per TRIPOD standards
- **MLOps Engineer**: Build CI/CD pipelines, deploy and monitor models, ensure reproducibility
- **Human Factors / UX**: Design intuitive interfaces that integrate naturally into practice
- **Data Manager**: Ensure secure, compliant data handling and metadata governance

### Governance & Metrics

All AI programs must address:

- **Human-in-the-Loop**: Required for all high-risk use cases
- **Equity & Fairness Reviews**: Bias detection across demographic subgroups during pilot and scale
- **Model Monitoring**: Automated alerts for performance drift and governance logs
- **Primary KPI Categories**:
  1. Operational Efficiency (time saved, throughput)
  2. Clinical Quality (accuracy, safety events avoided)
  3. Adoption & Satisfaction (active use rates, feedback)
  4. ROI (financial or capacity impact)

### Related Documents

- **Blueprint**: `docs/blueprints/ai-product-manager-strategy.yaml` - Complete strategic framework
- **Example**: Radiology Nodule Detection Assistant - Full lifecycle example in blueprint
- **Visual Canvas**: ASCII lifecycle canvas for quick reference

---

## 🤖 Product Manager Agent

The **ProductManagerAgent** is the main agent class that orchestrates the entire Discovery process. It implements the 6-step Discovery Workflow and provides the primary interface for processing ServiceNow tickets.

### Overview

```python
from src.agent.pm_agent import ProductManagerAgent

# Initialize agent
config = load_config("config/development.yaml")
agent = ProductManagerAgent(config)

# Process a ServiceNow ticket
result = await agent.process_ticket(ticket_text)

# Access generated form
print(result.form['title'])
print(f"Confidence: {result.confidence:.0%}")
print(f"Steps completed: {result.steps_completed}")
```

### Key Features

**Workflow Execution**:
- Implements complete 6-step Discovery Workflow
- Automatic iteration and self-correction
- Comprehensive observability and tracing

**Research Capabilities**:
- Vendor research (company background, capabilities, healthcare experience)
- Use case research (clinical context, best practices, evidence)
- Knowledge synthesis (combining research into actionable insights)

**Quality Assurance**:
- Self-verification across 5 quality dimensions
- Automatic issue correction
- Confidence scoring for each output

**Observability**:
- Step-by-step execution tracing
- Duration tracking
- Detailed logging of all actions

### Methods

#### `process_ticket(ticket_text: str) -> ProcessingResult`

Main entry point for processing ServiceNow tickets. Executes the full Discovery Workflow.

**Arguments**:
- `ticket_text`: Raw ServiceNow ticket text or user description

**Returns**: `ProcessingResult` containing:
- `form`: Complete AI Discovery Form (7 sections)
- `trace_id`: Unique trace identifier
- `verification`: Quality verification results
- `duration_seconds`: Total processing time
- `steps_completed`: List of completed workflow steps
- `confidence`: Overall confidence score (0.0-1.0)
- `requires_approval`: Whether human approval is needed

**Example**:
```python
ticket = """
ServiceNow Ticket INC0012345
Department: Cardiology
Title: Epic In Basket AI Implementation
...
"""

result = await agent.process_ticket(ticket)

if result.requires_approval:
    print(f"Form ready for review (confidence: {result.confidence:.0%})")
    print(f"Completed in {result.duration_seconds:.1f} seconds")
```

#### `extract_ticket_info(ticket_text: str) -> TicketInfo`

Extract basic information from ServiceNow ticket (Step 1).

**Returns**: `TicketInfo` with fields:
- `ticket_id`, `vendor`, `technology`, `use_case`
- `department`, `requestor`, `description`

#### `research_vendor(vendor_name: str) -> Dict[str, Any]`

Research AI vendor and technology (Step 2).

**Returns**: Dict with vendor information:
- Company background and AI focus areas
- Key AI products and capabilities
- Healthcare AI experience
- Integration capabilities
- Known risks or concerns
- Sources (citations)

#### `research_use_case(use_case: str, department: str) -> Dict[str, Any]`

Research clinical/operational use case (Step 3).

**Returns**: Dict with use case analysis:
- Current workflow and pain points
- How AI could help
- Similar implementations (best practices)
- Potential risks and challenges
- Success metrics to consider
- Sources (citations)

#### `synthesize_knowledge(...) -> Dict[str, Any]`

Synthesize vendor capabilities with use case needs (Step 4).

**Returns**: Dict with synthesis:
- How vendor capabilities map to use case needs
- Key opportunities and benefits
- Main risks and gaps
- Critical questions to address
- Recommended next steps

#### `draft_discovery_form(...) -> Dict[str, Any]`

Draft complete AI Discovery Form (Step 5).

**Returns**: Dict with completed form:
- `title`: Program title
- `sections`: List of 7 sections with content

#### `verify_form(form: Dict[str, Any]) -> Dict[str, Any]`

Self-verify Discovery Form quality (Step 6).

**Returns**: Verification result:
- `passed`: Whether form passed quality checks
- `overall_score`: Quality score (0.0-1.0)
- `checks`: List of individual check results
- `issues`: List of identified issues

#### `correct_issues(form: Dict, verification: Dict) -> Dict[str, Any]`

Correct identified issues in form.

**Returns**: Corrected version of form

### Observability

The agent provides comprehensive tracing of all operations:

```python
# Get trace details
trace = agent.get_trace(result.trace_id)

# Trace contains:
# - operation: Name of operation
# - start_time, end_time: Timestamps
# - steps: List of all workflow steps
# - status: success/error
# - metadata: Additional context
```

### Data Structures

#### `TicketInfo`
```python
@dataclass
class TicketInfo:
    ticket_id: Optional[str]
    vendor: Optional[str]
    technology: Optional[str]
    use_case: Optional[str]
    department: Optional[str]
    requestor: Optional[str]
    description: Optional[str]
    raw_text: str
```

#### `ResearchContext`
```python
@dataclass
class ResearchContext:
    vendor_info: Dict[str, Any]
    use_case_info: Dict[str, Any]
    synthesis: Dict[str, Any]
    sources: List[str]
```

#### `ProcessingResult`
```python
@dataclass
class ProcessingResult:
    form: Dict[str, Any]
    trace_id: str
    verification: Dict[str, Any]
    duration_seconds: float
    steps_completed: List[str]
    confidence: float
    requires_approval: bool
```

### Testing

**Unit Tests**: `tests/unit/test_pm_agent.py`
- Tests for each individual method
- Mock LLM responses for fast execution
- 30+ test cases covering normal and edge cases

**Integration Tests**: `tests/integration/test_pm_agent_integration.py`
- End-to-end workflow testing
- Real LLM integration (requires API key)
- Multiple realistic ticket scenarios
- Performance and concurrency tests

**Run Tests**:
```bash
# Unit tests (fast, no API calls)
pytest tests/unit/test_pm_agent.py -v

# Integration tests (requires ANTHROPIC_API_KEY)
pytest tests/integration/test_pm_agent_integration.py -v -m integration

# Performance tests
pytest tests/integration/test_pm_agent_integration.py -v -m performance
```

### Configuration

The agent uses configuration from `config/development.yaml`:

```yaml
agent:
  model: "claude-sonnet-4-5-20250929"
  max_iterations: 10
  confidence_threshold: 0.7

blueprints:
  directory: "docs/blueprints"
  templates:
    ai_discovery_form: "ai-discovery-form.yaml"
  workflows:
    discovery: "discovery-workflow.yaml"
```

### Related Files

- **Implementation**: `src/agent/pm_agent.py` (~900 lines)
- **Tests**: `tests/unit/test_pm_agent.py`, `tests/integration/test_pm_agent_integration.py`
- **Workflow Blueprint**: `docs/blueprints/discovery-workflow.yaml`
- **Form Template**: `docs/blueprints/ai-discovery-form.yaml`
- **Strategic Framework**: `docs/blueprints/ai-product-manager-strategy.yaml`

---

## 🔄 Discovery Workflow

The agent follows a structured 6-step workflow to generate high-quality AI Discovery Forms from ServiceNow tickets or user input. This workflow implements the Gather → Plan → Act → Verify → Iterate pattern.

### Workflow Overview

**Objective**: Generate a complete, evidence-based AI Discovery Form that meets governance requirements

**Inputs**: ServiceNow ticket, user description, or existing intake brief

**Outputs**: Completed 7-section Discovery Form with citations, gaps identified, confidence assessment

**Typical Duration**: 2-4 hours (agent time)

### Six Steps

#### Step 1: Extract Basics (5-10 min)
**Objective**: Extract fundamental information from source

**Actions**:
- Retrieve ServiceNow ticket or parse user input
- Extract vendor, technology, use case, department, stakeholders
- Normalize and categorize information

**Outputs**: Vendor name, technology type, use case category, problem statement draft

**Verification**: Vendor identified, use case clear, problem articulated

#### Step 2: Research Vendor (30-45 min)
**Objective**: Gather comprehensive vendor information

**Actions**:
- Search vendor capabilities, healthcare experience, case studies
- Research integration requirements and pricing
- Document certifications and compliance

**Search Queries**:
- "{vendor} healthcare AI capabilities"
- "{vendor} {technology} implementation guide"
- "{vendor} integration requirements"
- "{vendor} case studies healthcare"

**Outputs**: Vendor profile (capabilities, experience, integration, pricing), citations

**Verification**: Capabilities documented, healthcare experience verified, integration requirements known

#### Step 3: Research Use Case (45-60 min)
**Objective**: Understand clinical/operational problem deeply

**Actions**:
- Search problem domain literature
- Find best practices and evidence
- Identify metrics and benchmarks
- Research equity considerations and risks

**Search Queries**:
- "{use_case} in healthcare challenges"
- "{use_case} AI solutions best practices"
- "{use_case} ROI metrics healthcare"
- "{use_case} health disparities"
- "{use_case} AI bias concerns"

**Outputs**: Problem context, solution landscape, success metrics, equity considerations, risks, citations

**Verification**: Problem understood, evidence found, metrics identified, equity research complete

#### Step 4: Synthesize Context (15-30 min)
**Objective**: Combine all research into coherent understanding

**Actions**:
- Map findings to form sections
- Reconcile conflicting information
- Generate initial content
- Assess confidence by section
- Identify gaps and assumptions

**Outputs**: Comprehensive synthesis, confidence assessment, gaps identified

**Verification**: Synthesis complete, form sections mapped, contradictions resolved

#### Step 5: Draft Form (45-75 min)
**Objective**: Populate all 7 sections with evidence-based content

**Actions**:
- Generate content for each section using synthesis
- Follow plain language guidelines
- Include citations for all claims
- Show calculations for estimates
- Use placeholders for missing information

**Section Order**:
1. Basic Information
2. Problem Definition
3. Approach
4. Success Metrics
5. Potential Benefits
6. Risk Assessment
7. Equity Considerations

**Outputs**: Completed form (7 sections), completeness report, citations appendix

**Verification**: All sections present, required fields populated, plain language used, citations included

#### Step 6: Self-Verify (10-20 min)
**Objective**: Verify form quality against standards

**Actions**:
- Check completeness (>90% fields complete)
- Check clarity (plain language, examples)
- Check evidence-based (>80% claims cited)
- Check actionable (sufficient detail)
- Check policy compliance (100% requirements met)

**Quality Dimensions**:
- **Completeness**: All required fields populated with content
- **Clarity**: Plain language, specific examples, clear relationships
- **Evidence-Based**: Claims cited, calculations shown, assumptions stated
- **Actionable**: Sufficient detail for stakeholder decision-making
- **Policy Compliance**: Equity, risk, HITL, monitoring addressed

**Outputs**: Verification report with quality score (0.0-1.0), issues found (critical/moderate/minor), recommendations

**Decision Logic**:
- Quality >0.85: Present to user for approval
- Quality 0.70-0.85: Present with caveats and gaps
- Quality <0.70: Iterate or escalate

### Iteration Strategy

**When to Iterate**:
- Self-verification identifies critical gaps
- User feedback requires changes
- Confidence below threshold
- New information available

**How to Adapt**:
- Missing information → Additional research or user questions
- Clarity issues → Simplify language, add examples
- Evidence gaps → Search for sources, acknowledge uncertainty
- User feedback → Incorporate precisely, re-verify

**Max Iterations**: 3 (then escalate or accept gaps)

### Success Metrics

**Quality**:
- Discovery forms achieve >0.85 quality score
- Self-verification catches >90% of issues
- <10% require major revision after user review

**Efficiency**:
- Workflow completes in <4 hours
- <2 iterations needed on average
- Relevant sources found >80% of the time

**Adoption**:
- Users approve without modification >60% of the time
- Stakeholder needs met in reviews

### Example Execution

**Scenario**: Epic In Basket AI for Cardiology

- **Step 1** (5 min): Extract vendor (Epic), use case (inbox prioritization), department (Cardiology)
- **Step 2** (30 min): Research Epic capabilities - found 8 sources, identified NLP technology, 50+ deployments
- **Step 3** (45 min): Research inbox overload problem - found 12 sources, 30-40% time savings typical, equity concerns noted
- **Step 4** (20 min): Synthesize - confidence 0.78, gaps in Cardiology-specific workflow
- **Step 5** (60 min): Draft form - 7/7 sections complete, 3 placeholders, 4200 words
- **Step 6** (15 min): Verify - quality score 0.82, 2 moderate issues, ready for review

**Total**: 2 hours 55 minutes, **Result**: PRESENTED TO USER FOR REVIEW

### Related Documents

- **Blueprint**: `docs/blueprints/discovery-workflow.yaml` - Complete workflow specification
- **Form Template**: `docs/blueprints/ai-discovery-form.yaml` - Target document structure
- **Strategy**: `docs/blueprints/ai-product-manager-strategy.yaml` - Discovery phase context

---

## 🔧 Configuration

### Environment Variables

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_pm_agent
SERVICENOW_API_URL=https://your-instance.service-now.com/api/now
SERVICENOW_API_KEY=...

# Azure DevOps Integration
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-organization
AZURE_DEVOPS_PAT=your-personal-access-token
AZURE_DEVOPS_PROJECT=your-default-project

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
  azure_devops:
    timeout: 30
    retry_attempts: 3

  servicenow:
    timeout: 30
    retry_attempts: 3

  document_generator:
    output_format: markdown
    citation_required: true
```

---

## 🔗 Azure DevOps Integration

The AI Product Manager Agent integrates with Azure DevOps to manage work items, boards, and projects. This enables the agent to track AI initiatives in your existing Azure DevOps workflow.

### Setup

1. **Install Azure DevOps CLI**:
```bash
# Install Azure CLI (if not already installed)
brew install azure-cli

# Add Azure DevOps extension
az extension add --name azure-devops
```

2. **Generate Personal Access Token (PAT)**:
   - Go to: `https://dev.azure.com/your-organization/_usersSettings/tokens`
   - Click "New Token"
   - Select scopes: `Work Items (Read, Write)`, `Project and Team (Read)`
   - Copy the generated token

3. **Configure Environment**:
```bash
# Add to .env file
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-organization
AZURE_DEVOPS_PAT=your-personal-access-token-here
AZURE_DEVOPS_PROJECT=your-default-project  # Optional
```

### Supported Operations

- **`list_projects`**: List all projects in your organization
- **`get_project`**: Get details of a specific project
- **`list_work_items`**: List work items with optional filters
- **`get_work_item`**: Get detailed information about a work item
- **`update_work_item`**: Update work item fields (title, state, assignee, etc.)
- **`query_work_items`**: Execute custom WIQL queries
- **`list_boards`**: List boards and iterations in a project

### Usage Examples

#### List All Projects
```python
from src.tools.azure_devops_client import AzureDevOpsTool
from src.tools.base import ExecutionContext

tool = AzureDevOpsTool()
context = ExecutionContext(session_id="session-123")

result = await tool.execute(
    {"operation": "list_projects"},
    context
)
print(result.data)
# Output: {"value": [...], "count": 5}
```

#### Get Work Item Details
```python
result = await tool.execute(
    {
        "operation": "get_work_item",
        "work_item_id": "12345"
    },
    context
)
print(result.data["fields"]["System.Title"])
```

#### List Active Work Items
```python
result = await tool.execute(
    {
        "operation": "list_work_items",
        "project": "AI-Initiatives",
        "state": "Active",
        "top": 10
    },
    context
)
```

#### Update Work Item Status
```python
result = await tool.execute(
    {
        "operation": "update_work_item",
        "work_item_id": "12345",
        "fields": {
            "System.State": "Completed",
            "System.AssignedTo": "user@example.com"
        }
    },
    context
)
```

#### Custom WIQL Query
```python
query = """
    SELECT [System.Id], [System.Title], [System.State]
    FROM WorkItems
    WHERE [System.WorkItemType] = 'User Story'
    AND [System.Tags] CONTAINS 'AI'
    ORDER BY [System.ChangedDate] DESC
"""

result = await tool.execute(
    {
        "operation": "query_work_items",
        "query": query,
        "project": "AI-Initiatives"
    },
    context
)
```

### Testing

Run the Azure DevOps tool tests:
```bash
# Run all Azure DevOps tests
pytest tests/unit/test_tools/test_azure_devops_client.py -v

# Run specific test
pytest tests/unit/test_tools/test_azure_devops_client.py::TestListProjects -v
```

### Troubleshooting

**Authentication Error:**
- Verify PAT token is valid and hasn't expired
- Check PAT has correct scopes (Work Items: Read/Write, Project: Read)
- Ensure `AZURE_DEVOPS_ORG_URL` matches your organization

**Command Timeout:**
- Increase timeout in config: `tools.azure_devops.timeout_seconds`
- Check network connectivity to Azure DevOps

**Permission Denied:**
- Verify you have access to the project
- Check PAT token permissions

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
