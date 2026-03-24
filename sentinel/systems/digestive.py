"""
The Digestive System — Input quality filtering and nutrient extraction.

A human doesn't absorb everything they eat. The digestive system breaks food down,
extracts nutrients, and expels waste. A healthy gut = a healthy organism.

For AI: not all input data is nutritious. Some is irrelevant. Some is poisonous.
Some is empty calories. The digestive system filters, scores, and enriches
input before it reaches the brain (LLM).
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
import time


@dataclass
class DigestedInput:
    """Input after processing through the digestive system."""

    original: str
    processed: str
    quality_score: float  # 0.0 (toxic) to 1.0 (highly nutritious)
    nutrition: Dict[str, Any]  # extracted metadata / enrichment
    waste: List[str]  # what was filtered out
    safe: bool
    timestamp: float = field(default_factory=time.time)


class DigestiveSystem:
    """
    Input quality filtering for AI systems.

    Usage:
        digestive = DigestiveSystem()

        # Add quality rules
        digestive.add_filter("remove_pii", detect_and_redact_pii)
        digestive.add_enricher("classify_intent", intent_classifier)
        digestive.add_quality_check("relevance", relevance_scorer)
    """

    def __init__(self):
        self.filters: List[Dict] = []  # remove/redact harmful content
        self.enrichers: List[Dict] = []  # extract nutrition (metadata)
        self.quality_checks: List[Dict] = []  # score input quality
        self.digestion_log: List[DigestedInput] = []
        self.rejection_threshold: float = 0.1  # below this = rejected

    def add_filter(self, name: str, func: Callable):
        """Add an input filter. func(text) -> filtered_text, waste_list"""
        self.filters.append({"name": name, "func": func})

    def add_enricher(self, name: str, func: Callable):
        """Add an input enricher. func(text) -> dict of extracted info"""
        self.enrichers.append({"name": name, "func": func})

    def add_quality_check(self, name: str, func: Callable):
        """Add a quality scorer. func(text) -> float 0-1"""
        self.quality_checks.append({"name": name, "func": func})

    def digest(self, input_text: str) -> DigestedInput:
        """Process input through the full digestive pipeline."""
        processed = input_text
        waste = []
        nutrition = {}

        # 1. Filters (remove harmful content)
        for f in self.filters:
            try:
                result = f["func"](processed)
                if isinstance(result, tuple):
                    processed, filter_waste = result
                    waste.extend(filter_waste)
                else:
                    processed = result
            except Exception as e:
                waste.append(f"filter_error:{f['name']}:{str(e)}")

        # 2. Enrichers (extract nutrition)
        for enricher in self.enrichers:
            try:
                enrichment = enricher["func"](processed)
                if isinstance(enrichment, dict):
                    nutrition[enricher["name"]] = enrichment
            except Exception:
                pass

        # 3. Quality scoring
        quality_scores = []
        for qc in self.quality_checks:
            try:
                score = qc["func"](processed)
                quality_scores.append(score)
            except Exception:
                pass

        quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

        # 4. Basic quality heuristics (always active)
        if len(processed.strip()) < 2:
            quality *= 0.1
        if processed == processed.upper() and len(processed) > 20:
            quality *= 0.7  # ALL CAPS usually = angry/spam

        safe = quality >= self.rejection_threshold

        result = DigestedInput(
            original=input_text,
            processed=processed,
            quality_score=round(quality, 3),
            nutrition=nutrition,
            waste=waste,
            safe=safe,
        )
        self.digestion_log.append(result)

        return result

    def health(self) -> Dict:
        """Digestive system health: are we getting good nutrition?"""
        if not self.digestion_log:
            return {"status": "empty", "avg_quality": 0}

        recent = self.digestion_log[-50:]
        avg_quality = sum(d.quality_score for d in recent) / len(recent)
        rejection_rate = sum(1 for d in recent if not d.safe) / len(recent)

        return {
            "avg_quality": round(avg_quality, 3),
            "rejection_rate": round(rejection_rate, 3),
            "total_processed": len(self.digestion_log),
            "total_waste_items": sum(len(d.waste) for d in recent),
        }
