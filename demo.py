#!/usr/bin/env python3
"""
AI Product Manager Agent - Interactive Demo
Demonstrates the ProductManagerAgent processing a ServiceNow ticket

This demo shows:
1. Loading configuration
2. Initializing the ProductManagerAgent
3. Processing a sample ServiceNow ticket
4. Displaying the generated Discovery Form
5. Showing execution trace and observability

Usage:
    python demo.py
"""

import asyncio
import json
import sys
from pathlib import Path

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.pm_agent import ProductManagerAgent

console = Console()


def print_banner():
    """Display demo banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║  AI Product Manager Agent - Interactive Demo                 ║
║  Geisinger's First Production Agentic System                 ║
╚══════════════════════════════════════════════════════════════╝

This demo shows the complete Discovery Workflow in action:
  1. Extract ticket information
  2. Research vendor capabilities
  3. Research use case context
  4. Synthesize knowledge
  5. Draft Discovery Form
  6. Self-verify quality

The agent uses Claude to process a ServiceNow ticket and generate
a complete AI Discovery Form following Geisinger's governance
requirements.
"""
    console.print(Panel(banner, style="bold blue"))


def load_config():
    """Load configuration from development.yaml"""
    config_path = Path("config/development.yaml")

    if not config_path.exists():
        console.print("[red]Error: config/development.yaml not found[/red]")
        console.print("[yellow]Creating minimal configuration...[/yellow]")
        return {
            "agent": {
                "model": "claude-sonnet-4-5-20250929",
                "max_iterations": 10,
                "confidence_threshold": 0.7,
            },
            "blueprints": {
                "directory": "docs/blueprints",
                "templates": {
                    "ai_discovery_form": "ai-discovery-form.yaml"
                },
                "workflows": {
                    "discovery": "discovery-workflow.yaml"
                },
            },
        }

    with open(config_path) as f:
        return yaml.safe_load(f)


def get_sample_ticket():
    """Get sample ServiceNow ticket"""
    return """
ServiceNow Ticket INC0012345

Department: Cardiology
Requestor: Dr. Sarah Johnson, Chief of Cardiology
Priority: Medium
Date: January 15, 2025

Title: Epic In Basket AI Priority Scoring Implementation

Description:
The Cardiology department would like to implement Epic's In Basket AI feature
to help our physicians manage their electronic inbox more effectively.

PROBLEM:
Currently, our 25 cardiologists spend 2-3 hours per day processing inbox
messages. Critical clinical communications sometimes get buried among routine
notifications, administrative tasks, and system alerts. This leads to:
- Delayed responses to urgent patient needs
- Physician burnout and dissatisfaction
- Risk of missed critical communications

PROPOSED SOLUTION:
Epic's In Basket Priority Scoring uses machine learning to analyze inbox
messages and score them by urgency and clinical importance. The AI helps
physicians quickly identify and address the most critical items first.

VENDOR: Epic Systems
TECHNOLOGY: In Basket Priority Scoring with Machine Learning
EXPECTED USERS: 25 cardiologists initially, potential expansion to other specialties
TIMELINE: Pilot in Q2 2025, full rollout Q3 2025

EXPECTED BENEFITS:
- Reduce inbox processing time by 30-40% (45-60 minutes saved per physician daily)
- Ensure critical clinical communications are addressed within 1 hour
- Reduce physician burnout from inbox overload
- Improve patient safety by preventing missed urgent messages

BUSINESS CASE:
- Time savings: 25 physicians × 50 min/day × 200 days/year = 4,167 hours annually
- At $200/hour loaded cost = $833,400 in annual value
- Physician satisfaction improvement
- Patient safety improvement (reduced missed communications)

IMPLEMENTATION CONSIDERATIONS:
- Integration with Epic EHR (we're on Epic Foundation System)
- Training for all cardiology physicians
- Monitoring and adjustment period
- Potential expansion to other departments if successful

RISKS TO CONSIDER:
- Alert fatigue if too many messages flagged as high priority
- Over-reliance on AI leading to missed items the AI doesn't flag
- Need to validate performance with our specific patient population
- Equity considerations: ensure AI performs equally across patient demographics

NEXT STEPS:
We need a formal Discovery Form for the AI Governance Committee to review.
Please assist in creating comprehensive documentation that addresses all
governance requirements.

Contact: Dr. Sarah Johnson (sarah.johnson@geisinger.edu)
"""


