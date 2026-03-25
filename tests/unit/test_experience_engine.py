from sentinel.performance.experience_engine import ExperienceEngine


def test_experience_engine_records_and_builds_insights():
    engine = ExperienceEngine()
    ids = []
    for _ in range(8):
        iid = engine.record(
            input_text="This is too expensive, can you help?",
            output_text="I understand. Let me show value first.",
            category="sales",
        )
        ids.append(iid)
    for iid in ids:
        engine.record_outcome(iid, 0.85)
    insights = engine.get_insights(category="sales", min_confidence=0.1, min_evidence=5)
    assert len(insights) > 0


def test_experience_engine_recommendations_return_strings():
    engine = ExperienceEngine()
    for _ in range(10):
        iid = engine.record("I want a refund", "I can help with your refund request.", category="support")
        engine.record_outcome(iid, 0.2)
    recs = engine.recommend("Refund please, this is urgent", category="support")
    assert isinstance(recs, list)
