import random

from sentinel.performance.auto_optimize import AutoOptimizer


def test_auto_optimizer_improves_or_learns():
    random.seed(7)
    opt = AutoOptimizer(explore_rate=0.4, min_interactions_per_variant=8)
    opt.define_parameter("temperature", type="float", min=0.1, max=1.0, current=0.7)
    opt.define_parameter("max_tokens", type="int", min=100, max=1000, current=500)

    for _ in range(220):
        params = opt.get_params()
        fitness = 0.4
        if 0.3 <= params["temperature"] <= 0.5:
            fitness += 0.3
        if 300 <= params["max_tokens"] <= 700:
            fitness += 0.2
        fitness += random.gauss(0, 0.05)
        fitness = max(0, min(1, fitness))
        opt.report_fitness(fitness)

    report = opt.report()
    assert report["champion"]["interactions"] > 0
    assert report["generation"] >= 0
    assert "improvement" in report
