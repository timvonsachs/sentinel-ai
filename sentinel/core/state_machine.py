"""
Organism State Machine — lifecycle with hysteresis.
"""

from typing import Dict, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import time


class OrganismState(Enum):
    NASCENT = "nascent"
    STABLE = "stable"
    THRIVING = "thriving"
    STRESSED = "stressed"
    SICK = "sick"
    HEALING = "healing"
    RECOVERING = "recovering"
    HIBERNATING = "hibernating"
    DEAD = "dead"


@dataclass
class Transition:
    from_state: OrganismState
    to_state: OrganismState
    condition: Callable
    min_duration: int = 1
    description: str = ""


@dataclass
class StateChange:
    from_state: OrganismState
    to_state: OrganismState
    reason: str
    timestamp: float = field(default_factory=time.time)


class OrganismStateMachine:
    """Manages organism lifecycle with hysteresis."""

    def __init__(self):
        self.current = OrganismState.NASCENT
        self.entered_at = time.time()
        self.tick_count = 0
        self.condition_streak: Dict[str, int] = {}
        self.history: List[StateChange] = []
        self.transitions: List[Transition] = []
        self._setup_default_transitions()

    def _setup_default_transitions(self):
        self.add_transition(
            OrganismState.NASCENT,
            OrganismState.STABLE,
            condition=lambda ctx: ctx.get("confidence", 0) >= 80,
            min_duration=1,
            description="Baseline calibrated",
        )
        self.add_transition(
            OrganismState.STABLE,
            OrganismState.THRIVING,
            condition=lambda ctx: ctx.get("pain", 1) < 0.1 and ctx.get("confidence", 0) >= 90,
            min_duration=5,
            description="Sustained excellent performance",
        )
        self.add_transition(
            OrganismState.THRIVING,
            OrganismState.STABLE,
            condition=lambda ctx: ctx.get("pain", 0) >= 0.1,
            min_duration=2,
            description="Performance returning to baseline",
        )
        self.add_transition(
            OrganismState.STABLE,
            OrganismState.STRESSED,
            condition=lambda ctx: ctx.get("pain", 0) > 0.3,
            min_duration=3,
            description="Sustained elevated pain",
        )
        self.add_transition(
            OrganismState.THRIVING,
            OrganismState.STRESSED,
            condition=lambda ctx: ctx.get("pain", 0) > 0.3,
            min_duration=2,
            description="Performance drop from peak",
        )
        self.add_transition(
            OrganismState.STRESSED,
            OrganismState.SICK,
            condition=lambda ctx: ctx.get("pain", 0) > 0.6,
            min_duration=3,
            description="Critical deterioration",
        )
        self.add_transition(
            OrganismState.STRESSED,
            OrganismState.STABLE,
            condition=lambda ctx: ctx.get("pain", 0) < 0.2,
            min_duration=5,
            description="Natural recovery from stress",
        )
        self.add_transition(
            OrganismState.SICK,
            OrganismState.HEALING,
            condition=lambda ctx: ctx.get("healing_active", False),
            min_duration=1,
            description="Healing initiated",
        )
        self.add_transition(
            OrganismState.SICK,
            OrganismState.HIBERNATING,
            condition=lambda ctx: ctx.get("pain", 0) > 0.85,
            min_duration=2,
            description="Emergency hibernation",
        )
        self.add_transition(
            OrganismState.HEALING,
            OrganismState.RECOVERING,
            condition=lambda ctx: ctx.get("pain", 0) < 0.4,
            min_duration=3,
            description="Healing showing results",
        )
        self.add_transition(
            OrganismState.HEALING,
            OrganismState.SICK,
            condition=lambda ctx: ctx.get("pain", 0) > 0.7,
            min_duration=5,
            description="Healing unsuccessful",
        )
        self.add_transition(
            OrganismState.RECOVERING,
            OrganismState.STABLE,
            condition=lambda ctx: ctx.get("pain", 0) < 0.15,
            min_duration=5,
            description="Full recovery",
        )
        self.add_transition(
            OrganismState.RECOVERING,
            OrganismState.STRESSED,
            condition=lambda ctx: ctx.get("pain", 0) > 0.4,
            min_duration=3,
            description="Relapse during recovery",
        )
        self.add_transition(
            OrganismState.HIBERNATING,
            OrganismState.RECOVERING,
            condition=lambda ctx: ctx.get("wake_signal", False),
            min_duration=1,
            description="Waking from hibernation",
        )

    def add_transition(
        self,
        from_state: OrganismState,
        to_state: OrganismState,
        condition: Callable,
        min_duration: int = 1,
        description: str = "",
    ):
        self.transitions.append(
            Transition(
                from_state=from_state,
                to_state=to_state,
                condition=condition,
                min_duration=min_duration,
                description=description,
            )
        )

    def evaluate(self, **context) -> OrganismState:
        self.tick_count += 1
        for transition in self.transitions:
            if transition.from_state != self.current:
                continue
            key = f"{transition.from_state.value}->{transition.to_state.value}"
            try:
                if transition.condition(context):
                    self.condition_streak[key] = self.condition_streak.get(key, 0) + 1
                    if self.condition_streak[key] >= transition.min_duration:
                        self._transition(transition.to_state, transition.description)
                        self.condition_streak = {}
                        break
                else:
                    self.condition_streak[key] = 0
            except Exception:
                self.condition_streak[key] = 0
        return self.current

    def _transition(self, new_state: OrganismState, reason: str):
        self.history.append(StateChange(from_state=self.current, to_state=new_state, reason=reason))
        self.current = new_state
        self.entered_at = time.time()

    def force(self, state: OrganismState, reason: str = "manual"):
        self._transition(state, f"FORCED: {reason}")

    @property
    def duration(self) -> float:
        return time.time() - self.entered_at

    @property
    def is_healthy(self) -> bool:
        return self.current in (OrganismState.STABLE, OrganismState.THRIVING)

    @property
    def needs_attention(self) -> bool:
        return self.current in (OrganismState.STRESSED, OrganismState.SICK, OrganismState.HEALING)

    def to_dict(self) -> Dict:
        return {
            "state": self.current.value,
            "duration_seconds": self.duration,
            "tick_count": self.tick_count,
            "is_healthy": self.is_healthy,
            "history_length": len(self.history),
            "last_transition": (
                {
                    "from": self.history[-1].from_state.value,
                    "to": self.history[-1].to_state.value,
                    "reason": self.history[-1].reason,
                }
                if self.history
                else None
            ),
        }
