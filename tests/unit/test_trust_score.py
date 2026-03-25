from sentinel.performance.trust_score import TrustScoreEngine


def test_trust_score_penalizes_low_sample_high_risk():
    engine = TrustScoreEngine(min_samples_for_trust=5)
    report = engine.evaluate(
        query="What dosage should I take?",
        response="Take 400mg.",
        category="medical",
        model_confidence=0.95,
    )
    assert report.score < 0.8
    assert report.confidence_level in {"low", "very_low", "medium"}


def test_trust_score_improves_with_recorded_correct_outcomes():
    engine = TrustScoreEngine(min_samples_for_trust=3)
    for _ in range(5):
        engine.evaluate("How much is shipping?", "Shipping is $5.", category="pricing", model_confidence=0.8)
        engine.record_outcome(category="pricing", outcome="correct")

    follow_up = engine.evaluate("How much is shipping to Berlin?", "Shipping is $7.", category="pricing", model_confidence=0.8)
    assert follow_up.historical_accuracy >= 0.9
    assert follow_up.score >= 0.75
