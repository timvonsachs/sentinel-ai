"""Tests for EventBus."""

from sentinel.core.event_bus import EventBus, Event


def test_exact_and_wildcard_subscription():
    bus = EventBus()
    hit = {"exact": 0, "domain": 0, "all": 0}

    bus.on("immune.drift", lambda e: hit.__setitem__("exact", hit["exact"] + 1))
    bus.on("immune.*", lambda e: hit.__setitem__("domain", hit["domain"] + 1))
    bus.on("*", lambda e: hit.__setitem__("all", hit["all"] + 1))

    bus.emit(Event(type="immune.drift", source="immune", data={}))
    assert hit["exact"] == 1
    assert hit["domain"] == 1
    assert hit["all"] == 1


def test_mute_blocks_events():
    bus = EventBus()
    hit = {"n": 0}
    bus.on("x", lambda e: hit.__setitem__("n", hit["n"] + 1))
    bus.mute("x")
    bus.emit(Event(type="x", source="t", data={}))
    assert hit["n"] == 0
