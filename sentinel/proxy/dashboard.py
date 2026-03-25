"""
Simple dashboard for savings and organism health.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..organism import Organism


def dashboard_html(organism: "Organism") -> str:
    cost_report = organism.router.cost_report()
    total_savings = cost_report.get("total_savings", 0)
    total_cost = cost_report.get("total_cost", 0)
    cost_without = cost_report.get("cost_without_routing", 0)
    savings_pct = cost_report.get("savings_percentage", 0)
    total_queries = cost_report.get("total_queries", 0)

    pain = organism.pain
    state = organism.state
    feeling = organism.feeling

    queries_by_model = cost_report.get("queries_by_model", {})
    model_rows = "".join(
        f"<tr><td>{model}</td><td>{count}</td><td>{count/max(1,total_queries)*100:.0f}%</td></tr>"
        for model, count in queries_by_model.items()
    )

    state_color = {
        "nascent": "#888",
        "stable": "#00C853",
        "thriving": "#00E676",
        "stressed": "#FFB300",
        "sick": "#FF5722",
        "healing": "#FF9100",
        "recovering": "#29B6F6",
        "hibernating": "#9E9E9E",
    }.get(state, "#888")

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Sentinel Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: #0a0a0f; color: #eee; font-family: -apple-system, sans-serif; padding: 24px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 24px; margin-bottom: 4px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 32px; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: #111119; border-radius: 12px; padding: 20px; }}
        .card-label {{ font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; }}
        .card-value {{ font-size: 32px; font-weight: 700; margin-top: 8px; }}
        .card-sub {{ font-size: 13px; color: #888; margin-top: 4px; }}
        .savings {{ color: #00E676; }}
        .state {{ color: {state_color}; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #222; font-size: 14px; }}
        th {{ color: #666; font-size: 11px; text-transform: uppercase; }}
        .footer {{ margin-top: 32px; text-align: center; color: #333; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sentinel Dashboard</h1>
        <p class="subtitle">Your AI is alive. One line of code.</p>
        <div class="grid">
            <div class="card">
                <div class="card-label">Total Savings</div>
                <div class="card-value savings">${total_savings:.2f}</div>
                <div class="card-sub">{savings_pct:.0f}% cheaper than without Sentinel</div>
            </div>
            <div class="card">
                <div class="card-label">Total Queries</div>
                <div class="card-value">{total_queries:,}</div>
                <div class="card-sub">Cost: ${total_cost:.2f} (was ${cost_without:.2f})</div>
            </div>
            <div class="card">
                <div class="card-label">Organism Health</div>
                <div class="card-value state">{state.upper()}</div>
                <div class="card-sub">Pain: {pain:.2f} - {feeling}</div>
            </div>
        </div>
        <div class="card">
            <div class="card-label">Model Routing Distribution</div>
            <table>
                <tr><th>Model</th><th>Queries</th><th>Share</th></tr>
                {model_rows}
            </table>
        </div>
        <div class="footer">
            Sentinel AI v0.5.0 - Cloudflare for AI<br>
            Changed one line. Saved ${total_savings:.2f}.
        </div>
    </div>
</body>
</html>"""
