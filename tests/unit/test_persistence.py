"""Tests for PersistenceLayer."""

import tempfile

from sentinel.core.persistence import PersistenceLayer


def test_save_and_load_state_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        p = PersistenceLayer(path=tmp, auto_save_interval=2)
        assert p.save({"name": "x", "state": "stable"}) is True
        state = p.load()
        assert state["name"] == "x"


def test_tick_auto_save_signal():
    with tempfile.TemporaryDirectory() as tmp:
        p = PersistenceLayer(path=tmp, auto_save_interval=3)
        assert p.tick() is False
        assert p.tick() is False
        assert p.tick() is True
