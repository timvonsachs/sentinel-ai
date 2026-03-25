"""
Sentinel proxy middleware pipeline.
"""

from typing import Dict, Any, Tuple
import time

from ..organism import Organism
from ..performance.smart_router import ModelConfig
from .config import ProxyConfig
from .openai_compat import ChatCompletionRequest


class SentinelMiddleware:
    """Processing pipeline for each API call."""

    def __init__(self, organism: Organism, config: ProxyConfig):
        self.organism = organism
        self.config = config
        self._setup_router(config)

    def _setup_router(self, config: ProxyConfig):
        for provider_config in config.providers.values():
            for model in provider_config.models:
                self.organism.router.add_model(
                    ModelConfig(
                        name=model,
                        cost_per_1k_input=provider_config.cost_per_1k_input.get(model, 0.01),
                        cost_per_1k_output=provider_config.cost_per_1k_output.get(model, 0.03),
                        quality_score=provider_config.quality_score.get(model, 0.8),
                        speed_ms=provider_config.speed_ms.get(model, 500),
                    )
                )
        if config.default_model:
            self.organism.router.set_default(config.default_model)

    async def process_request(self, request: ChatCompletionRequest) -> Tuple[ChatCompletionRequest, Dict[str, Any]]:
        metadata: Dict[str, Any] = {
            "original_model": request.model,
            "start_time": time.time(),
            "sentinel_actions": [],
        }

        if self.config.input_protection:
            skin_result = self.organism.skin.check(request.user_message)
            if not skin_result.safe:
                metadata["blocked"] = True
                metadata["block_reason"] = [t.type for t in skin_result.threats]
                metadata["sentinel_actions"].append("skin_blocked")
                return request, metadata

        if request.user_message:
            digested = self.organism.digestive.digest(request.user_message)
            metadata["input_quality"] = digested.quality_score

        if self.config.smart_routing:
            routing = self.organism.router.route(
                query=request.user_message,
                required_quality=request.sentinel_required_quality,
                max_cost=request.sentinel_max_cost,
                prefer_speed=request.sentinel_prefer_speed,
                organism_pain=self.organism.pain,
            )
            if routing.selected_model != request.model:
                metadata["routed_from"] = request.model
                metadata["routed_to"] = routing.selected_model
                metadata["routing_reason"] = routing.reason
                metadata["estimated_savings"] = routing.savings_vs_default
                metadata["sentinel_actions"].append(f"routed:{request.model}->{routing.selected_model}")
                request.model = routing.selected_model

        if request.temperature is None:
            creativity = self.organism.endocrine.get("creativity")
            request.temperature = round(creativity, 2)
            metadata["sentinel_temperature"] = request.temperature
            metadata["sentinel_actions"].append(f"temperature_set:{request.temperature}")

        return request, metadata

    async def process_response(self, response: dict, request: ChatCompletionRequest, metadata: dict) -> Tuple[dict, Dict[str, Any]]:
        latency = (time.time() - metadata["start_time"]) * 1000
        content = ""
        if response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")

        usage = response.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        if self.config.trust_scoring and content:
            trust_report = self.organism.trust.evaluate(
                query=request.user_message,
                response=content,
                model_confidence=None,
            )
            metadata["trust_score"] = trust_report.score
            metadata["trust_level"] = trust_report.confidence_level
            metadata["trust_recommendation"] = trust_report.recommendation
            if trust_report.score < 0.3:
                metadata["sentinel_actions"].append("low_trust_warning")

        if self.config.output_monitoring and content:
            self.organism.lymph.process_output(
                content,
                {"model": request.model, "query_length": len(request.user_message)},
            )

        self.organism.observe("latency", latency)
        self.organism.observe("output_tokens", float(output_tokens))
        self.organism.observe("input_tokens", float(input_tokens))
        if content:
            self.organism.observe("response_length", float(len(content)))

        if self.config.cost_tracking:
            self.organism.router.record_usage(request.model, input_tokens, output_tokens)
            cost_report = self.organism.router.cost_report()
            metadata["total_savings"] = cost_report.get("total_savings", 0)
            metadata["total_cost"] = cost_report.get("total_cost", 0)

        if self.config.experience_learning:
            interaction_id = self.organism.experience.record(
                input_text=request.user_message,
                output_text=content,
                category="chat",
                context={
                    "model": request.model,
                    "latency": latency,
                    "tokens": input_tokens + output_tokens,
                },
            )
            metadata["experience_id"] = interaction_id

        self.organism.signal(
            {
                "latency": latency,
                "output_tokens": output_tokens,
                "trust_score": metadata.get("trust_score", 1.0),
            }
        )

        metadata["latency_ms"] = round(latency, 1)
        metadata["model_used"] = request.model
        metadata["input_tokens"] = input_tokens
        metadata["output_tokens"] = output_tokens
        metadata["organism_pain"] = self.organism.pain
        metadata["organism_state"] = self.organism.state

        response["sentinel"] = {
            "model_used": request.model,
            "original_model": metadata.get("original_model"),
            "routed": metadata.get("routed_from") is not None,
            "trust_score": metadata.get("trust_score"),
            "trust_level": metadata.get("trust_level"),
            "latency_ms": metadata["latency_ms"],
            "savings_this_call": metadata.get("estimated_savings", 0),
            "total_savings": metadata.get("total_savings", 0),
            "organism_state": metadata["organism_state"],
            "actions": metadata["sentinel_actions"],
        }
        return response, metadata
