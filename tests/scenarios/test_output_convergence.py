"""Scenario: output convergence should be visible in lymphatic scan."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_output_convergence_increases_staleness():
    body = Organism("convergence")
    template = "Thank you for contacting support. We are happy to help today."
    for _ in range(30):
        body.process_output(template)
    scan = body.lymph.scan()
    assert "staleness_score" in scan
    assert scan["staleness_score"] >= 0.3
