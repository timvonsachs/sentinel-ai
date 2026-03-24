"""
Telepathy — Direct experience transfer between organisms.

No biological creature can do this.
You can't copy your memories into another brain.
But AI can. Instantly. Losslessly.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import copy
import time


@dataclass
class ExperiencePacket:
    """A transferable unit of experience."""

    source: str
    domain: str  # "sales", "support", "coding", etc.
    insight: str  # human-readable
    data: Dict[str, Any]  # machine-readable
    confidence: float  # how reliable is this insight
    transfers: int = 0  # how many times has this been transferred
    timestamp: float = field(default_factory=time.time)


class TelepathyBridge:
    """
    Direct experience transfer between AI organisms.
    """

    def __init__(self, organism_id: str):
        self.organism_id = organism_id
        self.experiences: List[ExperiencePacket] = []
        self.received: List[ExperiencePacket] = []

    def encode_experience(self, domain: str, insight: str, data: Dict[str, Any], confidence: float = 0.8):
        """Encode a new experience for potential transfer."""
        packet = ExperiencePacket(
            source=self.organism_id,
            domain=domain,
            insight=insight,
            data=data,
            confidence=confidence,
        )
        self.experiences.append(packet)
        return packet

    def transfer_to(self, target: "TelepathyBridge", domain: str = None, min_confidence: float = 0.5):
        """Transfer experiences to another organism."""
        to_transfer = self.experiences
        if domain:
            to_transfer = [e for e in to_transfer if e.domain == domain]
        to_transfer = [e for e in to_transfer if e.confidence >= min_confidence]

        for exp in to_transfer:
            transferred = copy.deepcopy(exp)
            transferred.transfers += 1
            # Confidence degrades slightly with each transfer
            transferred.confidence *= 0.95
            target.received.append(transferred)

    def recall(self, domain: str = None, min_confidence: float = 0) -> List[ExperiencePacket]:
        """Recall experiences (own + received)."""
        all_exp = self.experiences + self.received
        if domain:
            all_exp = [e for e in all_exp if e.domain == domain]
        all_exp = [e for e in all_exp if e.confidence >= min_confidence]
        all_exp.sort(key=lambda e: e.confidence, reverse=True)
        return all_exp

    def best_insight(self, domain: str) -> Optional[ExperiencePacket]:
        """Get the highest-confidence insight for a domain."""
        relevant = self.recall(domain)
        return relevant[0] if relevant else None

    def knowledge_base(self) -> Dict:
        """Summary of all knowledge (own + received)."""
        all_exp = self.experiences + self.received
        domains = {}
        for exp in all_exp:
            if exp.domain not in domains:
                domains[exp.domain] = {"count": 0, "avg_confidence": 0, "insights": []}
            domains[exp.domain]["count"] += 1
            domains[exp.domain]["insights"].append(exp.insight)

        for domain in domains:
            relevant = [e for e in all_exp if e.domain == domain]
            domains[domain]["avg_confidence"] = (
                sum(e.confidence for e in relevant) / len(relevant) if relevant else 0
            )

        return {
            "organism": self.organism_id,
            "own_experiences": len(self.experiences),
            "received_experiences": len(self.received),
            "domains": domains,
        }
