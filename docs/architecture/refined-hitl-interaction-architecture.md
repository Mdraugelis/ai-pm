# Refined Architecture: HITL as Interaction Pattern
## Fixing the Conceptual Split Between Governance and Conversation
**Version 1.1 | January 2025**

---

## The Issue You Identified

**Original Architecture Problem:**
- Layer 9 (HITL) handled both:
  1. Policy decisions (WHEN approval is needed)
  2. Approval workflows (HOW to get approval)
  
- Layer 5 (Interactions) handled:
  1. User requests
  2. Agent responses
  3. But NOT approval interactions

**Your Insight:**
> *"When the agent asks me 'Should I do X? Yes/No/Do something else' - that's a conversation, not just governance!"*

**You're absolutely right.** Approval requests ARE interactions.

---

## Refined Architecture: Clear Separation of Concerns

### Layer 9: HITL Governance (Policy Engine)
**Responsibility**: *Determine WHEN approval is needed*

```
┌─────────────────────────────────────────────┐
│  HITL GOVERNANCE LAYER                       │
│  (Policy Engine - No User Interaction)       │
├─────────────────────────────────────────────┤
│                                              │
│  1. Self-Verification Suite                  │
│     ├─ Run policy checks                     │
│     ├─ Validate completeness                 │
│     ├─ Assess quality                        │
│     └─ Calculate confidence                  │
│                                              │
│  2. Tier Classification Engine               │
│     ├─ Analyze action risk                   │
│     ├─ Check data sensitivity                │
│     ├─ Evaluate reversibility                │
│     └─ Determine: Tier 1/2/3/4               │
│                                              │
│  3. Policy Decision                          │
│     ├─ Tier 1/2 → Auto-approve              │
│     └─ Tier 3/4 → Needs approval            │
│                                              │
└─────────────────────────────────────────────┘
                    ↓
            (If approval needed)
                    ↓
         Hand off to Interaction Layer
```

### Layer 5: Interaction Layer (Conversation Handler)
**Responsibility**: *Handle HOW approval conversations happen*

```
┌─────────────────────────────────────────────┐
│  INTERACTION LAYER                           │
│  (Conversation Handler - User Facing)        │
├─────────────────────────────────────────────┤
│                                              │
│  1. Conversational UI                        │
│     ├─ Initial user requests                 │
│     ├─ Ongoing dialogue                      │
│     └─ Final responses                       │
│                                              │
│  2. Approval Interaction Module (NEW!)       │
│     ├─ Present proposal to user              │
│     ├─ Show reasoning & evidence             │
│     ├─ Offer clear options                   │
│     └─ Handle user response                  │
│                                              │
│  3. Feedback & Modification Handler          │
│     ├─ Capture "Do something else"           │
│     ├─ Parse modification requests           │
│     └─ Route back to planning                │
│                                              │
│  4. Explanation Interface                    │
│     ├─ "Why this action?"                    │
│     ├─ "What alternatives considered?"       │
│     └─ "What are the risks?"                 │
│                                              │
└─────────────────────────────────────────────┘
```

---

## Complete HITL + Interaction Flow

### Step-by-Step Example: "Schedule Surgery"

