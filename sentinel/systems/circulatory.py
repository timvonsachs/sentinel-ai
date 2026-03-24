"""
The Circulatory System — State flows between all components.

In a human body, blood carries oxygen, nutrients, hormones, and immune cells
to EVERY cell. Without circulation, organs are isolated. They can't coordinate.

For AI: the circulatory system ensures every component knows what every
other component knows. The immune system's alert reaches the endocrine system.
The skin's threat detection reaches the memory. The pain score reaches everything.
"""

from typing import Dict, Any, List, Callable
from dataclasses import dataclass, field
import time


@dataclass
class StatePacket:
    """A unit of state flowing through the circulatory system."""

    source: str  # which system sent this
    type: str  # "alert", "metric", "hormone", "memory", "command"
    data: Dict[str, Any]
    priority: int = 0  # 0=normal, 1=elevated, 2=urgent, 3=emergency
    timestamp: float = field(default_factory=time.time)


class CirculatorySystem:
    """
    Cross-component state flow for AI organisms.

    Usage:
        circ = CirculatorySystem()

        # Systems publish state
        circ.pump(StatePacket(source="immune", type="alert",
                              data={"metric": "conversion", "z": -2.1}))

        # Systems subscribe to state
        circ.subscribe("endocrine",
                       filter_type="alert",
                       handler=adjust_hormones)

        # Global state query
        state = circ.state()
        # Returns aggregated state from all systems
    """

    def __init__(self, max_history: int = 1000):
        self.subscribers: Dict[str, List[Dict]] = {}
        self.state_log: List[StatePacket] = []
        self.current_state: Dict[str, Any] = {}
        self.max_history = max_history

    def pump(self, packet: StatePacket):
        """Pump a state packet through the system."""
        self.state_log.append(packet)

        # Update current state
        key = f"{packet.source}.{packet.type}"
        self.current_state[key] = {
            "data": packet.data,
            "timestamp": packet.timestamp,
            "priority": packet.priority,
        }

        # Deliver to subscribers
        for sub_list in self.subscribers.values():
            for sub in sub_list:
                if sub.get("filter_type") and sub["filter_type"] != packet.type:
                    continue
                if sub.get("filter_source") and sub["filter_source"] != packet.source:
                    continue
                if sub.get("min_priority", 0) > packet.priority:
                    continue
                try:
                    sub["handler"](packet)
                except Exception:
                    pass

        # Trim history
        if len(self.state_log) > self.max_history:
            self.state_log = self.state_log[-self.max_history :]

    def subscribe(
        self,
        subscriber: str,
        handler: Callable,
        filter_type: str = None,
        filter_source: str = None,
        min_priority: int = 0,
    ):
        """Subscribe a system to state updates."""
        if subscriber not in self.subscribers:
            self.subscribers[subscriber] = []
        self.subscribers[subscriber].append(
            {
                "handler": handler,
                "filter_type": filter_type,
                "filter_source": filter_source,
                "min_priority": min_priority,
            }
        )

    def state(self) -> Dict[str, Any]:
        """Current aggregated state of the entire organism."""
        return dict(self.current_state)

    def recent(self, source: str = None, type: str = None, seconds: float = 3600) -> List[StatePacket]:
        """Get recent state packets, optionally filtered."""
        cutoff = time.time() - seconds
        results = [p for p in self.state_log if p.timestamp > cutoff]
        if source:
            results = [p for p in results if p.source == source]
        if type:
            results = [p for p in results if p.type == type]
        return results

    def pressure(self) -> float:
        """System 'blood pressure' — how much state traffic is flowing."""
        recent = self.recent(seconds=300)  # last 5 minutes
        if not recent:
            return 0.0

        urgency_sum = sum(p.priority for p in recent)
        return min(1.0, urgency_sum / (len(recent) * 3))
