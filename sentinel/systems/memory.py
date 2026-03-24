"""
Memory — The AI remembers its own history.

Not conversation memory. EXPERIENTIAL memory.
"Last time I drifted like this, the cause was X and the fix was Y."
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import time


@dataclass
class Experience:
    event: str
    context: Dict[str, Any]
    outcome: Optional[str] = None
    fix: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)


class MemorySystem:
    """
    Experiential memory for AI systems.

    Usage:
        memory = MemorySystem()
        memory.remember("drift_event", {
            "metric": "conversion",
            "cause": "model_update",
            "z_score": -2.1,
            "fix": "revert_prompt_v3"
        })

        # Later, when similar drift occurs:
        similar = memory.recall("drift_event",
                               context={"metric": "conversion"})
        # Returns the previous experience with fix
    """

    def __init__(self, max_memories: int = 10000):
        self.experiences: List[Experience] = []
        self.max_memories = max_memories

    def remember(
        self,
        event: str,
        context: Dict[str, Any],
        outcome: str = None,
        fix: str = None,
        tags: List[str] = None,
    ):
        exp = Experience(event=event, context=context, outcome=outcome, fix=fix, tags=tags or [])
        self.experiences.append(exp)

        if len(self.experiences) > self.max_memories:
            self.experiences = self.experiences[-self.max_memories :]

    def recall(
        self,
        event: str = None,
        context: Dict[str, Any] = None,
        tags: List[str] = None,
        limit: int = 5,
    ) -> List[Experience]:
        """Recall similar experiences."""
        results = self.experiences.copy()

        if event:
            results = [e for e in results if e.event == event]

        if tags:
            results = [e for e in results if any(t in e.tags for t in tags)]

        if context:
            # Score by context similarity
            def similarity(exp):
                common = set(exp.context.keys()) & set(context.keys())
                if not common:
                    return 0
                matches = sum(1 for k in common if exp.context[k] == context[k])
                return matches / len(common)

            results.sort(key=similarity, reverse=True)

        return results[:limit]

    def has_seen(self, event: str) -> bool:
        return any(e.event == event for e in self.experiences)

    def last(self, event: str = None) -> Optional[Experience]:
        if event:
            matching = [e for e in self.experiences if e.event == event]
            return matching[-1] if matching else None
        return self.experiences[-1] if self.experiences else None
