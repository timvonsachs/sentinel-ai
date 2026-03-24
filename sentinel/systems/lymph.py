"""
The Lymphatic System — Internal cleanup and purification.

Filters toxins. Removes waste. Keeps the internal environment clean.
For AI: detects accumulating bias, hallucination patterns,
output convergence, and diversity collapse.
"""

from typing import List, Dict, Callable
from dataclasses import dataclass, field
from collections import Counter
import math
import time


@dataclass
class ContaminationEvent:
    type: str  # "bias", "convergence", "hallucination", "staleness"
    severity: float  # 0.0-1.0
    details: str
    timestamp: float = field(default_factory=time.time)


class LymphaticSystem:
    """
    Internal purification for AI systems.

    Usage:
        lymph = LymphaticSystem()

        # After every AI output
        lymph.process_output(output_text, metadata={"topic": "pricing"})

        # Periodic health check
        report = lymph.scan()
        # {"bias_score": 0.3, "diversity_score": 0.7, ...}
    """

    def __init__(self, window_size: int = 200):
        self.window_size = window_size
        self.output_history: List[Dict] = []
        self.contamination_log: List[ContaminationEvent] = []
        self.bias_detectors: List[Callable] = []
        self.hallucination_detectors: List[Callable] = []

    def process_output(self, output: str, metadata: Dict = None):
        """Process an AI output through the lymphatic system."""
        entry = {
            "output": output,
            "length": len(output),
            "metadata": metadata or {},
            "timestamp": time.time(),
            "tokens": output.lower().split(),
        }
        self.output_history.append(entry)

        # Keep window
        if len(self.output_history) > self.window_size:
            self.output_history = self.output_history[-self.window_size :]

    def scan(self) -> Dict:
        """Full lymphatic scan. Returns contamination report."""
        if len(self.output_history) < 10:
            return {"status": "insufficient_data", "outputs_analyzed": len(self.output_history)}

        diversity = self._check_diversity()
        convergence = self._check_convergence()
        length_drift = self._check_length_drift()
        staleness = self._check_staleness()

        # Overall contamination score
        contamination = (1 - diversity) * 0.3 + convergence * 0.3 + length_drift * 0.2 + staleness * 0.2

        return {
            "contamination_score": round(contamination, 3),
            "diversity_score": round(diversity, 3),
            "convergence_score": round(convergence, 3),
            "length_drift_score": round(length_drift, 3),
            "staleness_score": round(staleness, 3),
            "outputs_analyzed": len(self.output_history),
            "events": len(self.contamination_log),
        }

    def _check_diversity(self) -> float:
        """Shannon entropy of output vocabulary. High = diverse = healthy."""
        if not self.output_history:
            return 1.0

        all_tokens = []
        for entry in self.output_history[-50:]:
            all_tokens.extend(entry["tokens"][:100])  # cap per output

        if not all_tokens:
            return 1.0

        counter = Counter(all_tokens)
        total = sum(counter.values())
        entropy = -sum((c / total) * math.log2(c / total) for c in counter.values() if c > 0)

        # Normalize: max entropy for this vocabulary size
        max_entropy = math.log2(len(counter)) if len(counter) > 1 else 1
        normalized = entropy / max_entropy if max_entropy > 0 else 1.0

        if normalized < 0.5:
            self.contamination_log.append(
                ContaminationEvent("convergence", 1 - normalized, f"Output vocabulary diversity dropping: {normalized:.2f}")
            )

        return normalized

    def _check_convergence(self) -> float:
        """Are outputs becoming more similar to each other? High = converging = bad."""
        if len(self.output_history) < 20:
            return 0.0

        recent = self.output_history[-20:]
        older = self.output_history[-40:-20] if len(self.output_history) >= 40 else self.output_history[:20]

        def avg_similarity(entries):
            if len(entries) < 2:
                return 0
            sims = []
            for i in range(len(entries)):
                for j in range(i + 1, min(i + 5, len(entries))):
                    set_a = set(entries[i]["tokens"][:50])
                    set_b = set(entries[j]["tokens"][:50])
                    if set_a | set_b:
                        sim = len(set_a & set_b) / len(set_a | set_b)
                        sims.append(sim)
            return sum(sims) / len(sims) if sims else 0

        recent_sim = avg_similarity(recent)
        older_sim = avg_similarity(older)

        # Convergence = recent similarity increasing vs older
        if older_sim > 0:
            convergence = max(0, (recent_sim - older_sim) / older_sim)
        else:
            convergence = recent_sim

        return min(1.0, convergence)

    def _check_length_drift(self) -> float:
        """Are outputs getting systematically longer or shorter?"""
        if len(self.output_history) < 20:
            return 0.0

        recent_lengths = [e["length"] for e in self.output_history[-10:]]
        older_lengths = [e["length"] for e in self.output_history[-20:-10]]

        recent_avg = sum(recent_lengths) / len(recent_lengths)
        older_avg = sum(older_lengths) / len(older_lengths)

        if older_avg > 0:
            drift = abs(recent_avg - older_avg) / older_avg
        else:
            drift = 0

        return min(1.0, drift)

    def _check_staleness(self) -> float:
        """Are the same phrases being repeated? Template detection."""
        if len(self.output_history) < 10:
            return 0.0

        # Check for repeated opening phrases
        openings = [" ".join(e["tokens"][:5]) for e in self.output_history[-20:] if len(e["tokens"]) >= 5]
        if not openings:
            return 0.0

        counter = Counter(openings)
        most_common_count = counter.most_common(1)[0][1]
        staleness = most_common_count / len(openings)

        if staleness > 0.3:
            self.contamination_log.append(
                ContaminationEvent(
                    "staleness",
                    staleness,
                    f"Repeated opening pattern detected: {counter.most_common(1)[0][0]}",
                )
            )

        return staleness

    def add_bias_detector(self, detector: Callable):
        """Add custom bias detection function."""
        self.bias_detectors.append(detector)

    def cleanse(self) -> Dict:
        """Active cleansing recommendations."""
        scan = self.scan()
        recommendations = []

        if scan.get("diversity_score", 1) < 0.5:
            recommendations.append(
                "INCREASE_TEMPERATURE: Output diversity is low. Consider raising temperature or adding diversity prompts."
            )
        if scan.get("convergence_score", 0) > 0.3:
            recommendations.append(
                "VARY_PROMPTS: Outputs are converging. Introduce variation in system prompts or examples."
            )
        if scan.get("staleness_score", 0) > 0.3:
            recommendations.append("REFRESH_TEMPLATES: Repetitive patterns detected. Rotate response templates.")
        if scan.get("length_drift_score", 0) > 0.3:
            recommendations.append("CHECK_LENGTH: Output length is drifting. Review length constraints.")

        return {
            "scan": scan,
            "recommendations": recommendations,
            "action_needed": len(recommendations) > 0,
        }
