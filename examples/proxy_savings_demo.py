"""
Proxy savings demo using a running local proxy.
"""

import asyncio
import os
import sys

try:
    import httpx
except ImportError:
    print("pip install httpx")
    sys.exit(1)


async def main():
    base_url = "http://localhost:8741/v1"
    print("Sentinel Proxy Savings Demo")
    print("=" * 50)
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get("http://localhost:8741/")
            if r.status_code != 200:
                print("Start proxy first: python examples/proxy_quickstart.py")
                return
        except Exception:
            print("Start proxy first: python examples/proxy_quickstart.py")
            return

    queries = [
        ("What is 2+2?", "simple"),
        ("Hello!", "trivial"),
        ("Explain quantum computing in detail and practical applications.", "complex"),
        ("Write a Python linked-list merge sort with explanation.", "code"),
    ]

    headers = {"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', 'sk-test')}"}
    async with httpx.AsyncClient(timeout=60) as client:
        for query, label in queries:
            print(f"\n[{label}] {query[:60]}")
            r = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 200,
                },
            )
            data = r.json()
            if "error" in data:
                print("Error:", data["error"].get("message"))
                continue
            meta = data.get("sentinel", {})
            print("Model:", meta.get("model_used"))
            print("Routed:", meta.get("routed"))
            print("Trust:", meta.get("trust_score"))
            print("Savings call:", meta.get("savings_this_call", 0))

    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8741/v1/sentinel/savings")
        report = r.json()
        print("\nSavings report:", report)


if __name__ == "__main__":
    asyncio.run(main())
