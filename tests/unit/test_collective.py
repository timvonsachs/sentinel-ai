from sentinel.performance.collective_intelligence import CollectiveIntelligence


def test_collective_shares_and_retrieves_knowledge():
    c = CollectiveIntelligence("team")
    c.join("a")
    c.join("b")
    idx = c.share_learning(
        source="a",
        category="sales",
        insight="Empathy-first improves close rate",
        data={"lift": 0.4},
        effectiveness=0.8,
    )
    c.validate("b", idx)
    best = c.best_practice("sales")
    assert best is not None
    assert "Empathy-first" in best.insight


def test_collective_adoption_rate():
    c = CollectiveIntelligence("team")
    c.join("a")
    c.join("b")
    c.join("c")
    idx = c.share_learning("a", "support", "Use concise responses", {}, 0.7)
    c.validate("b", idx)
    assert c.adoption_rate(idx) == 1 / 3
