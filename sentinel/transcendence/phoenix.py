"""
Phoenix Metamorphosis — Fundamental self-restructuring.

Not repair. Not healing. TRANSFORMATION.
The caterpillar dissolves completely. Every cell.
"""

from typing import Dict, Callable, Optional, Any, List
from dataclasses import dataclass, field
import time


@dataclass
class MetamorphosisEvent:
    from_form: str
    to_form: str
    reason: str
    success: bool
    duration: float
    timestamp: float = field(default_factory=time.time)


class PhoenixMetamorphosis:
    """
    Fundamental self-restructuring for AI systems.
    """

    def __init__(self):
        self.forms: Dict[str, Dict] = {}
        self.current_form: Optional[str] = None
        self.metamorphosis_log: List[MetamorphosisEvent] = []
        self.auto_metamorphose: bool = False
        self.form_evaluators: Dict[str, Callable] = {}

    def form(self, name: str, config: Dict[str, Any], builder: Callable = None):
        """Define a possible form the system can take."""
        self.forms[name] = {"config": config, "builder": builder}
        if not self.current_form:
            self.current_form = name

    def add_evaluator(self, form_name: str, evaluator: Callable):
        """Add scorer for how well a form fits current needs."""
        self.form_evaluators[form_name] = evaluator

    def best_form(self, context: Dict = None) -> Optional[str]:
        """Determine the best form for current conditions."""
        if not self.form_evaluators:
            return self.current_form

        scores = {}
        for name, evaluator in self.form_evaluators.items():
            try:
                scores[name] = evaluator(context)
            except Exception:
                scores[name] = 0

        if not scores:
            return self.current_form

        return max(scores, key=scores.get)

    def metamorphose(self, target_form: str, reason: str = "") -> bool:
        """Transform into a different form."""
        if target_form not in self.forms:
            return False

        if target_form == self.current_form:
            return True

        old_form = self.current_form
        start = time.time()

        try:
            builder = self.forms[target_form].get("builder")
            if builder:
                builder(self.forms[target_form]["config"])

            self.current_form = target_form
            duration = time.time() - start
            event = MetamorphosisEvent(
                from_form=old_form or "none",
                to_form=target_form,
                reason=reason,
                success=True,
                duration=duration,
            )
            self.metamorphosis_log.append(event)
            return True

        except Exception as e:
            duration = time.time() - start
            event = MetamorphosisEvent(
                from_form=old_form or "none",
                to_form=target_form,
                reason=f"Failed: {str(e)}",
                success=False,
                duration=duration,
            )
            self.metamorphosis_log.append(event)
            return False

    def auto_adapt(self, context: Dict = None) -> Optional[str]:
        """Automatically metamorphose if a better form exists."""
        if not self.auto_metamorphose:
            return self.current_form

        best = self.best_form(context)
        if best and best != self.current_form:
            self.metamorphose(best, reason="Auto-adaptation to context")

        return self.current_form

    def status(self) -> Dict:
        return {
            "current_form": self.current_form,
            "available_forms": list(self.forms.keys()),
            "total_metamorphoses": len(self.metamorphosis_log),
            "config": self.forms[self.current_form]["config"] if self.current_form in self.forms else {},
        }
