"""
The Respiratory System — Compute self-regulation.

Breathing: fast during exercise, slow during rest.
For AI: use more compute when needed, less when not.
Dynamic quality-speed tradeoff. Energy conservation.
"""

from typing import Dict, List
from dataclasses import dataclass, field
import time


@dataclass
class BreathingState:
    rate: str  # "deep" (high quality), "normal", "shallow" (fast/cheap)
    compute_budget: float  # 0.0 (minimum) to 1.0 (maximum)
    reason: str
    timestamp: float = field(default_factory=time.time)


class RespiratorySystem:
    """
    Compute self-regulation for AI systems.
    """

    def __init__(self):
        self.modes: Dict[str, Dict] = {
            "deep": {"compute": 1.0, "description": "Full quality, maximum compute"},
            "normal": {"compute": 0.6, "description": "Balanced quality and speed"},
            "shallow": {"compute": 0.3, "description": "Fast response, reduced quality"},
            "emergency": {"compute": 0.1, "description": "Survival mode, minimum compute"},
        }
        self.current_mode: str = "normal"
        self.budget: float = 0.6
        self.history: List[BreathingState] = []
        self.auto_regulate: bool = True

    def mode(self, name: str, compute: float, description: str = ""):
        self.modes[name] = {"compute": compute, "description": description}

    def breathe(self, load: float = 0.5, pain: float = 0.0, urgency: float = 0.5) -> BreathingState:
        """
        Regulate breathing based on current conditions.

        load: system load 0-1
        pain: organism pain score 0-1
        urgency: how urgent is the current request 0-1
        """
        if not self.auto_regulate:
            state = BreathingState(self.current_mode, self.budget, "manual")
            self.history.append(state)
            return state

        # High pain = shallow breathing (conserve resources)
        if pain > 0.7:
            new_mode = "emergency"
            reason = "High pain score — entering survival mode"
        elif pain > 0.4:
            new_mode = "shallow"
            reason = "Elevated pain — reducing compute"
        # High load = shallow breathing
        elif load > 0.9:
            new_mode = "shallow"
            reason = "High load — conserving resources"
        # High urgency = deep breathing (need best quality)
        elif urgency > 0.8:
            new_mode = "deep"
            reason = "High urgency — maximum quality"
        else:
            new_mode = "normal"
            reason = "Normal operation"

        self.current_mode = new_mode
        self.budget = self.modes[new_mode]["compute"]

        state = BreathingState(new_mode, self.budget, reason)
        self.history.append(state)

        return state

    def force_mode(self, mode: str):
        """Manually override breathing mode."""
        if mode in self.modes:
            self.current_mode = mode
            self.budget = self.modes[mode]["compute"]

    def stats(self) -> Dict:
        if not self.history:
            return {"current_mode": self.current_mode, "budget": self.budget}

        recent = self.history[-100:]
        mode_counts = {}
        for state in recent:
            mode_counts[state.rate] = mode_counts.get(state.rate, 0) + 1

        return {
            "current_mode": self.current_mode,
            "budget": self.budget,
            "mode_distribution": mode_counts,
            "avg_budget": sum(s.compute_budget for s in recent) / len(recent),
        }
