"""
Immortal Evolution — The impossible combination.

Biology requires death for evolution.
No organism can be both immortal AND evolving.
AI can.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import copy
import random
import time


@dataclass
class Generation:
    id: int
    config: Dict[str, Any]
    fitness: float
    born: float = field(default_factory=time.time)
    observations: int = 0
    is_champion: bool = False


class ImmortalEvolution:
    """
    Immortality with evolution — keeping the best while improving.
    """

    def __init__(self, mutation_rate: float = 0.1):
        self.champion: Optional[Generation] = None
        self.challengers: List[Generation] = []
        self.generation_count: int = 0
        self.mutation_rate = mutation_rate
        self.evolution_history: List[Dict] = []
        self.genome_spec: Dict[str, Dict] = {}

    def set_genome(self, spec: Dict[str, Dict]):
        """Define what can evolve. Same format as ReproductiveSystem."""
        self.genome_spec = spec

    def set_champion(self, config: Dict[str, Any]):
        """Set the current immortal champion."""
        self.generation_count += 1
        self.champion = Generation(
            id=self.generation_count,
            config=config,
            fitness=0,
            is_champion=True,
        )

    def spawn_challenger(self) -> Optional[Generation]:
        """Create a mutated challenger from the champion."""
        if not self.champion:
            return None

        self.generation_count += 1
        challenger_config = copy.deepcopy(self.champion.config)

        # Mutate
        for key, spec in self.genome_spec.items():
            if key not in challenger_config:
                continue
            if random.random() > self.mutation_rate:
                continue

            if "options" in spec:
                challenger_config[key] = random.choice(spec["options"])
            elif "min" in spec and "max" in spec:
                current = challenger_config[key]
                range_size = spec["max"] - spec["min"]
                mutation = random.gauss(0, range_size * 0.15)
                challenger_config[key] = max(spec["min"], min(spec["max"], current + mutation))

        challenger = Generation(id=self.generation_count, config=challenger_config, fitness=0)
        self.challengers.append(challenger)
        return challenger

    def report_fitness(self, role: str, score: float):
        """Report fitness for champion or latest challenger."""
        if role == "champion" and self.champion:
            n = self.champion.observations + 1
            self.champion.fitness = (self.champion.fitness * (n - 1) + score) / n
            self.champion.observations = n
        elif role == "challenger" and self.challengers:
            challenger = self.challengers[-1]
            n = challenger.observations + 1
            challenger.fitness = (challenger.fitness * (n - 1) + score) / n
            challenger.observations = n

    def tournament(self, min_observations: int = 10) -> Optional[Dict]:
        """
        Run a tournament. If a challenger beats the champion,
        the challenger becomes the new immortal.
        """
        if not self.champion or not self.challengers:
            return None

        # Find best challenger with enough observations
        viable = [c for c in self.challengers if c.observations >= min_observations]
        if not viable:
            return {"result": "insufficient_data", "champion_stays": True}

        best_challenger = max(viable, key=lambda c: c.fitness)

        if self.champion.observations < min_observations:
            return {"result": "champion_needs_more_data", "champion_stays": True}

        if best_challenger.fitness > self.champion.fitness:
            # New champion
            old_champion = self.champion
            self.champion = best_challenger
            self.champion.is_champion = True
            self.challengers = []

            event = {
                "event": "new_champion",
                "old_fitness": old_champion.fitness,
                "new_fitness": best_challenger.fitness,
                "improvement": best_challenger.fitness - old_champion.fitness,
                "generation": self.generation_count,
                "timestamp": time.time(),
            }
            self.evolution_history.append(event)

            return {
                "result": "new_champion",
                "improvement": best_challenger.fitness - old_champion.fitness,
                "config": best_challenger.config,
            }

        # Champion survives; clear weak challengers
        self.challengers = [c for c in self.challengers if c.observations < min_observations]
        return {
            "result": "champion_defended",
            "champion_fitness": self.champion.fitness,
            "challenger_fitness": best_challenger.fitness,
        }

    def lineage(self) -> List[Dict]:
        """The evolutionary history of champions."""
        return self.evolution_history

    def status(self) -> Dict:
        return {
            "champion": {
                "generation": self.champion.id if self.champion else None,
                "fitness": self.champion.fitness if self.champion else 0,
                "observations": self.champion.observations if self.champion else 0,
                "config": self.champion.config if self.champion else {},
            },
            "active_challengers": len(self.challengers),
            "total_generations": self.generation_count,
            "champion_changes": len(self.evolution_history),
        }
