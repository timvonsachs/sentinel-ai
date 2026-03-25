"""Tests for OrganismStateMachine."""

from sentinel.core.state_machine import OrganismStateMachine, OrganismState


def test_nascent_to_stable():
    sm = OrganismStateMachine()
    sm.evaluate(confidence=90, pain=0.1)
    assert sm.current == OrganismState.STABLE


def test_stable_to_stressed_with_hysteresis():
    sm = OrganismStateMachine()
    sm.force(OrganismState.STABLE, "setup")
    sm.evaluate(pain=0.35, confidence=100)
    sm.evaluate(pain=0.36, confidence=100)
    assert sm.current == OrganismState.STABLE
    sm.evaluate(pain=0.37, confidence=100)
    assert sm.current == OrganismState.STRESSED
