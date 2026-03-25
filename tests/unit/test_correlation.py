"""Tests for CorrelationEngine."""

from sentinel.core.correlation import CorrelationEngine


def test_detects_positive_correlation():
    c = CorrelationEngine(min_samples=5)
    for i in range(10):
        c.update_single("a", float(i))
        c.update_single("b", float(i) * 2)
    results = c.analyze()
    assert len(results) >= 1
    assert results[0].direction == "positive"


def test_syndrome_diagnosis():
    c = CorrelationEngine()
    matches = c.diagnose(
        current_z={"output_quality": -1.5, "latency": 1.6, "response_length": 1.2},
        trends={"output_quality": "falling", "latency": "rising", "response_length": "rising"},
    )
    assert len(matches) >= 1
