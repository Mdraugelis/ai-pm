"""
AI Product Manager Agent - Main Entry Point
Geisinger's First Production Agentic System

Usage:
    python src/main.py --interactive
    python src/main.py --ticket INC0012345
    python src/main.py --initiative "Epic AI Inbox Prioritization"
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


def print_banner():
    """Display application banner"""
    banner_text = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   AI Product Manager Agent v0.1.0                         ║
    ║   Geisinger's First Production Agentic System             ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text, style="bold blue"))


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Product Manager Agent CLI"""
    pass


@cli.command()
@click.option(
    "--ticket",
    "-t",
    help="ServiceNow ticket number to process (e.g., INC0012345)",
)
@click.option(
    "--initiative",
    "-i",
    help="Initiative title to work on",
)
def run(ticket: str, initiative: str):
    """
    Run the agent to process a ticket or initiative

    Examples:
        python src/main.py run --ticket INC0012345
        python src/main.py run --initiative "Epic AI Inbox"
    """
    print_banner()

    if not ticket and not initiative:
        console.print("[red]Error: Please provide either --ticket or --initiative[/red]")
        sys.exit(1)

    console.print(f"[yellow]Note: Agent implementation in progress...[/yellow]")
    console.print(f"[green]Would process: {ticket or initiative}[/green]")

    # TODO: Implement agent execution
    # from src.agent.orchestrator import AgentOrchestrator
    # orchestrator = AgentOrchestrator()
    # result = asyncio.run(orchestrator.execute_task(task))


@cli.command()
def interactive():
    """
    Run the agent in interactive mode

    Example:
        python src/main.py interactive
    """
    print_banner()
    console.print("[bold green]Interactive mode starting...[/bold green]")
    console.print()

    console.print("Available commands:")
    console.print("  - Type a SNOW ticket number (e.g., INC0012345)")
    console.print("  - Type 'list' to see all initiatives")
    console.print("  - Type 'help' for more options")
    console.print("  - Type 'exit' to quit")
    console.print()

    while True:
        try:
            user_input = console.input("[bold cyan]Agent>[/bold cyan] ").strip()

            if user_input.lower() == "exit":
                console.print("[yellow]Goodbye![/yellow]")
                break

            elif user_input.lower() == "help":
                console.print("[green]Help: Agent commands will be available soon![/green]")

            elif user_input.lower() == "list":
                console.print("[yellow]Feature in progress: Would list all initiatives[/yellow]")

            elif user_input.startswith("INC"):
                console.print(f"[green]Would process ticket: {user_input}[/green]")

            else:
                console.print("[yellow]Unknown command. Type 'help' for options.[/yellow]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except EOFError:
            break


@cli.command()
def setup():
    """
    Setup development environment

    Example:
        python src/main.py setup
    """
    print_banner()
    console.print("[bold green]Setting up development environment...[/bold green]")
    console.print()

    # Check for required files
    checks = [
        (".env", "Environment variables"),
        ("docs/blueprints/meta-blueprint.yaml", "Meta-blueprint"),
        ("docs/blueprints/product-mgmt-blueprint.yaml", "Product Management blueprint"),
    ]

    for file_path, description in checks:
        path = Path(file_path)
        if path.exists():
            console.print(f"  ✓ {description} found")
        else:
            console.print(f"  ✗ {description} missing: {file_path}")

    console.print()
    console.print("[yellow]Next steps:[/yellow]")
    console.print("  1. Copy .env.example to .env and add your API keys")
    console.print("  2. Run: make db-up")
    console.print("  3. Run: make db-migrate")
    console.print("  4. Run: make db-seed")
    console.print("  5. Run: python src/main.py interactive")


@cli.command()
def test_db():
    """
    Test database connection

    Example:
        python src/main.py test-db
    """
    print_banner()
    console.print("[bold green]Testing database connection...[/bold green]")

    try:
        # TODO: Implement database connection test
        # from src.memory.database import DatabaseManager
        # db = DatabaseManager()
        # db.test_connection()
        console.print("[yellow]Database module not yet implemented[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def load_blueprints():
    """
    Load and validate blueprints

    Example:
        python src/main.py load-blueprints
    """
    print_banner()
    console.print("[bold green]Loading blueprints...[/bold green]")

    try:
        # TODO: Implement blueprint loading
        # from src.knowledge.blueprint_loader import BluePrintLoader
        # loader = BluePrintLoader()
        # blueprints = loader.load_all()
        console.print("[yellow]Blueprint loader not yet implemented[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    cli()
