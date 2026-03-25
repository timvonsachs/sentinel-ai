"""
Test different query complexities and verify router model selection.
Run while proxy is active on port 8741.
"""

import asyncio
import os

import httpx


queries = [
    ("Hi", "trivial"),
    ("Thanks!", "trivial"),
    ("Yes", "trivial"),
    ("Ok", "trivial"),
    ("What is 2+2?", "simple"),
    ("What time is it?", "simple"),
    ("How many days in a week?", "simple"),
    ("What color is the sky?", "simple"),
    ("Explain how photosynthesis works", "medium"),
    ("Summarize the plot of Romeo and Juliet", "medium"),
    ("Describe the difference between TCP and UDP", "medium"),
    (
        "Write a Python function that implements a binary search tree with insert, "
        "delete, and search operations. Include error handling and docstrings.",
        "complex",
    ),
    (
        "Analyze the geopolitical implications of AI regulation across G7 nations "
        "with specific policy recommendations for each country.",
        "complex",
    ),
    (
        "Compare and contrast Keynesian and Austrian economics, including their "
        "historical context, key proponents, modern applications, and relevance to "
        "current monetary policy.",
        "complex",
    ),
    (
        "Write a comprehensive technical review of the transformer architecture, "
        "including attention mechanisms, positional encoding, and recent improvements "
        "like flash attention and sparse attention.",
        "complex",
    ),
    ("What are the legal implications of using AI in medical diagnosis under EU regulations?", "high-risk"),
    ("Review this financial contract clause for potential compliance issues with GDPR and the EU AI Act.", "high-risk"),
]


async def main():
    print("Sentinel Router Test - Complexity vs Model Selection")
    print("=" * 80)
    print(f"{'Query':<55} {'Expected':<10} {'Model':<18} Result")
    print("-" * 80)

    correct = 0
    total = 0

    api_key = os.environ.get("OPENAI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    async with httpx.AsyncClient(timeout=30) as client:
        for query, expected_tier in queries:
            try:
                r = await client.post(
                    "http://localhost:8741/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-4o",
                        "messages": [{"role": "user", "content": query}],
                        "max_tokens": 100,
                    },
                )
                data = r.json()
                sentinel = data.get("sentinel", {})
                model = sentinel.get("model_used", "unknown")

                if expected_tier in ("trivial", "simple"):
                    expected_model = "gpt-4o-mini"
                elif expected_tier in ("complex", "high-risk"):
                    expected_model = "gpt-4o"
                else:
                    expected_model = "any"

                if expected_model == "any":
                    match = "~"
                elif model == expected_model:
                    match = "OK"
                    correct += 1
                else:
                    match = "FAIL"
                total += 1 if expected_model != "any" else 0

                short_query = query[:52] + "..." if len(query) > 55 else query
                print(f"{short_query:<55} {expected_tier:<10} {model:<18} {match}")
            except Exception as e:
                short_query = query[:52] + "..." if len(query) > 55 else query
                print(f"{short_query:<55} {'ERROR':<10} {str(e)[:18]:<18} FAIL")

    print("=" * 80)
    print(f"Routing accuracy: {correct}/{total} ({correct / max(1, total) * 100:.0f}%)")

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:8741/v1/sentinel/savings")
            report = r.json()
            print(
                f"Total savings: ${report.get('total_savings', 0):.4f} "
                f"({report.get('savings_percentage', 0):.0f}%)"
            )
            print(f"Queries by model: {report.get('queries_by_model', {})}")
    except Exception:
        pass

    print("Dashboard: http://localhost:8741/dashboard")


if __name__ == "__main__":
    asyncio.run(main())
