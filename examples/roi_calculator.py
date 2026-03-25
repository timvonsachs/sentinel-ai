"""
ROI calculator for Sentinel Performance Layer.
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.performance.smart_router import SmartRouter, ModelConfig
from sentinel.performance.auto_optimize import AutoOptimizer


def main():
    print("=" * 60)
    print("SENTINEL ROI CALCULATOR")
    print("=" * 60)

    print("\nScenario: 10,000 AI queries per month")
    print("-" * 60)

    router = SmartRouter(default_model="gpt-4o")
    router.add_model(ModelConfig("gpt-4o", 0.005, 0.015, 0.95, 800))
    router.add_model(ModelConfig("gpt-4o-mini", 0.00015, 0.0006, 0.75, 300))
    router.add_model(ModelConfig("claude-sonnet", 0.003, 0.015, 0.90, 600))

    queries = [
        ("What are your business hours?", 200),
        ("How much does shipping cost?", 150),
        ("Can I return my order?", 180),
        ("I need help with a technical issue in my account settings and billing", 300),
        (
            "Analyze this contract and identify key risk clauses affecting liability "
            "in the European market considering recent regulatory changes.",
            800,
        ),
        ("Hello", 50),
        ("Thanks!", 30),
        ("Explain the difference between your premium and basic plans in detail", 500),
        ("Write a comprehensive Q2 marketing strategy with budget and KPI targets", 1200),
        ("What is your refund policy?", 150),
    ]

    total_queries = 10000
    random.seed(7)
    for _ in range(total_queries):
        query, est_output = random.choice(queries)
        decision = router.route(query)
        est_input = len(query.split()) * 2
        router.record_usage(decision.selected_model, est_input, est_output)

    report = router.cost_report()

    print("\nWITHOUT smart routing (all gpt-4o):")
    print(f"  Cost: ${report['cost_without_routing']:.2f}")
    print("\nWITH smart routing:")
    print(f"  Cost: ${report['total_cost']:.2f}")
    print(f"\nSAVINGS: ${report['total_savings']:.2f} ({report['savings_percentage']}%)")
    print("\nModel distribution:")
    for model, count in report["queries_by_model"].items():
        pct = count / total_queries * 100
        print(f"  {model}: {count} queries ({pct:.0f}%)")

    monthly_savings = report["total_savings"]
    yearly_savings = monthly_savings * 12
    print(f"\nProjected yearly savings: ${yearly_savings:.2f}")
    print("Sentinel cost: $588/year ($49/month)")
    print(f"Net savings: ${yearly_savings - 588:.2f}")
    print(f"ROI: {((yearly_savings - 588) / 588 * 100):.0f}x")

    print("\n" + "=" * 60)
    print("AUTO-OPTIMIZATION")
    print("=" * 60)

    optimizer = AutoOptimizer(explore_rate=0.2, min_interactions_per_variant=20)
    optimizer.define_parameter("temperature", type="float", min=0.1, max=1.0, current=0.7)
    optimizer.define_parameter("max_tokens", type="int", min=100, max=2000, current=500)

    for _ in range(500):
        params = optimizer.get_params()
        fitness = 0.5
        temp = params.get("temperature", 0.7)
        tokens = params.get("max_tokens", 500)
        if 0.3 <= temp <= 0.5:
            fitness += 0.2
        if 300 <= tokens <= 700:
            fitness += 0.1
        fitness += random.gauss(0, 0.1)
        fitness = max(0, min(1, fitness))
        optimizer.report_fitness(fitness)

    improvement = optimizer.improvement_so_far()
    if "improvement_percentage" in improvement:
        print(f"Initial performance: {improvement['initial_fitness']:.3f}")
        print(f"Current performance: {improvement['current_fitness']:.3f}")
        print(f"Improvement: {improvement['improvement_percentage']:.1f}%")
        print(f"Generations evolved: {improvement['generations']}")
    else:
        print(f"Still learning: {improvement}")


if __name__ == "__main__":
    main()
