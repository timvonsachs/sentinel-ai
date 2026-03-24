"""Tests for Pain Sense."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_pain_score_in_range():
    body = Organism("pain-test")
    for _ in range(25):
        body.observe("conversion", 0.37 + random.gauss(0, 0.005))
    s = body.pain
    assert 0.0 <= s <= 1.0


def test_feeling_returns_text():
    body = Organism("pain-test2")
    assert isinstance(body.feeling, str)
