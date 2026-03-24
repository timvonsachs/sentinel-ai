"""Scenario: self-evolution systems produce candidates and tournament outcomes."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel import Organism


def test_self_evolution_flow():
    random.seed(123)
    body = Organism("evo-scenario")

    body.reproductive.genome(
        {
            "temperature": {"min": 0.1, "max": 1.0, "current": 0.6},
            "max_tokens": {"min": 128, "max": 1024, "current": 512},
        }
    )
    for variant in body.reproductive.population:
        variant.observations = 5
        variant.fitness = random.random()
    params = body.reproductive.evolve()
    assert "temperature" in params

    body.immortal.set_genome({"temperature": {"min": 0.1, "max": 1.0}})
    body.immortal.set_champion({"temperature": 0.6})
    body.immortal.spawn_challenger()
    for _ in range(10):
        body.immortal.report_fitness("champion", 0.6)
        body.immortal.report_fitness("challenger", 0.65)
    result = body.immortal.tournament(min_observations=10)
    assert result is not None
