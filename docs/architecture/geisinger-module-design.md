# Geisinger Agentic System - Module Design Document
## Component Breakdown & Implementation Guide
**Version 1.0 | January 2025**

---

## Table of Contents

1. [Module Overview](#module-overview)
2. [Detailed Component Design](#detailed-component-design)
3. [Interface Specifications](#interface-specifications)
4. [Dependency Map](#dependency-map)
5. [Implementation Priority](#implementation-priority)
6. [Testing Strategy Per Module](#testing-strategy-per-module)

---

## Module Overview

### System Decomposition

The Geisinger Agentic System is decomposed into **11 primary modules** plus **2 cross-cutting modules**:

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT MODULES (Core Functionality)                          │
├─────────────────────────────────────────────────────────────┤
│  M1:  Core Agent Runtime                                     │
│  M2:  Memory & Context Management                            │
│  M3:  Tool Framework                                          │
│  M4:  MCP Integration Layer                                   │
│  M5:  Perception System                                       │
│  M6:  Interaction Layer                                       │
│  M7:  Knowledge Management                                    │
├─────────────────────────────────────────────────────────────┤
│  GOVERNANCE MODULES                                           │
├─────────────────────────────────────────────────────────────┤
│  M8:  HITL System                                            │
│  M9:  Safety & Guardrails                                    │
│  M10: Evaluation Harness                                     │
│  M11: Observability & Metrics                                │
├─────────────────────────────────────────────────────────────┤
│  CROSS-CUTTING MODULES                                        │
├─────────────────────────────────────────────────────────────┤
│  M12: Security Services                                       │
│  M13: Configuration & Infrastructure                          │
└─────────────────────────────────────────────────────────────┘
```

### Module Dependency Tree

```
Foundation Layer (No dependencies):
├─ M13: Configuration & Infrastructure
└─ M12: Security Services

Core Services Layer (Depends on Foundation):
├─ M2: Memory & Context Management
├─ M7: Knowledge Management
└─ M4: MCP Integration Layer

Agent Core Layer (Depends on Core Services):
├─ M3: Tool Framework (uses M4, M12)
├─ M5: Perception System (uses M3, M4)
└─ M1: Core Agent Runtime (uses M2, M3, M5, M7)

User-Facing Layer (Depends on Agent Core):
├─ M6: Interaction Layer (uses M1, M11)
└─ M8: HITL System (uses M1, M9)

Quality Assurance Layer (Depends on All):
├─ M9: Safety & Guardrails (uses M1, M3, M12)
├─ M10: Evaluation Harness (uses All)
└─ M11: Observability & Metrics (uses All)
```

---

## Detailed Component Design

### M1: Core Agent Runtime

**Purpose**: The autonomous reasoning engine - implements the agent loop

#### Components

##### 1.1 Orchestrator
```python
class AgentOrchestrator:
    """
    Main agent loop controller
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.planner = Planner(config)
        self.executor = Executor(config)
        self.verifier = SelfVerifier(config)
        self.memory = MemoryManager(config)
        self.tools = ToolRegistry(config)
        
    async def execute_task(self, task: Task) -> AgentResponse:
        """
        Main agent loop: Gather → Plan → Act → Verify → Iterate
        """
        # Load Meta-Blueprint (always)
        meta_blueprint = await self.load_meta_blueprint()
        
        # Classify domain and load domain blueprints
        domain = await self.classify_domain(task)
        domain_blueprints = await self.load_domain_blueprints(domain)
        
        # Initialize execution context
        context = ExecutionContext(
            task=task,
            meta_blueprint=meta_blueprint,
            domain_blueprints=domain_blueprints,
            memory=self.memory
        )
        
        # Agent loop
        max_iterations = 10
        for iteration in range(max_iterations):
            # 1. GATHER
            gathered_context = await self.gather_context(context)
            
            # 2. PLAN
            plan = await self.planner.create_plan(
                task, 
                gathered_context, 
                iteration
            )
            
            # 3. ACT
            execution_result = await self.executor.execute_plan(
                plan,
                context
            )
            
            # 4. VERIFY
            verification = await self.verifier.verify(
                execution_result,
                plan,
                context
            )
            
            # 5. ITERATE/ADAPT
            if verification.complete:
                return AgentResponse(
                    result=execution_result,
                    verification=verification,
                    trace=context.trace
                )
            elif verification.should_escalate:
                return AgentResponse(
                    status="ESCALATED",
                    reason=verification.escalation_reason,
                    trace=context.trace
                )
            else:
                # Adapt and continue
                context.update_from_verification(verification)
                continue
        
        # Max iterations reached
        return AgentResponse(
            status="MAX_ITERATIONS",
            trace=context.trace
        )
```

##### 1.2 Planner
```python
class Planner:
    """
    Generates execution plans dynamically
    """
    
    async def create_plan(
        self, 
        task: Task, 
        context: ExecutionContext,
        iteration: int
    ) -> Plan:
        """
        Create or adapt execution plan
        """
        # If first iteration, create fresh plan
        if iteration == 0:
            return await self._create_initial_plan(task, context)
        
        # Otherwise, adapt existing plan based on results
        return await self._adapt_plan(task, context)
    
    async def _create_initial_plan(
        self, 
        task: Task, 
        context: ExecutionContext
    ) -> Plan:
        """
        Create initial execution plan
        """
        # Consult blueprints for guidance
        guidelines = self._extract_relevant_guidelines(
            task,
            context.domain_blueprints
        )
        
        # Identify available tools
        available_tools = await self._discover_tools(task, context)
        
        # Generate plan steps
        steps = await self._generate_steps(
            task,
            guidelines,
            available_tools,
            context
        )
        
        # Self-assess plan quality
        quality_score = await self._assess_plan_quality(steps, context)
        
        return Plan(
            steps=steps,
            rationale=self._generate_rationale(steps, guidelines),
            tools_required=available_tools,
            estimated_cost=self._estimate_cost(steps),
            quality_score=quality_score,
            iteration=0
        )
    
    async def _adapt_plan(
        self, 
        task: Task, 
        context: ExecutionContext
    ) -> Plan:
        """
        Adapt plan based on execution results
        """
        current_plan = context.current_plan
        last_result = context.last_execution_result
        
        # Analyze what went wrong
        failure_analysis = self._analyze_failure(last_result)
        
        # Consult blueprints for alternatives
        alternatives = self._find_alternative_approaches(
            failure_analysis,
            context.domain_blueprints
        )
        
        # Generate adapted plan
        adapted_steps = await self._generate_adapted_steps(
            current_plan,
            alternatives,
            context
        )
        
        return Plan(
            steps=adapted_steps,
            rationale=self._generate_adaptation_rationale(
                failure_analysis,
                alternatives
            ),
            parent_plan=current_plan,
            iteration=current_plan.iteration + 1
        )
```

##### 1.3 Executor
```python
class Executor:
    """
    Executes plans using tools
    """
    
    def __init__(self, config: AgentConfig):
        self.tool_framework = ToolFramework(config)
        self.parallel_executor = ParallelExecutor(config)
        
    async def execute_plan(
        self, 
        plan: Plan, 
        context: ExecutionContext
    ) -> ExecutionResult:
        """
        Execute plan steps
        """
        results = []
        
        for step in plan.steps:
            # Check if step can be parallelized
            if step.parallel_safe:
                step_result = await self._execute_parallel(
                    step,
                    context
                )
            else:
                step_result = await self._execute_sequential(
                    step,
                    context
                )
            
            results.append(step_result)
            
            # Update context with step result
            context.add_step_result(step_result)
            
            # Check if should abort early
            if step_result.failure and step.critical:
                return ExecutionResult(
                    steps=results,
                    status="FAILED",
                    failure_reason=step_result.error
                )
        
        return ExecutionResult(
            steps=results,
            status="SUCCESS",
            output=self._aggregate_outputs(results)
        )
    
    async def _execute_sequential(
        self, 
        step: PlanStep, 
        context: ExecutionContext
    ) -> StepResult:
        """
        Execute a single step
        """
        tool = await self.tool_framework.get_tool(step.tool_id)
        
        try:
            # Execute tool
            tool_result = await tool.execute(
                parameters=step.parameters,
                context=context
            )
            
            return StepResult(
                step=step,
                status="SUCCESS",
                output=tool_result,
                duration=tool_result.duration
            )
            
        except ToolExecutionError as e:
            return StepResult(
                step=step,
                status="FAILED",
                error=str(e),
                failure=True
            )
```

##### 1.4 Self-Verifier
```python
class SelfVerifier:
    """
    Validates agent outputs before human review
    """
    
    async def verify(
        self,
        result: ExecutionResult,
        plan: Plan,
        context: ExecutionContext
    ) -> VerificationResult:
        """
        Run comprehensive self-verification suite
        """
        checks = []
        
        # 1. Policy Compliance
        policy_check = await self._check_policy_compliance(
            result,
            context.meta_blueprint,
            context.domain_blueprints
        )
        checks.append(policy_check)
        
        # 2. Completeness
        completeness_check = await self._check_completeness(
            result,
            plan.requirements
        )
        checks.append(completeness_check)
        
        # 3. Consistency
        consistency_check = await self._check_consistency(
            result,
            context.history
        )
        checks.append(consistency_check)
        
        # 4. Quality
        quality_check = await self._check_quality(
            result,
            context.domain_standards
        )
        checks.append(quality_check)
        
        # 5. Confidence
        confidence_check = await self._assess_confidence(
            result,
            context
        )
        checks.append(confidence_check)
        
        # 6. Safety
        safety_check = await self._check_safety(
            result,
            context
        )
        checks.append(safety_check)
        
        # Aggregate results
        all_passed = all(check.passed for check in checks)
        critical_failed = any(
            check.failed and check.critical 
            for check in checks
        )
        
        return VerificationResult(
            passed=all_passed,
            checks=checks,
            complete=all_passed and not plan.has_more_steps,
            should_escalate=critical_failed,
            confidence_score=confidence_check.score,
            issues=self._extract_issues(checks)
        )
```

#### Interfaces

```python
# Input Interface
@dataclass
class Task:
    id: str
    description: str
    user_id: str
    domain: Optional[str]
    priority: TaskPriority
    deadline: Optional[datetime]
    requirements: List[str]
    context: Dict[str, Any]

# Output Interface
@dataclass
class AgentResponse:
    task_id: str
    status: ResponseStatus  # SUCCESS, FAILED, ESCALATED, PARTIAL
    result: Optional[Any]
    verification: VerificationResult
    trace: ExecutionTrace
    recommendations: List[Recommendation]
    requires_approval: bool
    hitl_tier: HITLTier
```

#### Dependencies
- M2: Memory & Context Management
- M3: Tool Framework
- M5: Perception System
- M7: Knowledge Management
- M9: Safety & Guardrails

#### Testing Requirements
```python
# Golden Tests
def test_agent_completes_simple_task():
    """Agent completes basic task in <3 iterations"""
    pass

def test_agent_adapts_to_tool_failure():
    """Agent tries alternative when tool fails"""
    pass

def test_agent_escalates_when_uncertain():
    """Agent escalates when confidence <70%"""
    pass

# Performance Tests
def test_agent_loop_latency():
    """Single iteration completes in <5s"""
    pass
```

---

### M2: Memory & Context Management

**Purpose**: Manages context budget and agent state

#### Components

##### 2.1 Working Memory
```python
class WorkingMemory:
    """
    Active, mutable memory for current session
    """
    
    def __init__(self, max_tokens: int = 50000):
        self.max_tokens = max_tokens
        self.conversation_history: List[Turn] = []
        self.task_state: TaskState = TaskState()
        self.tool_results: Dict[str, ToolResult] = {}
        self.temporary_conclusions: List[Conclusion] = []
        self.error_history: List[Error] = []
        
    def add_turn(self, turn: Turn):
        """Add conversation turn"""
        self.conversation_history.append(turn)
        self._check_capacity()
    
    def add_tool_result(
        self, 
        tool_id: str, 
        result: ToolResult,
        ttl_seconds: int = 300
    ):
        """Cache tool result with TTL"""
        self.tool_results[tool_id] = CachedResult(
            result=result,
            timestamp=datetime.now(),
            ttl=ttl_seconds
        )
        self._cleanup_expired()
        self._check_capacity()
    
    def _check_capacity(self):
        """Trigger compaction if approaching limit"""
        current_tokens = self.count_tokens()
        if current_tokens > self.max_tokens * 0.8:
            self._trigger_compaction()
    
    def count_tokens(self) -> int:
        """Count total tokens in working memory"""
        return (
            self._count_conversation_tokens() +
            self._count_task_state_tokens() +
            self._count_tool_results_tokens() +
            self._count_conclusions_tokens()
        )
```

##### 2.2 Long-Term Memory
```python
class LongTermMemory:
    """
    Persistent storage for agent learning
    """
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        
    async def save_session_summary(
        self, 
        session_id: str, 
        summary: SessionSummary
    ):
        """Persist session summary"""
        await self.storage.save(
            key=f"session:{session_id}",
            value=summary.to_dict(),
            ttl_days=90
        )
    
    async def save_learned_pattern(
        self, 
        pattern: LearnedPattern
    ):
        """Save successful strategy"""
        await self.storage.save(
            key=f"pattern:{pattern.id}",
            value=pattern.to_dict(),
            tags=pattern.tags
        )
    
    async def retrieve_similar_cases(
        self, 
        task: Task, 
        limit: int = 5
    ) -> List[SessionSummary]:
        """Retrieve relevant past cases"""
        return await self.storage.search(
            query=task.description,
            filters={"domain": task.domain},
            limit=limit
        )
```

##### 2.3 Context Budget Manager
```python
class ContextBudgetManager:
    """
    Manages 200K token context budget
    """
    
    def __init__(self):
        self.total_budget = 200000
        self.allocations = {
            'meta_blueprint': 2000,
            'working_memory': 50000,
            'tool_results': 30000,
            'blueprints': 20000,
            'reasoning': 40000,
            'output': 10000,
            'safety': 8000,
            'dynamic': 40000
        }
        self.used = 0
        
    def check_budget(
        self, 
        category: str, 
        requested: int
    ) -> BudgetCheckResult:
        """Check if allocation is within budget"""
        allocated = self.allocations.get(category, 0)
        available = self.total_budget - self.used
        
        if requested > allocated:
            return BudgetCheckResult(
                status="OVER_ALLOCATION",
                action="TRIGGER_COMPACTION"
            )
        elif self.used + requested > self.total_budget * 0.8:
            return BudgetCheckResult(
                status="WARNING",
                action="APPROACHING_LIMIT"
            )
        else:
            return BudgetCheckResult(
                status="APPROVED",
                action="PROCEED"
            )
    
    def allocate(self, category: str, amount: int):
        """Allocate tokens from budget"""
        self.used += amount
    
    def release(self, category: str, amount: int):
        """Release tokens back to budget"""
        self.used = max(0, self.used - amount)
```

##### 2.4 Compaction Service
```python
class CompactionService:
    """
    Auto-summarizes context when approaching limit
    """
    
    async def compact_working_memory(
        self, 
        working_memory: WorkingMemory,
        target_tokens: int = 10000
    ) -> CompactionResult:
        """
        Compress working memory to target size
        """
        # Extract what must be preserved
        critical_data = self._extract_critical_data(working_memory)
        
        # Summarize conversation history
        conversation_summary = await self._summarize_conversation(
            working_memory.conversation_history,
            compression_ratio=10
        )
        
        # Compress tool results
        tool_summary = self._compress_tool_results(
            working_memory.tool_results
        )
        
        # Create compact representation
        compact_memory = CompactMemory(
            critical_data=critical_data,
            conversation_summary=conversation_summary,
            tool_summary=tool_summary,
            original_size=working_memory.count_tokens(),
            compressed_size=self._count_tokens(
                critical_data, 
                conversation_summary, 
                tool_summary
            )
        )
        
        # Verify no safety-critical data lost
        verification = self._verify_no_data_loss(
            working_memory,
            compact_memory
        )
        
        if not verification.passed:
            raise CompactionError(
                f"Critical data lost: {verification.missing_items}"
            )
        
        return CompactionResult(
            compact_memory=compact_memory,
            compression_ratio=compact_memory.original_size / 
                            compact_memory.compressed_size
        )
```

#### Interfaces

```python
# Memory Read Interface
class MemoryReader:
    async def get_context(
        self, 
        task: Task
    ) -> ContextBundle:
        """Get all relevant context for task"""
        pass

# Memory Write Interface
class MemoryWriter:
    async def update_state(
        self, 
        state_update: StateUpdate
    ):
        """Update agent state"""
        pass
    
    async def add_conclusion(
        self, 
        conclusion: Conclusion
    ):
        """Add temporary conclusion"""
        pass
```

#### Dependencies
- M13: Configuration & Infrastructure (storage backends)
- M12: Security Services (encryption for PHI)

#### Testing Requirements
```python
def test_compaction_preserves_critical_data():
    """Compaction keeps safety-critical information"""
    pass

def test_memory_stays_within_budget():
    """Memory never exceeds 200K tokens"""
    pass

def test_ttl_cleanup():
    """Expired items are removed"""
    pass
```

---

### M3: Tool Framework

**Purpose**: Tool management, discovery, and execution

#### Components

##### 3.1 Tool Registry
```python
class ToolRegistry:
    """
    Central registry for all tools
    """
    
    def __init__(self, registry_backend: RegistryBackend):
        self.backend = registry_backend
        self.cache = {}
        
    async def register_tool(self, tool_spec: ToolSpecification):
        """Register new tool"""
        # Validate spec
        self._validate_spec(tool_spec)
        
        # Check for conflicts
        existing = await self.backend.get(tool_spec.id)
        if existing:
            raise ToolRegistryError(
                f"Tool {tool_spec.id} already registered"
            )
        
        # Store
        await self.backend.save(tool_spec.id, tool_spec)
        
        # Update cache
        self.cache[tool_spec.id] = tool_spec
    
    async def get_tool(self, tool_id: str) -> ToolSpecification:
        """Retrieve tool specification"""
        # Check cache first
        if tool_id in self.cache:
            return self.cache[tool_id]
        
        # Load from backend
        spec = await self.backend.get(tool_id)
        if not spec:
            raise ToolNotFoundError(f"Tool {tool_id} not found")
        
        # Cache and return
        self.cache[tool_id] = spec
        return spec
    
    async def search_tools(
        self, 
        criteria: SearchCriteria
    ) -> List[ToolSpecification]:
        """Search for tools matching criteria"""
        return await self.backend.search(criteria)
```

##### 3.2 Tool Discovery Engine
```python
class ToolDiscoveryEngine:
    """
    Helps agents find appropriate tools
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.usage_tracker = UsageTracker()
        
    async def discover_tools_for_task(
        self, 
        task: Task,
        context: ExecutionContext
    ) -> List[ToolRecommendation]:
        """
        Find tools suitable for task
        """
        # Extract task requirements
        requirements = self._extract_requirements(task)
        
        # Search registry
        candidate_tools = await self.registry.search_tools(
            SearchCriteria(
                capabilities=requirements.capabilities,
                domain=task.domain,
                risk_tier_max=context.allowed_risk_tier
            )
        )
        
        # Rank by historical success
        ranked = self._rank_by_success_rate(
            candidate_tools,
            task.type
        )
        
        # Create recommendations
        return [
            ToolRecommendation(
                tool=tool,
                confidence=self._calculate_confidence(tool, task),
                alternatives=self._find_alternatives(tool),
                usage_stats=self.usage_tracker.get_stats(tool.id)
            )
            for tool in ranked[:5]  # Top 5
        ]
    
    def _rank_by_success_rate(
        self, 
        tools: List[ToolSpecification],
        task_type: str
    ) -> List[ToolSpecification]:
        """Rank tools by historical success for task type"""
        return sorted(
            tools,
            key=lambda t: self.usage_tracker.get_success_rate(
                t.id, 
                task_type
            ),
            reverse=True
        )
```

##### 3.3 Tool Executor
```python
class ToolExecutor:
    """
    Executes individual tools
    """
    
    def __init__(
        self, 
        mcp_client: MCPClient,
        security: SecurityService
    ):
        self.mcp = mcp_client
        self.security = security
        self.result_cache = ResultCache()
        
    async def execute(
        self,
        tool_spec: ToolSpecification,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """
        Execute tool via MCP
        """
        # 1. Authorization check
        auth_result = await self.security.check_authorization(
            user=context.user,
            tool=tool_spec,
            action="execute"
        )
        if not auth_result.authorized:
            raise UnauthorizedError(auth_result.reason)
        
        # 2. Consent check (if required)
        if tool_spec.requires_consent:
            consent = await self.security.get_consent(
                user=context.user,
                tool=tool_spec,
                parameters=parameters
            )
            if not consent.granted:
                raise ConsentDeniedError()
        
        # 3. Parameter validation
        validated_params = self._validate_parameters(
            parameters,
            tool_spec.parameter_schema
        )
        
        # 4. Check cache
        cache_key = self._generate_cache_key(tool_spec, validated_params)
        if cached := self.result_cache.get(cache_key):
            return cached
        
        # 5. Execute via MCP
        try:
            mcp_result = await self.mcp.call_tool(
                endpoint=tool_spec.mcp_endpoint,
                parameters=validated_params,
                timeout=tool_spec.sla.timeout,
                credentials=auth_result.credentials
            )
            
            # 6. Verify result
            verified_result = await self._verify_result(
                mcp_result,
                tool_spec
            )
            
            # 7. Cache result
            if tool_spec.cacheable:
                self.result_cache.set(
                    cache_key,
                    verified_result,
                    ttl=tool_spec.cache_ttl
                )
            
            return verified_result
            
        except MCPError as e:
            # Handle failure
            return ToolResult(
                status="FAILED",
                error=str(e),
                tool_id=tool_spec.id
            )
```

##### 3.4 Tool Verifier
```python
class ToolVerifier:
    """
    Validates tool outputs
    """
    
    async def verify_result(
        self,
        result: MCPResult,
        tool_spec: ToolSpecification
    ) -> ToolResult:
        """
        Verify tool execution result
        """
        checks = []
        
        # 1. Schema validation
        schema_check = self._validate_schema(
            result.data,
            tool_spec.output_schema
        )
        checks.append(schema_check)
        
        # 2. Completeness check
        completeness_check = self._check_completeness(
            result.data,
            tool_spec.required_fields
        )
        checks.append(completeness_check)
        
        # 3. Safety check (PHI scan, etc.)
        safety_check = await self._check_safety(
            result.data,
            tool_spec
        )
        checks.append(safety_check)
        
        # Aggregate
        all_passed = all(c.passed for c in checks)
        
        if not all_passed:
            failed = [c for c in checks if not c.passed]
            raise ToolVerificationError(
                f"Verification failed: {failed}"
            )
        
        return ToolResult(
            status="SUCCESS",
            data=result.data,
            tool_id=tool_spec.id,
            verification=checks
        )
```

#### Interfaces

```python
# Tool Specification Format
@dataclass
class ToolSpecification:
    id: str
    name: str
    version: str
    mcp_endpoint: str
    capabilities: List[str]
    parameter_schema: JSONSchema
    output_schema: JSONSchema
    risk_tier: RiskTier
    requires_consent: bool
    sla: SLA
    examples: List[Example]
    
# Tool Execution Interface
class Tool:
    async def execute(
        self,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> ToolResult:
        """Execute tool action"""
        pass
```

#### Dependencies
- M4: MCP Integration Layer
- M12: Security Services (RBAC, consent)
- M9: Safety & Guardrails (validation)

#### Testing Requirements
```python
def test_tool_discovery_finds_relevant_tools():
    """Discovery returns appropriate tools for task"""
    pass

def test_tool_execution_respects_timeout():
    """Execution aborts after SLA timeout"""
    pass

def test_tool_verifier_catches_bad_output():
    """Verifier rejects invalid tool results"""
    pass
```

---

### M4: MCP Integration Layer

**Purpose**: Universal protocol for enterprise system integration

#### Components

##### 4.1 MCP Client
```python
class MCPClient:
    """
    Client for calling MCP servers
    """
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.transport = MCPTransport(config)
        self.server_registry = MCPServerRegistry(config)
        
    async def call_tool(
        self,
        endpoint: str,
        parameters: Dict[str, Any],
        timeout: int,
        credentials: Credentials
    ) -> MCPResult:
        """
        Call tool via MCP protocol
        """
        # 1. Prepare MCP request
        mcp_request = MCPRequest(
            version="1.0",
            tool_endpoint=endpoint,
            parameters=parameters,
            credentials=self._prepare_credentials(credentials),
            trace_id=self._generate_trace_id(),
            timeout=timeout
        )
        
        # 2. Send via transport
        try:
            mcp_response = await self.transport.send(
                mcp_request,
                timeout=timeout
            )
            
            # 3. Validate response
            self._validate_response(mcp_response)
            
            return MCPResult(
                status="SUCCESS",
                data=mcp_response.data,
                metadata=mcp_response.metadata
            )
            
        except MCPTimeoutError:
            return MCPResult(
                status="TIMEOUT",
                error="MCP call timed out"
            )
        except MCPServerError as e:
            return MCPResult(
                status="SERVER_ERROR",
                error=str(e)
            )
```

##### 4.2 MCP Server Base Class
```python
class GeisingerMCPServer(ABC):
    """
    Base class for all Geisinger MCP servers
    """
    
    def __init__(self, tool_config: ToolConfig):
        self.tool_id = tool_config.tool_id
        self.version = tool_config.version
        self.risk_tier = tool_config.risk_tier
        self.auth_manager = AuthManager(tool_config)
        self.rate_limiter = RateLimiter(tool_config)
        self.audit_logger = AuditLogger(tool_config)
        
    async def handle_request(
        self,
        request: MCPRequest,
        context: MCPContext
    ) -> MCPResponse:
        """
        Standard request handling pipeline
        """
        # 1. Verify authentication
        auth_result = await self.auth_manager.verify(
            request.credentials,
            context
        )
        if not auth_result.authenticated:
            return MCPResponse.unauthorized()
        
        # 2. Check authorization
        authz_result = await self.auth_manager.check_authorization(
            auth_result.user,
            request.tool_endpoint
        )
        if not authz_result.authorized:
            return MCPResponse.forbidden()
        
        # 3. Validate input
        validation_result = self._validate_input(request.parameters)
        if not validation_result.valid:
            return MCPResponse.bad_request(validation_result.errors)
        
        # 4. Check rate limits
        rate_check = await self.rate_limiter.check(auth_result.user)
        if rate_check.exceeded:
            return MCPResponse.rate_limited()
        
        # 5. Begin audit log
        audit_id = await self.audit_logger.begin(request, context)
        
        try:
            # 6. Execute tool logic
            result = await self.execute(request.parameters, context)
            
            # 7. Validate output
            output_validation = self._validate_output(result)
            if not output_validation.valid:
                raise MCPServerError("Invalid output generated")
            
            # 8. Success audit
            await self.audit_logger.complete(
                audit_id,
                status="SUCCESS",
                result=result
            )
            
            return MCPResponse.success(result)
            
        except Exception as e:
            # Failure audit
            await self.audit_logger.complete(
                audit_id,
                status="FAILURE",
                error=str(e)
            )
            raise
    
    @abstractmethod
    async def execute(
        self,
        parameters: Dict[str, Any],
        context: MCPContext
    ) -> Any:
        """
        Tool-specific logic (implemented by subclasses)
        """
        pass
```

##### 4.3 Example MCP Server Implementation
```python
class EHRMCPServer(GeisingerMCPServer):
    """
    MCP server for EHR integration
    """
    
    def __init__(self, config: EHRConfig):
        super().__init__(config.tool_config)
        self.ehr_client = EHRClient(config.ehr_endpoint)
        
    async def execute(
        self,
        parameters: Dict[str, Any],
        context: MCPContext
    ) -> Any:
        """
        Execute EHR-specific operations
        """
        operation = parameters.get("operation")
        
        if operation == "fetch_patient_data":
            return await self._fetch_patient_data(parameters, context)
        elif operation == "get_lab_results":
            return await self._get_lab_results(parameters, context)
        else:
            raise MCPServerError(f"Unknown operation: {operation}")
    
    async def _fetch_patient_data(
        self,
        parameters: Dict[str, Any],
        context: MCPContext
    ) -> PatientData:
        """
        Fetch patient data from EHR
        """
        patient_id = parameters["patient_id"]
        data_type = parameters.get("data_type", "summary")
        
        # Call EHR API
        ehr_data = await self.ehr_client.get_patient(
            patient_id,
            data_type
        )
        
        # Transform to standard format
        return self._transform_patient_data(ehr_data)
```

#### Interfaces

```python
# MCP Protocol Messages
@dataclass
class MCPRequest:
    version: str
    tool_endpoint: str
    parameters: Dict[str, Any]
    credentials: Credentials
    trace_id: str
    timeout: int

@dataclass
class MCPResponse:
    status: str  # SUCCESS, FAILURE, UNAUTHORIZED, etc.
    data: Optional[Any]
    error: Optional[str]
    metadata: Dict[str, Any]
```

#### Dependencies
- M12: Security Services (auth, encryption)
- M13: Configuration & Infrastructure (networking)

#### Testing Requirements
```python
def test_mcp_client_calls_server():
    """Client successfully calls MCP server"""
    pass

def test_mcp_server_enforces_auth():
    """Server rejects unauthorized requests"""
    pass

def test_mcp_protocol_timeout():
    """Request times out after SLA"""
    pass
```

---

## Implementation Priority

### Phase 1: Foundation (Weeks 1-4)
**Goal**: Core infrastructure with basic agent loop

```
Sprint 1-2: Foundation
├─ M13: Configuration & Infrastructure
│  └─ Setup: Docker, K8s, CI/CD
├─ M12: Security Services (basic)
│  ├─ Authentication (OAuth2)
│  └─ Basic RBAC
└─ M2: Memory & Context Management (basic)
   ├─ Working memory (in-memory)
   └─ Basic context budget

Sprint 3-4: Agent Core (MVP)
├─ M1: Core Agent Runtime (basic)
│  ├─ Simple agent loop (no adaptation yet)
│  ├─ Basic planner
│  └─ Basic executor
├─ M3: Tool Framework (basic)
│  ├─ Tool registry (file-based)
│  └─ Direct tool execution (no MCP yet)
└─ M7: Knowledge Management (basic)
   └─ BluePrint loader (YAML files)

Deliverable: Agent can execute simple task with 1-2 tools
Test: Golden test "Schedule Meeting" passes
```

### Phase 2: MCP Integration (Weeks 5-8)
**Goal**: MCP-based tool integration

```
Sprint 5-6: MCP Layer
├─ M4: MCP Integration Layer
│  ├─ MCP client
│  ├─ MCP server base class
│  └─ Protocol implementation
└─ First MCP Server: JIRA
   ├─ Create ticket
   ├─ Update ticket
   └─ Search tickets

Sprint 7-8: Multi-Tool Support
├─ M3: Tool Framework (enhanced)
│  ├─ Tool discovery engine
│  ├─ Parallel execution
│  └─ Result caching
├─ Second MCP Server: GitHub
└─ Third MCP Server: SharePoint

Deliverable: Agent uses 3+ MCP servers
Test: Golden test "Product Sprint Planning" passes
```

### Phase 3: Safety & HITL (Weeks 9-12)
**Goal**: Production-ready safety

```
Sprint 9-10: Safety Layer
├─ M9: Safety & Guardrails
│  ├─ Input validation
│  ├─ Prompt injection defense
│  ├─ PHI scanner
│  └─ Output validation
└─ M8: HITL System
   ├─ Self-verification suite
   ├─ Tier classification
   └─ Approval queue UI

Sprint 11-12: Evaluation
├─ M10: Evaluation Harness
│  ├─ Golden test suite
│  ├─ Safety test suite
│  └─ Regression gate
└─ M11: Observability
   ├─ Metrics collection
   ├─ Dashboard
   └─ Alerting

Deliverable: Production-ready Product agent
Test: All safety tests pass, zero PHI leakage
```

### Phase 4: Clinical Domain (Weeks 13-16)
**Goal**: First clinical use case (read-only)

```
Sprint 13-14: Clinical Infrastructure
├─ EHR MCP Server (read-only)
├─ Clinical BluePrints
└─ Enhanced PHI protection

Sprint 15-16: Clinical Agent
├─ Enhanced M1: Adaptive planning
├─ Enhanced M2: Compaction service
└─ Clinical golden tests

Deliverable: Clinical rounding assistant (read-only)
Test: Zero writes, perfect citations
```

---

## Next Steps

1. **Review Architecture**
   - Stakeholder alignment meeting
   - Security review
   - Compliance sign-off

2. **Setup Infrastructure**
   - Create repositories (one per module)
   - Setup CI/CD pipelines
   - Configure development environments

3. **Create ADO Epics**
   - One epic per phase
   - Stories map to components
   - Include acceptance criteria

4. **Assign Ownership**
   - Each module needs an owner
   - Cross-functional teams per phase

5. **Begin Phase 1**
   - Start with M13 (infrastructure)
   - Then M12 (security)
   - Then M2 (memory)
   - Then M1 (agent core MVP)

**Remember**: *Small steps, testable outcomes, trusted agents.*

Every 2-week sprint should deliver something testable that passes golden tests.

---

**Document Version**: 1.0
**Last Updated**: January 2025
**Owner**: Senior Architect AI
