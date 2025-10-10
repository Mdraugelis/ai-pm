# ProductManagerAgent Examples

This directory contains example scripts showing how to use the AI Product Manager Agent.

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

The simplest way to use the ProductManagerAgent:

```bash
python examples/basic_usage.py
```

**What it does**:
- Loads configuration
- Creates ProductManagerAgent
- Processes a simple ServiceNow ticket
- Displays results
- Saves Discovery Form to file

**Best for**: Understanding the basic API

### 2. Interactive Demo (`../demo.py`)

Full interactive demonstration with Rich UI:

```bash
python demo.py
```

**What it does**:
- Shows complete Discovery Workflow (all 6 steps)
- Displays progress with spinners
- Shows detailed results in formatted tables
- Provides trace information
- Offers to save results

**Best for**: Seeing the full agent capabilities

## Prerequisites

### Required

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Configuration file**
   ```bash
   # config/development.yaml must exist
   # Or the examples will create a minimal config
   ```

3. **Anthropic API Key** (for real LLM calls)
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```

   Without API key, examples will still run but may have limited functionality.

### Optional

- **Blueprint files** (in `docs/blueprints/`)
  - `discovery-workflow.yaml`
  - `ai-discovery-form.yaml`

  Examples work without these, but load them if available.

## Usage Patterns

### Pattern 1: Simple Ticket Processing

```python
from src.agent.pm_agent import ProductManagerAgent

# Initialize
agent = ProductManagerAgent(config)

# Process
result = await agent.process_ticket(ticket_text)

# Use results
print(result.form['title'])
```

### Pattern 2: Step-by-Step Processing

```python
# Extract info
ticket_info = await agent.extract_ticket_info(ticket_text)

# Research
vendor_info = await agent.research_vendor(ticket_info.vendor)
use_case_info = await agent.research_use_case(ticket_info.use_case)

# Synthesize
synthesis = await agent.synthesize_knowledge(
    ticket_info, vendor_info, use_case_info
)

# Draft
research = ResearchContext(
    vendor_info=vendor_info,
    use_case_info=use_case_info,
    synthesis=synthesis
)
form = await agent.draft_discovery_form(ticket_info, research)

# Verify
verification = await agent.verify_form(form)
```

### Pattern 3: With Observability

```python
# Process with tracing
result = await agent.process_ticket(ticket)

# Get trace
trace = agent.get_trace(result.trace_id)

# Analyze
for step in trace['steps']:
    print(f"{step['step_id']}: {step['status']}")
```

## Example Tickets

### Cardiology Inbox AI
```
ServiceNow Ticket INC0012345
Department: Cardiology
Title: Epic In Basket AI Implementation
Description: Implement Epic's AI to prioritize physician inbox messages...
```

### Radiology Nodule Detection
```
ServiceNow Ticket INC0056789
Department: Radiology
Title: AI Lung Nodule Detection
Description: Evaluate Aidoc's AI for detecting lung nodules on CT scans...
```

### Simple Request
```
ServiceNow Ticket INC0099999
Department: IT
We want to use ChatGPT to help write emails.
Vendor: OpenAI
```

## Output Examples

### Discovery Form Structure
```json
{
  "title": "Epic In Basket AI - Cardiology Inbox Prioritization",
  "sections": [
    {
      "id": "basic_information",
      "title": "Basic Information",
      "fields": {
        "program_owner": "Dr. Sarah Johnson",
        "department": "Cardiology",
        "vendor": "Epic Systems"
      }
    },
    {
      "id": "problem_definition",
      "title": "Problem Definition",
      "fields": {
        "background": "...",
        "goal": "..."
      }
    },
    ...
  ]
}
```

### Processing Result
```python
ProcessingResult(
    form={...},
    trace_id="process_ticket_1737123456.789",
    verification={'passed': True, 'overall_score': 0.85},
    duration_seconds=45.2,
    steps_completed=['extract_basics', 'research_vendor', ...],
    confidence=0.85,
    requires_approval=True
)
```

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### "config/development.yaml not found"
Examples will create minimal config automatically, or:
```bash
cp config/development.yaml.example config/development.yaml
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt

# Or for development
pip install -e .
```

### "Blueprint file not found"
This is a warning, not an error. Examples work without blueprints but load them if available.

## Next Steps

After running the examples:

1. **Review generated forms** in `output/` directory
2. **Examine traces** to understand agent decisions
3. **Customize workflows** by editing blueprint files
4. **Build your own tools** using the tool framework
5. **Integrate with your systems** (ServiceNow, Azure DevOps, etc.)

## Additional Resources

- **Main README**: `../README.md`
- **Architecture docs**: `../docs/architecture/`
- **Blueprint specs**: `../docs/blueprints/`
- **Test examples**: `../tests/integration/test_pm_agent_integration.py`
