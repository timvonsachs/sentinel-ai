"""
The Event Bus — The organism's central nervous system.
"""

from typing import Callable, Dict, List, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import time


@dataclass
class Event:
    """An event flowing through the organism."""

    type: str
    source: str
    data: Dict[str, Any]
    severity: int = 0
    timestamp: float = field(default_factory=time.time)

    @property
    def domain(self) -> str:
        return self.type.split(".")[0] if "." in self.type else self.type


class EventBus:
    """Central event system for the organism."""

    def __init__(self, max_history: int = 5000):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._history: List[Event] = []
        self._max_history = max_history
        self._muted: Set[str] = set()
        self._event_counts: Dict[str, int] = defaultdict(int)

    def on(self, event_type: str, handler: Callable):
        self._subscribers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable = None):
        if handler:
            self._subscribers[event_type] = [h for h in self._subscribers[event_type] if h != handler]
        else:
            self._subscribers[event_type] = []

    def emit(self, event: Event):
        if event.type in self._muted:
            return

        self._history.append(event)
        self._event_counts[event.type] += 1
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

        handlers = set()

        for handler in self._subscribers.get(event.type, []):
            handlers.add(id(handler))
            self._safe_call(handler, event)

        domain_wild = f"{event.domain}.*"
        for handler in self._subscribers.get(domain_wild, []):
            if id(handler) not in handlers:
                handlers.add(id(handler))
                self._safe_call(handler, event)

        if "." in event.type:
            suffix = event.type.split(".", 1)[1]
            suffix_wild = f"*.{suffix}"
            for handler in self._subscribers.get(suffix_wild, []):
                if id(handler) not in handlers:
                    handlers.add(id(handler))
                    self._safe_call(handler, event)

        for handler in self._subscribers.get("*", []):
            if id(handler) not in handlers:
                handlers.add(id(handler))
                self._safe_call(handler, event)

    def _safe_call(self, handler: Callable, event: Event):
        try:
            handler(event)
        except Exception:
            pass

    def mute(self, event_type: str):
        self._muted.add(event_type)

    def unmute(self, event_type: str):
        self._muted.discard(event_type)

    def history(
        self,
        event_type: str = None,
        source: str = None,
        min_severity: int = 0,
        seconds: float = 3600,
    ) -> List[Event]:
        cutoff = time.time() - seconds
        results = [e for e in self._history if e.timestamp > cutoff]
        if event_type:
            results = [e for e in results if e.type == event_type]
        if source:
            results = [e for e in results if e.source == source]
        if min_severity > 0:
            results = [e for e in results if e.severity >= min_severity]
        return results

    def stats(self) -> Dict:
        return {
            "total_events": sum(self._event_counts.values()),
            "by_type": dict(self._event_counts),
            "subscribers": {k: len(v) for k, v in self._subscribers.items()},
            "history_size": len(self._history),
            "muted": list(self._muted),
        }
