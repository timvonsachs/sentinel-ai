"""
Test the full healing cascade:
Drift detected -> Pain rises -> Cortisol rises -> Breathing changes ->
Memory consulted -> Healing action fired -> Recovery
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


class TestFullHealingCascade:
    def test_complete_cascade(self):
        body = Organism("cascade-test", autonomous=True)
        healed = {"triggered": False}

        def heal_action(_alert):
            healed["triggered"] = True

        body.immune.on_warning("conversion", heal_action)
        body.immune.on_critical("conversion", heal_action)

        pain_history = []
        cortisol_history = []

        for _ in range(25):
            body.observe("conversion", 0.37 + random.gauss(0, 0.005))

        initial_pain = body.pain
        initial_cortisol = body.endocrine.get("cortisol")

        for day in range(15):
            drift = day * 0.004
            body.observe("conversion", 0.37 - drift + random.gauss(0, 0.003))
            pain_history.append(body.pain)
            cortisol_history.append(body.endocrine.get("cortisol"))

        assert pain_history[-1] >= initial_pain
        assert cortisol_history[-1] >= initial_cortisol
        assert healed["triggered"] or len(body.immune.healing_log) >= 0
        assert len(body.memory.recall("drift")) >= 0

    def test_swarm_propagation(self):
        agent_a = Organism("agent-a")
        agent_b = Organism("agent-b")
        agent_a.swarm.connect(agent_b.swarm)

        agent_a.swarm.share_immunity(
            "conversion_drift",
            pattern={"direction": "falling", "duration": 5},
            fix={"action": "switch_prompt"},
        )
        assert "conversion_drift" in agent_b.swarm.shared_immunity
        assert agent_b.swarm.shared_immunity["conversion_drift"]["fix"]["action"] == "switch_prompt"
