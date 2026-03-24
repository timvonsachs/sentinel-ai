"""Tests for Swarm Intelligence — The Mycelium Network."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.capabilities.swarm import SwarmIntelligence, SwarmSignal


class TestSwarm:
    def test_connect(self):
        a = SwarmIntelligence("agent-a")
        b = SwarmIntelligence("agent-b")
        a.connect(b)
        assert "agent-b" in a.peers
        assert "agent-a" in b.peers

    def test_broadcast_reaches_peers(self):
        a = SwarmIntelligence("agent-a")
        b = SwarmIntelligence("agent-b")
        a.connect(b)

        a.broadcast(SwarmSignal(type="alert", source_id="agent-a", data={"threat": "model_drift"}))
        signals = b.receive("alert")
        assert len(signals) > 0
        assert signals[0].data["threat"] == "model_drift"

    def test_broadcast_does_not_loop(self):
        a = SwarmIntelligence("agent-a")
        b = SwarmIntelligence("agent-b")
        c = SwarmIntelligence("agent-c")
        a.connect(b)
        b.connect(c)
        a.broadcast(SwarmSignal(type="alert", source_id="agent-a", data={"test": True}, ttl=3))
        # Direct peer delivery to b should work; loop prevention should not duplicate.
        b_signals = b.receive("alert")
        assert len(b_signals) > 0
        assert len({s.id for s in b_signals}) == len(b_signals)

    def test_share_immunity(self):
        a = SwarmIntelligence("agent-a")
        b = SwarmIntelligence("agent-b")
        a.connect(b)
        a.share_immunity("gpt4o_drift", pattern={"z_score_drop": 1.5}, fix={"action": "revert_prompt"})
        assert "gpt4o_drift" in b.shared_immunity

    def test_collective_health(self):
        a = SwarmIntelligence("agent-a")
        b = SwarmIntelligence("agent-b")
        a.connect(b)
        health = a.collective_health()
        assert health["swarm_size"] == 2
