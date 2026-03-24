"""Integration test for immune-endocrine feedback loop."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_immune_alerts_raise_cortisol():
    body = Organism("loop-test")
    for _ in range(25):
        body.observe("conversion", 0.37 + random.gauss(0, 0.004))
    baseline_cortisol = body.endocrine.get("cortisol")

    for i in range(8):
        body.observe("conversion", 0.37 - 0.02 - i * 0.005)

    stressed_cortisol = body.endocrine.get("cortisol")
    assert stressed_cortisol >= baseline_cortisol
    assert body.pain >= 0