```
Step 1: Agent Plans Action
┌─────────────────────────────────────────┐
│ Agent Loop (Layer 1)                     │
│ Plan: "Schedule surgery for patient"     │
│ Tools needed: [calendar, ehr, notify]    │
└─────────────────────────────────────────┘
              ↓
              
Step 2: Self-Verification (Layer 9)
┌─────────────────────────────────────────┐
│ HITL Governance: Self-Verify             │
│ ✓ Policy compliance: Check consent       │
│ ✓ Completeness: All required info        │
│ ✓ Quality: Scheduling logic correct      │
│ ✓ Confidence: 85% (high)                 │
└─────────────────────────────────────────┘
              ↓
              
Step 3: Tier Classification (Layer 9)
┌─────────────────────────────────────────┐
│ HITL Governance: Classify Risk           │
│ Action: "Schedule surgery"               │
│ Impact: High (patient care)              │
│ Reversibility: Partial (can reschedule)  │
│ Data: PHI involved                       │
│ → DECISION: Tier 3 (Active Approval)    │
└─────────────────────────────────────────┘
              ↓
       (Needs approval)
              ↓
              
Step 4: Approval Interaction (Layer 5)
┌─────────────────────────────────────────────────┐
│ Interaction Layer: Present to User              │
│                                                  │
│ ┌─────────────────────────────────────────────┐ │
│ │  Agent Proposal                              │ │
│ │                                              │ │
│ │  I recommend scheduling:                     │ │
│ │  • Patient: John Doe (ID: 12345)            │ │
│ │  • Procedure: Knee replacement               │ │
│ │  • Date: Feb 15, 2025 at 8:00 AM            │ │
│ │  • Surgeon: Dr. Smith                        │ │
│ │  • Location: OR-3                            │ │
│ │                                              │ │
│ │  Reasoning:                                  │ │
│ │  ✓ Patient consent verified                  │ │
│ │  ✓ Pre-op complete                           │ │
│ │  ✓ Surgeon available                         │ │
│ │  ✓ OR available                              │ │
│ │  ✓ Meets clinical guidelines                 │ │
│ │                                              │ │
│ │  Confidence: 85%                             │ │
│ │  Risk: Medium (reversible)                   │ │
│ │                                              │ │
│ │  [Approve] [Deny] [Modify] [Explain More]   │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
              ↓
    (User interacts)
              ↓
              
Step 5: User Response (Layer 5)
┌─────────────────────────────────────────┐
│ User clicks one of:                      │
│                                          │
│ Option A: [Approve]                      │
│   → Execute action                       │
│                                          │
│ Option B: [Deny]                         │
│   → Log denial, stop execution           │
│   → Ask: "Why? How can I help instead?"  │
│                                          │
│ Option C: [Modify]                       │
│   → Show modification dialog             │
│   → "Change date to Feb 16 instead"      │
│   → Re-plan with modification            │
│                                          │
│ Option D: [Explain More]                 │
│   → Show detailed reasoning              │
│   → Show alternatives considered         │
│   → Show risk analysis                   │
│   → Return to approval options           │
└─────────────────────────────────────────┘
```

---

## Updated Component Responsibilities

### Layer 9: HITL Governance Components

#### 1. Self-Verification Suite
```python
class SelfVerificationSuite:
    """
    Validates agent work quality (no user interaction)
    """
    
    async def verify(
        self,
        plan: Plan,
        context: ExecutionContext
    ) -> VerificationResult:
        """
        Run all self-checks
        """
        checks = [
            await self.check_policy_compliance(plan),
            await self.check_completeness(plan),
            await self.check_consistency(plan),
            await self.check_quality(plan),
            await self.assess_confidence(plan)
        ]
        
        return VerificationResult(
            all_passed=all(c.passed for c in checks),
            checks=checks
        )
```

#### 2. Tier Classification Engine
```python
class TierClassificationEngine:
    """
    Determines if approval is needed (no user interaction)
    """
    
    def classify_action(
        self,
        action: Action,
        verification: VerificationResult
    ) -> HITLTier:
        """
        Classify action into risk tier
        """
        # Analyze action characteristics
        impact = self.assess_impact(action)
        reversibility = self.assess_reversibility(action)
        data_sensitivity = self.assess_data_sensitivity(action)
        
        # Determine tier
        if impact == "LOW" and reversibility == "FULL":
            return HITLTier.TIER_1  # Auto-approve
        elif impact == "MEDIUM" and reversibility in ["FULL", "PARTIAL"]:
            return HITLTier.TIER_2  # Passive review
        elif impact == "HIGH" or data_sensitivity == "PHI":
            return HITLTier.TIER_3  # Active approval
        else:
            return HITLTier.TIER_4  # Immediate escalation
```

#### 3. Approval Policy Manager
```python
class ApprovalPolicyManager:
    """
    Manages approval policies (no user interaction)
    """
    
    def should_request_approval(
        self,
        tier: HITLTier
    ) -> bool:
        """
        Policy decision: is approval required?
        """
        return tier in [HITLTier.TIER_3, HITLTier.TIER_4]
    
    def get_approval_requirements(
        self,
        action: Action,
        tier: HITLTier
    ) -> ApprovalRequirements:
        """
        Define what approval looks like for this action
        """
        return ApprovalRequirements(
            tier=tier,
            timeout=self._get_timeout(tier),
            required_role=self._get_required_approver(action),
            can_modify=tier == HITLTier.TIER_3,
            emergency_override=tier != HITLTier.TIER_4
        )
```

---

### Layer 5: Interaction Layer Components

