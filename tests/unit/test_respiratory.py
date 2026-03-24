"""Tests for Respiratory System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.respiratory import RespiratorySystem


def test_high_pain_enters_emergency():
    rs = RespiratorySystem()
    state = rs.breathe(pain=0.9)
    assert state.rate == "emergency"
    assert rs.budget == 0.1


def test_high_urgency_enters_deep():
    rs = RespiratorySystem()
    state = rs.breathe(urgency=0.95, pain=0.0, load=0.2)
    assert state.rate == "deep"
