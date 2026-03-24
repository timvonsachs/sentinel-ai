"""Core types for Sentinel."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class HealthStatus(Enum):
    THRIVING = "thriving"  # Besser als Baseline
    HEALTHY = "healthy"  # Normal
    LEARNING = "learning"  # Baseline aufbauend
    WATCH = "watch"  # Leichte Abweichung
    WARNING = "warning"  # Deutliche Abweichung
    CRITICAL = "critical"  # Handlung noetig
    HIBERNATING = "hibernating"  # Tardigrade-Modus: sicherer Shutdown


@dataclass
class HealthReport:
    status: HealthStatus
    pain_score: float  # 0.0 (perfekt) bis 1.0 (kritisch)
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Any] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class HealingAction:
    system: str  # welches System hat geheilt
    action: str  # was wurde getan
    reason: str  # warum
    timestamp: float = 0.0
    success: Optional[bool] = None