#### 1. Approval Interaction Module (NEW!)
```python
class ApprovalInteractionModule:
    """
    Handles approval conversations with users
    """
    
    async def request_approval(
        self,
        proposal: ActionProposal,
        requirements: ApprovalRequirements
    ) -> ApprovalResponse:
        """
        Present proposal to user and get response
        """
        # Build approval UI
        approval_ui = self._build_approval_ui(proposal, requirements)
        
        # Present to user
        user_response = await self._present_to_user(approval_ui)
        
        # Handle response
        if user_response.action == "APPROVE":
            return ApprovalResponse(
                decision="APPROVED",
                timestamp=datetime.now(),
                user=user_response.user
            )
            
        elif user_response.action == "DENY":
            return ApprovalResponse(
                decision="DENIED",
                reason=user_response.reason,
                timestamp=datetime.now(),
                user=user_response.user
            )
            
        elif user_response.action == "MODIFY":
            return ApprovalResponse(
                decision="MODIFY",
                modifications=user_response.modifications,
                timestamp=datetime.now(),
                user=user_response.user
            )
            
        elif user_response.action == "EXPLAIN":
            # Show more details, then loop back
            await self._show_detailed_explanation(proposal)
            return await self.request_approval(proposal, requirements)
    
    def _build_approval_ui(
        self,
        proposal: ActionProposal,
        requirements: ApprovalRequirements
    ) -> ApprovalUI:
        """
        Construct the approval interface
        """
        return ApprovalUI(
            title="Action Approval Required",
            
            summary=self._generate_summary(proposal),
            
            details={
                "action": proposal.action_description,
                "parameters": proposal.parameters,
                "reasoning": proposal.reasoning,
                "confidence": f"{proposal.confidence}%",
                "risk": proposal.risk_level
            },
            
            evidence=[
                f"✓ {check.description}" 
                for check in proposal.verification_checks 
                if check.passed
            ],
            
            buttons=[
                Button("Approve", action="APPROVE", style="success"),
                Button("Deny", action="DENY", style="danger"),
                Button("Modify", action="MODIFY", style="warning") 
                    if requirements.can_modify else None,
                Button("Explain More", action="EXPLAIN", style="info")
            ],
            
            timeout=requirements.timeout
        )
```

#### 2. Feedback and Modification Handler
```python
class FeedbackHandler:
    """
    Handles user modifications and alternative requests
    """
    
    async def handle_modification(
        self,
        original_proposal: ActionProposal,
        user_modification: UserModification
    ) -> ModificationResult:
        """
        Process user's requested changes
        """
        # Parse modification
        parsed_mod = self._parse_modification(user_modification)
        
        # Create modified plan
        modified_plan = self._apply_modification(
            original_proposal.plan,
            parsed_mod
        )
        
        # Send back to agent for re-planning
        return ModificationResult(
            modified_plan=modified_plan,
            user_intent=parsed_mod.intent,
            constraints=parsed_mod.constraints
        )
    
    async def handle_denial(
        self,
        proposal: ActionProposal,
        denial_reason: str
    ) -> DenialResult:
        """
        Process denial and ask for alternatives
        """
        # Log denial
        await self._log_denial(proposal, denial_reason)
        
        # Ask user what they want instead
        alternative = await self._request_alternative_intent(
            original_proposal=proposal,
            why_denied=denial_reason
        )
        
        return DenialResult(
            denied_proposal=proposal,
            alternative_intent=alternative
        )
```

#### 3. Explanation Interface
```python
class ExplanationInterface:
    """
    Provides detailed explanations on demand
    """
    
    async def explain_proposal(
        self,
        proposal: ActionProposal
    ) -> DetailedExplanation:
        """
        Generate comprehensive explanation
        """
        return DetailedExplanation(
            
            reasoning_chain=[
                f"Step {i+1}: {step.description}"
                for i, step in enumerate(proposal.reasoning_steps)
            ],
            
            data_sources=[
                f"• {source.name}: {source.description}"
                for source in proposal.data_sources
            ],
            
            policies_applied=[
                f"• {policy.name} (from {policy.blueprint})"
                for policy in proposal.policies_consulted
            ],
            
            alternatives_considered=[
                {
                    "option": alt.description,
                    "why_not_chosen": alt.rejection_reason,
                    "confidence": alt.confidence
                }
                for alt in proposal.alternatives
            ],
            
            risk_analysis={
                "potential_benefits": proposal.benefits,
                "potential_risks": proposal.risks,
                "mitigation_steps": proposal.mitigations
            },
            
            confidence_factors={
                "supporting": [
                    f"✓ {factor}" 
                    for factor in proposal.confidence_supports
                ],
                "limiting": [
                    f"⚠ {factor}" 
                    for factor in proposal.confidence_limits
                ]
            }
        )
```

