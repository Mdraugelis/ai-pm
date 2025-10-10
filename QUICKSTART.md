# Quick Start Guide - AI Product Manager Agent

Welcome! This guide gets you up and running with the AI Product Manager Agent in 5 minutes.

## ✅ What's Currently Available

The system currently has:

### Core Components ✓
- **ProductManagerAgent** - Main agent class (`src/agent/pm_agent.py`)
- **AgentOrchestrator** - Agent loop controller (`src/agent/orchestrator.py`)
- **LLMInterface** - Claude SDK integration (`src/agent/llm_interface.py`)
- **Tool Framework** - Base classes and Azure DevOps integration (`src/tools/`)

### Domain Knowledge ✓
- **Discovery Workflow** - 6-step process blueprint (`docs/blueprints/discovery-workflow.yaml`)
- **AI Discovery Form** - Complete form specification (`docs/blueprints/ai-discovery-form.yaml`)
- **AI PM Strategy** - Strategic framework (`docs/blueprints/ai-product-manager-strategy.yaml`)

### Testing ✓
- **Unit Tests** - 30+ tests for ProductManagerAgent (`tests/unit/test_pm_agent.py`)
- **Integration Tests** - End-to-end workflow tests (`tests/integration/test_pm_agent_integration.py`)

### User Experience ✓
- **Interactive Demo** - Full featured demo (`demo.py`)
- **Basic Usage Example** - Simple API example (`examples/basic_usage.py`)
- **CLI Skeleton** - Command-line interface (`src/main.py`)

## 🚀 Fastest Way to See It Work

### Option 1: Interactive Demo (Recommended)

The interactive demo shows the complete Discovery Workflow with rich formatting.

```bash
# 1. Set your API key
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 2. Run the demo
python demo.py
```

**What you'll see**:
- Complete 6-step Discovery Workflow execution
- Progress indicators and spinners
- Results in formatted tables
- Quality verification results
- Execution trace
- Option to save the generated Discovery Form

**Example output**:
```
╔══════════════════════════════════════════════════════════════╗
║  AI Product Manager Agent - Interactive Demo                 ║
║  Geisinger's First Production Agentic System                 ║
╚══════════════════════════════════════════════════════════════╝

Step 1: Checking environment...
✓ ANTHROPIC_API_KEY found

Step 2: Loading configuration...
✓ Configuration loaded
  Model: claude-sonnet-4-5-20250929
  Max iterations: 10

Step 3: Initializing ProductManagerAgent...
✓ Agent initialized
  Workflow loaded: True
  Template loaded: True

Step 4: Sample ServiceNow Ticket
[Shows sample ticket...]

Process this ticket? (y/n): y

Step 5: Processing ticket through Discovery Workflow...
⠋ Running Discovery Workflow...
✓ Workflow completed successfully!

Step 6: Results
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Metric            ┃ Value            ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ Duration          │ 45.2 seconds     │
│ Steps Completed   │ 6/6              │
│ Confidence        │ 85%              │
│ Quality Score     │ 85%              │
│ Requires Approval │ Yes              │
└───────────────────┴──────────────────┘

[Shows form preview, trace, and save option...]
```

### Option 2: Basic Usage Script

Simpler script showing the core API:

```bash
python examples/basic_usage.py
```

**Example output**:
```
Processing ticket...

✓ Discovery Form Generated
  Title: Epic In Basket AI - Cardiology Inbox Prioritization
  Sections: 7
  Confidence: 85%
  Duration: 42.1s
  Steps: extract_basics, research_vendor, research_use_case, synthesize, draft_form, self_verify

✓ Quality checks passed

✓ Form saved to: output/discovery_form.txt
```

### Option 3: Run Tests

See the agent in action through automated tests:

```bash
# Unit tests (fast, mocked LLM)
pytest tests/unit/test_pm_agent.py -v

# Integration tests (requires API key)
pytest tests/integration/test_pm_agent_integration.py -v -m integration
```

## 📋 Prerequisites

### Required
1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Anthropic API Key**
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

   Get one at: https://console.anthropic.com/

### Optional
- **Brave Search API Key** (for real web search - uses mock results without it)
  ```bash
  export BRAVE_SEARCH_API_KEY=your-brave-api-key
  ```
  Get free tier (2,000 queries/month) at: https://brave.com/search/api/

- Configuration file (`config/development.yaml`) - auto-created if missing
- Blueprint files in `docs/blueprints/` - loaded if available
- PostgreSQL database - not required for demo/examples

## 💻 Code Usage Examples

### Example 1: Process a Ticket

