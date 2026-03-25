"""
EWMA Baseline Engine — Born in a psychiatric clinic.
Ported from NOVA (bipolar early warning system) to be domain-agnostic.

The algorithm is simple. The insight is profound:
Self-awareness is not about knowing your current state.
It's about knowing your current state RELATIVE TO YOUR OWN BASELINE.
"""

import math
import time
from typing import Optional, Dict, List
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

    def critical_slowing_down(self, window: int = 10) -> Optional[Dict]:
        """
        Detect critical slowing down as phase-transition early warning.
        """
        if len(self.history) < window * 2:
            return None

        values = [h.value for h in self.history]
        older = values[-(window * 2) : -window]
        recent = values[-window:]

        var_older = self._calc_variance(older)
        var_recent = self._calc_variance(recent)
        var_ratio = (var_recent / var_older) if var_older > 0 else 1.0

        ac_older = self._calc_autocorrelation(older)
        ac_recent = self._calc_autocorrelation(recent)
        ac_change = ac_recent - ac_older

        var_trend = "rising" if var_ratio > 1.3 else "falling" if var_ratio < 0.7 else "stable"
        ac_trend = "rising" if ac_change > 0.15 else "falling" if ac_change < -0.15 else "stable"

        ew_score = 0.0
        if var_trend == "rising":
            ew_score += min(0.5, (var_ratio - 1.0) * 0.5)
        if ac_trend == "rising":
            ew_score += min(0.5, ac_change * 2.0)
        ew_score = max(0.0, min(1.0, ew_score))

        if ew_score > 0.7:
            risk = "critical"
        elif ew_score > 0.4:
            risk = "high"
        elif ew_score > 0.2:
            risk = "moderate"
        else:
            risk = "low"

        return {
            "variance_trend": var_trend,
            "variance_ratio": round(var_ratio, 3),
            "autocorrelation_trend": ac_trend,
            "autocorrelation_change": round(ac_change, 3),
            "early_warning_score": round(ew_score, 3),
            "phase_transition_risk": risk,
            "window_size": window,
        }

    @staticmethod
    def _calc_variance(values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / (len(values) - 1)

    @staticmethod
    def _calc_autocorrelation(values: List[float], lag: int = 1) -> float:
        if len(values) < lag + 2:
            return 0.0
        n = len(values)
        mean = sum(values) / n
        numerator = sum((values[i] - mean) * (values[i + lag] - mean) for i in range(n - lag))
        denominator = sum((v - mean) ** 2 for v in values)
        if denominator < 1e-10:
            return 0.0
        return numerator / denominator