---

## Complete Interaction Flow

### Scenario: Agent Wants to Send Important Email

```python
# 1. AGENT PLANS (Layer 1)
plan = agent.create_plan(
    task="Send contract to vendor",
    action="email.send",
    parameters={
        "to": "vendor@company.com",
        "subject": "Contract for Review",
        "body": "Please review attached contract...",
        "attachments": ["contract_v3.pdf"]
    }
)

# 2. SELF-VERIFY (Layer 9 - HITL Governance)
verification = self_verifier.verify(plan)
# Result: All checks passed

# 3. CLASSIFY TIER (Layer 9 - HITL Governance)
tier = tier_classifier.classify(plan)
# Result: Tier 3 (contract = high impact, needs approval)

# 4. CHECK POLICY (Layer 9 - HITL Governance)
needs_approval = policy_manager.should_request_approval(tier)
# Result: True (Tier 3 requires approval)

requirements = policy_manager.get_approval_requirements(plan, tier)
# Result: Active approval, 5 min timeout, can modify

# 5. REQUEST APPROVAL (Layer 5 - Interaction)
approval_response = await approval_interaction.request_approval(
    proposal=ActionProposal(
        plan=plan,
        verification=verification,
        reasoning="Contract ready for vendor review..."
    ),
    requirements=requirements
)

# 6. HANDLE USER RESPONSE (Layer 5 - Interaction)
if approval_response.decision == "APPROVED":
    # Execute the action
    result = await executor.execute(plan)
    
elif approval_response.decision == "DENIED":
    # Handle denial
    denial_result = await feedback_handler.handle_denial(
        proposal=plan,
        reason=approval_response.reason
    )
    # Ask user: "What would you like me to do instead?"
    
elif approval_response.decision == "MODIFY":
    # Handle modification
    mod_result = await feedback_handler.handle_modification(
        original_proposal=plan,
        user_modification=approval_response.modifications
    )
    # Re-plan: "Send to legal@company.com instead of vendor"
    new_plan = agent.replan_with_modification(mod_result)
    # Loop back to step 2 (self-verify new plan)
```

---

## User Experience Examples

### Example 1: Simple Approval (Tier 3)

```
┌───────────────────────────────────────────────────────┐
│  Action Approval Required                              │
├───────────────────────────────────────────────────────┤
│                                                        │
│  I recommend: Send email to vendor@company.com         │
│                                                        │
│  Details:                                              │
│  • Subject: Contract for Review                        │
│  • Attachment: contract_v3.pdf                         │
│  • Estimated send time: <1 second                      │
│                                                        │
│  Reasoning:                                            │
│  ✓ Contract finalized by legal                         │
│  ✓ Vendor expecting this document                      │
│  ✓ All signatures obtained                             │
│  ✓ Email template validated                            │
│                                                        │
│  Confidence: 92%                                       │
│  Risk: Low (can recall if needed)                      │
│                                                        │
│  [Approve] [Deny] [Modify] [Explain More]             │
│                                                        │
│  Timeout: This request expires in 5 minutes            │
└───────────────────────────────────────────────────────┘
```

### Example 2: User Clicks "Modify"

```
┌───────────────────────────────────────────────────────┐
│  Modify Action                                         │
├───────────────────────────────────────────────────────┤
│                                                        │
│  Original: Send to vendor@company.com                  │
│                                                        │
│  What would you like to change?                        │
│                                                        │
│  Recipient: [vendor@company.com            ] [Change]  │
│  Subject:   [Contract for Review           ] [Change]  │
│  Body:      [Please review attached...     ] [Edit]    │
│  Attach:    [contract_v3.pdf              ] [Change]  │
│                                                        │
│  Or describe changes:                                  │
│  ┌────────────────────────────────────────────────┐   │
│  │ "Send to legal@company.com for review first"   │   │
│  │                                                 │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  [Apply Changes] [Cancel]                              │
└───────────────────────────────────────────────────────┘
```

### Example 3: User Clicks "Explain More"

