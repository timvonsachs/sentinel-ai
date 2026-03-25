"""
Collective Intelligence — share validated learnings across agents.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time


@dataclass
class CollectiveLearning:
    source_agent: str
    category: str
    insight: str
    data: Dict[str, Any]
    effectiveness: float
    adopted_by: List[str] = field(default_factory=list)
    times_validated: int = 0
    times_contradicted: int = 0
    created_at: float = field(default_factory=time.time)


class CollectiveIntelligence:
    """Collective knowledge base with validation loops."""

    def __init__(self, collective_name: str):
        self.name = collective_name
        self.members: List[str] = []
        self.learnings: List[CollectiveLearning] = []
        self.learning_index: Dict[str, List[int]] = {}

    def join(self, agent_id: str):
        if agent_id not in self.members:
            self.members.append(agent_id)

    def leave(self, agent_id: str):
        self.members = [m for m in self.members if m != agent_id]

    def share_learning(self, source: str, category: str, insight: str, data: Dict[str, Any], effectiveness: float = 0.5) -> int:
        learning = CollectiveLearning(
            source_agent=source,
            category=category,
            insight=insight,
            data=data,
            effectiveness=effectiveness,
        )
        idx = len(self.learnings)
        self.learnings.append(learning)
        if category not in self.learning_index:
            self.learning_index[category] = []
        self.learning_index[category].append(idx)
        return idx

    def get_knowledge(self, category: str = None, min_effectiveness: float = 0.3, min_validations: int = 0) -> List[CollectiveLearning]:
        if category:
            indices = self.learning_index.get(category, [])
            results = [self.learnings[i] for i in indices]
        else:
            results = list(self.learnings)
        results = [l for l in results if l.effectiveness >= min_effectiveness]
        if min_validations > 0:
            results = [l for l in results if l.times_validated >= min_validations]

        def sort_key(l: CollectiveLearning):
            validation_score = l.times_validated / max(1, l.times_validated + l.times_contradicted)
            return l.effectiveness * (0.5 + 0.5 * validation_score)

        results.sort(key=sort_key, reverse=True)
        return results

    def validate(self, agent_id: str, learning_index: int):
        if 0 <= learning_index < len(self.learnings):
            learning = self.learnings[learning_index]
            learning.times_validated += 1
            if agent_id not in learning.adopted_by:
                learning.adopted_by.append(agent_id)

    def contradict(self, agent_id: str, learning_index: int):
        _ = agent_id
        if 0 <= learning_index < len(self.learnings):
            learning = self.learnings[learning_index]
            learning.times_contradicted += 1
            total = learning.times_validated + learning.times_contradicted
            if total > 0:
                learning.effectiveness *= learning.times_validated / total

    def best_practice(self, category: str) -> Optional[CollectiveLearning]:
        knowledge = self.get_knowledge(category=category, min_validations=1)
        return knowledge[0] if knowledge else None

    def adoption_rate(self, learning_index: int) -> float:
        if not self.members or learning_index >= len(self.learnings):
            return 0.0
        return len(self.learnings[learning_index].adopted_by) / len(self.members)

    def report(self) -> Dict:
        return {
            "name": self.name,
            "members": len(self.members),
            "total_learnings": len(self.learnings),
            "categories": list(self.learning_index.keys()),
            "avg_effectiveness": round(sum(l.effectiveness for l in self.learnings) / max(1, len(self.learnings)), 3),
            "most_validated": max(self.learnings, key=lambda l: l.times_validated).insight if self.learnings else None,
            "adoption_rates": {l.insight[:50]: self.adoption_rate(i) for i, l in enumerate(self.learnings[:10])},
        }
