"""
Proxy quickstart for local testing.
"""

import os


def main():
    print("Sentinel Proxy Quickstart")
    print("=" * 40)
    if not os.environ.get("OPENAI_API_KEY"):
        print("Set OPENAI_API_KEY first.")
        return

    print("Starting proxy on http://localhost:8741")
    print("Dashboard: http://localhost:8741/dashboard")
    print('Use: OpenAI(base_url="http://localhost:8741/v1")')
    from sentinel.proxy.server import run

    run(port=8741)


if __name__ == "__main__":
    main()
