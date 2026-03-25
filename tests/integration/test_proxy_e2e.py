from fastapi.testclient import TestClient

from sentinel.proxy.config import ProxyConfig, ProviderConfig
from sentinel.proxy.server import create_app
from sentinel.proxy import provider_clients


def test_proxy_e2e_pipeline(monkeypatch):
    async def fake_chat_completion(self, request_data, model=None):
        _ = request_data
        used_model = model or "gpt-4o-mini"
        return {
            "id": "fake-1",
            "object": "chat.completion",
            "created": 1,
            "model": used_model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello from fake model"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
        }

    monkeypatch.setattr(provider_clients.ProviderClient, "chat_completion", fake_chat_completion)

    cfg = ProxyConfig(
        providers={
            "openai": ProviderConfig(
                name="openai",
                api_key="test",
                base_url="https://api.openai.com/v1",
                models=["gpt-4o", "gpt-4o-mini"],
                cost_per_1k_input={"gpt-4o": 0.005, "gpt-4o-mini": 0.00015},
                cost_per_1k_output={"gpt-4o": 0.015, "gpt-4o-mini": 0.0006},
                quality_score={"gpt-4o": 0.95, "gpt-4o-mini": 0.75},
                speed_ms={"gpt-4o": 800, "gpt-4o-mini": 300},
            )
        },
        default_model="gpt-4o",
        persist_path="./sentinel_proxy_state_test",
    )

    app = create_app(cfg)
    client = TestClient(app)

    response = client.post(
        "/v1/chat/completions",
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": "What is 2+2?"}], "max_tokens": 120},
    )
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert "sentinel" in data
    assert "model_used" in data["sentinel"]

    health = client.get("/v1/sentinel/health")
    assert health.status_code == 200
    assert "state" in health.json()
