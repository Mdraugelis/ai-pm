#!/usr/bin/env python3
"""
Basic Usage Example - ProductManagerAgent

This example shows the simplest way to use the ProductManagerAgent
to process a ServiceNow ticket and generate a Discovery Form.

Usage:
    python examples/basic_usage.py
"""

import asyncio
import sys
from pathlib import Path

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.pm_agent import ProductManagerAgent


async def main():
    """Basic usage example"""

    # 1. Load configuration
    config_path = Path("config/development.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # 2. Create agent
    agent = ProductManagerAgent(config)

    # 3. Define ticket
    ticket = """
ServiceNow Ticket INC0012345

Department: Cardiology
Requestor: Dr. Sarah Johnson

We want to implement Epic's In Basket AI to help prioritize inbox messages.
Our physicians spend 2-3 hours daily on inbox management.

Vendor: Epic Systems
Expected benefit: 30-40% time savings
    """

    # 4. Process ticket
    print("Processing ticket...")
    result = await agent.process_ticket(ticket)

    # 5. Display results
    print(f"\n✓ Discovery Form Generated")
    print(f"  Title: {result.form.get('title')}")
    print(f"  Sections: {len(result.form.get('sections', []))}")
    print(f"  Confidence: {result.confidence:.0%}")
    print(f"  Duration: {result.duration_seconds:.1f}s")
    print(f"  Steps: {', '.join(result.steps_completed)}")

    # 6. Check verification
    if result.verification['passed']:
        print(f"\n✓ Quality checks passed")
    else:
        print(f"\n⚠ Issues found: {result.verification['issues']}")

    # 7. Save form
    output_path = Path("output/discovery_form.txt")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(f"Title: {result.form.get('title')}\n\n")
        for section in result.form.get('sections', []):
            f.write(f"## {section.get('title', section.get('id'))}\n")
            f.write(f"{section.get('content', section.get('fields'))}\n\n")

    print(f"\n✓ Form saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
