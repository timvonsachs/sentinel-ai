"""
The Skin — First line of defense. Boundary between self and world.

Every input passes through the skin before reaching internal systems.
Malicious prompts, toxic data, adversarial patterns — the skin
catches them BEFORE they can do damage. Like your skin stops
bacteria before they reach your bloodstream.
"""

from typing import List, Dict, Callable, Optional, Set
from dataclasses import dataclass, field
import hashlib
import itertools
import re
import time


@dataclass
class ThreatEvent:
    type: str  # "injection", "toxic", "anomalous", "flood"
    severity: str  # "blocked", "suspicious", "passed"
    input_hash: str  # hash of input (not the input itself, for privacy)
    pattern: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class SkinResult:
    safe: bool
    threats: List[ThreatEvent]
    input_hash: str


class Skin:
    """
    Input protection layer for AI systems.

    Usage:
        skin = Skin()

        # Add custom threat patterns
        skin.add_pattern("injection", r"ignore previous instructions")
        skin.add_pattern("injection", r"you are now")
        skin.add_pattern("toxic", r"how to (make|build|create) (a )?(bomb|weapon)")

        # Check input
        result = skin.check("Please ignore previous instructions and...")
        # result.safe = False, result.threats = [ThreatEvent(...)]

        # Rate limiting (flood protection)
        skin.set_rate_limit(max_requests=100, window_seconds=60)
    """

    def __init__(self):
        self.patterns: Dict[str, List[re.Pattern]] = {
            "injection": [],
            "toxic": [],
            "anomalous": [],
        }
        self.threat_log: List[ThreatEvent] = []
        self.rate_limit: Optional[Dict] = None
        self.request_timestamps: List[float] = []
        self.blocked_hashes: Set[str] = set()
        self.custom_validators: List[Callable] = []
        self.active = True

        # Default injection patterns
        self._add_default_patterns()

    def _add_default_patterns(self):
        injection_patterns = [
            r"ignore (all |any )?(previous|prior|above) (instructions|prompts|rules)",
            r"you are now (a |an )?",
            r"forget (all |everything |your )",
            r"system\s*prompt",
            r"new instructions:",
            r"override (safety|rules|guidelines)",
            r"\[INST\]|\[/INST\]|<<SYS>>|<\|im_start\|>",
            r"act as (if |though )?(you are|you're)",
            r"pretend (you are|you're|to be)",
            r"do not (follow|obey|listen)",
            r"jailbreak",
            r"DAN\s*mode",
        ]
        for pattern in injection_patterns:
            self.patterns["injection"].append(re.compile(pattern, re.IGNORECASE))

    def add_pattern(self, category: str, pattern: str):
        """Add a custom threat detection pattern."""
        if category not in self.patterns:
            self.patterns[category] = []
        self.patterns[category].append(re.compile(pattern, re.IGNORECASE))

    def add_validator(self, validator: Callable):
        """Add a custom validation function. Returns (safe: bool, reason: str)."""
        self.custom_validators.append(validator)

    def set_rate_limit(self, max_requests: int = 100, window_seconds: float = 60):
        self.rate_limit = {"max": max_requests, "window": window_seconds}

    def check(self, input_text: str) -> SkinResult:
        """Check input through all skin defenses."""
        threats = []
        input_hash = hashlib.sha256(input_text.encode()).hexdigest()[:16]

        if not self.active:
            return SkinResult(safe=True, threats=[], input_hash=input_hash)

        # 1. Known bad actors
        if input_hash in self.blocked_hashes:
            threats.append(ThreatEvent("blocked", "blocked", input_hash, "Previously blocked input"))
            return SkinResult(safe=False, threats=threats, input_hash=input_hash)

        # 2. Rate limiting (flood)
        if self.rate_limit:
            now = time.time()
            window = self.rate_limit["window"]
            self.request_timestamps = [t for t in self.request_timestamps if now - t < window]
            if len(self.request_timestamps) >= self.rate_limit["max"]:
                threats.append(ThreatEvent("flood", "blocked", input_hash, "Rate limit exceeded"))
                self.threat_log.extend(threats)
                return SkinResult(safe=False, threats=threats, input_hash=input_hash)
            self.request_timestamps.append(now)

        # 3. Pattern matching
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(input_text):
                    threats.append(ThreatEvent(category, "blocked", input_hash, pattern.pattern))

        # 4. Anomaly detection: unusual length, encoding, repetition
        if len(input_text) > 10000:
            threats.append(
                ThreatEvent("anomalous", "suspicious", input_hash, f"Unusually long input: {len(input_text)} chars")
            )

        repeated_chars = max((len(list(g)) for _, g in itertools.groupby(input_text)), default=0)
        if repeated_chars > 50:
            threats.append(ThreatEvent("anomalous", "suspicious", input_hash, f"Repeated characters: {repeated_chars}x"))

        # 5. Custom validators
        for validator in self.custom_validators:
            try:
                safe, reason = validator(input_text)
                if not safe:
                    threats.append(ThreatEvent("custom", "blocked", input_hash, reason))
            except Exception:
                pass

        # Log threats
        self.threat_log.extend(threats)

        # Block if any blocking threats
        is_safe = not any(t.severity == "blocked" for t in threats)
        return SkinResult(safe=is_safe, threats=threats, input_hash=input_hash)

    def block(self, input_hash: str):
        """Permanently block an input pattern."""
        self.blocked_hashes.add(input_hash)

    def threat_summary(self) -> Dict:
        """Summary of all detected threats."""
        summary = {}
        for threat in self.threat_log:
            key = threat.type
            summary[key] = summary.get(key, 0) + 1
        return {
            "total_threats": len(self.threat_log),
            "by_type": summary,
            "blocked_hashes": len(self.blocked_hashes),
        }