async def run_demo():
    """Run the interactive demo"""
    print_banner()

    # Step 1: Check API key
    console.print("\n[bold cyan]Step 1: Checking environment...[/bold cyan]")

    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[yellow]Warning: ANTHROPIC_API_KEY not found in environment[/yellow]")
        console.print("[yellow]The demo will use mock responses instead of real Claude API calls[/yellow]")
        console.print()

        # Ask if they want to continue
        response = console.input("Continue with demo? (y/n): ")
        if response.lower() != 'y':
            console.print("[yellow]Demo cancelled. Set ANTHROPIC_API_KEY to use real API.[/yellow]")
            return
    else:
        console.print("[green]✓ ANTHROPIC_API_KEY found[/green]")

    # Step 2: Load configuration
    console.print("\n[bold cyan]Step 2: Loading configuration...[/bold cyan]")
    config = load_config()
    console.print(f"[green]✓ Configuration loaded[/green]")
    console.print(f"  Model: {config['agent']['model']}")
    console.print(f"  Max iterations: {config['agent']['max_iterations']}")

    # Step 3: Initialize agent
    console.print("\n[bold cyan]Step 3: Initializing ProductManagerAgent...[/bold cyan]")
    agent = ProductManagerAgent(config)
    console.print("[green]✓ Agent initialized[/green]")
    console.print(f"  Workflow loaded: {agent.discovery_workflow is not None}")
    console.print(f"  Template loaded: {agent.discovery_template is not None}")

    # Step 4: Display ticket
    console.print("\n[bold cyan]Step 4: Sample ServiceNow Ticket[/bold cyan]")
    ticket = get_sample_ticket()

    # Show first 500 chars
    preview = ticket[:500] + "..." if len(ticket) > 500 else ticket
    console.print(Panel(preview, title="ServiceNow Ticket INC0012345", border_style="blue"))

    console.print(f"\n[dim]Full ticket: {len(ticket)} characters[/dim]")

    # Ask to proceed
    console.print()
    response = console.input("[bold]Process this ticket? (y/n): [/bold]")
    if response.lower() != 'y':
        console.print("[yellow]Demo cancelled.[/yellow]")
        return

    # Step 5: Process ticket
    console.print("\n[bold cyan]Step 5: Processing ticket through Discovery Workflow...[/bold cyan]")
    console.print("[dim]This will take a few moments as the agent executes all 6 steps[/dim]\n")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Running Discovery Workflow...", total=None)

            # Process the ticket
            result = await agent.process_ticket(ticket)

            progress.update(task, completed=True)

        console.print("[green]✓ Workflow completed successfully![/green]\n")

        # Step 6: Display results
        console.print("[bold cyan]Step 6: Results[/bold cyan]\n")

        # Create results table
        results_table = Table(title="Processing Results", show_header=True, header_style="bold magenta")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")

        results_table.add_row("Duration", f"{result.duration_seconds:.1f} seconds")
        results_table.add_row("Steps Completed", f"{len(result.steps_completed)}/6")
        results_table.add_row("Confidence", f"{result.confidence:.0%}")
        results_table.add_row("Quality Score", f"{result.verification.get('overall_score', 0):.0%}")
        results_table.add_row("Requires Approval", "Yes" if result.requires_approval else "No")
        results_table.add_row("Trace ID", result.trace_id)

        console.print(results_table)
        console.print()

        # Display steps completed
        console.print("[bold]Workflow Steps Completed:[/bold]")
        for i, step in enumerate(result.steps_completed, 1):
            console.print(f"  {i}. [green]✓[/green] {step}")
        console.print()

        # Display verification results
        console.print("[bold]Quality Verification:[/bold]")
        verification = result.verification

        if verification.get('checks'):
            for check in verification['checks']:
                status = "[green]✓[/green]" if check.get('passed') else "[red]✗[/red]"
                score = check.get('score', 0)
                console.print(f"  {status} {check.get('dimension')}: {score:.0%}")

        if verification.get('issues'):
            console.print(f"\n[yellow]Issues found: {', '.join(verification['issues'])}[/yellow]")
        console.print()

        # Display form preview
        console.print("[bold cyan]Step 7: Generated Discovery Form[/bold cyan]\n")

        form = result.form
        console.print(f"[bold]Title:[/bold] {form.get('title', 'N/A')}")
        console.print(f"[bold]Sections:[/bold] {len(form.get('sections', []))}")
        console.print()

        # Show sections
        if form.get('sections'):
            console.print("[bold]Form Sections:[/bold]")
            for i, section in enumerate(form['sections'][:3], 1):  # Show first 3
                section_id = section.get('id', f'section_{i}')
                section_title = section.get('title', section_id)
                content_preview = str(section.get('content', section.get('fields', '')))[:100]
                console.print(f"\n  {i}. [cyan]{section_title}[/cyan]")
                console.print(f"     {content_preview}...")

            if len(form['sections']) > 3:
                console.print(f"\n  [dim]... and {len(form['sections']) - 3} more sections[/dim]")
        console.print()

        # Display trace information
        console.print("[bold cyan]Step 8: Execution Trace[/bold cyan]\n")

        trace = agent.get_trace(result.trace_id)
        if trace:
            console.print(f"[bold]Operation:[/bold] {trace.get('operation')}")
            console.print(f"[bold]Status:[/bold] {trace.get('status')}")
            console.print(f"[bold]Start Time:[/bold] {trace.get('start_time')}")
            console.print(f"[bold]End Time:[/bold] {trace.get('end_time')}")
            console.print(f"[bold]Total Steps:[/bold] {len(trace.get('steps', []))}")
            console.print()

            # Show step details
            if trace.get('steps'):
                console.print("[bold]Step Details:[/bold]")
                for step in trace['steps']:
                    status_icon = "[green]✓[/green]" if step['status'] == 'completed' else "[yellow]⟳[/yellow]"
                    console.print(f"  {status_icon} {step['step_id']}: {step['description']}")

        console.print()

        # Offer to save results
        console.print("[bold cyan]Step 9: Save Results?[/bold cyan]\n")
        response = console.input("Save Discovery Form to file? (y/n): ")

        if response.lower() == 'y':
            output_file = Path("output") / f"discovery_form_{result.trace_id}.json"
            output_file.parent.mkdir(exist_ok=True)

            # Save full result
            output_data = {
                "form": form,
                "metadata": {
                    "trace_id": result.trace_id,
                    "duration_seconds": result.duration_seconds,
                    "confidence": result.confidence,
                    "steps_completed": result.steps_completed,
                },
                "verification": verification,
            }

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            console.print(f"[green]✓ Saved to: {output_file}[/green]")

        console.print()
        console.print("[bold green]Demo completed successfully![/bold green]")
        console.print()
        console.print("[dim]Next steps:[/dim]")
        console.print("[dim]  • Review the generated Discovery Form[/dim]")
        console.print("[dim]  • Submit for human approval (Tier 3 HITL)[/dim]")
        console.print("[dim]  • Present to AI Governance Committee[/dim]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[yellow]This might be due to missing API key or configuration[/yellow]")

    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print(f"[dim]Error type: {type(e).__name__}[/dim]")

        # Show trace if available
        import traceback
        console.print("\n[dim]Traceback:[/dim]")
        console.print(traceback.format_exc())


def main():
    """Main entry point"""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
