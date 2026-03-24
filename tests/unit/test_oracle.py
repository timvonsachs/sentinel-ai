"""Tests for Oracle Vision."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.transcendence.oracle import OracleVision


def test_foresee_with_simulator():
    oracle = OracleVision()
    oracle.set_simulator(lambda params, sid: {"outcome": sid * 0.1 - 0.2, "side_effects": []})
    report = oracle.foresee({"prompt": "v2"}, scenarios=5)
    assert len(report.simulations) == 5
    assert isinstance(report.expected, float)


def test_accuracy_bounds():
    oracle = OracleVision()
    oracle.simulation_history.append({"expected": 0.5})
    oracle.validate(0, actual_outcome=0.6)
    acc = oracle.accuracy()
    assert 0 <= acc <= 1
