"""
Sentinel AI — The living layer for artificial intelligence.
"""

from .organism import Organism
from .core.types import HealthStatus, HealthReport, HealingAction
from .core.ewma import EWMABaseline
from .core.event_bus import EventBus, Event
from .core.state_machine import OrganismStateMachine, OrganismState
from .core.correlation import CorrelationEngine

__version__ = "0.3.0"
__all__ = [
    "Organism",
    "HealthStatus",
    "HealthReport",
    "HealingAction",
    "EWMABaseline",
    "EventBus",
    "Event",
    "OrganismStateMachine",
    "OrganismState",
    "CorrelationEngine",
]
