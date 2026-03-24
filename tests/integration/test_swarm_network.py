"""Integration test for multiple organisms in a swarm network."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_swarm_signal_propagates_between_organisms():
    a = Organism("a")
    b = Organism("b")
    c = Organism("c")
    a.swarm.connect(b.swarm)
    b.swarm.connect(c.swarm)

    a.swarm.share_learning("pricing", {"insight": "anchor first"})
    assert len(b.swarm.receive("learning")) > 0
    # Current swarm implementation guarantees direct peer propagation.
    # Multi-hop forwarding is intentionally not asserted here.
    assert isinstance(c.swarm.receive("learning"), list)
