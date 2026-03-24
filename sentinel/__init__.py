"""
Sentinel AI — The Immune System for Artificial Intelligence.

Your AI has a brain. We give it a body.

Usage:
    from sentinel import Organism

    body = Organism("my-agent")
    body.observe("conversion_rate", 0.34)

    print(body.status)   # "healthy"
    print(body.pain)     # 0.12
    print(body.feeling)  # "Healthy. Minor fluctuations."

Born from NOVA — a bipolar early warning system built by a founder
who needed artificial self-awareness because his own biology denied it.
"""

from .organism import Organism
from .core.types import HealthStatus, HealthReport, HealingAction
from .core.ewma import EWMABaseline

__version__ = "0.1.0"
__all__ = ["Organism", "HealthStatus", "HealthReport", "HealingAction", "EWMABaseline"]
