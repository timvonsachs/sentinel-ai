"""Tests for Memory System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.memory import MemorySystem


def test_remember_and_recall():
    mem = MemorySystem()
    mem.remember("drift", {"metric": "conversion"}, fix="revert_prompt")
    results = mem.recall("drift", context={"metric": "conversion"})
    assert len(results) == 1
    assert results[0].fix == "revert_prompt"


def test_last_and_has_seen():
    mem = MemorySystem()
    mem.remember("a", {"x": 1})
    assert mem.has_seen("a")
    assert mem.last().event == "a"
