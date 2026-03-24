"""
EWMA Baseline Engine — Born in a psychiatric clinic.
Ported from NOVA (bipolar early warning system) to be domain-agnostic.

The algorithm is simple. The insight is profound:
Self-awareness is not about knowing your current state.
It's about knowing your current state RELATIVE TO YOUR OWN BASELINE.
"""

import math
import time
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Observation:
    value: float
    z_score: float
    baseline: float
    variance: float
    timestamp: float
    count: int


class EWMABaseline:
    """
    Exponentially Weighted Moving Average Baseline.

    Lambda = 0.1 means the last ~10 observations dominate.
    Z-score is calculated BEFORE the baseline update.
    This is critical: the observation must not relativize itself.

    Phases:
        Learning (1-6):    Baseline building. Z-scores damped.
        Refining (7-20):   EWMA active. Confidence growing.
        Calibrated (21+):  Full confidence. Z-scores at full strength.
    """

    def __init__(self, lambda_: float = 0.1, epsilon: float = 0.0001, z_clip: float = 3.0):
        self.lambda_ = lambda_
        self.epsilon = epsilon
        self.z_clip = z_clip
        self.mean: Optional[float] = None
        self.variance: float = epsilon
        self.count: int = 0
        self.history: List[Observation] = []

    def observe(self, value: float) -> Observation:
        """Observe a new value. Returns observation with z-score."""
        self.count += 1
        ts = time.time()

        if self.mean is None:
            self.mean = value
            self.variance = self.epsilon
            obs = Observation(
                value=value,
                z_score=0.0,
                baseline=value,
                variance=self.variance,
                timestamp=ts,
                count=self.count,
            )
            self.history.append(obs)
            return obs

        # Z-score BEFORE update (NOVA's critical insight)
        std = max(math.sqrt(self.variance), self.epsilon)
        z = (value - self.mean) / std
        z = max(-self.z_clip, min(self.z_clip, z))

        # EWMA update
        old_mean = self.mean
        self.mean = self.lambda_ * value + (1 - self.lambda_) * self.mean
        self.variance = self.lambda_ * (value - old_mean) ** 2 + (1 - self.lambda_) * self.variance

        # Damping based on confidence
        damped_z = z * self._damping_factor()

        obs = Observation(
            value=value,
            z_score=damped_z,
            baseline=self.mean,
            variance=self.variance,
            timestamp=ts,
            count=self.count,
        )
        self.history.append(obs)
        return obs

    def _damping_factor(self) -> float:
        """NOVA's damping: 0% days 1-6, 60-100% days 7-20, 100% day 21+."""
        if self.count < 7:
            return 0.0
        if self.count >= 21:
            return 1.0
        return 0.6 + ((self.count - 7) / 14.0) * 0.4

    @property
    def phase(self) -> str:
        if self.count < 7:
            return "learning"
        if self.count < 21:
            return "refining"
        return "calibrated"

    @property
    def confidence(self) -> float:
        if self.count < 7:
            return (self.count / 7.0) * 50.0
        if self.count >= 21:
            return 100.0
        return 60.0 + ((self.count - 7) / 14.0) * 40.0

    def to_dict(self) -> dict:
        return {
            "mean": self.mean,
            "variance": self.variance,
            "count": self.count,
            "phase": self.phase,
            "confidence": self.confidence,
        }
