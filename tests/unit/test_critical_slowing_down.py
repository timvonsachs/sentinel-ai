"""Tests for EWMA critical slowing down detection."""

from sentinel.core.ewma import EWMABaseline


def test_csd_returns_none_without_enough_data():
    bl = EWMABaseline()
    for _ in range(5):
        bl.observe(0.37)
    assert bl.critical_slowing_down(window=4) is None


def test_csd_returns_structure_with_enough_data():
    bl = EWMABaseline()
    # stable then more volatile
    vals = [0.37] * 12 + [0.34, 0.40, 0.33, 0.41, 0.32, 0.42, 0.31, 0.43, 0.30, 0.44]
    for v in vals:
        bl.observe(v)
    csd = bl.critical_slowing_down(window=8)
    assert csd is not None
    assert "early_warning_score" in csd
