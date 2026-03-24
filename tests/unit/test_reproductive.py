"""Tests for Reproductive System."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sentinel.systems.reproductive import ReproductiveSystem


def test_genome_initializes_population():
    rs = ReproductiveSystem(population_size=4)
    rs.genome({"temperature": {"min": 0.1, "max": 1.0, "current": 0.7}})
    assert len(rs.population) == 4
    assert rs.active_variant is not None


def test_evolve_returns_params():
    rs = ReproductiveSystem(population_size=3, mutation_rate=0.5)
    rs.genome({"temperature": {"min": 0.1, "max": 1.0, "current": 0.7}})
    for variant in rs.population:
        variant.observations = 5
        variant.fitness = 0.5
    params = rs.evolve()
    assert "temperature" in params
