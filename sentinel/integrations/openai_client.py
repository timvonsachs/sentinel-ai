"""OpenAI client wrapper placeholder."""

from typing import Any, Dict


class SentinelOpenAIClient:
    """Minimal wrapper that can be extended with instrumentation."""

    def __init__(self, client: Any, organism: Any = None):
        self.client = client
        self.organism = organism

    def create(self, **kwargs) -> Dict[str, Any]:
        # Placeholder passthrough behavior
        response = self.client.create(**kwargs)
        return {"response": response}
