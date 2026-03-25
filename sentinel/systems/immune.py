"""
The Immune System — Drift Detection + Self-Healing.

Born in a psychiatric clinic. Tested on a human mind.
Now protecting every AI system on the planet.
"""

from typing import Dict, List, Callable, Optional
from ..core.ewma import EWMABaseline, Observation
from ..core.detection import DetectionEngine, Alert
from ..core.types import HealthStatus, HealthReport, HealingAction
import time


class ImmuneSystem:
    """
    The first biological system for AI.

    Usage:
        immune = ImmuneSystem()
        immune.observe("conversion_rate", 0.34)
        health = immune.health("conversion_rate")

        # Self-healing
        immune.on_warning("conversion_rate", switch_to_safe_prompt)
        immune.on_critical("conversion_rate", escalate_to_human)
    """

    def __init__(self, **kwargs):
        self.baselines: Dict[str, EWMABaseline] = {}
        self.detector = DetectionEngine(**kwargs)
        self.healers: Dict[str, Dict[str, List[Callable]]] = {}
        self.healing_log: List[HealingAction] = []
        self.active = True
        self.last_diagnosis: Dict[str, Dict] = {}

    def observe(self, metric: str, value: float) -> Observation:
        """Observe a metric. Build baseline. Detect drift. Heal if needed."""
        if metric not in self.baselines:
            self.baselines[metric] = EWMABaseline()

        obs = self.baselines[metric].observe(value)

        # Check for alerts
        alerts = self.detector.check(metric, self.baselines[metric].history)

        # Auto-heal if handlers registered
        for alert in alerts:
            self._try_heal(metric, alert)

        self.last_diagnosis[metric] = self.diagnose(metric)

        return obs

    def diagnose(self, metric: str) -> Dict:
        """Lightweight diagnostic summary for a metric."""
        if metric not in self.baselines or not self.baselines[metric].history:
            return {"metric": metric, "status": "unknown", "signals": []}
        bl = self.baselines[metric]
        latest = bl.history[-1]
        alerts = self.detector.check(metric, bl.history)
        csd = bl.critical_slowing_down()
        return {
            "metric": metric,
            "phase": bl.phase,
            "confidence": bl.confidence,
            "latest_z": latest.z_score,
            "alerts": [a.type for a in alerts],
            "phase_transition_risk": (csd or {}).get("phase_transition_risk"),
        }

    def health(self, metric: Optional[str] = None) -> HealthReport:
        """Get health status for a metric or the entire system."""
        if metric:
            return self._metric_health(metric)
        return self._system_health()

    def _metric_health(self, metric: str) -> HealthReport:
        if metric not in self.baselines:
            return HealthReport(HealthStatus.LEARNING, 0.0, f"Unknown metric: {metric}")

        bl = self.baselines[metric]
        if bl.phase == "learning":
            return HealthReport(
                HealthStatus.LEARNING,
                0.0,
                f"Building baseline ({bl.count}/7)",
                {"confidence": bl.confidence},
            )

        alerts = self.detector.check(metric, bl.history)
        latest_z = bl.history[-1].z_score if bl.history else 0

        if any(a.severity == "critical" for a in alerts):
            status = HealthStatus.CRITICAL
        elif any(a.severity == "warning" for a in alerts):
            status = HealthStatus.WARNING
        elif abs(latest_z) > 1.0:
            status = HealthStatus.WATCH
        elif latest_z < -0.5:
            status = HealthStatus.THRIVING
        else:
            status = HealthStatus.HEALTHY

        pain = min(1.0, abs(latest_z) / 3.0)

        return HealthReport(
            status=status,
            pain_score=pain,
            message=alerts[0].message if alerts else "Within normal range",
            metrics={
                "z_score": latest_z,
                "baseline": bl.mean,
                "current": bl.history[-1].value if bl.history else None,
                "confidence": bl.confidence,
                "phase": bl.phase,
            },
            alerts=alerts,
            timestamp=time.time(),
        )

    def _system_health(self) -> HealthReport:
        """Composite health across ALL metrics."""
        if not self.baselines:
            return HealthReport(HealthStatus.LEARNING, 0.0, "No metrics observed yet")

        reports = {m: self._metric_health(m) for m in self.baselines}

        worst = max(reports.values(), key=lambda r: r.pain_score)
        avg_pain = sum(r.pain_score for r in reports.values()) / len(reports)

        all_alerts = []
        for r in reports.values():
            all_alerts.extend(r.alerts)

        return HealthReport(
            status=worst.status,
            pain_score=avg_pain,
            message=f"{len(all_alerts)} alerts across {len(self.baselines)} metrics",
            metrics={m: r.metrics for m, r in reports.items()},
            alerts=all_alerts,
            timestamp=time.time(),
        )

    # Self-Healing

    def on_warning(self, metric: str, handler: Callable):
        """Register a healing action for warning state."""
        self._register_healer(metric, "warning", handler)

    def on_critical(self, metric: str, handler: Callable):
        """Register a healing action for critical state."""
        self._register_healer(metric, "critical", handler)

    def _register_healer(self, metric: str, severity: str, handler: Callable):
        if metric not in self.healers:
            self.healers[metric] = {}
        if severity not in self.healers[metric]:
            self.healers[metric][severity] = []
        self.healers[metric][severity].append(handler)

    def _try_heal(self, metric: str, alert: Alert):
        handlers = self.healers.get(metric, {}).get(alert.severity, [])
        for handler in handlers:
            try:
                handler(alert)
                action = HealingAction(
                    system="immune",
                    action=handler.__name__,
                    reason=alert.message,
                    timestamp=time.time(),
                    success=True,
                )
                self.healing_log.append(action)
            except Exception as e:
                action = HealingAction(
                    system="immune",
                    action=handler.__name__,
                    reason=str(e),
                    timestamp=time.time(),
                    success=False,
                )
                self.healing_log.append(action)
