"""
Tardigrade Hibernation — Controlled survival shutdown.

When conditions are too harsh, the tardigrade enters cryptobiosis.
All metabolism stops. It can survive decades. Then wake up perfectly.
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
import time


@dataclass
class HibernationState:
    """Frozen state of the organism."""

    reason: str
    organism_state: Dict[str, Any]
    entered_at: float = field(default_factory=time.time)
    wake_conditions: list = field(default_factory=list)


class TardigradeHibernation:
    """
    Controlled survival shutdown for AI systems.
    """

    def __init__(self):
        self.is_hibernating: bool = False
        self.hibernate_conditions: List[Dict] = []
        self.wake_conditions: List[Dict] = []
        self.frozen_state: Optional[HibernationState] = None
        self.hibernation_history: List[HibernationState] = []
        self.fallback_response: Callable = lambda: "System is temporarily in safe mode. Please try again shortly."

    def hibernate_when(self, condition: Callable, reason: str = ""):
        """Add a condition that triggers hibernation."""
        self.hibernate_conditions.append({"condition": condition, "reason": reason})

    def wake_when(self, condition: Callable, reason: str = ""):
        """Add a condition that allows waking."""
        self.wake_conditions.append({"condition": condition, "reason": reason})

    def set_fallback(self, response_func: Callable):
        """Set what the system returns during hibernation."""
        self.fallback_response = response_func

    def should_hibernate(self, organism) -> bool:
        """Check if conditions warrant hibernation."""
        if self.is_hibernating:
            return False

        for cond in self.hibernate_conditions:
            try:
                if cond["condition"](organism):
                    return True
            except Exception:
                pass
        return False

    def enter(self, organism) -> HibernationState:
        """Enter hibernation. Freeze state. Go to safe mode."""
        state = HibernationState(
            reason="Conditions too harsh for reliable operation",
            organism_state=organism.report() if hasattr(organism, "report") else {},
            wake_conditions=[c["reason"] for c in self.wake_conditions],
        )

        self.frozen_state = state
        self.is_hibernating = True
        self.hibernation_history.append(state)

        return state

    def should_wake(self) -> bool:
        """Check if conditions allow waking."""
        if not self.is_hibernating:
            return False

        if not self.wake_conditions:
            return False

        for cond in self.wake_conditions:
            try:
                if cond["condition"]():
                    return True
            except Exception:
                pass
        return False

    def exit(self) -> Optional[Dict]:
        """Exit hibernation. Restore state."""
        if not self.is_hibernating:
            return None

        state = self.frozen_state.organism_state if self.frozen_state else {}
        self.is_hibernating = False
        self.frozen_state = None
        return state

    def respond(self) -> str:
        """Get fallback response during hibernation."""
        if self.is_hibernating:
            return self.fallback_response()
        return ""
