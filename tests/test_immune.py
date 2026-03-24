from sentinel.systems.immune import ImmuneSystem


def test_immune_starts_in_learning():
    immune = ImmuneSystem()
    report = immune.health("missing")
    assert report.status.value == "learning"
