"""
Octopus Intelligence — Distributed awareness.

An octopus has 9 brains. Each arm thinks independently.
They coordinate but don't depend on central command.
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
import time


@dataclass
class Tentacle:
    """An independent awareness node."""

    name: str
    health_checker: Callable  # returns 0-1 health score
    auto_action: Optional[Callable] = None  # autonomous reaction
    last_health: float = 1.0
    last_check: float = 0.0
    check_count: int = 0


class OctopusIntelligence:
    """
    Distributed intelligence across AI components.
    """

    def __init__(self):
        self.tentacles: Dict[str, Tentacle] = {}
        self.autonomous: bool = False
        self.coordination_log: List[Dict] = []

    def tentacle(self, name: str, health_checker: Callable, auto_action: Callable = None):
        """Register a component as a tentacle."""
        self.tentacles[name] = Tentacle(name=name, health_checker=health_checker, auto_action=auto_action)

    def check(self, name: str) -> float:
        """Check health of a specific tentacle."""
        if name not in self.tentacles:
            return 1.0

        tentacle = self.tentacles[name]
        try:
            health = tentacle.health_checker()
            tentacle.last_health = health
            tentacle.last_check = time.time()
            tentacle.check_count += 1

            # Autonomous reaction
            if self.autonomous and health < 0.3 and tentacle.auto_action:
                tentacle.auto_action()
                self.coordination_log.append(
                    {
                        "tentacle": name,
                        "action": "auto_heal",
                        "health": health,
                        "timestamp": time.time(),
                    }
                )

            return health
        except Exception:
            return 0.0

    def check_all(self) -> Dict[str, float]:
        """Check all tentacles. Returns health map."""
        results = {}
        for name in self.tentacles:
            results[name] = self.check(name)

        if results:
            results["overall"] = sum(results.values()) / len(results)

        return results

    def weakest(self) -> Optional[str]:
        """Which tentacle is weakest?"""
        health = self.check_all()
        health.pop("overall", None)
        if not health:
            return None
        return min(health, key=health.get)
