"""
The Organism — A complete, deeply integrated living AI system.

V3: Event Bus, State Machine, Persistence, Correlation Engine.
"""

from typing import Optional, Dict, Any
from .core.event_bus import EventBus, Event
from .core.state_machine import OrganismStateMachine, OrganismState
from .core.persistence import PersistenceLayer
from .core.correlation import CorrelationEngine
from .systems.immune import ImmuneSystem
from .systems.nervous import NervousSystem
from .systems.endocrine import EndocrineSystem
from .systems.memory import MemorySystem
from .systems.pain import PainSense
from .systems.skin import Skin
from .systems.lymph import LymphaticSystem
from .systems.circulatory import CirculatorySystem
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
from .performance.trust_score import TrustScoreEngine
from .performance.smart_router import SmartRouter
from .performance.experience_engine import ExperienceEngine
from .performance.collective_intelligence import CollectiveIntelligence
from .performance.auto_optimize import AutoOptimizer
from .core.types import HealthStatus, HealthReport
import json
import time


class Organism:
    """A complete living AI system with deep integration."""

    def __init__(self, name: str = "unnamed", autonomous: bool = False, persist_path: str = None):
        self.name = name
        self.autonomous = autonomous
        self.born_at = time.time()

        # Core infrastructure
        self.bus = EventBus()
        self.state_machine = OrganismStateMachine()
        self.persistence = PersistenceLayer(persist_path or f"./sentinel_state/{name}")
        self.correlation = CorrelationEngine()
        self._plugins: Dict[str, Any] = {}

        # Biological systems
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

        # Animal capabilities
        self.octopus = OctopusIntelligence()
        self.chameleon = ChameleonAdaptation()
        self.tardigrade = TardigradeHibernation()
        self.salamander = SalamanderRegeneration()
        self.swarm = SwarmIntelligence(name)

        # Transcendence
        self.oracle = OracleVision()
        self.telepathy = TelepathyBridge(name)
        self.phoenix = PhoenixMetamorphosis()
        self.immortal = ImmortalEvolution()

        # Performance layer
        self.trust = TrustScoreEngine()
        self.router = SmartRouter()
        self.experience = ExperienceEngine()
        self.collective = CollectiveIntelligence(name)
        self.optimizer = AutoOptimizer()

        self._setup_defaults()
        self._wire_event_bus()
        self._load_state()

    def _setup_defaults(self):
        self.endocrine.add_hormone("cortisol", base=0.3, min=0.0, max=1.0, speed=0.05)
        self.endocrine.add_hormone("creativity", base=0.7, min=0.1, max=1.0, speed=0.03)
        self.endocrine.add_hormone("caution", base=0.3, min=0.0, max=1.0, speed=0.04)
        self.endocrine.add_hormone("vigilance", base=0.5, min=0.1, max=1.0, speed=0.06)

        self.endocrine.regulate("cortisol", lambda ctx: ctx.get("pain", 0) * 1.5 if ctx else 0)
        self.endocrine.regulate("creativity", lambda ctx: -ctx.get("pain", 0) * 1.2 if ctx else 0)
        self.endocrine.regulate("caution", lambda ctx: ctx.get("pain", 0) * 0.8 if ctx else 0)
        self.endocrine.regulate("vigilance", lambda ctx: ctx.get("threat_level", 0) if ctx else 0)

        self.tardigrade.hibernate_when(lambda org: org.pain > 0.85, reason="Pain critical — entering safe mode")

    def _wire_event_bus(self):
        def immune_to_endocrine(event: Event):
            z = abs(event.data.get("z_score", 0))
            if z > 1.5:
                self.endocrine.update({"pain": self.pain, "threat_level": z / 3.0})

        def immune_to_memory(event: Event):
            if event.severity >= 2:
                self.memory.remember(f"immune_{event.type}", event.data, tags=["immune", "auto"])

        def skin_to_endocrine(event: Event):
            if event.data.get("blocked"):
                self.endocrine.update({"threat_level": 0.8})

        def skin_to_memory(event: Event):
            self.memory.remember("attack", event.data, tags=["security"])

        def state_to_memory(event: Event):
            self.memory.remember("state_change", event.data, tags=["lifecycle"])

        def critical_to_respiratory(event: Event):
            if event.severity >= 3:
                self.respiratory.breathe(pain=self.pain, load=0.8, urgency=0.9)

        self.bus.on("immune.*", immune_to_endocrine)
        self.bus.on("immune.*", immune_to_memory)
        self.bus.on("skin.*", skin_to_endocrine)
        self.bus.on("skin.blocked", skin_to_memory)
        self.bus.on("organism.state_change", state_to_memory)
        self.bus.on("*.critical", critical_to_respiratory)

    def _load_state(self):
        if self.persistence.exists():
            state = self.persistence.load()
            if state:
                self._restore_state(state)
                self.bus.emit(
                    Event(type="organism.restored", source="persistence", data={"age": self.persistence.age()}, severity=0)
                )

    def _restore_state(self, state: Dict):
        _ = state
        baselines = self.persistence.load_baselines()
        if baselines:
            from .core.ewma import EWMABaseline

            for metric, bl_data in baselines.items():
                bl = EWMABaseline(lambda_=bl_data.get("lambda", 0.1))
                bl.mean = bl_data.get("mean")
                bl.variance = bl_data.get("variance", 0.0001)
                bl.count = bl_data.get("count", 0)
                self.immune.baselines[metric] = bl

        memories = self.persistence.load_memories()
        if memories:
            from .systems.memory import Experience

            for m in memories:
                self.memory.experiences.append(
                    Experience(
                        event=m["event"],
                        context=m.get("context", {}),
                        outcome=m.get("outcome"),
                        fix=m.get("fix"),
                        timestamp=m.get("timestamp", 0),
                        tags=m.get("tags", []),
                    )
                )

    @property
    def alive(self) -> bool:
        return not self.tardigrade.is_hibernating and self.state_machine.current != OrganismState.DEAD

    @property
    def state(self) -> str:
        return self.state_machine.current.value

    @property
    def status(self) -> str:
        """Backward-compatible health status view."""
        if self.tardigrade.is_hibernating:
            return "hibernating"
        return self.immune.health().status.value

    @property
    def pain(self) -> float:
        return self.pain_sense.score(self)

    @property
    def feeling(self) -> str:
        return self.pain_sense.feeling(self)

    @property
    def diagnosis(self) -> list:
        if not self.immune.baselines:
            return []
        current_z = {}
        trends = {}
        for metric, bl in self.immune.baselines.items():
            if bl.history:
                current_z[metric] = bl.history[-1].z_score
                trends[metric] = self.correlation.get_trend(metric) or "stable"
        return self.correlation.diagnose(current_z, trends)

    @property
    def early_warnings(self) -> Dict:
        warnings = {}
        for metric, bl in self.immune.baselines.items():
            csd = bl.critical_slowing_down()
            if csd and csd["phase_transition_risk"] in ("high", "critical"):
                warnings[metric] = csd
        return warnings

    @property
    def confidence(self) -> float:
        if not self.immune.baselines:
            return 0
        confs = [bl.confidence for bl in self.immune.baselines.values()]
        return sum(confs) / len(confs)

    @property
    def age(self) -> float:
        return time.time() - self.born_at

    def observe(self, metric: str, value: float):
        if self.tardigrade.is_hibernating:
            self.bus.emit(
                Event(
                    type="organism.rejected",
                    source="tardigrade",
                    data={"reason": "hibernating", "metric": metric},
                    severity=1,
                )
            )
            return None

        obs = self.immune.observe(metric, value)
        health = self.immune.health(metric)

        severity = 0
        if health.status == HealthStatus.CRITICAL:
            severity = 3
        elif health.status == HealthStatus.WARNING:
            severity = 2
        elif health.status == HealthStatus.WATCH:
            severity = 1

        self.bus.emit(
            Event(
                type="immune.observation",
                source="immune",
                data={
                    "metric": metric,
                    "value": value,
                    "z_score": obs.z_score,
                    "baseline": obs.baseline,
                    "status": health.status.value,
                    "pain": health.pain_score,
                },
                severity=severity,
            )
        )

        if severity >= 2:
            self.bus.emit(
                Event(
                    type="immune.drift",
                    source="immune",
                    data={"metric": metric, "z_score": obs.z_score, "status": health.status.value},
                    severity=severity,
                )
            )

        self.correlation.update_single(metric, obs.z_score)
        p = self.pain
        self.endocrine.update({"pain": p, "threat_level": severity / 4.0})
        self.respiratory.breathe(pain=p, load=severity / 4.0)

        healing_active = False
        if self.immune.healing_log:
            healing_active = any(h.success for h in self.immune.healing_log[-3:])

        old_state = self.state_machine.current
        new_state = self.state_machine.evaluate(
            pain=p,
            confidence=self.confidence,
            healing_active=healing_active,
            wake_signal=False,
        )
        if new_state != old_state:
            self.bus.emit(
                Event(
                    type="organism.state_change",
                    source="state_machine",
                    data={"from": old_state.value, "to": new_state.value, "pain": p},
                    severity=2 if new_state in (OrganismState.SICK, OrganismState.HIBERNATING) else 1,
                )
            )

        if self.tardigrade.should_hibernate(self):
            self.tardigrade.enter(self)
            self.state_machine.force(OrganismState.HIBERNATING, "Pain threshold exceeded")
            self.bus.emit(
                Event(
                    type="organism.hibernation",
                    source="tardigrade",
                    data={"pain": p, "reason": "critical_pain"},
                    severity=4,
                )
            )
            self.save()
            return obs

        if self.autonomous and severity >= 2:
            self._auto_heal(metric, health, obs)

        if self.persistence.tick():
            self.save()

        return obs

    def process_input(self, input_text: str) -> Dict:
        skin_result = self.skin.check(input_text)
        if not skin_result.safe:
            self.bus.emit(
                Event(
                    type="skin.blocked",
                    source="skin",
                    data={"threats": [t.type for t in skin_result.threats], "blocked": True},
                    severity=2,
                )
            )
            return {
                "safe": False,
                "blocked_by": "skin",
                "threats": [t.type for t in skin_result.threats],
            }

        digested = self.digestive.digest(input_text)
        if not digested.safe:
            self.bus.emit(
                Event(
                    type="digestive.rejected",
                    source="digestive",
                    data={"quality": digested.quality_score},
                    severity=1,
                )
            )
            return {
                "safe": False,
                "blocked_by": "digestive",
                "quality": digested.quality_score,
            }

        self.bus.emit(
            Event(
                type="input.processed",
                source="digestive",
                data={"quality": digested.quality_score},
                severity=0,
            )
        )

        return {
            "safe": True,
            "processed": digested.processed,
            "quality": digested.quality_score,
            "nutrition": digested.nutrition,
        }

    def process_output(self, output_text: str, metadata: Dict = None):
        self.lymph.process_output(output_text, metadata)
        scan = self.lymph.scan()
        if scan.get("contamination_score", 0) > 0.5:
            self.bus.emit(Event(type="lymph.contamination", source="lymph", data=scan, severity=2))

    def signal(self, metrics: Dict):
        triggered = self.nervous.signal(metrics)
        for reflex_name in triggered:
            self.bus.emit(
                Event(
                    type="nervous.reflex",
                    source="nervous",
                    data={"reflex": reflex_name, "metrics": metrics},
                    severity=2,
                )
            )
        return triggered

    def _auto_heal(self, metric: str, health: HealthReport, obs):
        similar = self.memory.recall("drift", context={"metric": metric})
        fix_applied = None
        if similar and similar[0].fix:
            fix_applied = similar[0].fix

        diag = self.diagnosis
        if diag:
            best = diag[0]
            if best.syndrome.recommended_action:
                fix_applied = best.syndrome.recommended_action

        self.memory.remember(
            "drift",
            {
                "metric": metric,
                "z_score": obs.z_score,
                "status": health.status.value,
                "diagnosis": diag[0].syndrome.name if diag else None,
                "fix_applied": fix_applied,
            },
            tags=["drift", "auto_heal"],
        )

        self.bus.emit(
            Event(
                type="immune.healing",
                source="immune",
                data={
                    "metric": metric,
                    "fix": fix_applied,
                    "based_on_memory": bool(similar),
                    "diagnosis": diag[0].syndrome.name if diag else None,
                },
                severity=2,
            )
        )

    def install(self, name: str, plugin: Any):
        self._plugins[name] = plugin
        setattr(self, name, plugin)
        if hasattr(plugin, "attach"):
            plugin.attach(self)
        self.bus.emit(Event(type="organism.plugin_installed", source="organism", data={"plugin": name}, severity=0))

    @property
    def plugins(self) -> Dict:
        return dict(self._plugins)

    def save(self, path: Optional[str] = None) -> bool:
        """Save complete organism state or write report to path (compat)."""
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.report(), f, indent=2, default=str)
            return True

        self.persistence.save_baselines(self.immune.baselines)
        self.persistence.save_memories(self.memory.experiences)
        return self.persistence.save(
            {
                "name": self.name,
                "born_at": self.born_at,
                "state": self.state,
                "endocrine": self.endocrine.state(),
                "respiratory_mode": self.respiratory.current_mode,
                "skin_threats": self.skin.threat_summary(),
                "saved_at": time.time(),
            }
        )

    def report(self) -> Dict:
        return {
            "name": self.name,
            "alive": self.alive,
            "state": self.state,
            "status": self.status,
            "state_duration": self.state_machine.duration,
            "pain": self.pain,
            "feeling": self.feeling,
            "confidence": self.confidence,
            "age_seconds": self.age,
            "diagnosis": [
                {"syndrome": d.syndrome.name, "score": d.match_score, "action": d.syndrome.recommended_action}
                for d in self.diagnosis
            ],
            "early_warnings": self.early_warnings,
            "systems": {
                "immune": {m: self.immune.health(m).metrics for m in self.immune.baselines},
                "endocrine": self.endocrine.state(),
                "respiratory": self.respiratory.stats(),
                "lymph": self.lymph.scan() if self.lymph.output_history else {},
                "skin": self.skin.threat_summary(),
                "memory": {
                    "experiences": len(self.memory.experiences),
                    "last_event": self.memory.last().event if self.memory.last() else None,
                },
                "nervous": {
                    "reflexes": len(self.nervous.reflexes),
                    "triggers": sum(r.trigger_count for r in self.nervous.reflexes),
                },
                "correlation": {
                    "metrics_tracked": len(self.correlation.metric_data),
                    "syndromes_defined": len(self.correlation.syndromes),
                },
            },
            "capabilities": {
                "octopus_tentacles": len(self.octopus.tentacles),
                "swarm_peers": len(self.swarm.peers),
                "phoenix_form": self.phoenix.current_form,
                "immortal_generation": self.immortal.generation_count,
                "plugins": list(self._plugins.keys()),
            },
            "performance": {
                "trust": self.trust.report(),
                "router": self.router.cost_report(),
                "experience": self.experience.report(),
                "collective": self.collective.report(),
                "optimizer": self.optimizer.report(),
            },
            "event_bus": self.bus.stats(),
        }

    def __repr__(self):
        return f"Organism('{self.name}', state={self.state}, alive={self.alive}, pain={self.pain:.2f})"
