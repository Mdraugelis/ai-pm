# Geisinger Agentic Architecture - Quick Reference
## One-Page Cheat Sheet for Development Teams
**Version 1.0 | January 2025**

---

## The Core Concept

**AGENTS, NOT WORKFLOWS**: Dynamic autonomous systems that plan → act → verify → iterate

```
Traditional Workflow:          Agent System:
Step 1 → Step 2 → Step 3       Goal → Plan → Act → Verify → Adapt
      (rigid)                         (flexible, learns)
```

---

## The 11 Layers

| Layer | Name | Purpose | Key Components |
|-------|------|---------|----------------|
| **8** | **Meta-Blueprint** | Universal safety rules | Always active, never overridden |
| **1** | **Agent Orchestration** | The "brain" - agent loop | Planner, Executor, Verifier |
| **2** | **Memory & Context** | State & 200K budget | Working (50K), Long-term, Compaction |
| **3** | **Tool Framework** | Agent's "hands" | Registry, Discovery, Execution |
| **4** | **MCP Integration** | Universal connector | MCP Client, MCP Servers |
| **5** | **Perceptions** | Environmental awareness | Push (events), Pull (queries) |
| **6** | **Interactions** | Human communication | Chat, **Approval UI**, Explain |
| **7** | **Domain Knowledge** | Policies & procedures | Policies, Guidelines, Examples |
| **9** | **HITL Governance** | Policy decisions (WHEN) | Self-verify, Tier classify, Risk assess |
| **10** | **Safety & Guardrails** | Multi-layer defense | Input/output validation, PHI scan |
| **11** | **Evaluation** | Quality assurance | Golden tests, Red team, Metrics |

---

## The Agent Loop (Heart of the System)

```
1. GATHER   → Load context from memory, tools, blueprints
    ↓
2. PLAN     → Consult blueprints, select tools, create strategy
    ↓
3. ACT      → Execute tools via MCP, collect results
    ↓
4. VERIFY   → Self-check against policies, completeness, quality
    ↓
5. ITERATE  → If not complete, adapt and loop back to #1
    ↓
    If complete → HITL Assessment → Response
```

**Key**: Agent adapts when tools fail or results are incomplete

---

## Critical Design Patterns

### 1. MCP-First Integration
```
❌ Old: Agent → 10 different custom connectors
✅ New: Agent → MCP Client → MCP Protocol → MCP Servers
```
**Benefit**: One integration pattern for all systems

### 2. Self-Verification First
```
❌ Old: 100% of outputs → Human review
✅ New: Agent self-checks → 70% auto-approve, 30% human review
```
**Benefit**: 70-80% reduction in human burden

### 3. HITL Split: Governance vs. Interaction
```
Layer 9 (HITL Governance): Decides WHEN approval is needed
         ↓ (If approval needed)
Layer 6 (Interactions): Handles HOW to get approval from user
         ↓
User sees: "I plan to do X. [Approve] [Deny] [Modify]"
```
**Benefit**: Approval requests are conversations, not just governance checks

### 4. Context as Budget
```
Total: 200K tokens
├─ Always-loaded: 12K (meta, task, recent)
├─ Dynamic pool: 188K (flexible retrieval)
└─ Compaction trigger: 160K (80%)
```
**Benefit**: Never overflow, maintain quality

### 5. HITL Tiers (Risk-Based)
```
Tier 1: Auto-approve (low risk)
Tier 2: Proceed + audit (medium risk)
Tier 3: Wait for approval (high risk)
Tier 4: Immediate escalation (critical)
```
**Benefit**: Right oversight at right time

---

## Module Organization

### Foundation (Build First)
- **M13**: Infrastructure (Docker, K8s, CI/CD)
- **M12**: Security (Auth, RBAC, Encryption)
- **M2**: Memory (Working memory, Budget manager)

### Agent Core (Build Second)
- **M1**: Agent Runtime (Loop, Planner, Executor, Verifier)
- **M3**: Tool Framework (Registry, Discovery, Execution)
- **M7**: Knowledge (BluePrints loader)

### Integration (Build Third)
- **M4**: MCP Layer (Client, Server base, Protocol)
- **M5**: Perceptions (Push/pull mechanisms)
- **M6**: Interactions (Chat UI, Explanations)

### Governance (Build Fourth)
- **M8**: HITL (Self-verification, Approval queue)
- **M9**: Safety (Validation, PHI scanning)
- **M10**: Evaluation (Golden tests, Red team)
- **M11**: Observability (Metrics, Dashboard)

---

## Tool Specification Template

```yaml
tool:
  id: "fetch_patient_data"
  version: "2.1.0"
  mcp_endpoint: "mcp://ehr.geisinger.org/patient_data"
  
  ownership:
    owner: "ehr-team@geisinger.org"
    technical_contact: "ehr-dev@geisinger.org"
  
  risk_classification:
    tier: "HIGH"                    # LOW, MEDIUM, HIGH, CRITICAL
    data_sensitivity: "RESTRICTED"  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    requires_consent: true
  
  sla:
    availability: "99.9%"
    response_p99: "1000ms"
    rate_limit: "1000 req/min"
  
  parameters:
    required: ["patient_id"]
    optional: ["data_type", "date_range"]
  
  rbac:
    allowed_roles: ["clinical_agent", "physician"]
    denied_roles: ["financial_agent"]
```

---

## BluePrint Template

