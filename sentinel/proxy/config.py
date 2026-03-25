"""
Proxy configuration.
"""

from dataclasses import dataclass, field
from typing import Dict, List
import json
import os


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""

    name: str
    api_key: str
    base_url: str
    models: List[str] = field(default_factory=list)
    cost_per_1k_input: Dict[str, float] = field(default_factory=dict)
    cost_per_1k_output: Dict[str, float] = field(default_factory=dict)
    quality_score: Dict[str, float] = field(default_factory=dict)
    speed_ms: Dict[str, float] = field(default_factory=dict)


@dataclass
class ProxyConfig:
    """Main proxy configuration."""

    host: str = "0.0.0.0"
    port: int = 8741
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    default_provider: str = "openai"
    default_model: str = "gpt-4o"
    smart_routing: bool = True
    trust_scoring: bool = True
    hallucination_check: bool = True
    experience_learning: bool = True
    auto_optimize: bool = True
    input_protection: bool = True
    output_monitoring: bool = True
    cost_tracking: bool = True
    persist_path: str = "./sentinel_proxy_state"
    dashboard_enabled: bool = True
    savings_split: float = 0.2

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        config = cls()

        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            config.providers["openai"] = ProviderConfig(
                name="openai",
                api_key=openai_key,
                base_url="https://api.openai.com/v1",
                models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                cost_per_1k_input={"gpt-4o": 0.005, "gpt-4o-mini": 0.00015, "gpt-4-turbo": 0.01, "gpt-3.5-turbo": 0.0005},
                cost_per_1k_output={"gpt-4o": 0.015, "gpt-4o-mini": 0.0006, "gpt-4-turbo": 0.03, "gpt-3.5-turbo": 0.0015},
                quality_score={"gpt-4o": 0.95, "gpt-4o-mini": 0.75, "gpt-4-turbo": 0.92, "gpt-3.5-turbo": 0.65},
                speed_ms={"gpt-4o": 800, "gpt-4o-mini": 300, "gpt-4-turbo": 1200, "gpt-3.5-turbo": 200},
            )

        anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            config.providers["anthropic"] = ProviderConfig(
                name="anthropic",
                api_key=anthropic_key,
                base_url="https://api.anthropic.com/v1",
                models=["claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"],
                cost_per_1k_input={"claude-sonnet-4-20250514": 0.003, "claude-haiku-4-5-20251001": 0.0008},
                cost_per_1k_output={"claude-sonnet-4-20250514": 0.015, "claude-haiku-4-5-20251001": 0.004},
                quality_score={"claude-sonnet-4-20250514": 0.93, "claude-haiku-4-5-20251001": 0.78},
                speed_ms={"claude-sonnet-4-20250514": 600, "claude-haiku-4-5-20251001": 250},
            )

        config.port = int(os.environ.get("SENTINEL_PORT", 8741))
        config.smart_routing = os.environ.get("SENTINEL_SMART_ROUTING", "true").lower() == "true"
        config.persist_path = os.environ.get("SENTINEL_STATE_PATH", "./sentinel_proxy_state")
        return config

    @classmethod
    def from_file(cls, path: str) -> "ProxyConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = cls()
        for key, value in data.items():
            if key == "providers" and isinstance(value, dict):
                parsed = {}
                for provider_name, provider_data in value.items():
                    parsed[provider_name] = ProviderConfig(**provider_data)
                setattr(config, "providers", parsed)
            elif hasattr(config, key):
                setattr(config, key, value)
        return config
