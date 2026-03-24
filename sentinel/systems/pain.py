"""
The Pain Sense — Composite intuition across ALL systems.

No biological organism has a single point of failure detection.
Instead: a FEELING. "Something is wrong."
The pain score integrates all systems into one number.
"""

from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..organism import Organism


class PainSense:
    """
    Composite health score: 0.0 (perfect) to 1.0 (critical).

    Not just one metric. ALL systems. Weighted. Integrated.
    Like how you FEEL when you're getting sick -
    before you can name what's wrong.
    """

    def __init__(self):
        self.weights = {
            "immune": 0.35,
            "nervous": 0.15,
            "endocrine": 0.15,
            "memory": 0.05,
            "lymph": 0.15,
            "skin": 0.15,
        }
        self.history: List[Dict] = []

    def score(self, organism: "Organism") -> float:
        """
        Calculate composite pain score from all active systems.
        Returns 0.0 (no pain) to 1.0 (maximum pain).
        """
        total_pain = 0.0
        total_weight = 0.0
        signals = {}

        # Immune system pain
        if organism.immune and organism.immune.baselines:
            health = organism.immune.health()
            immune_pain = health.pain_score
            signals["immune"] = immune_pain
            total_pain += immune_pain * self.weights.get("immune", 0.3)
            total_weight += self.weights.get("immune", 0.3)

        # Nervous system pain (frequency of reflex triggers)
        if organism.nervous and organism.nervous.signal_log:
            recent = [
                s
                for s in organism.nervous.signal_log
                if s["timestamp"] > (organism.nervous.signal_log[-1]["timestamp"] - 3600)
            ]
            nervous_pain = min(1.0, len(recent) / 20)  # 20 triggers/hour = max pain
            signals["nervous"] = nervous_pain
            total_pain += nervous_pain * self.weights.get("nervous", 0.15)
            total_weight += self.weights.get("nervous", 0.15)

        # Endocrine pain (hormones far from baseline)
        if organism.endocrine and organism.endocrine.hormones:
            hormone_deviations = []
            for h in organism.endocrine.hormones.values():
                deviation = abs(h.level - h.base_level) / (h.max_level - h.min_level)
                hormone_deviations.append(deviation)
            endo_pain = sum(hormone_deviations) / len(hormone_deviations) if hormone_deviations else 0
            signals["endocrine"] = endo_pain
            total_pain += endo_pain * self.weights.get("endocrine", 0.15)
            total_weight += self.weights.get("endocrine", 0.15)

        composite = total_pain / total_weight if total_weight > 0 else 0

        self.history.append(
            {
                "score": composite,
                "signals": signals,
            }
        )

        return round(composite, 4)

    def feeling(self, organism: "Organism") -> str:
        """Human-readable pain description."""
        s = self.score(organism)
        if s < 0.1:
            return "Thriving. All systems nominal."
        if s < 0.25:
            return "Healthy. Minor fluctuations."
        if s < 0.4:
            return "Uncomfortable. Something needs attention."
        if s < 0.6:
            return "In pain. Multiple systems stressed."
        if s < 0.8:
            return "Suffering. Immediate action recommended."
        return "Critical. System integrity at risk."
