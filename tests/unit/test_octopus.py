"""Tests for Octopus Intelligence."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.capabilities.octopus import OctopusIntelligence


def test_tentacle_registration_and_check():
    octo = OctopusIntelligence()
    octo.tentacle("retrieval", health_checker=lambda: 0.8)
    assert octo.check("retrieval") == 0.8


def test_check_all_has_overall():
    octo = OctopusIntelligence()
    octo.tentacle("a", lambda: 1.0)
    octo.tentacle("b", lambda: 0.5)
    res = octo.check_all()
    assert "overall" in res
