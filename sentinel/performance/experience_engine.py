"""
Experience Engine — learn from each interaction without retraining.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class Interaction:
    id: str
    input_text: str
    output_text: str
    category: str = "general"
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: Optional[float] = None
    patterns: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Insight:
    pattern: str
    action: str
    evidence_count: int
    success_rate: float
    confidence: float
    discovered_at: float = field(default_factory=time.time)
    last_used: float = 0.0
    times_applied: int = 0


class ExperienceEngine:
    """Learns practical patterns from production interactions."""

    def __init__(self, max_interactions: int = 50000):
        self.interactions: List[Interaction] = []
        self.insights: List[Insight] = []
        self.max_interactions = max_interactions
        self.pattern_extractors: List[Callable] = []
        self._outcome_pending: Dict[str, Interaction] = {}
        self._setup_default_extractors()

    def _setup_default_extractors(self):
        def extract_length_pattern(interaction: Interaction) -> List[str]:
            patterns = []
            input_len = len(interaction.input_text.split())
            output_len = len(interaction.output_text.split())
            if input_len < 10:
                patterns.append("short_input")
            elif input_len > 100:
                patterns.append("long_input")
            if output_len < 50:
                patterns.append("short_response")
            elif output_len > 300:
                patterns.append("long_response")
            patterns.append(f"response_ratio_{output_len // max(1, input_len)}")
            return patterns

        def extract_keyword_patterns(interaction: Interaction) -> List[str]:
            patterns = []
            text = interaction.input_text.lower()
            keywords = {
                "price": "mentions_price",
                "expensive": "mentions_expensive",
                "cheap": "mentions_cheap",
                "urgent": "mentions_urgency",
                "help": "asks_for_help",
                "problem": "has_problem",
                "love": "positive_sentiment",
                "hate": "negative_sentiment",
                "competitor": "mentions_competitor",
                "cancel": "mentions_cancel",
                "refund": "mentions_refund",
            }
            for word, pattern in keywords.items():
                if word in text:
                    patterns.append(pattern)
            return patterns

        self.pattern_extractors = [extract_length_pattern, extract_keyword_patterns]

    def add_pattern_extractor(self, func: Callable):
        self.pattern_extractors.append(func)

    def record(self, input_text: str, output_text: str, category: str = "general", context: Dict = None) -> str:
        interaction_id = hashlib.sha256(f"{time.time()}:{input_text[:50]}".encode()).hexdigest()[:12]
        interaction = Interaction(
            id=interaction_id,
            input_text=input_text,
            output_text=output_text,
            category=category,
            context=context or {},
        )
        for extractor in self.pattern_extractors:
            try:
                interaction.patterns.extend(extractor(interaction))
            except Exception:
                pass
        self._outcome_pending[interaction_id] = interaction

        if len(self.interactions) > self.max_interactions:
            self.interactions = self.interactions[-self.max_interactions :]
        return interaction_id

    def record_outcome(self, interaction_id: str, outcome: float):
        if interaction_id in self._outcome_pending:
            interaction = self._outcome_pending.pop(interaction_id)
            interaction.outcome = outcome
            self.interactions.append(interaction)
            self._update_insights(interaction)

    def _update_insights(self, interaction: Interaction):
        if interaction.outcome is None:
            return
        for pattern in interaction.patterns:
            existing = None
            for insight in self.insights:
                if insight.pattern == f"{interaction.category}:{pattern}":
                    existing = insight
                    break
            if existing:
                n = existing.evidence_count + 1
                existing.success_rate = (existing.success_rate * (n - 1) + interaction.outcome) / n
                existing.evidence_count = n
                existing.confidence = min(1.0, n / 20)
            else:
                self.insights.append(
                    Insight(
                        pattern=f"{interaction.category}:{pattern}",
                        action=f"Pattern '{pattern}' observed in {interaction.category}",
                        evidence_count=1,
                        success_rate=interaction.outcome,
                        confidence=0.05,
                    )
                )

    def get_insights(self, category: str = None, min_confidence: float = 0.3, min_evidence: int = 5) -> List[Insight]:
        results = self.insights
        if category:
            results = [i for i in results if i.pattern.startswith(f"{category}:")]
        results = [i for i in results if i.confidence >= min_confidence and i.evidence_count >= min_evidence]
        results.sort(key=lambda i: i.confidence * abs(i.success_rate - 0.5), reverse=True)
        return results

    def recommend(self, input_text: str, category: str = "general", context: Dict = None) -> List[str]:
        temp = Interaction(id="temp", input_text=input_text, output_text="", category=category, context=context or {})
        patterns = []
        for extractor in self.pattern_extractors:
            try:
                patterns.extend(extractor(temp))
            except Exception:
                pass

        recommendations = []
        for pattern in patterns:
            key = f"{category}:{pattern}"
            matching = [i for i in self.insights if i.pattern == key and i.confidence >= 0.3]
            for insight in matching:
                if insight.success_rate >= 0.7:
                    recommendations.append(
                        f"POSITIVE: '{pattern}' => {insight.success_rate*100:.0f}% success ({insight.evidence_count} samples)"
                    )
                elif insight.success_rate <= 0.3:
                    recommendations.append(
                        f"WARNING: '{pattern}' => poor outcomes ({insight.success_rate*100:.0f}% success)"
                    )
        return recommendations

    def performance_over_time(self, category: str = None, window: int = 50) -> List[Dict]:
        interactions = self.interactions
        if category:
            interactions = [i for i in interactions if i.category == category]
        interactions = [i for i in interactions if i.outcome is not None]
        if len(interactions) < window:
            return []

        result = []
        for i in range(window, len(interactions) + 1, max(1, window // 5)):
            window_data = interactions[i - window : i]
            avg_outcome = sum(x.outcome for x in window_data) / len(window_data)
            result.append(
                {
                    "period_end": i,
                    "avg_outcome": round(avg_outcome, 3),
                    "sample_size": len(window_data),
                    "timestamp": window_data[-1].timestamp,
                }
            )
        return result

    def report(self) -> Dict:
        outcomes = [i.outcome for i in self.interactions if i.outcome is not None]
        return {
            "total_interactions": len(self.interactions),
            "outcomes_recorded": len(outcomes),
            "pending_outcomes": len(self._outcome_pending),
            "avg_outcome": round(sum(outcomes) / len(outcomes), 3) if outcomes else None,
            "total_insights": len(self.insights),
            "actionable_insights": len(self.get_insights()),
            "categories": list(set(i.pattern.split(":")[0] for i in self.insights)),
        }
