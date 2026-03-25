"""
Auto Optimize — autonomous optimization of prompts/parameters.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import copy
import hashlib
import random
import time


@dataclass
class Variant:
    id: str
    parameters: Dict[str, Any]
    fitness: float = 0.0
    interactions: int = 0
    created_at: float = field(default_factory=time.time)
    parent_id: Optional[str] = None
    is_champion: bool = False


@dataclass
class OptimizationResult:
    champion_id: str
    champion_fitness: float
    challenger_id: Optional[str]
    challenger_fitness: Optional[float]
    improvement: float
    generation: int
    timestamp: float = field(default_factory=time.time)


class AutoOptimizer:
    """Evolutionary optimizer for runtime AI parameters."""

    def __init__(self, explore_rate: float = 0.2, min_interactions_per_variant: int = 20, mutation_strength: float = 0.15):
        self.parameters: Dict[str, Dict] = {}
        self.champion: Optional[Variant] = None
        self.challengers: List[Variant] = []
        self.active_variant: Optional[Variant] = None
        self.generation: int = 0
        self.explore_rate = explore_rate
        self.min_interactions = min_interactions_per_variant
        self.mutation_strength = mutation_strength
        self.history: List[OptimizationResult] = []
        self.initial_fitness: Optional[float] = None

    def define_parameter(
        self,
        name: str,
        type: str = "float",
        min: float = None,
        max: float = None,
        current: Any = None,
        options: List = None,
    ):
        self.parameters[name] = {
            "type": type,
            "min": min,
            "max": max,
            "current": current,
            "options": options,
        }
        if self.champion is None:
            current_params = {k: v["current"] for k, v in self.parameters.items()}
            self.champion = Variant(id="initial", parameters=current_params, is_champion=True)
        else:
            # Keep champion in sync when new parameters are defined later.
            if name not in self.champion.parameters:
                self.champion.parameters[name] = current

    def get_params(self) -> Dict[str, Any]:
        if self.champion is None:
            return {}

        if random.random() < self.explore_rate:
            if not self.challengers or all(c.interactions >= self.min_interactions for c in self.challengers):
                challenger = self._create_challenger()
                self.challengers.append(challenger)
                self.active_variant = challenger
            else:
                undertested = [c for c in self.challengers if c.interactions < self.min_interactions]
                self.active_variant = random.choice(undertested)
        else:
            self.active_variant = self.champion
        return dict(self.active_variant.parameters)

    def report_fitness(self, score: float):
        if self.active_variant is None:
            return
        v = self.active_variant
        v.interactions += 1
        n = v.interactions
        v.fitness = (v.fitness * (n - 1) + score) / n

        if v.is_champion and self.initial_fitness is None and n >= self.min_interactions:
            self.initial_fitness = v.fitness
        self._maybe_promote()

    def _create_challenger(self) -> Variant:
        new_params = copy.deepcopy(self.champion.parameters)
        for name, spec in self.parameters.items():
            if random.random() > 0.5:
                continue
            if spec["type"] == "choice" and spec.get("options"):
                new_params[name] = random.choice(spec["options"])
            elif spec["type"] == "float" and spec.get("min") is not None:
                current = new_params.get(name, spec.get("current", 0.5))
                range_size = spec["max"] - spec["min"]
                mutation = random.gauss(0, range_size * self.mutation_strength)
                new_params[name] = round(max(spec["min"], min(spec["max"], current + mutation)), 4)
            elif spec["type"] == "int" and spec.get("min") is not None:
                current = new_params.get(name, spec.get("current", 100))
                range_size = spec["max"] - spec["min"]
                mutation = int(random.gauss(0, range_size * self.mutation_strength))
                new_params[name] = max(spec["min"], min(spec["max"], current + mutation))

        variant_id = hashlib.sha256(f"{time.time()}:{str(new_params)}".encode()).hexdigest()[:8]
        return Variant(id=f"gen{self.generation}_{variant_id}", parameters=new_params, parent_id=self.champion.id)

    def _maybe_promote(self):
        viable = [c for c in self.challengers if c.interactions >= self.min_interactions]
        if not viable:
            return
        if self.champion.interactions < self.min_interactions:
            return
        best = max(viable, key=lambda c: c.fitness)
        if best.fitness > self.champion.fitness:
            improvement = best.fitness - self.champion.fitness
            self.generation += 1
            old_champion = self.champion
            best.is_champion = True
            old_champion.is_champion = False
            self.champion = best
            self.challengers = [c for c in self.challengers if c.interactions < self.min_interactions]
            self.history.append(
                OptimizationResult(
                    champion_id=best.id,
                    champion_fitness=best.fitness,
                    challenger_id=old_champion.id,
                    challenger_fitness=old_champion.fitness,
                    improvement=improvement,
                    generation=self.generation,
                )
            )

    def improvement_so_far(self) -> Dict:
        if self.initial_fitness is None or self.champion is None:
            return {
                "status": "still_learning",
                "interactions": self.champion.interactions if self.champion else 0,
            }
        improvement = self.champion.fitness - self.initial_fitness
        improvement_pct = (improvement / max(0.001, self.initial_fitness)) * 100
        return {
            "initial_fitness": round(self.initial_fitness, 4),
            "current_fitness": round(self.champion.fitness, 4),
            "improvement": round(improvement, 4),
            "improvement_percentage": round(improvement_pct, 1),
            "generations": self.generation,
            "total_variants_tested": len(self.challengers) + self.generation + 1,
            "current_champion": self.champion.parameters,
        }

    def report(self) -> Dict:
        return {
            "generation": self.generation,
            "champion": {
                "id": self.champion.id if self.champion else None,
                "fitness": round(self.champion.fitness, 4) if self.champion else 0,
                "interactions": self.champion.interactions if self.champion else 0,
                "parameters": self.champion.parameters if self.champion else {},
            },
            "active_challengers": len(self.challengers),
            "improvement": self.improvement_so_far(),
            "history": [{"generation": h.generation, "improvement": round(h.improvement, 4)} for h in self.history],
        }
