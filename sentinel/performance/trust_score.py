"""
Trust Score — calibrated confidence for every AI output.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class TrustRecord:
    query_hash: str
    category: str
    trust_score: float
    outcome: Optional[str] = None
    feedback_score: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrustReport:
    score: float
    confidence_level: str
    sample_size: int
    historical_accuracy: float
    recommendation: str
    factors: Dict[str, Any] = field(default_factory=dict)


class TrustScoreEngine:
    """Calibrated trust scoring based on empirical outcomes."""

    def __init__(self, min_samples_for_trust: int = 5):
        self.records: List[TrustRecord] = []
        self.category_stats: Dict[str, Dict] = {}
        self.min_samples = min_samples_for_trust
        self.categorizer: Optional[Callable] = None
        self._pending_records: Dict[str, TrustRecord] = {}

    def set_categorizer(self, func: Callable):
        self.categorizer = func

    def evaluate(
        self,
        query: str,
        response: str,
        category: str = None,
        model_confidence: float = None,
        context: Dict = None,
    ) -> TrustReport:
        if category is None and self.categorizer:
            try:
                category = self.categorizer(query)
            except Exception:
                category = "general"
        category = category or "general"
        query_hash = self._hash_query(query, category)

        cat_stats = self.category_stats.get(category, {})
        total = cat_stats.get("total", 0)
        correct = cat_stats.get("correct", 0)
        if total >= self.min_samples:
            historical_accuracy = correct / total
        else:
            historical_accuracy = (model_confidence or 0.5) * 0.7

        trust = self._calculate_trust(
            historical_accuracy=historical_accuracy,
            model_confidence=model_confidence,
            sample_size=total,
            response_length=len(response),
            category=category,
        )

        if trust >= 0.85 and total >= self.min_samples:
            level = "high"
            rec = "safe_to_use"
        elif trust >= 0.65:
            level = "medium"
            rec = "generally_reliable"
        elif trust >= 0.45:
            level = "low"
            rec = "verify"
        else:
            level = "very_low"
            rec = "do_not_use_without_review"

        self._pending_records[query_hash] = TrustRecord(
            query_hash=query_hash,
            category=category,
            trust_score=trust,
            metadata={
                "model_confidence": model_confidence,
                "response_length": len(response),
                "context": context or {},
            },
        )

        return TrustReport(
            score=round(trust, 3),
            confidence_level=level,
            sample_size=total,
            historical_accuracy=round(historical_accuracy, 3),
            recommendation=rec,
            factors={
                "category": category,
                "model_confidence": model_confidence,
                "historical_samples": total,
                "calibration_penalty": round(abs((model_confidence or 0.5) - historical_accuracy), 3)
                if total >= self.min_samples
                else None,
            },
        )

    def record_outcome(
        self,
        query_hash: str = None,
        category: str = None,
        outcome: str = "correct",
        feedback_score: float = None,
    ):
        record = None
        if query_hash and query_hash in self._pending_records:
            record = self._pending_records.pop(query_hash)

        cat = category or (record.category if record else "general")
        if cat not in self.category_stats:
            self.category_stats[cat] = {"total": 0, "correct": 0, "partial": 0, "incorrect": 0}

        self.category_stats[cat]["total"] += 1
        if outcome == "correct":
            self.category_stats[cat]["correct"] += 1
        elif outcome == "partial":
            self.category_stats[cat]["partial"] += 1
        elif outcome == "incorrect":
            self.category_stats[cat]["incorrect"] += 1

        if record:
            record.outcome = outcome
            record.feedback_score = feedback_score
            self.records.append(record)

    def _calculate_trust(
        self,
        historical_accuracy: float,
        model_confidence: Optional[float],
        sample_size: int,
        response_length: int,
        category: str,
    ) -> float:
        trust = historical_accuracy
        if model_confidence is not None:
            history_weight = min(0.9, sample_size / (self.min_samples * 4))
            model_weight = 1 - history_weight
            trust = trust * history_weight + model_confidence * model_weight

        if response_length > 2000:
            trust -= min(0.1, (response_length - 2000) / 20000)

        if category in {"medical", "legal", "financial", "safety"}:
            trust *= 0.85

        if sample_size < self.min_samples:
            trust *= 0.8
        elif sample_size > 100:
            trust *= 1.05

        return max(0.0, min(1.0, trust))

    def _hash_query(self, query: str, category: str) -> str:
        raw = f"{category}:{query[:100]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def report(self) -> Dict:
        return {
            "total_evaluations": len(self.records) + len(self._pending_records),
            "outcomes_recorded": len(self.records),
            "pending_outcomes": len(self._pending_records),
            "categories": {
                cat: {
                    "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else None,
                    "total": stats["total"],
                    "correct": stats["correct"],
                    "incorrect": stats["incorrect"],
                }
                for cat, stats in self.category_stats.items()
            },
        }

    def accuracy(self, category: str = None) -> Optional[float]:
        if category:
            stats = self.category_stats.get(category, {})
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            return correct / total if total > 0 else None

        total = sum(s.get("total", 0) for s in self.category_stats.values())
        correct = sum(s.get("correct", 0) for s in self.category_stats.values())
        return correct / total if total > 0 else None
