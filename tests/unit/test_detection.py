"""Tests for the Detection Engine — Persistence, Trend, Velocity."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.core.detection import DetectionEngine
from sentinel.core.ewma import Observation


def make_obs(z_scores):
    return [
        Observation(value=0, z_score=z, baseline=0, variance=1, timestamp=time.time() + i, count=i + 1)
        for i, z in enumerate(z_scores)
    ]


class TestPersistenceDetection:
    def test_no_alert_for_normal(self):
        engine = DetectionEngine()
        obs = make_obs([0.5, 0.3, -0.2, 0.1, 0.4])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "persistence"]) == 0

    def test_warning_for_sustained_deviation(self):
        engine = DetectionEngine(persistence_days=3, watch_threshold=1.5)
        obs = make_obs([0.5, 0.3, 1.6, 1.7, 1.8])
        alerts = engine.check("test", obs)
        p = [a for a in alerts if a.type == "persistence"]
        assert len(p) > 0
        assert p[0].severity == "warning"

    def test_critical_for_high_deviation(self):
        engine = DetectionEngine(persistence_days=3, warning_threshold=2.0)
        obs = make_obs([0.5, 2.1, 2.3, 2.5])
        alerts = engine.check("test", obs)
        assert any(a.severity == "critical" for a in alerts if a.type == "persistence")

    def test_negative_persistence(self):
        engine = DetectionEngine(persistence_days=3, watch_threshold=1.5)
        obs = make_obs([0.5, -1.6, -1.7, -1.8])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "persistence"]) > 0


class TestTrendDetection:
    def test_no_trend_in_random_data(self):
        engine = DetectionEngine(trend_days=5)
        obs = make_obs([0.5, -0.3, 0.8, -0.1, 0.6, -0.4])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "trend"]) == 0

    def test_detects_falling_trend(self):
        engine = DetectionEngine(trend_days=5, watch_threshold=1.0)
        obs = make_obs([-0.5, -0.8, -1.0, -1.3, -1.6])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "trend"]) > 0

    def test_detects_rising_trend(self):
        engine = DetectionEngine(trend_days=5, watch_threshold=1.0)
        obs = make_obs([0.5, 0.8, 1.0, 1.3, 1.6])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "trend"]) > 0


class TestVelocityDetection:
    def test_no_alert_for_small_change(self):
        engine = DetectionEngine(velocity_threshold=2.5)
        obs = make_obs([0.5, 0.8])
        alerts = engine.check("test", obs)
        assert len([a for a in alerts if a.type == "velocity"]) == 0

    def test_alert_for_sudden_jump(self):
        engine = DetectionEngine(velocity_threshold=2.5)
        obs = make_obs([0.5, 3.5])
        alerts = engine.check("test", obs)
        velocity = [a for a in alerts if a.type == "velocity"]
        assert len(velocity) > 0
        assert velocity[0].severity == "critical"
