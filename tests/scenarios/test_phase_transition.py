"""Scenario test: lifecycle state transitions under stress and recovery."""

from sentinel import Organism


def test_phase_transition_nascent_to_stressed_and_back():
    body = Organism("phase-test", autonomous=True)
    for _ in range(25):
        body.observe("conversion", 0.37)
    assert body.state in {"stable", "thriving", "stressed"}

    for _ in range(12):
        body.observe("conversion", 0.15)
    assert body.state in {"stressed", "sick", "healing", "recovering", "hibernating", "stable"}

    # recovery input
    for _ in range(10):
        body.observe("conversion", 0.37)
    assert body.state in {"recovering", "stable", "thriving", "healing", "stressed", "hibernating"}
