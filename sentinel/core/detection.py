"""
Three independent detection mechanisms from NOVA:
1. Persistence: sustained deviation over N periods
2. Trend: monotonic directional change
3. Velocity: sudden jumps
"""

from typing import List, Optional
from dataclasses import dataclass
from .ewma import Observation


@dataclass
class Alert:
    type: str  # "persistence", "trend", "velocity"
    severity: str  # "watch", "warning", "critical"
    metric: str
    message: str
    z_score: float
    duration: Optional[int] = None


class DetectionEngine:
    """Detects anomalies using three mechanisms."""

    def __init__(
        self,
        persistence_days: int = 3,
        trend_days: int = 5,
        watch_threshold: float = 1.5,
        warning_threshold: float = 2.0,
        velocity_threshold: float = 2.5,
    ):
        self.persistence_days = persistence_days
        self.trend_days = trend_days
        self.watch_threshold = watch_threshold
        self.warning_threshold = warning_threshold
        self.velocity_threshold = velocity_threshold

    def check(self, metric: str, history: List[Observation]) -> List[Alert]:
        alerts = []
        alerts.extend(self._check_persistence(metric, history))
        alerts.extend(self._check_trend(metric, history))
        alerts.extend(self._check_velocity(metric, history))
        return alerts

    def _check_persistence(self, metric: str, history: List[Observation]) -> List[Alert]:
        if len(history) < self.persistence_days:
            return []
        recent = history[-self.persistence_days :]
        zs = [h.z_score for h in recent]

        if all(z > self.warning_threshold for z in zs):
            return [
                Alert(
                    "persistence",
                    "critical",
                    metric,
                    f"{metric} critically elevated for {self.persistence_days} periods",
                    zs[-1],
                    self.persistence_days,
                )
            ]
        if all(z < -self.warning_threshold for z in zs):
            return [
                Alert(
                    "persistence",
                    "critical",
                    metric,
                    f"{metric} critically low for {self.persistence_days} periods",
                    zs[-1],
                    self.persistence_days,
                )
            ]
        if all(z > self.watch_threshold for z in zs):
            return [
                Alert(
                    "persistence",
                    "warning",
                    metric,
                    f"{metric} elevated for {self.persistence_days} periods",
                    zs[-1],
                    self.persistence_days,
                )
            ]
        if all(z < -self.watch_threshold for z in zs):
            return [
                Alert(
                    "persistence",
                    "warning",
                    metric,
                    f"{metric} low for {self.persistence_days} periods",
                    zs[-1],
                    self.persistence_days,
                )
            ]
        return []

    def _check_trend(self, metric: str, history: List[Observation]) -> List[Alert]:
        if len(history) < self.trend_days:
            return []
        recent = [h.z_score for h in history[-self.trend_days :]]

        rising = all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1))
        falling = all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1))

        if rising and recent[-1] > self.watch_threshold:
            return [
                Alert(
                    "trend",
                    "warning",
                    metric,
                    f"{metric} rising monotonically for {self.trend_days} periods",
                    recent[-1],
                    self.trend_days,
                )
            ]
        if falling and recent[-1] < -self.watch_threshold:
            return [
                Alert(
                    "trend",
                    "warning",
                    metric,
                    f"{metric} falling monotonically for {self.trend_days} periods",
                    recent[-1],
                    self.trend_days,
                )
            ]
        return []

    def _check_velocity(self, metric: str, history: List[Observation]) -> List[Alert]:
        if len(history) < 2:
            return []
        delta = abs(history[-1].z_score - history[-2].z_score)
        if delta > self.velocity_threshold:
            return [
                Alert(
                    "velocity",
                    "critical",
                    metric,
                    f"{metric} sudden jump: {delta:.1f} Z-score change",
                    history[-1].z_score,
                )
            ]
        return []
