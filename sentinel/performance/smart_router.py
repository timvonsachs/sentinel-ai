"""
Smart Router — route each query to the best cost/quality model.
"""

from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class ModelConfig:
    name: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    quality_score: float
    speed_ms: float
    max_tokens: int = 4096
    supports_tools: bool = True
    supports_vision: bool = False


@dataclass
class RoutingDecision:
    selected_model: str
    reason: str
    estimated_cost: float
    alternative_model: Optional[str] = None
    alternative_cost: Optional[float] = None
    savings_vs_default: float = 0.0
    complexity_score: float = 0.0


@dataclass
class CostReport:
    total_queries: int = 0
    total_cost: float = 0.0
    total_cost_without_routing: float = 0.0
    total_savings: float = 0.0
    queries_by_model: Dict[str, int] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)


class SmartRouter:
    """Intelligent model routing for cost optimization."""

    def __init__(self, default_model: str = None):
        self.models: Dict[str, ModelConfig] = {}
        self.default_model: Optional[str] = default_model
        self.cost_tracker = CostReport()
        self.complexity_rules: List[Dict] = []
        self.custom_router: Optional[Callable] = None
        self._setup_default_complexity_rules()

    def add_model(self, config: ModelConfig):
        self.models[config.name] = config

    def set_default(self, model_name: str):
        self.default_model = model_name

    def _setup_default_complexity_rules(self):
        self.complexity_rules = [
            {"pattern": r"^(what|when|where|who|how much|how many)\b.{0,50}\?$", "complexity": 0.1, "reason": "simple_factual_question"},
            {"pattern": r"^(yes|no|true|false|ok|thanks|hello|hi|hey)\b", "complexity": 0.05, "reason": "trivial_input"},
            {"pattern": r"^.{0,30}$", "complexity": 0.1, "reason": "very_short_query"},
            {"pattern": r"(explain|describe|compare|list|summarize)\b", "complexity": 0.5, "reason": "explanation_needed"},
            {"pattern": r"(help me|can you|could you|please)\b.{50,}", "complexity": 0.5, "reason": "moderate_request"},
            {"pattern": r"(analyze|evaluate|review|assess|critique)\b", "complexity": 0.8, "reason": "analysis_required"},
            {"pattern": r"(code|program|implement|build|create|write).{100,}", "complexity": 0.85, "reason": "complex_generation"},
            {"pattern": r".{500,}", "complexity": 0.7, "reason": "long_input"},
            {"pattern": r"(legal|medical|financial|contract|diagnos)", "complexity": 0.9, "reason": "high_risk_domain"},
        ]

    def add_complexity_rule(self, pattern: str, complexity: float, reason: str = ""):
        self.complexity_rules.append({"pattern": pattern, "complexity": complexity, "reason": reason})

    def estimate_complexity(self, query: str) -> Tuple[float, str]:
        max_complexity = 0.3
        reason = "default"
        for rule in self.complexity_rules:
            if re.search(rule["pattern"], query, re.IGNORECASE):
                if rule["complexity"] > max_complexity:
                    max_complexity = rule["complexity"]
                    reason = rule.get("reason", "rule_match")
        return max_complexity, reason

    def route(
        self,
        query: str,
        required_quality: float = None,
        max_cost: float = None,
        prefer_speed: bool = False,
        organism_pain: float = 0.0,
    ) -> RoutingDecision:
        if not self.models:
            return RoutingDecision("unknown", "no models configured", 0.0)

        if self.custom_router:
            try:
                result = self.custom_router(query, self.models)
                if result:
                    return result
            except Exception:
                pass

        complexity, complexity_reason = self.estimate_complexity(query)
        if organism_pain > 0.5:
            complexity *= 0.7

        if required_quality is None:
            required_quality = 0.5 + (complexity * 0.45)

        scored = []
        for name, model in self.models.items():
            if model.quality_score < required_quality:
                continue

            est_input_tokens = int(50 + complexity * 450)
            est_output_tokens = int(100 + complexity * 900)
            est_cost = (est_input_tokens / 1000) * model.cost_per_1k_input + (est_output_tokens / 1000) * model.cost_per_1k_output
            if max_cost is not None and est_cost > max_cost:
                continue

            quality_surplus = model.quality_score - required_quality
            cost_score = 1.0 / (est_cost + 0.0001)
            speed_score = 1.0 / (model.speed_ms + 1)
            if prefer_speed:
                total_score = quality_surplus * 0.2 + cost_score * 0.3 + speed_score * 0.5
            else:
                total_score = quality_surplus * 0.3 + cost_score * 0.6 + speed_score * 0.1
            scored.append((name, total_score, est_cost))

        if not scored:
            best = max(self.models.values(), key=lambda m: m.quality_score)
            return RoutingDecision(best.name, "fallback_to_best", 0.0, complexity_score=complexity)

        scored.sort(key=lambda x: x[1], reverse=True)
        selected = scored[0]
        alternative = scored[1] if len(scored) > 1 else None

        savings = 0.0
        if self.default_model and self.default_model in self.models:
            default = self.models[self.default_model]
            est_input = int(50 + complexity * 450)
            est_output = int(100 + complexity * 900)
            default_cost = (est_input / 1000) * default.cost_per_1k_input + (est_output / 1000) * default.cost_per_1k_output
            savings = default_cost - selected[2]

        return RoutingDecision(
            selected_model=selected[0],
            reason=f"complexity={complexity:.2f} ({complexity_reason}), quality_needed={required_quality:.2f}",
            estimated_cost=round(selected[2], 6),
            alternative_model=alternative[0] if alternative else None,
            alternative_cost=round(alternative[2], 6) if alternative else None,
            savings_vs_default=round(max(0, savings), 6),
            complexity_score=complexity,
        )

    def record_usage(self, model: str, input_tokens: int, output_tokens: int):
        if model not in self.models:
            return
        config = self.models[model]
        cost = (input_tokens / 1000) * config.cost_per_1k_input + (output_tokens / 1000) * config.cost_per_1k_output
        self.cost_tracker.total_queries += 1
        self.cost_tracker.total_cost += cost
        self.cost_tracker.queries_by_model[model] = self.cost_tracker.queries_by_model.get(model, 0) + 1
        self.cost_tracker.cost_by_model[model] = self.cost_tracker.cost_by_model.get(model, 0) + cost

        if self.default_model and self.default_model in self.models:
            default = self.models[self.default_model]
            default_cost = (input_tokens / 1000) * default.cost_per_1k_input + (output_tokens / 1000) * default.cost_per_1k_output
            self.cost_tracker.total_cost_without_routing += default_cost
            self.cost_tracker.total_savings = self.cost_tracker.total_cost_without_routing - self.cost_tracker.total_cost

    def cost_report(self) -> Dict:
        ct = self.cost_tracker
        savings_pct = (ct.total_savings / ct.total_cost_without_routing * 100) if ct.total_cost_without_routing > 0 else 0
        return {
            "total_queries": ct.total_queries,
            "total_cost": round(ct.total_cost, 4),
            "cost_without_routing": round(ct.total_cost_without_routing, 4),
            "total_savings": round(ct.total_savings, 4),
            "savings_percentage": round(savings_pct, 1),
            "queries_by_model": dict(ct.queries_by_model),
            "cost_by_model": {k: round(v, 4) for k, v in ct.cost_by_model.items()},
            "avg_cost_per_query": round(ct.total_cost / max(1, ct.total_queries), 6),
        }
