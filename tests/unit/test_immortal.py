"""Tests for Immortal Evolution."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.transcendence.immortal import ImmortalEvolution


def test_set_champion_and_spawn():
    im = ImmortalEvolution(mutation_rate=0.5)
    im.set_genome({"temperature": {"min": 0.1, "max": 1.0}})
    im.set_champion({"temperature": 0.5})
    challenger = im.spawn_challenger()
    assert challenger is not None
    assert im.champion is not None


def test_tournament_defends_or_replaces():
    im = ImmortalEvolution()
    im.set_genome({"temperature": {"min": 0.1, "max": 1.0}})
    im.set_champion({"temperature": 0.5})
    im.spawn_challenger()
    for _ in range(10):
        im.report_fitness("champion", 0.6)
        im.report_fitness("challenger", 0.55)
    result = im.tournament(min_observations=10)
    assert result is not None
