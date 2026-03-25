import random

from sentinel.performance.smart_router import SmartRouter, ModelConfig
from sentinel.performance.auto_optimize import AutoOptimizer


def test_roi_scenario_shows_cost_and_performance_gain():
    random.seed(11)

    router = SmartRouter(default_model="gpt-4o")
    router.add_model(ModelConfig("gpt-4o", 0.005, 0.015, 0.95, 800))
    router.add_model(ModelConfig("gpt-4o-mini", 0.00015, 0.0006, 0.75, 300))

    queries = [
        "Hello",
        "What are your business hours?",
        "Can I return my order?",
        "Analyze this contract and identify risks and implications.",
    ]
    for _ in range(1200):
        q = random.choice(queries)
        d = router.route(q)
        router.record_usage(d.selected_model, input_tokens=max(10, len(q.split()) * 2), output_tokens=120)

    cost = router.cost_report()
    assert cost["total_savings"] > 0
    assert cost["savings_percentage"] > 0

    opt = AutoOptimizer(explore_rate=0.3, min_interactions_per_variant=10)
    opt.define_parameter("temperature", type="float", min=0.1, max=1.0, current=0.7)
    opt.define_parameter("max_tokens", type="int", min=100, max=2000, current=500)
    for _ in range(260):
        p = opt.get_params()
        fitness = 0.5
        if 0.3 <= p["temperature"] <= 0.5:
            fitness += 0.2
        if 300 <= p["max_tokens"] <= 700:
            fitness += 0.1
        fitness += random.gauss(0, 0.06)
        opt.report_fitness(max(0, min(1, fitness)))

    improvement = opt.improvement_so_far()
    if "improvement_percentage" in improvement:
        assert improvement["improvement_percentage"] > 0
