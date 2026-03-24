from sentinel import Organism


def test_organism_can_observe_metric():
    body = Organism("test")
    body.observe("conversion", 0.4)
    assert "conversion" in body.immune.baselines
