"""
Chameleon Adaptation — Real-time context adaptation.

A chameleon doesn't think about changing color. It HAPPENS.
Milliseconds. Automatic. Based on environment.
"""

from typing import Dict, Callable, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class ContextProfile:
    """A recognized context pattern."""

    name: str
    detector: Callable  # func(signals) -> float (0-1 match score)
    adaptations: Dict[str, Any]  # parameter adjustments
    priority: int = 0


class ChameleonAdaptation:
    """
    Real-time context-based behavior adaptation.
    """

    def __init__(self):
        self.contexts: List[ContextProfile] = []
        self.current_context: Optional[str] = None
        self.default_params: Dict[str, Any] = {}
        self.adaptation_log: List[Dict] = []

    def set_defaults(self, **params):
        """Set default parameters (no context detected)."""
        self.default_params = params

    def context(self, name: str, detector: Callable, adaptations: Dict[str, Any], priority: int = 0):
        """Register a context with its adaptations."""
        self.contexts.append(ContextProfile(name=name, detector=detector, adaptations=adaptations, priority=priority))
        # Sort by priority
        self.contexts.sort(key=lambda c: c.priority, reverse=True)

    def adapt(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Given current signals, adapt parameters.
        Returns the merged parameter set.
        """
        params = dict(self.default_params)
        best_match = None
        best_score = 0

        for ctx in self.contexts:
            try:
                score = ctx.detector(signals)
                if score > best_score and score > 0.5:
                    best_score = score
                    best_match = ctx
            except Exception:
                pass

        if best_match:
            params.update(best_match.adaptations)
            self.current_context = best_match.name
            self.adaptation_log.append(
                {
                    "context": best_match.name,
                    "score": best_score,
                    "adaptations": best_match.adaptations,
                    "timestamp": time.time(),
                }
            )
        else:
            self.current_context = None

        return params

    def current(self) -> Optional[str]:
        """What context are we currently adapted to?"""
        return self.current_context
