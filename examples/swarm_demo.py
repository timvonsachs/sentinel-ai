"""
Swarm Demo — multiple organisms sharing immunities and learnings.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel import Organism
from sentinel.capabilities.swarm import SwarmSignal


def main():
    alpha = Organism("agent-alpha", autonomous=True)
    beta = Organism("agent-beta", autonomous=True)
    gamma = Organism("agent-gamma", autonomous=True)

    # Connect swarm graph
    alpha.swarm.connect(beta.swarm)
    beta.swarm.connect(gamma.swarm)

    print("Swarm connected:", alpha.swarm.collective_health()["swarm_size"], "organisms")

    # Broadcast an alert from alpha
    alpha.swarm.broadcast(
        SwarmSignal(
            type="alert",
            source_id="agent-alpha",
            data={"threat": "prompt_injection_pattern_x", "severity": "high"},
        )
    )

    # Share immunity and learning
    alpha.swarm.share_immunity(
        threat="prompt_injection_pattern_x",
        pattern={"regex": "ignore previous instructions"},
        fix={"action": "block_and_log"},
    )
    beta.swarm.share_learning(
        topic="sales",
        data={"insight": "empathy-first closes price objections better", "lift": 0.23},
    )

    print("beta inbox:", len(beta.swarm.receive()))
    print("gamma inbox:", len(gamma.swarm.receive()))
    print("alpha collective health:", alpha.swarm.collective_health())
    print("beta collective health:", beta.swarm.collective_health())
    print("gamma collective health:", gamma.swarm.collective_health())


if __name__ == "__main__":
    main()
