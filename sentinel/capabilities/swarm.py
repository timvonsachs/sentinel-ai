"""
Swarm Intelligence — The Mycelium Network.

No single ant knows the way. The swarm finds it.
No single tree knows the threat. The mycelium warns all.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
import hashlib
import time


@dataclass
class SwarmSignal:
    """A message traveling through the swarm network."""

    type: str  # "alert", "immunity", "learning", "pattern"
    source_id: str  # which organism sent this
    data: Dict[str, Any]
    ttl: int = 3  # how many hops this signal can travel
    timestamp: float = field(default_factory=time.time)

    @property
    def id(self) -> str:
        raw = f"{self.source_id}:{self.type}:{self.timestamp}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]


class SwarmIntelligence:
    """
    Collective intelligence across multiple AI organisms.
    """

    def __init__(self, organism_id: str):
        self.organism_id = organism_id
        self.peers: Dict[str, "SwarmIntelligence"] = {}
        self.inbox: List[SwarmSignal] = []
        self.outbox: List[SwarmSignal] = []
        self.seen_signals: set = set()  # prevent loops
        self.shared_immunity: Dict[str, Dict] = {}
        self.collective_memory: List[Dict] = []

    def connect(self, peer: "SwarmIntelligence"):
        """Connect to another organism in the swarm."""
        self.peers[peer.organism_id] = peer
        peer.peers[self.organism_id] = self

    def broadcast(self, signal: SwarmSignal):
        """Broadcast a signal to all connected organisms."""
        if signal.id in self.seen_signals:
            return

        self.seen_signals.add(signal.id)
        self.outbox.append(signal)

        # Forward to peers
        if signal.ttl > 0:
            forwarded = SwarmSignal(
                type=signal.type,
                source_id=signal.source_id,
                data=signal.data,
                ttl=signal.ttl - 1,
                timestamp=signal.timestamp,
            )
            for peer in self.peers.values():
                if peer.organism_id != signal.source_id:
                    peer._receive_signal(forwarded)

    def _receive_signal(self, signal: SwarmSignal):
        """Receive a signal from the network."""
        if signal.id in self.seen_signals:
            return

        self.seen_signals.add(signal.id)
        self.inbox.append(signal)

        # Auto-process certain signal types
        if signal.type == "immunity":
            self.shared_immunity[signal.data.get("threat", "unknown")] = signal.data

        if signal.type == "learning":
            self.collective_memory.append(signal.data)

        # Forward if TTL allows
        if signal.ttl > 0:
            self.broadcast(signal)

    def receive(self, type: str = None) -> List[SwarmSignal]:
        """Get received signals, optionally filtered by type."""
        if type:
            return [s for s in self.inbox if s.type == type]
        return list(self.inbox)

    def share_immunity(self, threat: str, pattern: Dict, fix: Dict = None):
        """Share an immunity (learned defense) with the swarm."""
        self.broadcast(
            SwarmSignal(
                type="immunity",
                source_id=self.organism_id,
                data={"threat": threat, "pattern": pattern, "fix": fix},
            )
        )

    def share_learning(self, topic: str, data: Dict):
        """Share a learning with the swarm."""
        self.broadcast(
            SwarmSignal(type="learning", source_id=self.organism_id, data={"topic": topic, **data})
        )

    def collective_health(self) -> Dict:
        """Get health status across the entire swarm."""
        health = {"self": self.organism_id, "peers": {}}

        for peer_id, peer in self.peers.items():
            recent_alerts = [
                s for s in peer.outbox if s.type == "alert" and time.time() - s.timestamp < 3600
            ]
            health["peers"][peer_id] = {
                "recent_alerts": len(recent_alerts),
                "connected": True,
            }

        health["swarm_size"] = len(self.peers) + 1
        health["shared_immunities"] = len(self.shared_immunity)
        health["collective_learnings"] = len(self.collective_memory)
        return health
