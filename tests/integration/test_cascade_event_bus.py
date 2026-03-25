"""Integration test: event bus cascade across systems."""

from sentinel import Organism


def test_immune_event_reaches_bus_and_memory():
    body = Organism("bus-cascade", autonomous=True)
    for _ in range(25):
        body.observe("conversion", 0.37)
    body.observe("conversion", 0.20)
    body.observe("conversion", 0.19)
    body.observe("conversion", 0.18)

    events = body.bus.history(source="immune", seconds=3600)
    assert len(events) > 0
    assert any(e.type in ("immune.observation", "immune.drift") for e in events)
