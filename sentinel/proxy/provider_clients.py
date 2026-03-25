"""
Multi-provider client for OpenAI-compatible proxy forwarding.
"""

from typing import Dict, Optional
import time

import httpx

from .config import ProviderConfig


class ProviderClient:
    """Generic LLM provider client."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=60.0,
            headers=self._default_headers(),
        )

    def _default_headers(self) -> dict:
        if self.config.name == "openai":
            return {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }
        if self.config.name == "anthropic":
            return {
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            }
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(self, request_data: dict, model: str = None) -> dict:
        if self.config.name == "openai":
            return await self._openai_completion(request_data, model)
        if self.config.name == "anthropic":
            return await self._anthropic_completion(request_data, model)
        return await self._generic_completion(request_data, model)

    async def _openai_completion(self, request_data: dict, model: str = None) -> dict:
        payload = {**request_data, "model": model} if model else request_data
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def _anthropic_completion(self, request_data: dict, model: str = None) -> dict:
        messages = request_data.get("messages", [])
        system = ""
        chat_messages = []
        for message in messages:
            if message.get("role") == "system":
                system = message.get("content", "")
            else:
                chat_messages.append(
                    {
                        "role": message.get("role", "user"),
                        "content": message.get("content", ""),
                    }
                )

        if not chat_messages or chat_messages[0]["role"] != "user":
            chat_messages.insert(0, {"role": "user", "content": "Hello"})

        anthropic_payload = {
            "model": model or request_data.get("model", "claude-sonnet-4-20250514"),
            "max_tokens": request_data.get("max_tokens", 1024),
            "messages": chat_messages,
        }
        if system:
            anthropic_payload["system"] = system
        if request_data.get("temperature") is not None:
            anthropic_payload["temperature"] = request_data["temperature"]

        response = await self.client.post("/messages", json=anthropic_payload)
        response.raise_for_status()
        data = response.json()

        content = ""
        if data.get("content"):
            content = "".join(block.get("text", "") for block in data["content"] if block.get("type") == "text")

        input_tokens = data.get("usage", {}).get("input_tokens", 0)
        output_tokens = data.get("usage", {}).get("output_tokens", 0)
        return {
            "id": data.get("id", f"sentinel-{int(time.time() * 1000)}"),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data.get("model", model),
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        }

    async def _generic_completion(self, request_data: dict, model: str = None) -> dict:
        payload = {**request_data, "model": model} if model else request_data
        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()


class ProviderPool:
    """Manages multiple provider clients."""

    def __init__(self):
        self.clients: Dict[str, ProviderClient] = {}
        self.model_to_provider: Dict[str, str] = {}

    def add_provider(self, config: ProviderConfig):
        self.clients[config.name] = ProviderClient(config)
        for model in config.models:
            self.model_to_provider[model] = config.name

    def get_client(self, model: str) -> Optional[ProviderClient]:
        provider_name = self.model_to_provider.get(model)
        if provider_name:
            return self.clients.get(provider_name)
        if self.clients:
            return list(self.clients.values())[0]
        return None

    def get_provider_for_model(self, model: str) -> Optional[str]:
        return self.model_to_provider.get(model)

    async def close_all(self):
        for client in self.clients.values():
            await client.close()
