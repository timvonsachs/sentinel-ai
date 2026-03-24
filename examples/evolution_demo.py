"""
Evolution Demo — reproductive + immortal systems in action.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel import Organism


def main():
    random.seed(7)
    body = Organism("evo-agent", autonomous=True)

    body.reproductive.genome(
        {
            "temperature": {"min": 0.1, "max": 1.0, "current": 0.6},
            "max_tokens": {"min": 128, "max": 2000, "current": 512},
            "prompt_version": {"options": ["v1", "v2", "v3"], "current": "v1"},
        }
    )

    body.immortal.set_genome(
        {
            "temperature": {"min": 0.1, "max": 1.0},
            "max_tokens": {"min": 128, "max": 2000},
            "prompt_version": {"options": ["v1", "v2", "v3"]},
        }
    )
    body.immortal.set_champion(
        {"temperature": 0.6, "max_tokens": 512, "prompt_version": "v1"}
    )
    body.immortal.spawn_challenger()

    print("=== Reproductive Evolution ===")
    for step in range(20):
        score = 0.4 + random.random() * 0.6
        body.reproductive.fitness(score)
        if step % 5 == 4:
            params = body.reproductive.evolve()
            print(f"step={step+1:2d} evolved params -> {params}")

    print("best reproductive:", body.reproductive.best())

    print("\n=== Immortal Tournament ===")
    for _ in range(12):
        body.immortal.report_fitness("champion", 0.55 + random.random() * 0.2)
        body.immortal.report_fitness("challenger", 0.5 + random.random() * 0.3)

    result = body.immortal.tournament(min_observations=10)
    print("tournament:", result)
    print("status:", body.immortal.status())


if __name__ == "__main__":
    main()
