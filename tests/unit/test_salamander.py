"""Tests for Salamander Regeneration."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.capabilities.salamander import SalamanderRegeneration


def test_regenerate_on_failed_healthcheck():
    s = SalamanderRegeneration()
    state = {"healthy": False, "rebuilt": False}

    def health_check():
        return state["healthy"]

    def regenerate():
        state["healthy"] = True
        state["rebuilt"] = True

    s.register("index", health_check, regenerate)
    ok = s.check("index")
    assert ok is False
    assert state["rebuilt"] is True
    assert s.check("index") is True


def test_status_has_component():
    s = SalamanderRegeneration()
    s.register("x", lambda: True, lambda: None)
    assert "x" in s.status()
