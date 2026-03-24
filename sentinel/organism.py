"""
The Organism — A complete living AI system.

11 biological systems. 5 animal capabilities. 4 transcendent abilities.
Your AI has a brain. We give it a body. And more.
"""

from typing import Dict
from .systems.immune import ImmuneSystem
from .systems.nervous import NervousSystem
from .systems.endocrine import EndocrineSystem
from .systems.memory import MemorySystem
from .systems.pain import PainSense
from .systems.skin import Skin
from .systems.lymph import LymphaticSystem
from .systems.circulatory import CirculatorySystem, StatePacket
from .systems.digestive import DigestiveSystem
from .systems.respiratory import RespiratorySystem
from .systems.reproductive import ReproductiveSystem
from .capabilities.octopus import OctopusIntelligence
from .capabilities.chameleon import ChameleonAdaptation
from .capabilities.tardigrade import TardigradeHibernation
from .capabilities.salamander import SalamanderRegeneration
from .capabilities.swarm import SwarmIntelligence
from .transcendence.oracle import OracleVision
from .transcendence.telepathy import TelepathyBridge
from .transcendence.phoenix import PhoenixMetamorphosis
from .transcendence.immortal import ImmortalEvolution
from .core.types import HealthStatus, HealthReport
import json
import time


class Organism:
    """
    A complete living AI system.

    Born from NOVA — a bipolar early warning system.
    The algorithm that monitors a human mind,
    now giving every AI a body, instincts, and abilities
    that no biological organism has ever possessed.
    """

    def __init__(self, name: str = "unnamed", autonomous: bool = False):
        self.name = name
        self.autonomous = autonomous
        self.born_at = time.time()

        # BIOLOGICAL SYSTEMS (11)
        self.immune = ImmuneSystem()
        self.nervous = NervousSystem()
        self.endocrine = EndocrineSystem()
        self.memory = MemorySystem()
        self.pain_sense = PainSense()
        self.skin = Skin()
        self.lymph = LymphaticSystem()
        self.circulatory = CirculatorySystem()
        self.digestive = DigestiveSystem()
        self.respiratory = RespiratorySystem()
        self.reproductive = ReproductiveSystem()

        # ANIMAL CAPABILITIES (5)
        self.octopus = OctopusIntelligence()
        self.chameleon = ChameleonAdaptation()
        self.tardigrade = TardigradeHibernation()
        self.salamander = SalamanderRegeneration()
        self.swarm = SwarmIntelligence(name)

        # TRANSCENDENCE (4)
        self.oracle = OracleVision()
        self.telepathy = TelepathyBridge(name)
        self.phoenix = PhoenixMetamorphosis()
        self.immortal = ImmortalEvolution()

        self._setup_defaults()

    def _setup_defaults(self):
        """Set up default hormone connections and reflexes."""
        # Hormones
        self.endocrine.add_hormone("cortisol", base=0.3, min=0.0, max=1.0)
        self.endocrine.add_hormone("creativity", base=0.7, min=0.1, max=1.0)
        self.endocrine.add_hormone("caution", base=0.3, min=0.0, max=1.0)

        # Connect cortisol to pain
        self.endocrine.regulate("cortisol", lambda ctx: ctx.get("pain", 0) if ctx else 0)
        self.endocrine.regulate("creativity", lambda ctx: -ctx.get("pain", 0) if ctx else 0)
        self.endocrine.regulate("caution", lambda ctx: ctx.get("pain", 0) * 0.5 if ctx else 0)

        # Tardigrade: hibernate when critically ill
        self.tardigrade.hibernate_when(
            lambda org: org.pain > 0.85,
            reason="Pain score critical — entering safe mode",
        )

    @property
    def alive(self) -> bool:
        """Is this organism alive (not hibernating, not dead)?"""
        return not self.tardigrade.is_hibernating

    @property
    def pain(self) -> float:
        """Current pain score: 0.0 (perfect) to 1.0 (critical)."""
        return self.pain_sense.score(self)

    @property
    def feeling(self) -> str:
        """Human-readable health description."""
        return self.pain_sense.feeling(self)

    @property
    def status(self) -> str:
        """Overall health status."""
        if self.tardigrade.is_hibernating:
            return "hibernating"
        health = self.immune.health()
        return health.status.value

    @property
    def age(self) -> float:
        """Age in seconds since creation."""
        return time.time() - self.born_at

    def observe(self, metric: str, value: float):
        """Observe a metric. The full organism responds."""
        # Tardigrade check: if hibernating, don't process
        if self.tardigrade.is_hibernating:
            return None

        # Immune system: baseline + drift detection
        obs = self.immune.observe(metric, value)

        # Pain update
        p = self.pain

        # Endocrine: adjust hormones based on pain
        self.endocrine.update({"pain": p})

        # Respiratory: adjust compute budget based on pain
        self.respiratory.breathe(pain=p)

        # Circulatory: pump state to all systems
        self.circulatory.pump(
            StatePacket(
                source="immune",
                type="observation",
                data={"metric": metric, "z_score": obs.z_score, "pain": p},
                priority=2 if abs(obs.z_score) > 2 else 0,
            )
        )

        # Tardigrade: check if we should hibernate
        if self.tardigrade.should_hibernate(self):
            self.tardigrade.enter(self)
            self.memory.remember(
                "hibernation",
                {"metric": metric, "pain": p, "reason": "Pain threshold exceeded"},
            )
            return obs

        # Autonomous healing
        if self.autonomous:
            health = self.immune.health(metric)
            if health.status in (HealthStatus.WARNING, HealthStatus.CRITICAL):
                self._auto_heal(metric, health)

        return obs

    def process_input(self, input_text: str) -> dict:
        """Full input pipeline: skin -> digestive -> processed."""
        # Skin: safety check
        skin_result = self.skin.check(input_text)
        if not skin_result.safe:
            return {
                "safe": False,
                "blocked_by": "skin",
                "threats": [t.type for t in skin_result.threats],
            }

        # Digestive: quality + enrichment
        digested = self.digestive.digest(input_text)
        if not digested.safe:
            return {
                "safe": False,
                "blocked_by": "digestive",
                "quality": digested.quality_score,
            }

        return {
            "safe": True,
            "processed": digested.processed,
            "quality": digested.quality_score,
            "nutrition": digested.nutrition,
        }

    def process_output(self, output_text: str, metadata: dict = None):
        """Monitor AI output through lymphatic system."""
        self.lymph.process_output(output_text, metadata)

    def signal(self, metrics: dict):
        """Real-time nervous system signals."""
        return self.nervous.signal(metrics)

    def _auto_heal(self, metric: str, health: HealthReport):
        """Orchestrated autonomous healing."""
        # Memory: have we seen this before?
        similar = self.memory.recall("drift", context={"metric": metric})

        if similar and similar[0].fix:
            self.memory.remember(
                "auto_heal",
                {
                    "metric": metric,
                    "applied_fix": similar[0].fix,
                    "based_on": similar[0].timestamp,
                },
            )

        # Record for future memory
        self.memory.remember(
            "drift",
            {
                "metric": metric,
                "z_score": health.metrics.get("z_score"),
                "status": health.status.value,
            },
        )

    def report(self) -> dict:
        """Full organism status report."""
        return {
            "name": self.name,
            "alive": self.alive,
            "status": self.status,
            "pain": self.pain,
            "feeling": self.feeling,
            "age_seconds": self.age,
            "systems": {
                "immune": {m: self.immune.health(m).metrics for m in self.immune.baselines},
                "endocrine": self.endocrine.state(),
                "respiratory": self.respiratory.stats(),
                "lymph": self.lymph.scan(),
                "skin": self.skin.threat_summary(),
                "memory": {
                    "experiences": len(self.memory.experiences),
                    "last_event": self.memory.last().event if self.memory.last() else None,
                },
                "nervous": {
                    "reflexes": len(self.nervous.reflexes),
                    "triggers": sum(r.trigger_count for r in self.nervous.reflexes),
                },
            },
            "capabilities": {
                "octopus": len(self.octopus.tentacles),
                "swarm_peers": len(self.swarm.peers),
                "phoenix_form": self.phoenix.current_form,
                "immortal_generation": self.immortal.generation_count,
            },
        }

    def save(self, path: str = None):
        """Save organism state."""
        path = path or f"{self.name}_organism.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.report(), f, indent=2, default=str)

    def __repr__(self):
        return f"Organism('{self.name}', alive={self.alive}, status={self.status}, pain={self.pain:.2f})"
