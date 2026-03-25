"""
Cross-Metric Correlation — patterns between metrics.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import math
import time


@dataclass
class CorrelationResult:
    metric_a: str
    metric_b: str
    correlation: float
    strength: str
    direction: str
    sample_size: int


@dataclass
class Syndrome:
    name: str
    conditions: Dict[str, str]
    description: str
    recommended_action: Optional[str] = None


@dataclass
class SyndromeMatch:
    syndrome: Syndrome
    match_score: float
    matching_metrics: List[str]
    timestamp: float = field(default_factory=time.time)


class CorrelationEngine:
    """Cross-metric correlation and syndrome detection."""

    def __init__(self, min_samples: int = 10):
        self.metric_data: Dict[str, List[float]] = {}
        self.syndromes: List[Syndrome] = []
        self.min_samples = min_samples
        self.diagnosis_log: List[SyndromeMatch] = []
        self._setup_default_syndromes()

    def _setup_default_syndromes(self):
        self.syndromes = [
            Syndrome(
                name="model_update_drift",
                conditions={"output_quality": "falling", "latency": "rising", "response_length": "rising"},
                description="Model provider likely updated weights.",
                recommended_action="evaluate_model_version",
            ),
            Syndrome(
                name="prompt_rot",
                conditions={"satisfaction": "falling", "response_length": "rising", "output_diversity": "falling"},
                description="System prompt effectiveness degrading over time.",
                recommended_action="refresh_system_prompt",
            ),
        ]

    def update(self, metric: str, z_scores: List[float]):
        self.metric_data[metric] = z_scores

    def update_single(self, metric: str, z_score: float):
        if metric not in self.metric_data:
            self.metric_data[metric] = []
        self.metric_data[metric].append(z_score)
        if len(self.metric_data[metric]) > 200:
            self.metric_data[metric] = self.metric_data[metric][-200:]

    def analyze(self) -> List[CorrelationResult]:
        results = []
        metrics = list(self.metric_data.keys())
        for i in range(len(metrics)):
            for j in range(i + 1, len(metrics)):
                corr = self._pearson(self.metric_data[metrics[i]], self.metric_data[metrics[j]])
                if corr is not None:
                    r, n = corr
                    strength = "strong" if abs(r) > 0.7 else "moderate" if abs(r) > 0.4 else "weak" if abs(r) > 0.2 else "none"
                    direction = "positive" if r > 0.2 else "negative" if r < -0.2 else "none"
                    results.append(
                        CorrelationResult(
                            metric_a=metrics[i],
                            metric_b=metrics[j],
                            correlation=round(r, 3),
                            strength=strength,
                            direction=direction,
                            sample_size=n,
                        )
                    )
        results.sort(key=lambda r: abs(r.correlation), reverse=True)
        return results

    def _pearson(self, x: List[float], y: List[float]) -> Optional[Tuple[float, int]]:
        n = min(len(x), len(y))
        if n < self.min_samples:
            return None
        x = x[-n:]
        y = y[-n:]
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        if std_x < 1e-10 or std_y < 1e-10:
            return None
        return (cov / (std_x * std_y), n)

    def define_syndrome(self, syndrome: Syndrome):
        self.syndromes.append(syndrome)

    def diagnose(self, current_z: Dict[str, float], trends: Dict[str, str]) -> List[SyndromeMatch]:
        matches = []
        for syndrome in self.syndromes:
            matching = []
            total = len(syndrome.conditions)
            for metric, expected in syndrome.conditions.items():
                actual_trend = trends.get(metric)
                actual_z = current_z.get(metric, 0)
                if actual_trend == expected:
                    matching.append(metric)
                elif expected == "rising" and actual_z > 1.0:
                    matching.append(metric)
                elif expected == "falling" and actual_z < -1.0:
                    matching.append(metric)
                elif expected == "high" and actual_z > 1.5:
                    matching.append(metric)
                elif expected == "low" and actual_z < -1.5:
                    matching.append(metric)
            if total > 0:
                score = len(matching) / total
                if score >= 0.5:
                    match = SyndromeMatch(syndrome=syndrome, match_score=score, matching_metrics=matching)
                    matches.append(match)
                    self.diagnosis_log.append(match)
        matches.sort(key=lambda m: m.match_score, reverse=True)
        return matches

    def get_trend(self, metric: str, window: int = 5) -> Optional[str]:
        data = self.metric_data.get(metric, [])
        if len(data) < window:
            return None
        recent = data[-window:]
        rising = all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1))
        falling = all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1))
        if rising:
            return "rising"
        if falling:
            return "falling"
        first_half = sum(recent[: len(recent) // 2]) / (len(recent) // 2)
        second_half = sum(recent[len(recent) // 2 :]) / (len(recent) - len(recent) // 2)
        if second_half > first_half + 0.3:
            return "rising"
        if second_half < first_half - 0.3:
            return "falling"
        return "stable"