```python
import asyncio
import yaml
from src.agent.pm_agent import ProductManagerAgent

async def main():
    # Load config
    with open("config/development.yaml") as f:
        config = yaml.safe_load(f)

    # Create agent
    agent = ProductManagerAgent(config)

    # Process ticket
    ticket = """
    ServiceNow Ticket INC0012345
    Department: Cardiology
    We want Epic's In Basket AI for inbox prioritization...
    """

    result = await agent.process_ticket(ticket)

    # Use results
    print(f"Form: {result.form['title']}")
    print(f"Confidence: {result.confidence:.0%}")

asyncio.run(main())
```

### Example 2: Step-by-Step Processing

```python
# Extract ticket information
ticket_info = await agent.extract_ticket_info(ticket_text)
print(f"Vendor: {ticket_info.vendor}")
print(f"Use case: {ticket_info.use_case}")

# Research vendor
vendor_info = await agent.research_vendor(ticket_info.vendor)
print(f"Capabilities: {vendor_info.get('ai_products')}")

# Research use case
use_case_info = await agent.research_use_case(
    ticket_info.use_case,
    ticket_info.department
)
print(f"Similar implementations: {use_case_info.get('similar_implementations')}")

# Continue with synthesis, drafting, verification...
```

### Example 3: With Observability

```python
# Process ticket
result = await agent.process_ticket(ticket)

# Get execution trace
trace = agent.get_trace(result.trace_id)

# Analyze what the agent did
print(f"Operation: {trace['operation']}")
print(f"Status: {trace['status']}")
print(f"Duration: {trace['end_time']} - {trace['start_time']}")

# Show each step
for step in trace['steps']:
    print(f"  {step['step_id']}: {step['status']}")
    if 'result' in step:
        print(f"    Result: {step['result']}")
```

## 🎯 What Each Demo Shows

### `demo.py` - Full Interactive Experience
**Shows**: Complete workflow, quality verification, tracing, rich UI
**Best for**: Understanding the full agent capabilities
**Runtime**: ~1-2 minutes with API calls

### `examples/basic_usage.py` - Simple API
**Shows**: Core API usage, minimal code
**Best for**: Learning the API quickly
**Runtime**: ~30-60 seconds with API calls

### Unit Tests - Individual Methods
**Shows**: Each agent method working independently
**Best for**: Understanding individual components
**Runtime**: <1 second (mocked)

### Integration Tests - End-to-End
**Shows**: Real workflows with actual LLM calls
**Best for**: Validating full system behavior
**Runtime**: ~2-3 minutes per test

## 📁 Output Files

After running demos, check:

```bash
output/
├── discovery_form_<trace_id>.json    # Full results from demo.py
└── discovery_form.txt                 # Text output from basic_usage.py
```

## 🔍 What's Not Yet Implemented

These features are planned but not yet built:

- ❌ ServiceNow integration (tool exists, not connected to agent)
- ❌ Database persistence (schema exists, not used by agent)
- ❌ HITL approval UI (framework exists, not interactive yet)
- ❌ Web search tool (using LLM knowledge instead)
- ❌ Document generator tool (agent uses LLM directly)
- ❌ Multi-agent orchestration
- ❌ Vector database / RAG
- ❌ Production deployment

**Current focus**: Core agent loop, LLM integration, workflow execution

## 🐛 Troubleshooting

### "No module named 'src'"
```bash
# Run from project root
cd /path/to/ai-pm
python demo.py
```

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Or add to .env file
```

### "config/development.yaml not found"
Demo will auto-create minimal config. Or:
```bash
# Check if file exists
ls -la config/development.yaml

# It should be there from git, if not:
# File is tracked in repo, pull latest
```

### "Too slow / Taking forever"
This is normal! Each workflow step makes LLM calls:
- Extract: ~5-10 seconds
- Research vendor: ~10-15 seconds
- Research use case: ~10-15 seconds
- Synthesize: ~5-10 seconds
- Draft form: ~15-20 seconds
- Verify: ~5-10 seconds

**Total: 50-80 seconds for full workflow**

## 🎓 Next Steps

Once you've run the demos:

1. **Explore the code**: Start with `src/agent/pm_agent.py`
2. **Read the blueprints**: Check `docs/blueprints/discovery-workflow.yaml`
3. **Try different tickets**: Modify the ticket text in examples
4. **Run the tests**: See `pytest tests/unit/ -v`
5. **Read the architecture**: See `docs/architecture/`

## 📚 Key Documentation

- **README.md** - Full project overview
- **CLAUDE.md** - Instructions for AI assistants
- **examples/README.md** - Detailed example documentation
- **docs/blueprints/** - Domain knowledge specifications

## ❓ Questions?

- Check the main **README.md** for architecture details
- Review **examples/README.md** for usage patterns
- Look at test files for more examples
- Read blueprint YAML files for workflow specifications

---

**Ready to see it in action?**

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python demo.py
```

Enjoy! 🚀
