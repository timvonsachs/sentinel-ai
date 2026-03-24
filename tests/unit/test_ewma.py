"""Tests for the EWMA Baseline Engine — the heart of Sentinel."""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.core.ewma import EWMABaseline


class TestEWMABaseline:
    def test_first_observation_z_score_is_zero(self):
        bl = EWMABaseline()
        obs = bl.observe(0.37)
        assert obs.z_score == 0.0, "First observation should have z_score=0"

    def test_baseline_tracks_stable_values(self):
        bl = EWMABaseline()
        for _ in range(30):
            bl.observe(0.37)
        assert abs(bl.mean - 0.37) < 0.01, "Baseline should converge to stable value"

    def test_high_z_score_for_deviation(self):
        bl = EWMABaseline()
        for _ in range(25):
            bl.observe(0.37)
        obs = bl.observe(0.50)
        assert obs.z_score > 1.5

    def test_negative_z_score_for_drop(self):
        bl = EWMABaseline()
        for _ in range(25):
            bl.observe(0.37)
        obs = bl.observe(0.25)
        assert obs.z_score < -1.5

    def test_z_score_clipping(self):
        bl = EWMABaseline(z_clip=3.0)
        for _ in range(25):
            bl.observe(0.37)
        obs = bl.observe(10.0)
        assert -3.0 <= obs.z_score <= 3.0

    def test_damping_during_learning_phase(self):
        bl = EWMABaseline()
        bl.observe(0.37)
        obs = bl.observe(0.50)
        assert obs.z_score == 0.0

    def test_damping_decreases_during_refining(self):
        bl = EWMABaseline()
        for _ in range(6):
            bl.observe(0.37)
        obs = bl.observe(0.50)
        assert obs.z_score != 0.0

    def test_full_confidence_after_21(self):
        bl = EWMABaseline()
        for _ in range(21):
            bl.observe(0.37)
        assert bl.phase == "calibrated"
        assert bl.confidence == 100.0

    def test_phases(self):
        bl = EWMABaseline()
        for i in range(1, 25):
            bl.observe(0.37)
            if i < 7:
                assert bl.phase == "learning"
            elif i < 21:
                assert bl.phase == "refining"
            else:
                assert bl.phase == "calibrated"

    def test_variance_increases_with_noise(self):
        bl = EWMABaseline()
        for _ in range(10):
            bl.observe(0.37)
        low_var = bl.variance
        for i in range(10):
            bl.observe(0.37 + (0.1 if i % 2 == 0 else -0.1))
        assert bl.variance > low_var

    def test_history_preserved(self):
        bl = EWMABaseline()
        for i in range(10):
            bl.observe(0.37 + i * 0.01)
        assert len(bl.history) == 10
        assert bl.history[0].count == 1
        assert bl.history[9].count == 10

    def test_lambda_sensitivity(self):
        fast = EWMABaseline(lambda_=0.3)
        slow = EWMABaseline(lambda_=0.05)
        for _ in range(20):
            fast.observe(0.37)
            slow.observe(0.37)
        fast.observe(0.50)
        slow.observe(0.50)
        assert abs(fast.mean - 0.50) < abs(slow.mean - 0.50)


class TestEWMAEdgeCases:
    def test_constant_values(self):
        bl = EWMABaseline()
        for _ in range(30):
            obs = bl.observe(0.37)
        assert abs(obs.z_score) < 0.1

    def test_zero_values(self):
        bl = EWMABaseline()
        for _ in range(10):
            bl.observe(0.0)
        assert bl.mean == pytest.approx(0.0, abs=0.01)

    def test_negative_values(self):
        bl = EWMABaseline()
        for _ in range(10):
            bl.observe(-5.0)
        assert bl.mean == pytest.approx(-5.0, abs=0.5)

    def test_very_large_values(self):
        bl = EWMABaseline()
        for _ in range(10):
            bl.observe(1_000_000.0)
        assert bl.mean == pytest.approx(1_000_000.0, rel=0.01)
