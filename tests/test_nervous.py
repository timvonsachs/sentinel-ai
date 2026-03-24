from sentinel.systems.nervous import NervousSystem


def test_nervous_reflex_triggers():
    system = NervousSystem()
    called = {"ok": False}

    def action(_):
        called["ok"] = True

    system.reflex("latency", lambda m: m["latency"] > 100, action)
    triggered = system.signal({"latency": 200})
    assert "latency" in triggered
    assert called["ok"]
