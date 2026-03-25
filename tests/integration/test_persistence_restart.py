"""Integration test: state survives restart via persistence."""

import tempfile

from sentinel import Organism


def test_persistence_roundtrip_baseline_and_memory():
    with tempfile.TemporaryDirectory() as tmp:
        a = Organism("persist-agent", persist_path=tmp, autonomous=True)
        for _ in range(30):
            a.observe("conversion", 0.37)
        a.memory.remember("drift", {"metric": "conversion"}, fix="revert_prompt")
        assert a.save() is True

        b = Organism("persist-agent", persist_path=tmp, autonomous=True)
        assert "conversion" in b.immune.baselines
        assert len(b.memory.experiences) >= 1
