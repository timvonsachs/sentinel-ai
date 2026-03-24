"""Tests for Lymphatic System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.lymph import LymphaticSystem


def test_scan_insufficient_data():
    lymph = LymphaticSystem()
    res = lymph.scan()
    assert res["status"] == "insufficient_data"


def test_scan_has_metrics_after_history():
    lymph = LymphaticSystem()
    for i in range(30):
        lymph.process_output(f"Response {i}: price is {i} dollars")
    res = lymph.scan()
    assert "contamination_score" in res
    assert 0 <= res["contamination_score"] <= 1
