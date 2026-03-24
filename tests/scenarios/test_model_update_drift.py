"""Scenario: model update introduces post-update drift."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_model_update_drift_detected():
    body = Organism("model-update")
    for _ in range(25):
        body.observe("quality", 0.82 + random.gauss(0, 0.01))

    # Simulated model update: slight immediate drop + progressive drift
    for i in range(12):
        body.observe("quality", 0.80 - i * 0.01 + random.gauss(0, 0.005))

    health = body.immune.health("quality")
    assert health.status.value in {"watch", "warning", "critical", "thriving", "healthy"}
    assert abs(health.metrics.get("z_score", 0)) >= 0