```
┌───────────────────────────────────────────────────────┐
│  Detailed Explanation                                  │
├───────────────────────────────────────────────────────┤
│                                                        │
│  Why this action?                                      │
│  1. You requested: "Send final contract to vendor"     │
│  2. I verified contract is signed                      │
│  3. I checked vendor is expecting it (calendar note)   │
│  4. I validated email format and attachments           │
│                                                        │
│  Data sources used:                                    │
│  • Document Management: contract_v3.pdf status         │
│  • Email: Previous correspondence thread               │
│  • Calendar: "Send contract" scheduled today           │
│  • Legal System: Final approval timestamp              │
│                                                        │
│  Policies applied:                                     │
│  • Contract Handling Policy (Legal Blueprint)          │
│  • Email Communication Standards (Corporate)           │
│  • PHI Protection Rules (Meta-Blueprint)               │
│                                                        │
│  Alternatives I considered:                            │
│  ✗ Send via secure file transfer                       │
│    → Rejected: Vendor doesn't have account             │
│  ✗ Print and mail physical copy                        │
│    → Rejected: Too slow, deadline is Friday            │
│  ✓ Email with PDF attachment                           │
│    → Selected: Fast, vendor preference, auditable      │
│                                                        │
│  Risk analysis:                                        │
│  Benefits:                                             │
│  • Fast delivery (seconds)                             │
│  • Creates audit trail                                 │
│  • Matches vendor preference                           │
│                                                        │
│  Risks:                                                │
│  • Email could be intercepted (LOW - encrypted)        │
│  • Wrong recipient (LOW - verified address)            │
│                                                        │
│  Confidence: 92%                                       │
│  What increases confidence:                            │
│  ✓ Clear user intent                                   │
│  ✓ All validations passed                              │
│  ✓ Standard, tested action                             │
│                                                        │
│  What limits confidence:                               │
│  ⚠ Can't verify vendor will receive (8% uncertainty)   │
│                                                        │
│  [Back to Approval] [Approve Anyway] [Deny]           │
└───────────────────────────────────────────────────────┘
```

---

## Summary: Clean Separation

### Layer 9 (HITL Governance)
**Role**: Policy Engine - "The Bouncer"
- **Input**: Proposed action
- **Output**: Decision (approve/need human)
- **NO user interaction**
- Components:
  - Self-verification suite
  - Tier classification engine
  - Policy decision maker

### Layer 5 (Interaction Layer)
**Role**: Conversation Handler - "The Diplomat"
- **Input**: Approval request
- **Output**: User decision
- **ALL user interaction**
- Components:
  - Approval interaction module
  - Feedback handler
  - Modification processor
  - Explanation interface

### The Handoff
```
Layer 9 says: "This needs approval"
      ↓
Layer 5 says: "Let me talk to the user"
      ↓
User says: "Yes/No/Modify"
      ↓
Layer 5 returns: User's decision
      ↓
Agent proceeds: Based on decision
```

---

## Implementation Changes

### Before (Unclear)
```python
# HITL layer did everything
class HITLSystem:
    async def check_and_approve(plan):
        # Mixed concerns!
        verification = self.verify(plan)
        tier = self.classify(plan)
        if needs_approval(tier):
            # WRONG: HITL talks to user directly
            user_response = await self.show_approval_ui(plan)
```

### After (Clean)
```python
# Layer 9: Policy engine
class HITLGovernance:
    async def evaluate_plan(plan):
        verification = self.verify(plan)
        tier = self.classify(plan)
        
        if self.policy.needs_approval(tier):
            return EvaluationResult(
                needs_approval=True,
                tier=tier,
                requirements=self.policy.get_requirements(tier)
            )
        else:
            return EvaluationResult(
                needs_approval=False,
                auto_approved=True
            )

# Layer 5: Conversation handler
class InteractionLayer:
    async def handle_approval_request(proposal, requirements):
        # RIGHT: Interaction layer talks to user
        response = await self.approval_ui.request_approval(
            proposal, 
            requirements
        )
        return response
```

---

## Benefits of This Architecture

1. **Clear Separation**: Policy vs. Conversation
2. **Reusable**: Approval UI works for any domain
3. **Testable**: Can test policy engine without UI
4. **User-Friendly**: Rich interaction options
5. **Flexible**: Easy to add new response types
6. **Auditable**: Clear handoff points

---

## Your Question Answered

> *"I always thought of the interactions would include the HITL approved actions that the agent can make."*

**You were correct!** 

The HITL system should be split:
- **Governance layer** (Layer 9) = Policy decisions
- **Interaction layer** (Layer 5) = Approval conversations

The agent creates valid actions (via planning), but **presenting** those actions for approval is fundamentally an interaction with the human.

Thank you for catching this architectural inconsistency!

---

**Updated Architecture Version**: 1.1
**Change**: HITL approval interactions moved to Layer 5
**Rationale**: Approval requests are conversations, not just governance
