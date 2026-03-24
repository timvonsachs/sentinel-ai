"""Scenario: sudden crash in key metric should trigger high pain/watch state."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_sudden_crash_spikes_pain():
    body = Organism("sudden-crash")
    for _ in range(25):
        body.observe("conversion", 0.37 + random.gauss(0, 0.004))
    baseline_pain = body.pain
    body.observe("conversion", 0.10)
    assert body.pain > baseline_pain
