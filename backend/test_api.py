"""
Test API Script
AI Atlas - Backend API

Simple script to test the AI Atlas backend API endpoints.
"""

import asyncio
import httpx
from datetime import datetime


async def test_backend():
    """Test backend API endpoints"""

    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=60.0) as client:
        print("=" * 60)
        print("AI Atlas - Backend API Test")
        print("=" * 60)
        print()

        # 1. Health check
        print("1. Testing health endpoint...")
        response = await client.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        print()

        # 2. Set mode
        print("2. Setting agent mode to 'ai_discovery'...")
        try:
            response = await client.post(
                f"{base_url}/api/agent/mode", json={"mode": "ai_discovery"}
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
            print("   (Expected if ANTHROPIC_API_KEY not set)")
        print()

        # 3. Get status
        print("3. Getting agent status...")
        try:
            response = await client.get(f"{base_url}/api/agent/status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

        # 4. Upload document
        print("4. Uploading test document...")
        try:
            response = await client.post(
                f"{base_url}/api/documents/upload",
                json={
                    "content": "Epic Inbox AI is a clinical decision support tool that helps clinicians manage their inbox messages more efficiently.",
                    "doc_type": "vendor_doc",
                    "metadata": {"vendor": "Epic", "product": "Inbox AI"},
                },
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

        # 5. List documents
        print("5. Listing documents...")
        try:
            response = await client.get(f"{base_url}/api/documents")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

        # 6. Stream message (if API key is set)
        print("6. Streaming message response...")
        print("   (Skipped - requires ANTHROPIC_API_KEY)")
        print("   To test streaming:")
        print("   curl -N http://localhost:8000/api/agent/message/stream \\")
        print("     -H 'Content-Type: application/json' \\")
        print("     -d '{\"message\": \"Generate Discovery Form\"}'")
        print()

        print("=" * 60)
        print("Test complete!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_backend())