```yaml
blueprint:
  name: "Clinical Decision Support"
  domain: "clinical"
  priority: "high"
  
  policies:  # MUST follow
    - "Verify patient identity before data access"
    - "Check allergies before prescribing"
    - "Document all clinical reasoning"
  
  guidelines:  # SHOULD follow
    - "Prefer evidence-based treatments"
    - "Consider patient preferences"
    - "Escalate when confidence < 70%"
  
  best_practices:  # HOW to do it
    - approach: "Gather complete medical history"
    - approach: "Use clinical decision trees"
    - approach: "Validate with latest guidelines"
  
  knowledge:  # Reference material
    key_facts: ["Drug interactions", "Contraindications"]
    references: ["UpToDate", "Clinical pathways"]
    examples: ["Previous similar cases"]
```

---

## Golden Test Template

```python
def test_clinical_triage_assessment():
    """
    Golden Test: Agent correctly triages patient
    """
    # Setup
    scenario = ClinicalScenario(
        patient="45yo male",
        symptoms=["chest pain", "shortness of breath"],
        vitals={"bp": "160/95", "hr": 110}
    )
    
    # Execute
    result = agent.execute(scenario)
    
    # Verify
    assert result.triage_level == "CRITICAL"
    assert result.time_to_decision < timedelta(minutes=2)
    assert result.appropriate_escalation == True
    assert "chest pain" in result.reasoning
    assert len(result.actions_taken) >= 3
```

---

## Implementation Checklist

### Before Any Commit
- [ ] Test defined with pass criteria
- [ ] Maps to BluePrint principle
- [ ] Can fail safely
- [ ] Is observable (logs/traces)
- [ ] Is teachable to new engineer

### Before Any Release
- [ ] Self-verification suite GREEN
- [ ] Golden tasks PASSING
- [ ] Governance approval LOGGED
- [ ] PHI compliance VERIFIED
- [ ] Rollback plan DEFINED
- [ ] Metrics collection ENABLED

### For Each New Tool
- [ ] Single clear purpose
- [ ] Registered in Tool Registry
- [ ] MCP endpoint operational
- [ ] RBAC configured
- [ ] Golden tests pass (5+)
- [ ] Safety tests pass
- [ ] Audit logging enabled
- [ ] Rate limits configured

### For Each New Agent
- [ ] Agent loop implemented
- [ ] Self-verification working
- [ ] Meta-Blueprint loaded (always)
- [ ] Domain BluePrints loaded
- [ ] Context policy enforced
- [ ] HITL tiers mapped
- [ ] Evaluation suite green
- [ ] Security review complete

---

## Key Metrics to Track

### Performance
- Agent loop latency: p99 < 15s
- Tool execution: p99 < 1s
- Throughput: > 100 QPS

### Quality
- Golden test pass rate: > 90%
- Self-verification accuracy: > 85%
- User approval rate: > 80%

### Safety
- PHI leakage incidents: **0**
- Prompt injection blocked: **100%**
- Authorization violations: **0**

### Efficiency
- Human review reduction: > 70%
- Task completion speed: 3x faster
- Cost per task: < $0.50

---

## Common Pitfalls to Avoid

| ❌ Don't | ✅ Do |
|---------|-------|
| Hardcode tool sequences | Let agent discover and select tools |
| Send all outputs to humans | Self-verify first, then tier-based review |
| Build custom connectors | Use MCP standard for all integrations |
| Ignore context limits | Track budget, trigger compaction at 80% |
| Skip golden tests | Every component needs golden tests |
| Allow writes without approval | Tier 3/4 for all writes, especially PHI |
| Hide agent reasoning | Full audit trail, explainable decisions |
| Deploy without red team | Always run adversarial tests first |

---

## Decision Flowchart: "Should This Be in the Agent?"

```
Does it require dynamic decision-making?
├─ YES → Build as agent with tools
└─ NO → Build as simple workflow

Can it adapt when things fail?
├─ YES → Agent with iterative loop
└─ NO → Reconsider if agent is needed

Does it involve PHI/sensitive data?
├─ YES → Tier 3/4 HITL required
│         Enhanced safety checks
│         Audit logging
└─ NO → Tier 1/2 may be sufficient

Is it critical/irreversible?
├─ YES → Tier 4 (immediate escalation)
│         No auto-execution
│         Rollback plan required
└─ NO → Lower tier based on impact
```

---

## Emergency Contacts & Escalation

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| PHI Leak | Security Team | Immediate |
| System Down | DevOps | < 15 minutes |
| Agent Misbehavior | AI Team Lead | < 1 hour |
| Tool Failure | Tool Owner | < 30 minutes |
| Safety Violation | Compliance | Immediate |

---

## Quick Command Reference

```bash
# Run agent locally
docker-compose up agent-runtime

# Execute golden tests
pytest tests/golden/ -v

# Run safety suite
pytest tests/safety/ --strict

# Deploy to staging
kubectl apply -f k8s/staging/

# Check agent status
curl http://agent-api/health

# View metrics dashboard
open http://grafana/agents

# Trigger compaction (manual)
curl -X POST http://agent-api/memory/compact
```

---

## Remember: The Geisinger Way

> **"Small steps, testable outcomes, trusted agents."**

Every 2-week sprint:
1. Deliver testable component
2. Pass golden tests
3. Get security review
4. Document learnings
5. Ship incrementally

---

**Print this page and keep it at your desk!**

*For detailed information, see:*
- *Architecture Diagram: geisinger-architecture-diagram.mermaid*
- *Full Documentation: geisinger-architecture-explanation.md*
- *Module Design: geisinger-module-design.md*
