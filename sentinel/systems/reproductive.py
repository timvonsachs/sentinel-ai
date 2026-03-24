"""
The Reproductive System — Autonomous self-evolution.

Not reproduction in the biological sense. EVOLUTION.
The system creates variants of itself. Tests them. Keeps the better one.
Continuous improvement without human intervention.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import copy
import random
import time


@dataclass
class Variant:
    id: str
    parameters: Dict[str, Any]
    fitness: float = 0.0
    observations: int = 0
    created: float = field(default_factory=time.time)
    parent: Optional[str] = None


class ReproductiveSystem:
    """
    Autonomous self-evolution for AI systems.
    """

    def __init__(self, population_size: int = 5, mutation_rate: float = 0.1):
        self.genome_spec: Dict[str, Dict] = {}
        self.population: List[Variant] = []
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.generation: int = 0
        self.best_ever: Optional[Variant] = None
        self.active_variant: Optional[Variant] = None
        self.evolution_log: List[Dict] = []

    def genome(self, spec: Dict[str, Dict]):
        """Define the genome: what parameters can be evolved."""
        self.genome_spec = spec

        # Create initial population
        current = {}
        for key, config in spec.items():
            current[key] = config.get("current", config.get("min", 0))

        self.active_variant = Variant(id="origin", parameters=current)
        self.population = [self.active_variant]

        # Generate initial variants
        for i in range(self.population_size - 1):
            variant = self._mutate(self.active_variant, f"gen0_{i}")
            self.population.append(variant)

    def fitness(self, score: float):
        """Report fitness of current active variant."""
        if self.active_variant:
            # Running average
            self.active_variant.observations += 1
            n = self.active_variant.observations
            self.active_variant.fitness = (self.active_variant.fitness * (n - 1) + score) / n

    def evolve(self) -> Dict[str, Any]:
        """
        Select the fittest variant. Reproduce. Mutate.
        Returns the parameters to use next.
        """
        if not self.population:
            return {}

        # Only evolve if we have enough observations
        evaluated = [v for v in self.population if v.observations >= 5]
        if len(evaluated) < 2:
            # Not enough data, keep current
            return self.active_variant.parameters if self.active_variant else {}

        # Selection: rank by fitness
        evaluated.sort(key=lambda v: v.fitness, reverse=True)

        # Update best ever
        if not self.best_ever or evaluated[0].fitness > self.best_ever.fitness:
            self.best_ever = evaluated[0]

        # New generation
        self.generation += 1
        survivors = evaluated[: max(2, self.population_size // 2)]

        new_population = list(survivors)
        while len(new_population) < self.population_size:
            parent = random.choice(survivors)
            child = self._mutate(parent, f"gen{self.generation}_{len(new_population)}")
            new_population.append(child)

        self.population = new_population
        self.active_variant = new_population[0]  # best goes active

        self.evolution_log.append(
            {
                "generation": self.generation,
                "best_fitness": evaluated[0].fitness,
                "best_params": evaluated[0].parameters,
                "population_size": len(self.population),
                "timestamp": time.time(),
            }
        )

        return self.active_variant.parameters

    def _mutate(self, parent: Variant, variant_id: str) -> Variant:
        """Create a mutated variant from a parent."""
        new_params = copy.deepcopy(parent.parameters)

        for key, config in self.genome_spec.items():
            if random.random() > self.mutation_rate:
                continue

            if "options" in config:
                # Categorical: random selection
                new_params[key] = random.choice(config["options"])
            elif "min" in config and "max" in config:
                # Numeric: gaussian mutation
                current = new_params.get(key, config["min"])
                range_size = config["max"] - config["min"]
                mutation = random.gauss(0, range_size * 0.1)
                new_val = max(config["min"], min(config["max"], current + mutation))
                new_params[key] = round(new_val, 4)

        return Variant(id=variant_id, parameters=new_params, parent=parent.id)

    def best(self) -> Optional[Dict]:
        """Get the best parameters ever found."""
        if self.best_ever:
            return {
                "parameters": self.best_ever.parameters,
                "fitness": self.best_ever.fitness,
                "generation": self.generation,
            }
        return None
