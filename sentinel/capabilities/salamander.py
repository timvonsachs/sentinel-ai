"""
Salamander Regeneration — Rebuild what's broken.

A salamander loses a limb. It grows back. Completely functional.
Not a scar. Not a workaround. Full regeneration.
"""

from typing import Dict, Callable, Optional, List
from dataclasses import dataclass, field
import time


@dataclass
class RegenerationEvent:
    component: str
    reason: str
    method: str  # "rebuild", "reconfigure", "substitute"
    success: bool
    duration: float  # seconds
    timestamp: float = field(default_factory=time.time)


class SalamanderRegeneration:
    """
    Self-regeneration for AI components.
    """

    def __init__(self):
        self.components: Dict[str, Dict] = {}
        self.regeneration_log: List[RegenerationEvent] = []
        self.auto_regenerate: bool = True

    def register(self, name: str, health_check: Callable, regenerate: Callable, fallback: Callable = None):
        """Register a component with its regeneration blueprint."""
        self.components[name] = {
            "health_check": health_check,
            "regenerate": regenerate,
            "fallback": fallback,
            "healthy": True,
            "regenerating": False,
            "last_check": 0,
        }

    def check(self, name: str) -> bool:
        """Check a component's health. Regenerate if needed."""
        if name not in self.components:
            return True

        comp = self.components[name]
        try:
            healthy = comp["health_check"]()
            comp["healthy"] = healthy
            comp["last_check"] = time.time()

            if not healthy and self.auto_regenerate and not comp["regenerating"]:
                self._regenerate(name)

            return healthy
        except Exception:
            comp["healthy"] = False
            if self.auto_regenerate and not comp["regenerating"]:
                self._regenerate(name)
            return False

    def check_all(self) -> Dict[str, bool]:
        """Check all components."""
        return {name: self.check(name) for name in self.components}

    def _regenerate(self, name: str):
        """Attempt to regenerate a component."""
        comp = self.components[name]
        comp["regenerating"] = True
        start = time.time()

        try:
            comp["regenerate"]()
            duration = time.time() - start
            comp["healthy"] = True
            comp["regenerating"] = False
            event = RegenerationEvent(
                component=name,
                reason="Component failure detected",
                method="rebuild",
                success=True,
                duration=duration,
            )
            self.regeneration_log.append(event)
        except Exception as e:
            duration = time.time() - start
            comp["regenerating"] = False
            event = RegenerationEvent(
                component=name,
                reason=str(e),
                method="rebuild",
                success=False,
                duration=duration,
            )
            self.regeneration_log.append(event)

    def get_fallback(self, name: str) -> Optional[Callable]:
        """Get fallback function for a broken component."""
        comp = self.components.get(name)
        if comp and not comp["healthy"] and comp.get("fallback"):
            return comp["fallback"]
        return None

    def status(self) -> Dict:
        return {
            name: {"healthy": comp["healthy"], "regenerating": comp["regenerating"]}
            for name, comp in self.components.items()
        }
