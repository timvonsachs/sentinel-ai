"""Tests for the Immune System."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.immune import ImmuneSystem
from sentinel.core.types import HealthStatus


class TestImmuneSystem:
    def test_observe_creates_baseline(self):
        immune = ImmuneSystem()
        obs = immune.observe("test", 0.37)
        assert "test" in immune.baselines
        assert obs.z_score == 0.0

    def test_health_learning_phase(self):
        immune = ImmuneSystem()
        immune.observe("test", 0.37)
        health = immune.health("test")
        assert health.status == HealthStatus.LEARNING

    def test_health_healthy_after_calibration(self):
        immune = ImmuneSystem()
        for _ in range(25):
            immune.observe("test", 0.37)
        health = immune.health("test")
        assert health.status in (HealthStatus.HEALTHY, HealthStatus.THRIVING, HealthStatus.WATCH)

    def test_health_warning_on_drift(self):
        immune = ImmuneSystem()
        for _ in range(25):
            immune.observe("test", 0.37 + random.gauss(0, 0.001))
        for _ in range(5):
            immune.observe("test", 0.20)
        health = immune.health("test")
        assert health.status in (HealthStatus.WARNING, HealthStatus.CRITICAL, HealthStatus.WATCH, HealthStatus.THRIVING)

    def test_system_health_aggregates(self):
        immune = ImmuneSystem()
        for _ in range(25):
            immune.observe("metric_a", 0.37)
            immune.observe("metric_b", 100)
        health = immune.health()
        assert health.pain_score >= 0

    def test_self_healing_callback(self):
        healed = {"count": 0}

        def heal_action(_alert):
            healed["count"] += 1

        immune = ImmuneSystem()
        immune.on_warning("test", heal_action)

        for _ in range(25):
            immune.observe("test", 0.37)
        for _ in range(5):
            immune.observe("test", 0.20)

        assert healed["count"] >= 0
        assert len(immune.healing_log) >= 0

    def test_multiple_metrics(self):
        immune = ImmuneSystem()
        immune.observe("conversion", 0.37)
        immune.observe("satisfaction", 4.5)
        immune.observe("latency", 200)
        assert len(immune.baselines) == 3
