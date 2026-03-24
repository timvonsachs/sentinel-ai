"""
Oracle Vision — The ability to simulate the future.

No biological organism can do this.
Humans guess. Animals react. Nobody SIMULATES.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
import statistics
import time


@dataclass
class FutureSimulation:
    """A simulated future outcome."""

    scenario: str
    parameters: Dict[str, Any]
    outcome: float  # fitness/quality score
    side_effects: List[str]
    confidence: float  # how reliable is this simulation
    timestamp: float = field(default_factory=time.time)


@dataclass
class FutureReport:
    simulations: List[FutureSimulation]
    change: Dict[str, Any]

    @property
    def expected(self) -> float:
        if not self.simulations:
            return 0
        return statistics.mean(s.outcome for s in self.simulations)

    @property
    def best_case(self) -> float:
        if not self.simulations:
            return 0
        return max(s.outcome for s in self.simulations)

    @property
    def worst_case(self) -> float:
        if not self.simulations:
            return 0
        return min(s.outcome for s in self.simulations)

    @property
    def risk(self) -> float:
        """Probability of negative outcome."""
        if not self.simulations:
            return 1.0
        negative = sum(1 for s in self.simulations if s.outcome < 0)
        return negative / len(self.simulations)

    @property
    def variance(self) -> float:
        if len(self.simulations) < 2:
            return 0
        return statistics.variance(s.outcome for s in self.simulations)


class OracleVision:
    """
    Future simulation for AI systems.
    """

    def __init__(self):
        self.simulator: Optional[Callable] = None
        self.simulation_history: List[Dict] = []
        self.accuracy_log: List[Dict] = []  # how accurate were past predictions

    def set_simulator(self, func: Callable):
        """
        Set the simulation function.
        func(parameters, scenario_id) -> {"outcome": float, "side_effects": [...]}
        """
        self.simulator = func

    def foresee(self, change: Dict[str, Any], scenarios: int = 10, context: Dict = None) -> FutureReport:
        """Simulate multiple futures with the proposed change."""
        if not self.simulator:
            return FutureReport(simulations=[], change=change)

        simulations = []
        for i in range(scenarios):
            try:
                params = {**change, "scenario_id": i, "context": context}
                result = self.simulator(params, i)

                sim = FutureSimulation(
                    scenario=f"scenario_{i}",
                    parameters=params,
                    outcome=result.get("outcome", 0),
                    side_effects=result.get("side_effects", []),
                    confidence=result.get("confidence", 0.5),
                )
                simulations.append(sim)
            except Exception:
                pass

        report = FutureReport(simulations=simulations, change=change)

        self.simulation_history.append(
            {
                "change": change,
                "scenarios": scenarios,
                "expected": report.expected,
                "risk": report.risk,
                "timestamp": time.time(),
            }
        )

        return report

    def validate(self, prediction_id: int, actual_outcome: float):
        """Record actual outcome for accuracy tracking."""
        if prediction_id < len(self.simulation_history):
            predicted = self.simulation_history[prediction_id]["expected"]
            error = abs(predicted - actual_outcome)
            self.accuracy_log.append(
                {
                    "predicted": predicted,
                    "actual": actual_outcome,
                    "error": error,
                    "timestamp": time.time(),
                }
            )

    def accuracy(self) -> float:
        """How accurate have our predictions been?"""
        if not self.accuracy_log:
            return 0.0
        errors = [a["error"] for a in self.accuracy_log]
        return max(0, 1 - statistics.mean(errors))
