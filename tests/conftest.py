"""Shared fixtures for all tests."""

import os
import random
import sys
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel import Organism


@pytest.fixture
def organism():
    """Fresh organism for each test."""
    return Organism("test-agent", autonomous=False)


@pytest.fixture
def autonomous_organism():
    """Organism with autonomous healing enabled."""
    return Organism("test-agent-auto", autonomous=True)


@pytest.fixture
def trained_organism():
    """Organism with 21+ observations (fully calibrated baseline)."""
    org = Organism("trained-agent", autonomous=True)
    for _ in range(25):
        org.observe("conversion", 0.37 + random.gauss(0, 0.005))
    return org


@pytest.fixture
def sick_organism():
    """Organism that has been drifting for days."""
    org = Organism("sick-agent", autonomous=False)
    # Build baseline
    for _ in range(15):
        org.observe("conversion", 0.37 + random.gauss(0, 0.005))
    # Introduce drift
    for i in range(10):
        drift = i * 0.005
        org.observe("conversion", 0.37 - drift + random.gauss(0, 0.003))
    return org


@pytest.fixture
def swarm_pair():
    """Two connected organisms."""
    a = Organism("agent-a")
    b = Organism("agent-b")
    a.swarm.connect(b.swarm)
    return a, b


def stable_value(base=0.37, noise=0.005):
    """Generate a stable metric value."""
    return base + random.gauss(0, noise)


def drifting_value(base=0.37, day=0, drift_rate=0.003, noise=0.005):
    """Generate a drifting metric value."""
    return base - (day * drift_rate) + random.gauss(0, noise)
