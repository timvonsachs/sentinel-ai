"""Metrics exporter placeholders (Prometheus, StatsD)."""

from typing import Dict, Any


def export_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Return exported payload (placeholder)."""
    return metrics
