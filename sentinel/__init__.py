"""
Sentinel AI — The complete living layer for artificial intelligence.

Your AI has a brain. We give it a body. And more.

11 Biological Systems. 5 Animal Capabilities. 4 Transcendent Abilities.
20 integrated modules that transform a naked algorithm into a living organism.
"""

from .organism import Organism
from .core.types import HealthStatus, HealthReport, HealingAction
from .core.ewma import EWMABaseline

__version__ = "0.2.0"
__all__ = ["Organism", "HealthStatus", "HealthReport", "HealingAction", "EWMABaseline"]
