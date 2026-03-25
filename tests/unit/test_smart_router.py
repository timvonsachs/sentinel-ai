from sentinel.performance.smart_router import SmartRouter, ModelConfig


def _router():
    router = SmartRouter(default_model="gpt-4o")
    router.add_model(ModelConfig("gpt-4o", 0.005, 0.015, 0.95, 800))
    router.add_model(ModelConfig("gpt-4o-mini", 0.00015, 0.0006, 0.75, 300))
    return router


def test_router_picks_cheaper_model_for_simple_query():
    router = _router()
    decision = router.route("What are your hours?", required_quality=0.7)
    assert decision.selected_model == "gpt-4o-mini"
    assert decision.savings_vs_default > 0


def test_router_cost_report_tracks_savings():
    router = _router()
    for _ in range(20):
        d = router.route("Hello", required_quality=0.6)
        router.record_usage(d.selected_model, 20, 40)
    report = router.cost_report()
    assert report["total_queries"] == 20
    assert report["total_savings"] >= 0


def test_router_prefers_top_model_for_complex_coding_query():
    router = _router()
    decision = router.route(
        "Write a Python function implementing merge sort with error handling and tests."
    )
    assert decision.selected_model == "gpt-4o"
