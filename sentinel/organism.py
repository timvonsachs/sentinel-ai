"""
The Organism — A living AI system.

Your AI has a brain. We give it a body.

Usage:
    from sentinel import Organism

    body = Organism("my-agent")
    body.immune.observe("conversion", 0.34)
    body.nervous.reflex("timeout", lambda m: m["latency"] > 3000, fallback)

    print(body.status)      # "healthy"
    print(body.pain)        # 0.12
    print(body.feeling)     # "Healthy. Minor fluctuations."

    body.autonomous = True  # Let it heal itself
"""

import json
from .systems.immune import ImmuneSystem
from .systems.nervous import NervousSystem
from .systems.endocrine import EndocrineSystem
from .systems.memory import MemorySystem
from .systems.pain import PainSense
from .core.types import HealthStatus, HealthReport


class Organism:
    """
    A living AI system with biological subsystems.

    Born from NOVA — a bipolar early warning system.
    The algorithm that monitors a human mind,
    now monitoring artificial ones.
    """

    def __init__(self, name: str = "unnamed", autonomous: bool = False):
        self.name = name
        self.autonomous = autonomous

        # Biological Systems
        self.immune = ImmuneSystem()
        self.nervous = NervousSystem()
        self.endocrine = EndocrineSystem()
        self.memory = MemorySystem()
        self.pain_sense = PainSense()

        # Default hormones
        self.endocrine.add_hormone("cortisol", base=0.3, min=0.0, max=1.0)
        self.endocrine.add_hormone("creativity", base=0.7, min=0.1, max=1.0)
        self.endocrine.add_hormone("caution", base=0.3, min=0.0, max=1.0)

        # Connect cortisol to immune system
        self.endocrine.regulate("cortisol", lambda ctx: ctx.get("pain", 0) if ctx else 0)
        self.endocrine.regulate("creativity", lambda ctx: -ctx.get("pain", 0) if ctx else 0)
        self.endocrine.regulate("caution", lambda ctx: ctx.get("pain", 0) * 0.5 if ctx else 0)

    @property
    def pain(self) -> float:
        """Current pain score: 0.0 (perfect) to 1.0 (critical)."""
        return self.pain_sense.score(self)

    @property
    def feeling(self) -> str:
        """Human-readable health description."""
        return self.pain_sense.feeling(self)

    @property
    def status(self) -> str:
        """Overall health status."""
        health = self.immune.health()
        return health.status.value

    def observe(self, metric: str, value: float):
        """Shortcut: observe a metric through the immune system."""
        obs = self.immune.observe(metric, value)

        # Update endocrine system
        p = self.pain
        self.endocrine.update({"pain": p})

        # Autonomous healing
        if self.autonomous:
            health = self.immune.health(metric)
            if health.status in (HealthStatus.WARNING, HealthStatus.CRITICAL):
                self._auto_heal(metric, health)

        return obs

    def signal(self, metrics: dict):
        """Send signals through nervous system (real-time reflexes)."""
        return self.nervous.signal(metrics)

    def _auto_heal(self, metric: str, health: HealthReport):
        """Autonomous self-healing."""
        # Check memory for similar events
        similar = self.memory.recall("drift", context={"metric": metric})
        if similar and similar[0].fix:
            # We've seen this before, apply known fix
            self.memory.remember(
                "auto_heal",
                {
                    "metric": metric,
                    "applied_fix": similar[0].fix,
                    "based_on_experience": similar[0].timestamp,
                },
            )

        # Record this event for future memory
        self.memory.remember(
            "drift",
            {
                "metric": metric,
                "z_score": health.metrics.get("z_score"),
                "status": health.status.value,
            },
        )

    def report(self) -> dict:
        """Full organism status report."""
        return {
            "name": self.name,
            "status": self.status,
            "pain": self.pain,
            "feeling": self.feeling,
            "immune": {m: self.immune.health(m).metrics for m in self.immune.baselines},
            "endocrine": self.endocrine.state(),
            "memory": {
                "total_experiences": len(self.memory.experiences),
                "last_event": self.memory.last().event if self.memory.last() else None,
            },
            "nervous": {
                "reflexes": len(self.nervous.reflexes),
                "total_triggers": sum(r.trigger_count for r in self.nervous.reflexes),
            },
        }

    def save(self, path: str = None):
        """Save organism state to disk."""
        path = path or f"{self.name}_organism.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.report(), f, indent=2, default=str)

    def __repr__(self):
        return f"Organism('{self.name}', status={self.status}, pain={self.pain:.2f})"
