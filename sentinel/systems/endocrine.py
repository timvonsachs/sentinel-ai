"""
The Endocrine System — Slow, persistent self-regulation.

Like cortisol adjusting your behavior over hours and days.
Not reflexes. MOODS. The AI's internal climate.
"""

from typing import Dict, Callable


class Hormone:
    def __init__(
        self,
        name: str,
        base_level: float,
        min_level: float,
        max_level: float,
        adaptation_speed: float = 0.05,
    ):
        self.name = name
        self.level = base_level
        self.base_level = base_level
        self.min_level = min_level
        self.max_level = max_level
        self.speed = adaptation_speed

    def stimulate(self, amount: float):
        self.level = max(self.min_level, min(self.max_level, self.level + amount * self.speed))

    def decay(self):
        """Natural return to baseline."""
        diff = self.base_level - self.level
        self.level += diff * self.speed * 0.5

    def __repr__(self):
        return f"Hormone({self.name}={self.level:.3f})"


class EndocrineSystem:
    """
    Long-term self-regulation through 'hormones'.

    Usage:
        endocrine = EndocrineSystem()
        endocrine.add_hormone("cortisol",    # stress response
            base=0.3, min=0.1, max=1.0)
        endocrine.add_hormone("creativity",  # temperature-like
            base=0.7, min=0.2, max=1.0)

        # Connect to immune system
        endocrine.regulate("cortisol",
            stimulator=lambda health: health.pain_score)

        # AI reads its own hormones
        temp = endocrine.get("creativity")  # dynamic temperature
    """

    def __init__(self):
        self.hormones: Dict[str, Hormone] = {}
        self.regulators: Dict[str, Callable] = {}

    def add_hormone(
        self,
        name: str,
        base: float = 0.5,
        min: float = 0.0,
        max: float = 1.0,
        speed: float = 0.05,
    ):
        self.hormones[name] = Hormone(name, base, min, max, speed)

    def regulate(self, hormone: str, stimulator: Callable):
        """Connect a hormone to a stimulus function."""
        self.regulators[hormone] = stimulator

    def update(self, context: dict = None):
        """Update all hormones based on current context."""
        for name, regulator in self.regulators.items():
            if name in self.hormones:
                try:
                    stimulus = regulator(context) if context else 0
                    self.hormones[name].stimulate(stimulus)
                except Exception:
                    pass

        # Natural decay toward baseline
        for hormone in self.hormones.values():
            hormone.decay()

    def get(self, hormone: str) -> float:
        return self.hormones[hormone].level if hormone in self.hormones else 0.5

    def state(self) -> Dict[str, float]:
        return {name: h.level for name, h in self.hormones.items()}
