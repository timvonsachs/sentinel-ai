"""
Scenario: Silent Drift

The AI degrades 0.3% per day; Sentinel should detect early.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism
from sentinel.core.types import HealthStatus


class TestSilentDrift:
    def test_detects_drift_before_traditional_threshold(self):
        body = Organism("drift-test", autonomous=False)

        sentinel_detected_day = None
        traditional_detected_day = None
        traditional_threshold = 0.30

        for day in range(1, 15):
            value = 0.37 + random.gauss(0, 0.008)
            body.observe("conversion", value)

        for day in range(15, 61):
            drift = (day - 14) * 0.003
            value = 0.37 - drift + random.gauss(0, 0.008)
            value = max(0.10, value)
            body.observe("conversion", value)

            health = body.immune.health("conversion")
            if sentinel_detected_day is None and health.status in (
                HealthStatus.WATCH,
                HealthStatus.WARNING,
                HealthStatus.CRITICAL,
            ):
                sentinel_detected_day = day

            if traditional_detected_day is None and value < traditional_threshold:
                traditional_detected_day = day

        assert sentinel_detected_day is not None
        if traditional_detected_day:
            assert sentinel_detected_day < traditional_detected_day
        assert (sentinel_detected_day - 14) <= 12

    def test_multiple_metrics_drift_independently(self):
        body = Organism("multi-drift", autonomous=False)

        for _ in range(25):
            body.observe("conversion", 0.37 + random.gauss(0, 0.005))
            body.observe("satisfaction", 4.2 + random.gauss(0, 0.1))
            body.observe("latency", 200 + random.gauss(0, 10))

        for i in range(15):
            body.observe("conversion", 0.37 - i * 0.004 + random.gauss(0, 0.005))
            body.observe("satisfaction", 4.2 + random.gauss(0, 0.1))
            body.observe("latency", 200 + random.gauss(0, 10))

        conv_health = body.immune.health("conversion")
        sat_health = body.immune.health("satisfaction")
        assert conv_health.status in (HealthStatus.WATCH, HealthStatus.WARNING, HealthStatus.CRITICAL, HealthStatus.THRIVING)
        assert sat_health.status in (HealthStatus.HEALTHY, HealthStatus.THRIVING, HealthStatus.LEARNING, HealthStatus.WATCH)


class TestSuddenCrash:
    def test_detects_sudden_crash(self):
        body = Organism("crash-test")
        for _ in range(25):
            body.observe("conversion", 0.37 + random.gauss(0, 0.005))
        body.observe("conversion", 0.15)
        health = body.immune.health("conversion")
        assert abs(health.metrics.get("z_score", 0)) > 1.5
