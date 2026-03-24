"""Tests for the Nervous System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.nervous import NervousSystem


def test_reflex_triggers_action():
    system = NervousSystem()
    state = {"called": False}

    def action(_metrics):
        state["called"] = True

    system.reflex("latency", lambda m: m.get("latency", 0) > 1000, action)
    triggered = system.signal({"latency": 1500})
    assert "latency" in triggered
    assert state["called"] is True


def test_cooldown_blocks_repeat_trigger():
    system = NervousSystem()
    count = {"n": 0}
    system.reflex("x", lambda _m: True, lambda _m: count.__setitem__("n", count["n"] + 1), cooldown=60)
    system.signal({})
    system.signal({})
    assert count["n"] == 1
