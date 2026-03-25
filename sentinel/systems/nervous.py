"""
The Nervous System — Real-time reflexes for AI.

Like a human pulling their hand from a hot stove
BEFORE conscious thought kicks in.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
import time


@dataclass
class Reflex:
    name: str
    condition: Callable[..., bool]
    action: Callable
    cooldown: float = 0  # seconds between triggers
    last_triggered: float = 0
    trigger_count: int = 0


class NervousSystem:
    """
    Instant reactions to dangerous conditions.
    No baseline needed. No history needed. Just: IF danger THEN act.

    Usage:
        nervous = NervousSystem()
        nervous.reflex("high_latency",
                       condition=lambda m: m.get("latency", 0) > 3000,
                       action=switch_to_fast_model)
    """

    def __init__(self):
        self.reflexes: List[Reflex] = []
        self.signal_log: List[Dict] = []
        self.bus = None

    def reflex(self, name: str, condition: Callable, action: Callable, cooldown: float = 0):
        """Register a reflex: condition -> action."""
        self.reflexes.append(Reflex(name=name, condition=condition, action=action, cooldown=cooldown))

    def signal(self, metrics: Dict[str, Any]) -> List[str]:
        """Send signals through the nervous system. Returns triggered reflexes."""
        triggered = []
        now = time.time()

        for reflex in self.reflexes:
            if now - reflex.last_triggered < reflex.cooldown:
                continue
            try:
                if reflex.condition(metrics):
                    reflex.action(metrics)
                    reflex.last_triggered = now
                    reflex.trigger_count += 1
                    triggered.append(reflex.name)
                    self.signal_log.append({"reflex": reflex.name, "timestamp": now, "metrics": metrics})
                    if self.bus is not None:
                        from ..core.event_bus import Event

                        self.bus.emit(
                            Event(
                                type="nervous.reflex",
                                source="nervous",
                                data={"reflex": reflex.name, "metrics": metrics},
                                severity=2,
                            )
                        )
            except Exception:
                pass

        return triggered

    def attach_bus(self, bus):
        self.bus = bus
